"""Outcome-blind N3 reference adapter for checkpoint043 development fixtures.

This module contains no environment dynamics, evaluation panel, goals or chooser.
Its only external interaction is the supplied reset()/step(action) interface.
The four arms preserve035 and the explicitly versioned042 assimilation clause.
Resource ceilings here are engineering fixtures, never treatment admission.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from functools import cmp_to_key
from itertools import count, product

from accounting043 import Limit, Meter, rational_operation
from reference_n1_043 import History


ARMS = ("FULL", "MACRO_OFF", "FEEDBACK_NULL", "COVERAGE")
_OWNERS = count()
NUMERIC = {"UNSEEN_KEY", "OBSERVED_SINGLE_OUTCOME", "OBSERVED_CONFLICT"}
UPDATE_COMPLETE = {"COMPLETE", "GRAMMAR_LIMITED", "FEATURE_LIMITED"}


def plain(value):
    """Canonical JSON values; rational arithmetic is never rounded."""
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def history_state(history):
    return {"observations": plain(history.observations), "actions": list(history.actions)}


def _bits(*values):
    result = 1
    for value in values:
        if isinstance(value, Fraction):
            result += abs(value.numerator).bit_length() + value.denominator.bit_length()
        elif isinstance(value, int):
            result += abs(value).bit_length()
    return result


def _limit_status(error):
    return getattr(error, "status", str(error))


def brier(prediction, observed, meter):
    """Exact sparse add-one Brier; an unavailable prediction has no score."""
    if prediction.get("status") not in NUMERIC:
        return None
    probabilities = prediction.get("probabilities")
    if probabilities is not None:
        # The finite N1 reference exposes all declared outcomes. Every term is
        # charged, including arithmetic bit lengths, rather than unit-cost sum.
        score = Fraction(1)
        seen = False
        for outcome, probability in probabilities.items():
            meter.charge("n3_brier_outcome", bits=_bits(probability, score))
            probability = Fraction(probability)
            meter.charge("n3_brier_square", bits=_bits(probability) ** 2)
            score = rational_operation(meter, "add", score, rational_operation(meter, "mul", probability, probability))
            meter.charge("n3_brier_observation_compare", units=max(1, len(observed)))
            if tuple(outcome) == tuple(observed):
                meter.charge("n3_brier_observed_term", bits=_bits(probability, score))
                score = rational_operation(meter, "sub", score, rational_operation(meter, "mul", 2, probability))
                seen = True
        if not seen:
            raise ValueError("observation absent from declared prediction alphabet")
        return score
    raise ValueError("numeric N1 prediction omitted exact probabilities")


class Scheduler:
    """Literal mutation proposals with acquisition-index parent provenance."""

    def __init__(self, actions, L, q, arm, meter):
        self.actions = tuple(actions)
        if not self.actions or len(set(self.actions)) != len(self.actions):
            raise ValueError("nonempty distinct supplied action order required")
        if L < 1 or q < 2 or arm not in ARMS:
            raise ValueError("invalid N3 scheduler configuration")
        self.L, self.q, self.arm, self.meter = L, q, arm, meter
        self.owner = "n3_scheduler_" + str(next(_OWNERS))
        self.F, self.M, self.queue = [], [], []
        self.completed = set()
        self._retain()

    def state(self):
        return {"actions": list(self.actions), "L": self.L, "q": self.q,
                "arm": self.arm, "recipes": plain(self.F), "macros": plain(self.M),
                "proposal_queue": plain(self.queue),
                "completed_word_index": [list(row["word"]) for row in self.F]}

    def _retain(self):
        self.meter.retain(self.owner, self.state())

    def _reserve_growth(self, value):
        size = len(self.meter.encode(value)) + 256
        self.meter.reserve(self.owner, self.meter.owners.get(self.owner, 0) + size)

    def _mean(self, recipe, operative=True):
        if operative and self.arm in ("FEEDBACK_NULL", "COVERAGE"):
            return Fraction(0)
        self.meter.charge("n3_utility_mean", bits=_bits(recipe["utility_sum"], recipe["utility_count"]))
        return rational_operation(self.meter, "div", recipe["utility_sum"], recipe["utility_count"]) if recipe["utility_count"] else Fraction(0)

    def add_completed(self, word, trial_id, credit=None, warmup=False):
        word = tuple(word)
        self.meter.charge("n3_recipe_membership", units=max(1, len(word)))
        existing = None
        for recipe in self.F:
            self.meter.charge("n3_recipe_compare", units=max(1, len(word)))
            if recipe["word"] == word:
                existing = recipe
                break
        if existing is None:
            existing = {"word": word, "acquisition_index": len(self.F), "trial_ids": [],
                        "utility_sum": Fraction(0), "utility_count": 0}
            self._reserve_growth(existing)
            self.F.append(existing)
            self.completed.add(word)
        self._reserve_growth({"trial_id": trial_id, "credit": credit,
                              "sum_size_bound": _bits(credit or 0, existing["utility_sum"]) * 4})
        existing["trial_ids"].append(trial_id)
        if credit is not None:
            self.meter.charge("n3_utility_accumulate", bits=_bits(credit, existing["utility_sum"], existing["utility_count"]))
            existing["utility_sum"] = rational_operation(self.meter, "add", existing["utility_sum"], credit)
            existing["utility_count"] += 1
        if warmup:
            self._add_macro(word, trial_id, None)
        elif credit is not None and credit > 0 and self.arm == "FULL":
            # Canonical length/lexicographic fragment order, duplicates removed.
            fragments = set()
            for size in range(1, len(word) + 1):
                for start in range(len(word) - size + 1):
                    self.meter.charge("n3_fragment_copy_and_dedup", units=2 * size + 1)
                    fragments.add(word[start:start + size])
            ordered = sorted(fragments, key=cmp_to_key(self._word_compare))
            for fragment in ordered:
                self._add_macro(fragment, trial_id, credit)
        self._retain()

    def _add_macro(self, word, trial_id, credit):
        self._reserve_growth({"word": word, "acquisition_index": len(self.M),
                              "provenance": [{"trial_id": trial_id, "credit": credit}]})
        for macro in self.M:
            self.meter.charge("n3_macro_compare", units=max(1, len(word)))
            if macro["word"] == word:
                # Its first acquisition is the insertion provenance; subsequent
                # supporting credits are retained as additional actual evidence.
                macro["provenance"].append({"trial_id": trial_id, "credit": credit})
                return
        self.M.append({"word": word, "acquisition_index": len(self.M),
                       "provenance": [{"trial_id": trial_id, "credit": credit}]})

    def _word_compare(self, left, right):
        self.meter.charge("n3_word_order_compare", units=1 + min(len(left), len(right)))
        a, b = (len(left), left), (len(right), right)
        return (a > b) - (a < b)

    def _coverage(self):
        for length in range(1, self.L + 1):
            for word in product(self.actions, repeat=length):
                self.meter.charge("n3_coverage_word_and_membership", units=2 * length + 1)
                if word not in self.completed:
                    return {"word": word, "route": "COVERAGE", "parents": [],
                            "selected_parent": None, "operative_score": Fraction(0)}
        return None

    def _mutations(self, word):
        # Order is frozen before measurement: insertion, deletion, replacement,
        # swap; positions increase, and macro acquisition order breaks ties.
        for position in range(len(word) + 1):
            for macro in self.M:
                self.meter.charge("n3_insert_word_copy", units=len(word) + len(macro["word"]) + 1)
                yield word[:position] + macro["word"] + word[position:], {"operator": "INSERT", "position": position, "macro_index": macro["acquisition_index"]}
        for position in range(len(word)):
            self.meter.charge("n3_delete_word_copy", units=len(word) + 1)
            yield word[:position] + word[position + 1:], {"operator": "DELETE", "position": position}
        for position in range(len(word)):
            for macro in self.M:
                self.meter.charge("n3_replace_word_copy", units=len(word) + len(macro["word"]) + 1)
                yield word[:position] + macro["word"] + word[position + 1:], {"operator": "REPLACE", "position": position, "macro_index": macro["acquisition_index"]}
        for position in range(len(word) - 1):
            self.meter.charge("n3_swap_word_copy", units=len(word) + 1)
            yield word[:position] + (word[position + 1], word[position]) + word[position + 2:], {"operator": "SWAP", "position": position}

    def _proposal_compare(self, left, right):
        self.meter.charge("n3_priority_rational_compare", bits=_bits(left["operative_score"], right["operative_score"]) ** 2)
        if left["operative_score"] != right["operative_score"]:
            return -1 if left["operative_score"] > right["operative_score"] else 1
        by_word = self._word_compare(left["word"], right["word"])
        if by_word:
            return by_word
        self.meter.charge("n3_parent_index_compare", bits=_bits(left["selected_parent"], right["selected_parent"]))
        return (left["selected_parent"] > right["selected_parent"]) - (left["selected_parent"] < right["selected_parent"])

    def select(self, next_t):
        if next_t < 1:
            raise ValueError("post-warmup experiment counter begins at one")
        self.meter.charge("n3_coverage_cadence", bits=_bits(next_t, self.q))
        self.queue = []
        if self.arm == "COVERAGE" or next_t % self.q == 0:
            self._retain()
            return self._coverage()
        by_word = {}
        for recipe in self.F:
            parent = recipe["acquisition_index"]
            score = self._mean(recipe)
            for child, derivation in self._mutations(recipe["word"]):
                self.meter.charge("n3_proposal_length_and_dedup", units=len(child) + 2)
                if not child or len(child) > self.L:
                    continue
                if child not in by_word:
                    proposal = {"word": child, "route": "MUTATION", "parents": [], "derivations": [],
                                "selected_parent": parent, "operative_score": score}
                    self._reserve_growth(proposal)
                    index_owner = self.owner + ":proposal_index"
                    self.meter.reserve(index_owner, self.meter.owners.get(index_owner, 0) + len(self.meter.encode(child)) + 64)
                    self.meter.charge("n3_proposal_index_insert", units=len(child) + 1)
                    by_word[child] = proposal
                    self.queue.append(proposal)
                proposal = by_word[child]
                self._reserve_growth({"parent": parent, "score": score, "derivation": derivation})
                self.meter.charge("n3_parent_dedup", units=max(1, len(proposal["parents"])))
                if parent not in proposal["parents"]:
                    proposal["parents"].append(parent)
                proposal["derivations"].append({"parent": parent, **derivation})
                self.meter.charge("n3_parent_priority_compare", bits=_bits(score, proposal["operative_score"]) ** 2)
                if score > proposal["operative_score"] or (score == proposal["operative_score"] and parent < proposal["selected_parent"]):
                    proposal["operative_score"], proposal["selected_parent"] = score, parent
        self.queue.sort(key=cmp_to_key(self._proposal_compare))
        self._retain()
        self.meter.release(self.owner + ":proposal_index")
        for proposal in self.queue:
            self.meter.charge("n3_completed_proposal_filter", units=max(1, len(proposal["word"])))
            if proposal["word"] not in self.completed:
                return proposal
        fallback = self._coverage()
        if fallback is not None:
            fallback["route"] = "COVERAGE_FALLBACK"
        return fallback


class Acquisition:
    """One active deterministic reset block; raw completed evidence is retained.

    ``snapshot_reservation_bytes`` is an explicit development envelope for the
    *post-trial* snapshot. It is reserved before trial execution. This adapter
    checks actual snapshot size against it; it does not pretend that a user-given
    envelope proves a worst-case complete-run bound.
    """

    def __init__(self, interface, learner, *, arm, L, V, q, B_env, meter,
                 snapshot_reservation_bytes, block_id="development-block", interface_contract=None):
        if V < 1 or B_env < 0 or snapshot_reservation_bytes < 0:
            raise ValueError("invalid N3 acquisition limits")
        if not callable(getattr(interface, "reset", None)) or not callable(getattr(interface, "step", None)):
            raise ValueError("UNSUPPORTED_INTERFACE")
        self.interface_contract = interface_contract or getattr(interface, "interface_contract", None)
        if self.interface_contract not in ("FABRICATED_PROTOCOL_FIXTURE", "DECLARED_STATIONARY_DETERMINISTIC_RESETTABLE"):
            raise ValueError("UNSUPPORTED_INTERFACE")
        self.interface, self.learner, self.meter = interface, learner, meter
        self.arm, self.L, self.V, self.q, self.B_env = arm, L, V, q, B_env
        self.snapshot_reservation_bytes = snapshot_reservation_bytes
        self.block_id = block_id
        self.actions = tuple(learner.actions)
        self.scheduler = Scheduler(self.actions, L, q, arm, meter)
        self.owner = "n3_acquisition_" + str(next(_OWNERS))
        self.events, self.trials, self.pending_validation = [], [], []
        self.encounter_inventory_pending = False
        self.t, self.env_calls, self.warmup_completed = 0, 0, 0
        self.history, self.status = None, "READY"
        self._retain()

    def state(self):
        return {"kind": "N3_REFERENCE_STATE_043_v1", "block_id": self.block_id,
                "interface_contract": self.interface_contract,
                "stationarity_or_reset_contract_empirically_verified": False,
                "arm": self.arm, "L": self.L, "V": self.V, "q": self.q,
                "B_env": self.B_env, "environment_calls": self.env_calls,
                "counter_t": self.t, "warmup_completed": self.warmup_completed,
                "status": self.status, "history": history_state(self.history) if self.history else None,
                "events": plain(self.events), "trials": plain(self.trials),
                "pending_validation": plain(self.pending_validation),
                "encounter_inventory_pending": self.encounter_inventory_pending or bool(self.pending_validation),
                "snapshot_reservation_bytes": self.snapshot_reservation_bytes,
                "complete_work_bound_proved": False,
                "learner_transition_count": len(self.learner.T)}

    def _retain(self):
        self.meter.retain(self.owner, self.state())

    def _reserve_growth(self, value):
        self.meter.reserve(self.owner, self.meter.owners.get(self.owner, 0) + len(self.meter.encode(value)) + 256)

    def _physically_completed(self, trial_id, word):
        rows = [row for row in self.events if row["trial_id"] == trial_id and row["phase"] in ("TRIAL", "WARMUP")]
        return bool(rows and rows[0]["kind"] == "RESET" and all(row["status"] == "COMPLETED" for row in rows)
                    and tuple(row["action"] for row in rows[1:]) == tuple(word))

    def _observe(self, action, phase, trial_id, predictions=None):
        if self.env_calls >= self.B_env:
            raise Limit("ENVIRONMENT_LIMIT")
        before = self.history
        event = {"index": len(self.events), "call": self.env_calls + 1,
                 "block_id": self.block_id, "trial_id": trial_id, "counter_t": self.t,
                 "phase": phase, "kind": "RESET" if action is None else "PRIMITIVE",
                 "action": action, "before": history_state(before) if before is not None and action is not None else None,
                 "predictions": predictions, "outcome": None, "status": "ISSUED"}
        # Finite alphabets bound every response; reserve the full new event plus
        # a whole maximum next history, so replacing the old history cannot
        # underreserve the increment. Retain reservation if interruption occurs.
        largest = tuple(max(alphabet, key=lambda token: len(str(token))) for alphabet in self.learner.observation_alphabets)
        event_max = {**event, "outcome": list(largest), "status": "COMPLETED"}
        history_max = History.initial(largest) if action is None else before.advance(action, largest)
        reserve_bytes = len(self.meter.encode(event_max)) + len(self.meter.encode(history_state(history_max))) + 128
        self.meter.reserve(self.owner, self.meter.owners.get(self.owner, 0) + reserve_bytes)
        self.meter.charge("n3_issue_environment_call", bits=_bits(self.env_calls))
        # The action/call is logged before entering the interface. Exceptions
        # retain the issued event and charged call; no successful response is
        # fabricated, and no partial trial becomes a completed endpoint.
        self.events.append(event)
        self.env_calls += 1
        try:
            outcome = tuple(self.interface.reset() if action is None else self.interface.step(action))
        except Exception:
            event["status"] = "INTERRUPTED"
            if action is not None:
                event["encounter_inventory_pending"] = True
                self.encounter_inventory_pending = True
            raise Limit("ENVIRONMENT_INTERRUPTED") from None
        event["outcome"], event["status"] = list(outcome), "COMPLETED"
        self.history = History.initial(outcome) if action is None else before.advance(action, outcome)
        if len(outcome) != len(self.learner.observation_alphabets) or any(value not in alphabet for value, alphabet in zip(outcome, self.learner.observation_alphabets)):
            raise Limit("UNSUPPORTED_INTERFACE")
        # Completed response stays in self.events even if subsequent serialized
        # bookkeeping cannot finish. The reservation covers it until finalizing.
        self._retain()
        return before, outcome, event

    def _append(self, before, action, outcome, *, delayed=False):
        result = self.learner.append(before, action, outcome)
        if result.get("status") not in UPDATE_COMPLETE:
            raise Limit(result.get("status", "COMPUTATION_INCOMPLETE"))
        return result

    def _trial(self, word, phase, trial_id):
        if self.env_calls + 1 + len(word) > self.B_env:
            raise Limit("ENVIRONMENT_LIMIT")
        _, outcome, _ = self._observe(None, phase, trial_id)
        self.learner.observe_reset(outcome)
        for action in word:
            before, outcome, event = self._observe(action, phase, trial_id)
            old_size = len(self.learner.T)
            try:
                self._append(before, action, outcome)
                event["assimilated"] = True
            except Limit:
                event["assimilated"] = len(self.learner.T) > old_size
                event["encounter_inventory_pending"] = True
                self.encounter_inventory_pending = True
                raise

    def _snapshot(self):
        if not self.learner.counts_ready:
            raise Limit("COMPUTATION_INCOMPLETE")
        return self.learner.snapshot()

    def _frozen_prediction(self, snapshot, action):
        refusals_before = len(self.meter.refusals)
        prediction = snapshot.predict(self.history, action)
        # N1 reports prediction failure as data. A global cap refusal is still
        # terminal for acquisition; do not spend its small residual allowance on
        # another snapshot, physical action, fitting or priority update.
        for refusal in self.meter.refusals[refusals_before:]:
            if refusal.get("status") in ("COMPUTATION_INCOMPLETE", "MEMORY_LIMIT"):
                raise Limit(refusal["status"])
        return prediction

    def _assimilate_validation(self, queue):
        # Credit has already been finalized and stored. Each new constant enters
        # through its chronological append, never through a preloaded batch.
        self.pending_validation = list(queue)
        for row in queue:
            before = History(tuple(tuple(o) for o in row["before"]["observations"]), tuple(row["before"]["actions"]))
            old_size = len(self.learner.T)
            try:
                self._append(before, row["action"], tuple(row["outcome"]), delayed=True)
            except Limit:
                if len(self.learner.T) > old_size:
                    self.pending_validation.pop(0)
                    self.events[row["event_index"]]["assimilated"] = True
                raise
            self.pending_validation.pop(0)
            self.events[row["event_index"]]["assimilated"] = True

    def _scored_trial(self, selection):
        word = tuple(selection["word"])
        trial_id = len(self.trials)
        record = {"id": trial_id, "counter_t": self.t, "word": word,
                  "selection": plain(selection), "status": "RESERVED", "credit_status": "INCOMPLETE",
                  "credit": None, "new_predicates": [], "validation": [], "utility_is_operative": self.arm in ("FULL", "MACRO_OFF")}
        self._reserve_growth(record)
        self.trials.append(record)
        self._retain()
        if self.env_calls + 1 + len(word) > self.B_env:
            raise Limit("ENVIRONMENT_LIMIT")
        before = after = None
        envelope_owner = self.owner + ":after_snapshot_envelope"
        stop = None
        trial_complete = False
        try:
            before = self._snapshot()
            self.meter.reserve(envelope_owner, self.snapshot_reservation_bytes)
            phi_start = len(self.learner.Phi)
            record["pre_table_size"] = len(self.learner.T)
            record["before_snapshot_sha256"] = hashlib.sha256(self.meter.encode(before.state())).hexdigest()
            self._trial(word, "TRIAL", trial_id)
            trial_complete = True
            record["status"] = "COMPLETED"
            record["post_table_size"] = len(self.learner.T)
            record["new_predicates"] = plain(self.learner.Phi[phi_start:])
            if self.learner.logical_bytes() > self.snapshot_reservation_bytes:
                raise Limit("SNAPSHOT_ENVELOPE_EXCEEDED")
            self.meter.release(envelope_owner)
            after = self._snapshot()
            record["after_snapshot_sha256"] = hashlib.sha256(self.meter.encode(after.state())).hexdigest()
            unavailable = False
            differences = []
            for index in range(self.V):
                if self.env_calls >= self.B_env:
                    raise Limit("ENVIRONMENT_LIMIT")
                action = self.actions[(self.t + index) % len(self.actions)]
                self.meter.charge("n3_validation_action_index", bits=_bits(self.t, index, len(self.actions)))
                pb = self._frozen_prediction(before, action)
                pa = self._frozen_prediction(after, action)
                # Distribution logging occurs before the observation arrives.
                logged = {"before": _prediction_log(pb), "after": _prediction_log(pa)}
                previous, outcome, event = self._observe(action, "VALIDATION", trial_id, logged)
                row = {"before": history_state(previous), "action": action, "outcome": list(outcome), "event_index": event["index"]}
                self._reserve_growth(row)
                record["validation"].append(row)
                bb, ba = brier(pb, outcome, self.meter), brier(pa, outcome, self.meter)
                if bb is None or ba is None:
                    unavailable = True
                    row["brier_difference"] = None
                else:
                    self.meter.charge("n3_brier_difference", bits=_bits(bb, ba) ** 2)
                    difference = rational_operation(self.meter, "sub", bb, ba)
                    differences.append(difference)
                    row["brier_difference"] = plain(difference)
            if unavailable:
                record["credit_status"] = "UNAVAILABLE"
            elif not record["new_predicates"]:
                record["credit_status"], record["credit"] = "AVAILABLE", Fraction(0)
            else:
                total = Fraction(0)
                for difference in differences:
                    self.meter.charge("n3_credit_mean_accumulate", bits=_bits(total, difference) ** 2)
                    total = rational_operation(self.meter, "add", total, difference)
                self.meter.charge("n3_credit_mean_divide", bits=_bits(total, self.V) ** 2)
                record["credit_status"], record["credit"] = "AVAILABLE", rational_operation(self.meter, "div", total, self.V)
        except Limit as error:
            stop = _limit_status(error)
            trial_complete = self._physically_completed(trial_id, word)
            complete_validation = sum(row["phase"] == "VALIDATION" and row["trial_id"] == trial_id and row["status"] == "COMPLETED" for row in self.events)
            if not trial_complete:
                record["status"] = "INCOMPLETE"
            else:
                record["status"] = "COMPLETED"
            record["credit_status"], record["credit"] = ("INCOMPLETE" if not trial_complete or complete_validation < self.V else "UNAVAILABLE"), None
        finally:
            try:
                self.meter.release(envelope_owner)
            except Limit as error:
                stop = stop or _limit_status(error)
            if before is not None:
                try:
                    before.close()
                except Limit as error:
                    stop = stop or _limit_status(error)
            if after is not None:
                try:
                    after.close()
                except Limit as error:
                    stop = stop or _limit_status(error)
        # Completion / credit first, then the mandatory delayed assimilation.
        # A compute/memory stop can leave an explicitly retained pending suffix;
        # it cannot authorize a budget refill or silently discard observations.
        record["finalized_before_validation_assimilation"] = True
        existing_rows = {row["event_index"]: row for row in record["validation"]}
        # If response serialization or scoring stopped, the original event is
        # still authoritative. Recover every completed response into the pending
        # assimilation suffix; no information is recreated from a hidden world.
        record["validation"] = [existing_rows.get(event["index"], {
            "before": event["before"], "action": event["action"],
            "outcome": event["outcome"], "event_index": event["index"],
            "brier_difference": None}) for event in self.events
            if event["trial_id"] == trial_id and event["phase"] == "VALIDATION" and event["status"] == "COMPLETED"]
        if stop and stop != "ENVIRONMENT_LIMIT":
            # A refused global work/memory debit is terminal. Its unspent tail
            # cannot be used for cheaper scientific updates after the refusal.
            # Physical evidence / finalized credit survive as pending records.
            record["library_update_pending"] = trial_complete
            record["assimilation_pending"] = bool(record["validation"])
            self.pending_validation = list(record["validation"])
            raise Limit(stop)
        if trial_complete:
            try:
                self.scheduler.add_completed(word, trial_id, record["credit"])
            except Limit as error:
                # A new global refusal during the final library update is just
                # as terminal as one during scoring. Preserve its partially
                # completed library state and do not start cheaper assimilation.
                record["library_update_pending"] = True
                record["assimilation_pending"] = bool(record["validation"])
                self.pending_validation = list(record["validation"])
                raise Limit(_limit_status(error))
        try:
            self._assimilate_validation(record["validation"])
        except Limit as error:
            stop = stop or _limit_status(error)
        if stop:
            raise Limit(stop)
        self._retain()

    def run(self):
        """Run the declared fixture budget once; never replenish after a stop."""
        if self.status != "READY":
            raise ValueError("resume requires separately specified unchanged-budget recovery")
        self.status = "RUNNING"
        try:
            for action in self.actions:
                trial_id = len(self.trials)
                record = {"id": trial_id, "counter_t": 0, "word": (action,), "phase": "WARMUP", "status": "INCOMPLETE", "credit_status": "UNSCORED", "credit": None}
                self._reserve_growth(record)
                self.trials.append(record)
                try:
                    self._trial((action,), "WARMUP", trial_id)
                except Limit:
                    if self._physically_completed(trial_id, (action,)):
                        record["status"] = "COMPLETED"
                        record["library_update_pending"] = True
                    raise
                record["status"] = "COMPLETED"
                self.scheduler.add_completed((action,), trial_id, warmup=True)
                self.warmup_completed += 1
                self._retain()
            self.t = 0
            while True:
                next_t = self.t + 1
                selection = self.scheduler.select(next_t)
                if selection is None:
                    self.status = "SEARCH_SPACE_EXHAUSTED"
                    break
                # Proposal construction precedes reservation. The counter is
                # persisted even when this reservation or trial cannot finish.
                self.t = next_t
                self._retain()
                self._scored_trial(selection)
        except Limit as error:
            self.status = _limit_status(error)
        return {"status": self.status, "state": self.state(), "scheduler": self.scheduler.state(),
                "target_scores_generated": False, "treatment_run": False}


def _prediction_log(prediction):
    result = {"status": prediction.get("status"), "features": plain(prediction.get("features"))}
    probabilities = prediction.get("probabilities")
    if probabilities is not None:
        result["probabilities"] = [{"outcome": list(outcome), "probability": plain(probability)} for outcome, probability in probabilities.items()]
    counts = prediction.get("counts")
    if counts is not None:
        result["counts"] = [{"outcome": list(outcome), "count": value} for outcome, value in counts.items()]
    return result


def run_acquisition(interface, learner, *, arm, L, V, q, B_env, meter,
                    snapshot_reservation_bytes, block_id="development-block", interface_contract=None):
    return Acquisition(interface, learner, arm=arm, L=L, V=V, q=q, B_env=B_env,
                       meter=meter, snapshot_reservation_bytes=snapshot_reservation_bytes,
                       block_id=block_id, interface_contract=interface_contract).run()
