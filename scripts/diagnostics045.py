"""Frozen-state diagnostic adapters; no target environment or execution entry point.

Every fit is an explicitly separate retained copy. Replay never calls an
interface or scheduler and never returns a replayed learner to acquisition.
The accounting convention remains declared named work and logical payload
reservations; it is not complete Python allocation/instruction accounting.
"""
from __future__ import annotations

import copy
import hashlib
from fractions import Fraction
from itertools import count

from accounting043 import Limit, Meter, bits, rational_operation
from reference_n1_043 import GenericReader, History, N1, Transition, tree_size
from reference_n3_043 import NUMERIC, UPDATE_COMPLETE, _prediction_log, brier, plain

_OWNERS = count()


def _tuple(value):
    return tuple(_tuple(x) for x in value) if isinstance(value, (tuple, list)) else value


def _history(value):
    return History(_tuple(value["observations"]), tuple(value["actions"]))


def _sha(value, meter):
    raw = meter.encode(value)
    meter.charge("diagnostic.sha256_input_bytes", len(raw), bits=8)
    return hashlib.sha256(raw).hexdigest()


def table_sha256(transitions, meter):
    meter.charge("diagnostic.table_state_view", len(transitions))
    return _sha([row.state() for row in transitions], meter)


def _fraction(value):
    if isinstance(value, Fraction):
        return value
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {"numerator", "denominator"}:
        return Fraction(value["numerator"], value["denominator"])
    raise ValueError("exact rational value required")


class PrescribedReader(N1):
    """Fit exact N1 counts on T at a supplied Phi; feature selection is absent."""

    def __init__(self, *, W=2, S=3, K=4, observation_alphabets=((0, 1, 2, 3, 4),),
                 actions=(0, 1, 2, 3, 4), meter=None):
        self._fit_complete = False
        self._fit_started = False
        self.source_table_sha256 = None
        self.source_phi_sha256 = None
        super().__init__(W=W, S=S, K=K, observation_alphabets=observation_alphabets,
                         actions=actions, meter=meter)

    @property
    def counts_ready(self):
        return self._fit_complete and super().counts_ready

    def _validate_predicate(self, predicate):
        self.meter.charge("diagnostic.predicate_syntax_node")
        if not isinstance(predicate, tuple) or not predicate or type(predicate[0]) is not int:
            raise ValueError("invalid prescribed predicate")
        op = predicate[0]
        if op == 0:
            if len(predicate) != 3:
                raise ValueError("invalid equality arity")
            left, right = predicate[1:]
            for term in (left, right):
                if not isinstance(term, tuple) or not all(type(x) is int for x in term):
                    raise ValueError("invalid typed operand")
                if len(term) == 4 and term[0] == 0:
                    _, typ, field, lag = term
                    if typ == 0 and 0 <= field < len(self.observation_alphabets) and 0 <= lag <= self.W:
                        continue
                    if typ == 1 and field == 0 and 1 <= lag <= self.W:
                        continue
                if len(term) == 3 and term[0] == 1:
                    _, typ, token = term
                    alphabet = set(x for a in self.observation_alphabets for x in a) if typ == 0 else self.actions if typ == 1 else ()
                    self.meter.charge("diagnostic.constant_membership", len(alphabet))
                    if token in alphabet:
                        continue
                raise ValueError("operand outside declared grammar")
            if left[0] != 0 or left[1] != right[1]:
                raise ValueError("equality must have a left term and matching types")
        elif op in (1, 2, 3) and len(predicate) == (2 if op == 1 else 3):
            for child in predicate[1:]:
                self._validate_predicate(child)
        else:
            raise ValueError("invalid Boolean constructor")

    def fit(self, transitions, Phi):
        if self._fit_started:
            raise ValueError("fit once on one prescribed frozen table and partition")
        self._fit_started = True
        predicates = _tuple(Phi)
        if not isinstance(predicates, tuple) or len(predicates) > self.K or len(set(predicates)) != len(predicates):
            raise ValueError("invalid prescribed predicate list")
        try:
            for predicate in predicates:
                self._validate_predicate(predicate)
                self.meter.charge("diagnostic.predicate_size_traversal", tree_size(predicate))
                if tree_size(predicate) > self.S:
                    raise ValueError("prescribed tree exceeds S")
            raw = self.meter.encode(predicates)
            self._reserve(len(raw) + 256)
            self.meter.charge("diagnostic.prescribed_phi_copy_bytes", len(raw))
            self.Phi = copy.deepcopy(list(predicates))
            self.phi_version = len(predicates)
            self.source_phi_sha256 = _sha(predicates, self.meter)
            # Frozen043 implementation validates and copies every Transition,
            # then rebuilds counts once. It never calls append or _search.
            return GenericReader.fit(self, transitions)
        except Limit as error:
            self.search_status = error.status
            return {"status": error.status, "counts_ready": False,
                    "source_table_sha256": self.source_table_sha256}

    def state(self):
        result = super().state()
        result.update(kind="PRESCRIBED_PARTITION_READER_045_v1", fit_complete=self._fit_complete,
                      fit_started=self._fit_started, source_table_sha256=self.source_table_sha256,
                      source_phi_sha256=self.source_phi_sha256, feature_search_requested=False)
        return result


