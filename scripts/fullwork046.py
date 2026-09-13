"""Fabricated complete-path workloads, never the042 world or evaluation panel.

Operational measurements are not a proof of complete abstract accounting.
Standalone envelope states are explicitly constructed, not acquired trajectories.
"""
from __future__ import annotations
import copy
import base64
import hashlib
import zlib
from fractions import Fraction
from itertools import islice, product

from accounting043 import Meter, canonical
from reference_n1_043 import History, N1, Transition
from reference_n3_043 import Acquisition, Scheduler, plain, UPDATE_COMPLETE
from diagnostics045 import DiagnosticSession, PrescribedReader, choose_goal, partition_controls, replay_acquisition, trial_decomposition

MECHANISM = {"W": 2, "S": 3, "K": 4, "L": 5, "V": 2, "q": 4}
ARMS = ("FULL", "MACRO_OFF", "FEEDBACK_NULL", "COVERAGE")
STRESS_CASES = ("n1_multigroup", "n1_k4_selection", "n3_long_raw", "n3_dense")


class FabricatedTape:
    """Paid reset restarts an8-token action-agnostic periodic tape.

    No binary setter, probe, goal, reward, role permutation or target panel.
    This is a deterministic manufactured protocol interface, not an AI task.
    """
    interface_contract = "FABRICATED_PROTOCOL_FIXTURE"
    tape = (0, 1, 0, 2, 0, 3, 0, 4)

    def __init__(self):
        self.position, self.calls = 0, 0

    def reset(self):
        self.position = 0
        self.calls += 1
        return (self.tape[0],)

    def step(self, action):
        if type(action) is not int or action not in range(5):
            raise ValueError("opaque action required")
        self.calls += 1
        self.position = (self.position + 1) % len(self.tape)
        return (self.tape[self.position],)


def history(previous=0, current=0, lag2=0):
    # All supplied action/observation tokens are explicitly present in older
    # fabricated history; no future acquisition constants are preloaded.
    return History(tuple((x,) for x in (0, 1, 2, 3, 4, lag2, previous, current)), (0, 1, 2, 3, 4, 0, 0))