class DiagnosticSession:
    """Own retained diagnostic outputs and exact copies until explicit close."""

    def __init__(self, meter=None):
        self.meter = meter or Meter()
        self.owner = "diagnostic045_" + str(next(_OWNERS))
        self.records = []
        self.readers = []
        self.meter.retain(self.owner, self.records)

    def retain(self, record):
        raw = self.meter.encode(record)
        self.meter.reserve(self.owner, self.meter.owners.get(self.owner, 0) + len(raw) + 32)
        self.meter.charge("diagnostic.provenance_materialization_bytes", len(raw))
        # This exact record is retained, not a second unaccounted deepcopy.
        # Callers must not mutate retained records or borrowed source objects.
        self.records.append(record)
        self.meter.retain(self.owner, self.records)
        return record

    def close(self):
        for reader in self.readers:
            reader.close()
        self.readers.clear()
        self.meter.release(self.owner)


def choose_goal(reader, history, goal, session):
    """All five opaque action forecasts; exact goal probability, numeric ties.

    A nonnumeric prediction blocks the decision. A global meter refusal stops
    immediately, with unattempted actions recorded; no residual-budget refill.
    No selected action is executed here and no outcome is used for training.
    """
    meter = session.meter
    if reader.meter is not meter:
        raise ValueError("reader and chooser require the same meter")
    if tuple(reader.actions) != (0, 1, 2, 3, 4):
        raise ValueError("chooser requires opaque action indices 0 through 4 in that order")
    goal = tuple(goal)
    result = {"status": "DECISION_UNAVAILABLE", "goal": list(goal), "action": None,
              "predictions": [], "unattempted_actions": [], "cause": None}
    try:
        if len(goal) != len(reader.observation_alphabets) or any(type(v) is not int or v not in alphabet for v, alphabet in zip(goal, reader.observation_alphabets)):
            raise ValueError("goal outside declared observation alphabet")
        meter.charge("diagnostic.chooser_history_input", len(meter.encode(history.state())))
        best_action, best_probability = None, None
        unavailable = False
        for action in reader.actions:
            meter.charge("diagnostic.chooser_action_request")
            refusal_start = len(meter.refusals)
            prediction = reader.predict(history, action, log=False)
            probability = (prediction.get("probabilities") or {}).get(goal)
            numeric = prediction.get("status") in NUMERIC and (type(probability) is int or isinstance(probability, Fraction))
            if numeric:
                probability = Fraction(probability)
                numeric = 0 <= probability <= 1
            logged = (_prediction_log(prediction) if probability is None or type(probability) is int or isinstance(probability, Fraction)
                      else {"status": prediction.get("status"), "features": plain(prediction.get("features")),
                            "probabilities": None, "invalid_exact_probability_type": type(probability).__name__})
            logged.update(action=action, required_goal_probability=plain(probability) if numeric else None)
            result["predictions"].append(logged)
            if len(meter.refusals) > refusal_start:
                result["cause"] = meter.refusals[-1]["status"]
                result["unattempted_actions"] = list(reader.actions[action + 1:])
                return result
            if not numeric:
                unavailable = True
                continue
            meter.charge("diagnostic.chooser_exact_rational_compare", bits=bits(probability) * bits(best_probability or 0))
            if best_probability is None or probability > best_probability:
                best_action, best_probability = action, probability
        if unavailable:
            result["cause"] = "REQUIRED_PREDICTION_NONNUMERIC"
        else:
            result.update(status="AVAILABLE", action=best_action, goal_probability=plain(best_probability))
        return session.retain(result)
    except Limit as error:
        result["cause"] = error.status
        attempted = {row["action"] for row in result["predictions"]}
        result["unattempted_actions"] = [a for a in reader.actions if a not in attempted]
        # At a terminal refusal, already allocated partial output is returned;
        # no new retained-memory exactness or successful seal is asserted.
        result["retained_payload_sealed"] = False
        return result