def fabricated_decisions(count=20):
    if count != 20:
        raise ValueError("046 freezes20 decisions per required readout")
    return [(history(i % 5, (i // 5) % 5, (i * 3) % 5), ((i * 2 + 1) % 5,)) for i in range(count)]


def serialize_retained(value, meter, label, preserve=True):
    """Hold payload and independent serialization concurrently, measure both.

    These declared logical owners do not count all Python temporaries. Source
    serialization is summarized by exact bytes/hash; diagnostic results remain
    fully present in the report rather than retaining repeated giant snapshots.
    """
    payload_bytes = meter.retain(label + ":payload", value)
    raw = meter.encode(value)
    meter.reserve(label + ":encoded", len(raw))
    meter.charge("fullwork046.sha256_bytes", len(raw), bits=8)
    if len(raw) > 128 * 1024 * 1024:
        raise ValueError("UNCOMPRESSED_EVIDENCE_LIMIT")
    result = {"payload_bytes": payload_bytes, "encoded_bytes": len(raw),
              "sha256": hashlib.sha256(raw).hexdigest(),
              "simultaneous_logical_owner_bytes": meter.retained_bytes,
              "owner_reservations": dict(sorted(meter.owners.items())),
              "python_temporary_allocation_complete": False}
    if preserve:
        meter.charge("fullwork046.archive_input_bytes", len(raw), bits=8)
        compressed = zlib.compress(raw, level=6)
        meter.reserve(label + ":compressed", len(compressed))
        encoded = base64.b64encode(compressed).decode("ascii")
        meter.reserve(label + ":base64", len(encoded))
        meter.charge("fullwork046.archive_output_bytes", len(encoded), bits=8)
        result["archive"] = {"encoding": "zlib6+base64", "data": encoded,
            "compressed_bytes": len(compressed), "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
            "uncompressed_bytes": len(raw), "uncompressed_sha256": result["sha256"],
            "uncompressed_limit_bytes": 128 * 1024 * 1024,
            "scope": "Complete fabricated payload; canonical043 JSON supports rational and nonstring-map tags"}
        result["peak_archive_overlap_logical_bytes"] = meter.retained_bytes
        meter.release(label + ":compressed")
        # The base64 data now remains held by the returned report. Keep its
        # logical owner live until the worker exits instead of silently freeing.
    meter.release(label + ":encoded")
    meter.release(label + ":payload")
    return result


def decisions_for(readers, session):
    decisions = fabricated_decisions()
    results = {}
    for name, reader in readers.items():
        rows = [choose_goal(reader, h, g, session) for h, g in decisions]
        if any(r["status"] != "AVAILABLE" or len(r["predictions"]) != 5 for r in rows):
            raise AssertionError("complete fabricated chooser path unavailable")
        results[name] = [{"status": row["status"], "goal": row["goal"], "action": row["action"],
            "goal_probability": row["goal_probability"],
            "five_forecasts": [{"action": p["action"], "status": p["status"],
                "goal_probability": p["required_goal_probability"]} for p in row["predictions"]],
            "full_diagnostic_sha256": hashlib.sha256(canonical(row)).hexdigest()} for row in rows]
    return results


def compact_decomposition(value):
    """Retain every score/effect/status; hash repeated full distributions.

    Full forecasts remain in the worker's concurrently retained session and its
    measured complete-evidence serialization. No trial or numerical effect is
    selected away. This report representation avoids redundant distribution
    copies at every successive table boundary.
    """
    result = {k: v for k, v in value.items() if k != "validation_rows"}
    result["full_diagnostic_sha256"] = hashlib.sha256(canonical(value)).hexdigest()
    result["validation_rows"] = [{**{k: v for k, v in row.items() if k != "predictions"},
        "full_forecasts_sha256": hashlib.sha256(canonical(row["predictions"])).hexdigest()}
        for row in value.get("validation_rows", [])]
    return result


def complete_chain(config, row, meter, progress=lambda *args: None):
    params = config["mechanism"]
    learner = N1(meter=meter, **{k: params[k] for k in ("W", "S", "K")})
    interface = FabricatedTape()
    size = next(s for s in config["sizes"] if s["name"] == row["size"])
    acquisition = Acquisition(interface, learner, arm=row["arm"], meter=meter,
        **{k: params[k] for k in ("L", "V", "q")}, B_env=size["B_env"],
        snapshot_reservation_bytes=config["snapshot_reservation_bytes"],
        block_id="fabricated046-tape")
    progress("acquisition", "STARTED", {"B_env": size["B_env"], "arm": row["arm"]})
    acquired = acquisition.run()
    if acquired["status"] != "ENVIRONMENT_LIMIT" or acquisition.env_calls != interface.calls:
        raise AssertionError("fabricated acquisition did not complete at its environmental allowance")
    if learner.search_status not in UPDATE_COMPLETE or not learner.counts_ready:
        raise AssertionError("acquisition left an incomplete N1 update")
    progress("acquisition", "COMPLETED", {"status": acquired["status"],
        "environment_calls": acquisition.env_calls, "transitions": len(learner.T),
        "selected_predicate_count": len(learner.Phi)})
    session = DiagnosticSession(meter)
    final_state = copy.deepcopy(learner.state())
    progress("replay", "STARTED", None)
    replay, boundaries = replay_acquisition(acquired["state"], final_state, session)
    if replay["status"] != "VERIFIED":
        raise AssertionError("complete acquisition replay unavailable")
    progress("replay", "COMPLETED", {"status": replay["status"], "boundaries": replay["boundaries"]})
    diagnostic_rows = []
    for boundary in boundaries:
        progress("trial_decomposition_" + str(boundary["trial_id"]), "STARTED", None)
        diagnostic = trial_decomposition(boundary, params["V"], session,
            **{k: params[k] for k in ("W", "S", "K")})
        diagnostic_rows.append(diagnostic)
        progress("trial_decomposition_" + str(boundary["trial_id"]), "COMPLETED", compact_decomposition(diagnostic))
    if any(r["status"] not in ("AVAILABLE", "INCOMPLETE_VALIDATION") for r in diagnostic_rows):
        raise AssertionError("trial reconstruction unavailable")
    scored_with_events = {e["trial_id"] for e in acquisition.events if e["phase"] != "WARMUP"}
    if scored_with_events != {b["trial_id"] for b in boundaries}:
        raise AssertionError("not every scored trial boundary reconstructed")
    progress("controls_and_choices", "STARTED", None)
    controls = partition_controls(learner.T, learner.Phi, session,
        **{k: params[k] for k in ("W", "S", "K")})
    choices = decisions_for(controls, session)
    expected_readouts = 4 + len(learner.Phi)
    if len(controls) != expected_readouts or len(choices) != expected_readouts:
        raise AssertionError("required selected/deletion/ORDER readers omitted")
    progress("controls_and_choices", "COMPLETED", {"readout_count": len(controls), "choices": choices})
    progress("complete_evidence_serialization", "STARTED", None)
    source_serialization = serialize_retained({"acquisition": acquired, "learner": final_state,
        "replay": replay, "diagnostic_records": session.records,
        "readers": {name: reader.state() for name, reader in controls.items()}}, meter, "chain.complete_evidence")
    summary = {"case": "complete_chain", "fabricated_interface": "ACTION_AGNOSTIC_PERIODIC_TAPE_046",
        "configuration": copy.deepcopy(params), "arm": row["arm"],
        "B_env": size["B_env"], "environment_calls": acquisition.env_calls,
        "unspent_environment_calls": size["B_env"] - acquisition.env_calls,
        "acquisition_status": acquired["status"], "retained_transitions": len(learner.T),
        "selected_predicates": plain(learner.Phi), "selected_predicate_count": len(learner.Phi),
        "completed_recipes": len(acquisition.scheduler.F), "macro_count": len(acquisition.scheduler.M),
        "scored_trial_count_with_events": len(scored_with_events), "replay": replay,
        "diagnostics": [compact_decomposition(row) for row in diagnostic_rows], "readout_count": len(controls),
        "deletion_readout_count": len(learner.Phi), "decisions_per_readout": 20,
        "five_action_prediction_count": len(controls) * 20 * 5, "choices": choices,
        "complete_evidence_serialization": source_serialization,
        "retained_reader_count_including_replay_and_trial_fits": len(session.readers),
        "complete_required_chain_paths": True, "target_scores_generated": False,
        "physical_target_evaluation_calls": 0, "target_11_call_protocol_measured": False,
        "maximal_geometry_proved": False}
    summary["output_serialization"] = serialize_retained(summary, meter, "chain.output", preserve=False)
    progress("complete_evidence_serialization", "COMPLETED", source_serialization)
    session.close()
    learner.close()
    meter.release(acquisition.owner)
    meter.release(acquisition.scheduler.owner)
    return summary


def geometry_transitions(n=245):
    if n < 2 or n > 245:
        raise ValueError("finite multigroup fixture")
    rows = []
    keys = list(product(range(5), repeat=3))
    for index in range(n):
        # Odd final record adds a third outcome to the last conflicting pair;
        # all245 records therefore belong to122 conflicting groups.
        group_index = index // 2 if index < n - 1 or n % 2 == 0 else max(0, index // 2 - 1)
        current, action, previous = keys[group_index]
        outcome = 2 if index == n - 1 and n % 2 else index % 2
        rows.append(Transition(history(previous, current), action, (outcome,), index))
    return rows


def multigroup_case(config, meter):
    n = config["stress"]["retained_records"]
    T = geometry_transitions(n)
    Phi = [(0, (0, 0, 0, 1), (1, 0, token)) for token in range(4)]
    session = DiagnosticSession(meter)
    reader = PrescribedReader(meter=meter)
    session.readers.append(reader)
    if reader.fit(T, Phi)["status"] != "COMPLETE":
        raise AssertionError("prescribed geometry fit unavailable")
    reader._ensure_inventory()
    reader._ensure_groups()
    if len(reader.inventory) != 3002 or len(reader.groups) != n // 2:
        raise AssertionError("multigroup envelope geometry not reached")
    # AtK4 real_search stops; these extra gain calls are a conservative
    # standalone over-approximation, never described as a reachable search pass.
    gains = [reader._gain(reader._signature(expr)) for expr in reader.inventory]
    if set(gains) != {0}:
        raise AssertionError("identical-window conflict pairs acquired separator")
    controls = partition_controls(T, Phi, session)
    choices = decisions_for(controls, session)
    result = {"case": "n1_multigroup", "transitions": n, "conflicting_groups": len(reader.groups),
        "outcome_entries": sum(len(g["outcomes"]) for g in reader.groups),
        "full_grammar_candidates": len(reader.inventory), "prescribed_K": 4,
        "gain_calls": len(gains), "all_gains_zero": True, "reachable_search_pass": False,
        "standalone_geometry_overapproximation": True, "readout_count": len(controls),
        "deletion_readout_count": 4, "decisions_per_readout": 20, "choices": choices}
    result["overlap_serialization"] = serialize_retained({"geometry_reader": reader.state(),
        "all_readers": {k: v.state() for k, v in controls.items()}, "records": session.records,
        "summary": result}, meter, "multigroup.overlap")
    session.close()
    return result


def k4_case(config, meter):
    learner = N1(meter=meter)
    n = config["stress"]["retained_records"]
    for index in range(n):
        previous = index % 5
        result = learner.append(history(previous), 0, (previous,))
        if result["status"] not in UPDATE_COMPLETE or not result["counts_ready"]:
            raise AssertionError("chronological K4 fixture incomplete")
    if len(learner.Phi) != 4 or len(learner.inventory) != 3002:
        raise AssertionError("actual K4 construction/full grammar not reached")
    session = DiagnosticSession(meter)
    controls = partition_controls(learner.T, learner.Phi, session)
    choices = decisions_for(controls, session)
    result = {"case": "n1_k4_selection", "chronological_updates": n,
        "selected_predicate_count": 4, "selected_predicates": plain(learner.Phi),
        "construction_log": plain(learner.construction_log), "full_grammar_candidates": 3002,
        "readout_count": 8, "deletion_readout_count": 4, "decisions_per_readout": 20,
        "choices": choices, "fabricated_table_not_acquisition_trajectory": True}
    result["overlap_serialization"] = serialize_retained({"live": learner.state(),
        "readers": {k: v.state() for k, v in controls.items()}, "records": session.records,
        "summary": result}, meter, "k4.overlap")
    session.close()
    learner.close()
    return result


def scheduler_case(config, meter, dense=False):
    sizes = config["stress"]
    scheduler = Scheduler(tuple(range(5)), 5, 4, "FULL", meter)
    words = list(islice(product(range(5), repeat=5), sizes["completed_recipes"]))
    # Construct source-valid component states directly: no claim these F/M
    # inventories, credits and maximal lengths arose together in acquisition.
    macros = ([(i,) for i in range(5)] + words[:sizes["macro_words"] - 5]) if dense else words[:sizes["macro_words"]]
    for i, word in enumerate(words):
        scheduler.add_completed(word, i, credit=None)
        scheduler.F[i]["utility_sum"] = Fraction((1 << 65) + i, (1 << 64) + 1 + i)
        scheduler.F[i]["utility_count"] = 1
    for i, word in enumerate(macros):
        scheduler._add_macro(word, i, None)
    scheduler._retain()
    # Enumerate raw lengths separately using the same actual mutation generator;
    # this additional instrumentation is reported, not hidden in one assembly.
    raw_count = raw_max = 0
    for recipe in scheduler.F:
        for word, _ in scheduler._mutations(recipe["word"]):
            raw_count += 1
            raw_max = max(raw_max, len(word))
    selected = scheduler.select(1)
    if raw_max != 10 or raw_count != 27720 or selected is None:
        raise AssertionError("declared N3 L5 raw geometry missing")
    if any(len(p["word"]) > 5 for p in scheduler.queue):
        raise AssertionError("long raw words escaped admissibility filter")
    mutation_selection = plain(selected)
    queue_copy = copy.deepcopy(scheduler.queue)
    result = {"case": "n3_dense" if dense else "n3_long_raw", "F": len(scheduler.F), "M": len(scheduler.M),
        "parent_lengths": sorted({len(r["word"]) for r in scheduler.F}),
        "macro_lengths": sorted({len(r["word"]) for r in scheduler.M}),
        "raw_mutations_per_enumeration": raw_count, "raw_enumerations": 2, "raw_max_tokens": raw_max,
        "proposal_assemblies": 1, "accepted_unique_proposals": len(queue_copy),
        "retained_derivations": sum(len(p["derivations"]) for p in queue_copy),
        "maximum_parent_provenance": max(len(p["parents"]) for p in queue_copy),
        "max_credit_numerator_bits": max(r["utility_sum"].numerator.bit_length() for r in scheduler.F),
        "max_credit_denominator_bits": max(r["utility_sum"].denominator.bit_length() for r in scheduler.F),
        "mutation_selection": mutation_selection, "manufactured_component_state": True,
        "joint_reachability_asserted": False, "queue_maximality_proved": False}
    if result["max_credit_numerator_bits"] < 66 or result["max_credit_denominator_bits"] < 65:
        raise AssertionError("large exact fraction operand coverage missing")
    result["overlap_serialization"] = serialize_retained({"scheduler": scheduler.state(),
        "independent_queue_copy": queue_copy, "summary": result}, meter, "n3.overlap")
    coverage = scheduler.select(4)
    if coverage["route"] != "COVERAGE":
        raise AssertionError("forced coverage cadence missing")
    result["forced_coverage_selection"] = plain(coverage)
    meter.release(scheduler.owner)
    return result


def workload(config, row, meter, progress=lambda *args: None):
    if row["case"] == "complete_chain":
        return complete_chain(config, row, meter, progress)
    progress(row["case"], "STARTED", {"declared_stress": config["stress"]})
    if row["case"] == "n1_multigroup":
        result = multigroup_case(config, meter)
    elif row["case"] == "n1_k4_selection":
        result = k4_case(config, meter)
    elif row["case"] in ("n3_long_raw", "n3_dense"):
        result = scheduler_case(config, meter, row["case"] == "n3_dense")
    else:
        raise ValueError("unrecognized frozen workload")
    progress(row["case"], "COMPLETED", {k: v for k, v in result.items() if k not in ("choices", "overlap_serialization")})
    return result