def partition_controls(transitions, Phi, session, **configuration):
    """Selected, every single deletion, and prescribed ORDER0/1/2, same T."""
    source_sha = table_sha256(transitions, session.meter)
    partitions = [("SELECTED", tuple(Phi))]
    partitions += [("DELETE_" + str(i), tuple(Phi[:i]) + tuple(Phi[i + 1:])) for i in range(len(Phi))]
    readers = {}
    for name, predicates in partitions:
        reader = PrescribedReader(meter=session.meter, **configuration)
        session.readers.append(reader)
        fit = reader.fit(transitions, predicates)
        if fit["status"] != "COMPLETE":
            raise Limit(fit["status"])
        if reader.source_table_sha256 != source_sha:
            raise ValueError("same-table identity failed")
        readers[name] = reader
    for order in (0, 1, 2):
        reader = GenericReader(order, observation_alphabets=configuration.get("observation_alphabets", ((0, 1, 2, 3, 4),)),
                               actions=configuration.get("actions", (0, 1, 2, 3, 4)), meter=session.meter)
        session.readers.append(reader)
        fit = reader.fit(transitions)
        if fit["status"] != "COMPLETE":
            raise Limit(fit["status"])
        if reader.source_table_sha256 != source_sha:
            raise ValueError("same-table identity failed")
        readers["ORDER" + str(order)] = reader
    session.retain({"kind": "PARTITION_CONTROLS_045_v1", "source_table_sha256": source_sha,
                    "readers": {name: {"source_table_sha256": reader.source_table_sha256,
                              "Phi": plain(reader.Phi), "order": getattr(reader, "order", None)} for name, reader in readers.items()},
                    "pending_evidence_added": False, "feature_search_requested": False})
    return readers


def replay_acquisition(source, final_learner_state, session):
    """Reconstruct retained N1 update order from immutable043 acquisition state.

    Every event/history/assimilation marker is checked against chronological
    physical evidence. Pre/post trial states must match original snapshot hashes.
    Mid-append resource cursor progress is not fully exposed by043's event log;
    if it prevents final-state equality, report unavailable, never verified.
    """
    meter = session.meter
    config = copy.deepcopy(final_learner_state["configuration"])
    if source.get("kind") != "N3_REFERENCE_STATE_043_v1" or final_learner_state.get("block") != 0 or final_learner_state.get("archives"):
        raise ValueError("replay requires the declared empty-state single block")
    learner = N1(meter=meter, **config)
    session.readers.append(learner)
    source_copy_bytes = len(meter.encode({"source": source, "final": final_learner_state}))
    meter.charge("diagnostic.replay_source_copy_bytes", source_copy_bytes)
    source, final_learner_state = copy.deepcopy(source), copy.deepcopy(final_learner_state)
    session.retain({"kind": "REPLAY_SOURCE_COPY_045_v1", "source": source, "final_learner_state": final_learner_state})
    boundaries, trace = [], []
    events = source["events"]
    if source["environment_calls"] != len(events) or source["learner_transition_count"] != len(final_learner_state["transitions"]):
        raise ValueError("event or retained transition cardinality mismatch")
    physical_history = None
    stopped = False
    pending_indices = [r["event_index"] for r in source["pending_validation"]]
    unassimilated_validation = []
    expected_event_index = 0

    def capture():
        state = learner.state()
        meter.charge("diagnostic.replay_boundary_copy_bytes", len(meter.encode({"T": [r.state() for r in learner.T], "Phi": learner.Phi})))
        return {"T": copy.deepcopy(learner.T), "Phi": copy.deepcopy(learner.Phi),
                "snapshot_sha256": _sha(state, meter), "table_sha256": table_sha256(learner.T, meter)}

    def append_event(event, phase):
        nonlocal stopped
        if stopped:
            raise ValueError("assimilation after retained pending suffix")
        result = learner.append(_history(event["before"]), event["action"], tuple(event["outcome"]))
        trace.append({"operation": "APPEND", "event_index": event["index"], "phase": phase,
                      "table_size": len(learner.T), "Phi": plain(learner.Phi), "status": result["status"],
                      "observed_constants": [sorted(v) for v in learner.observed]})
        if result["status"] not in UPDATE_COMPLETE:
            raise Limit(result["status"])

    for trial_index, trial in enumerate(source["trials"]):
        if trial["id"] != trial_index:
            raise ValueError("trial identity is not sequential")
        trial_events = [event for event in events if event["trial_id"] == trial_index]
        meter.charge("diagnostic.replay_trial_event_scan", len(events))
        if not trial_events:
            if trial_index != len(source["trials"]) - 1 or trial.get("status") not in ("RESERVED", "INCOMPLETE") or source["status"] in ("READY", "RUNNING", "SEARCH_SPACE_EXHAUSTED"):
                raise ValueError("empty-event trial is not a terminal reservation")
            continue  # A reserved next trial may fail before its first call.
        warmup = trial.get("phase") == "WARMUP"
        if warmup and (trial_index >= len(learner.actions) or trial["counter_t"] != 0 or list(trial["word"]) != [learner.actions[trial_index]]):
            raise ValueError("warmup word or counter disagrees with supplied action order")
        pre = capture() if not warmup else None
        if pre and trial.get("before_snapshot_sha256") and pre["snapshot_sha256"] != trial["before_snapshot_sha256"]:
            raise ValueError("pre-trial snapshot mismatch")
        trial_rows, validation_rows = [], []
        validation_started = False
        post = None
        for event in trial_events:
            meter.charge("diagnostic.replay_event_validation")
            if event["index"] != expected_event_index or event["call"] != expected_event_index + 1 or event["block_id"] != source["block_id"]:
                raise ValueError("event ordering or block mismatch")
            expected_event_index += 1
            if event["counter_t"] != trial["counter_t"]:
                raise ValueError("trial counter mismatch")
            phase = event["phase"]
            if phase not in (("WARMUP",) if warmup else ("TRIAL", "VALIDATION")):
                raise ValueError("event phase mismatches trial")
            if phase == "VALIDATION":
                if not validation_started:
                    post = capture()
                    validation_started = True
                validation_rows.append(event)
            else:
                if validation_started:
                    raise ValueError("trial action after validation")
                trial_rows.append(event)
            if event["kind"] == "RESET":
                if event["action"] is not None or event["before"] is not None or phase == "VALIDATION" or len(trial_rows) != 1:
                    raise ValueError("invalid RESET boundary")
            elif event["kind"] == "PRIMITIVE":
                if physical_history is None or _history(event["before"]) != physical_history or event["action"] not in learner.actions:
                    raise ValueError("event history is not chronological physical history")
            else:
                raise ValueError("unknown event kind")
            if event["status"] != "COMPLETED":
                if event["status"] not in ("ISSUED", "INTERRUPTED") or event["outcome"] is not None or event.get("assimilated") or event is not events[-1]:
                    raise ValueError("invalid interrupted event")
                stopped = True
                trace.append({"operation": "PENDING_ISSUED", "event_index": event["index"], "action": event["action"]})
                continue
            outcome = tuple(event["outcome"])
            physical_history = History.initial(outcome) if event["kind"] == "RESET" else physical_history.advance(event["action"], outcome)
            if event["kind"] == "RESET":
                # The observed RESET token enters N1 before the first action.
                learner.observe_reset(outcome)
                trace.append({"operation": "OBSERVE_RESET", "event_index": event["index"],
                              "table_size": len(learner.T), "observed_constants": [sorted(v) for v in learner.observed]})
            elif phase != "VALIDATION":
                if event.get("assimilated"):
                    append_event(event, "IMMEDIATE_TRIAL")
                else:
                    stopped = True
                    trace.append({"operation": "PENDING_TRIAL", "event_index": event["index"]})
        physically_complete = (trial_rows and trial_rows[0]["kind"] == "RESET" and all(e["status"] == "COMPLETED" for e in trial_rows)
                               and [e["action"] for e in trial_rows[1:]] == list(trial["word"]))
        if (trial["status"] == "COMPLETED") != bool(physically_complete):
            raise ValueError("physical trial completion mismatch")
        if not warmup:
            post = post or capture()
            if trial.get("after_snapshot_sha256") and post["snapshot_sha256"] != trial["after_snapshot_sha256"]:
                raise ValueError("post-trial snapshot mismatch")
            if "pre_table_size" in trial and trial["pre_table_size"] != len(pre["T"]):
                raise ValueError("pre-trial table size mismatch")
            if "post_table_size" in trial and trial["post_table_size"] != len(post["T"]):
                raise ValueError("post-trial table size mismatch")
            if trial.get("after_snapshot_sha256") and _tuple(trial["new_predicates"]) != tuple(post["Phi"][len(pre["Phi"]):]):
                raise ValueError("fresh-predicate provenance mismatch")
            completed_validation = [e for e in validation_rows if e["status"] == "COMPLETED"]
            if [r["event_index"] for r in trial["validation"]] != [e["index"] for e in completed_validation]:
                raise ValueError("validation provenance mismatch")
            for row, event in zip(trial["validation"], completed_validation):
                if row["before"] != event["before"] or row["action"] != event["action"] or row["outcome"] != event["outcome"]:
                    raise ValueError("validation row differs from physical evidence")
            if completed_validation and trial.get("finalized_before_validation_assimilation") is not True:
                raise ValueError("missing credit-finalization boundary")
            boundaries.append({"trial_id": trial_index, "pre": pre, "post": post, "trial": copy.deepcopy(trial),
                               "validation_events": copy.deepcopy(completed_validation)})
            trace.append({"operation": "FINALIZE_CREDIT", "trial_id": trial_index,
                          "table_size": len(learner.T), "credit_status": trial["credit_status"]})
            for event in completed_validation:
                if event.get("assimilated"):
                    append_event(event, "DELAYED_VALIDATION")
                else:
                    stopped = True
                    unassimilated_validation.append(event["index"])
                    trace.append({"operation": "PENDING_VALIDATION", "event_index": event["index"]})
    if expected_event_index != len(events) or pending_indices != unassimilated_validation:
        raise ValueError("unmatched events or pending-validation suffix")
    if source.get("history") != (plain(physical_history.state()) if physical_history else None):
        raise ValueError("final physical history mismatch")
    final_sha = _sha(learner.state(), meter)
    expected_sha = _sha(final_learner_state, meter)
    status = "VERIFIED" if final_sha == expected_sha else "FINAL_UPDATE_UNAVAILABLE"
    if status != "VERIFIED" and source["status"] not in ("COMPUTATION_INCOMPLETE", "MEMORY_LIMIT"):
        raise ValueError("final learner state mismatch after complete updates")
    report = {"kind": "BOUNDARY_REPLAY_045_v1", "status": status,
              "replayed_final_state_sha256": final_sha, "source_final_state_sha256": expected_sha,
              "source_state_sha256": _sha(source, meter), "trace": trace,
              "pending_validation_event_indices": pending_indices,
              "pending_issued_preserved": any(e["status"] != "COMPLETED" for e in events),
              "environment_calls_issued_by_replay": 0, "scheduler_calls_by_replay": 0,
              "partial_update_cursor_reconstruction_supported": False,
              "boundaries": [{"trial_id": b["trial_id"], "pre_table_sha256": b["pre"]["table_sha256"],
                              "post_table_sha256": b["post"]["table_sha256"], "Phi0": plain(b["pre"]["Phi"]),
                              "Phi1": plain(b["post"]["Phi"])} for b in boundaries]}
    # T/Phi copies remain owned until session close, including simultaneous
    # before/after tables, physical evidence, reader copies, and provenance.
    session.retain({"report": report, "boundary_copies": [{"trial_id": b["trial_id"],
        "pre": {"T": [r.state() for r in b["pre"]["T"]], "Phi": b["pre"]["Phi"]},
        "post": {"T": [r.state() for r in b["post"]["T"]], "Phi": b["post"]["Phi"]}} for b in boundaries]})
    return report, boundaries


def trial_decomposition(boundary, V, session, **configuration):
    try:
        return _trial_decomposition(boundary, V, session, **configuration)
    except Limit as error:
        return {"kind": "TRIAL_BRIER_DECOMPOSITION_045_v1", "status": "UNAVAILABLE", "cause": error.status,
                "mean_raw_gain": None, "gated_credit": None, "operative_priority_credit": None,
                "identity_verified": False, "retained_payload_sealed": False}


def _trial_decomposition(boundary, V, session, **configuration):
    """Exact sequential Brier decomposition on identical retained validation.

    Incomplete validation preserves numeric prefix diagnostics but has no full
    mean or operative credit. The fresh-predicate gate is applied only to the
    original full pre/post mean; it never zeroes the reported raw count effect.
    """
    meter = session.meter
    if type(V) is not int or V < 1:
        raise ValueError("positive prescribed validation count required")
    pre, post, trial = boundary["pre"], boundary["post"], boundary["trial"]
    specs = (("P00", pre["T"], pre["Phi"]), ("P10", post["T"], pre["Phi"]), ("P11", post["T"], post["Phi"]))
    readers = {}
    for name, transitions, predicates in specs:
        reader = PrescribedReader(meter=meter, **configuration)
        session.readers.append(reader)
        fitted = reader.fit(transitions, predicates)
        if fitted["status"] != "COMPLETE":
            return {"status": "UNAVAILABLE", "cause": fitted["status"], "mean_raw_gain": None,
                    "gated_credit": None, "identity_verified": False}
        readers[name] = reader
    rows, totals, unavailable = [], {name: Fraction(0) for name in ("count", "partition", "raw")}, False
    for event in boundary["validation_events"]:
        history = _history(event["before"])
        forecasts = {}
        for name, reader in readers.items():
            refusals_before = len(meter.refusals)
            forecasts[name] = reader.predict(history, event["action"], log=False)
            if len(meter.refusals) != refusals_before:
                return {"kind": "TRIAL_BRIER_DECOMPOSITION_045_v1", "status": "UNAVAILABLE",
                        "cause": meter.refusals[-1]["status"], "validation_rows": rows,
                        "partial_predictions": {k: _prediction_log(v) for k, v in forecasts.items()},
                        "mean_raw_gain": None, "gated_credit": None, "operative_priority_credit": None,
                        "identity_verified": False, "retained_payload_sealed": False}
        # Frozen source distributions are independently retained before outcomes.
        source_forecasts = {}
        for name, original in (("P00", "before"), ("P11", "after")):
            logged = (event.get("predictions") or {}).get(original)
            if logged and logged.get("status") in NUMERIC and forecasts[name].get("status") in NUMERIC and _prediction_log(forecasts[name]) != logged:
                raise ValueError("reconstructed predictor differs from logged frozen forecast")
            source_forecasts[name] = ("RECONSTRUCTION_UNAVAILABLE" if forecasts[name].get("status") not in NUMERIC else
                                     "VERIFIED" if logged and logged.get("status") in NUMERIC else "SOURCE_FORECAST_UNAVAILABLE")
        scores = {name: brier(forecast, tuple(event["outcome"]), meter) for name, forecast in forecasts.items()}
        row = {"event_index": event["index"], "predictions": {name: _prediction_log(value) for name, value in forecasts.items()},
               "brier": plain(scores), "count_effect": None, "partition_effect": None, "raw_gain": None,
               "identity_verified": False, "source_forecast_verification": source_forecasts}
        if any(value is None for value in scores.values()):
            unavailable = True
        else:
            count_effect = rational_operation(meter, "sub", scores["P00"], scores["P10"])
            partition_effect = rational_operation(meter, "sub", scores["P10"], scores["P11"])
            raw_gain = rational_operation(meter, "sub", scores["P00"], scores["P11"])
            identity = rational_operation(meter, "add", count_effect, partition_effect) == raw_gain
            meter.charge("diagnostic.brier_identity_compare", bits=bits(raw_gain))
            if not identity:
                raise AssertionError("exact Brier identity failed")
            row.update(count_effect=plain(count_effect), partition_effect=plain(partition_effect),
                       raw_gain=plain(raw_gain), identity_verified=True)
            for name, value in (("count", count_effect), ("partition", partition_effect), ("raw", raw_gain)):
                totals[name] = rational_operation(meter, "add", totals[name], value)
        rows.append(row)
    complete = len(rows) == V and trial["status"] == "COMPLETED"
    status = "UNAVAILABLE" if unavailable else "AVAILABLE" if complete else "INCOMPLETE_VALIDATION"
    means = {name: rational_operation(meter, "div", total, V) if status == "AVAILABLE" else None for name, total in totals.items()}
    fresh = bool(post["Phi"][len(pre["Phi"]):])
    gated = (means["raw"] if fresh else Fraction(0)) if status == "AVAILABLE" else None
    if trial["credit_status"] == "AVAILABLE" and status == "AVAILABLE" and gated != _fraction(trial["credit"]):
        raise ValueError("recomputed gated credit differs from source")
    result = {"kind": "TRIAL_BRIER_DECOMPOSITION_045_v1", "trial_id": boundary["trial_id"], "status": status,
              "validation_rows": rows, "required_validation_count": V,
              "T0_sha256": readers["P00"].source_table_sha256,
              "T1_P10_sha256": readers["P10"].source_table_sha256,
              "T1_P11_sha256": readers["P11"].source_table_sha256,
              "mean_count_effect": plain(means["count"]), "mean_partition_effect": plain(means["partition"]),
              "mean_raw_gain": plain(means["raw"]), "gated_credit": plain(gated),
              "fresh_predicate": fresh, "source_credit_status": trial["credit_status"],
              "source_credit": plain(trial["credit"]), "utility_is_operative": trial.get("utility_is_operative", False),
              "operative_priority_credit": plain(trial["credit"]) if trial.get("utility_is_operative") and trial["credit_status"] == "AVAILABLE" else None,
              "reconstructed_gated_credit_is_new_diagnostic_only": trial["credit_status"] != "AVAILABLE",
              "identity_verified": bool(rows) and all(r["identity_verified"] for r in rows),
              "identity_scope": "numeric retained validation prefix; full mean only when all V rows are available",
              "gate_changed": False, "counts_refit_once_per_prescribed_reader": True}
    return session.retain(result)
