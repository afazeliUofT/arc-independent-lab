"""Frozen fabricated045 cases; actual adapters, independent arithmetic oracles."""
import copy
import json
from fractions import Fraction
from pathlib import Path
import unittest
from unittest.mock import patch

from accounting043 import Limit, Meter, canonical
from reference_n1_043 import GenericReader, History, N1, Transition
from reference_n3_043 import Acquisition
from diagnostics045 import (DiagnosticSession, PrescribedReader, choose_goal,
                            partition_controls, replay_acquisition,
                            table_sha256, trial_decomposition)

CONFIG = json.loads((Path(__file__).resolve().parents[1] / "configs/P3_DIAGNOSTIC_FIXTURES_045.json").read_text())
CASE_RESULTS = {}


def get_results():
    return {"kind": "P3_DIAGNOSTIC_CASE_RESULTS_045_v1", "cases": copy.deepcopy(CASE_RESULTS),
            "target_experiment_started": False, "complete_work_profile": False,
            "B_comp": None, "B_mem": None, "future_experiment_admission": False,
            "accounting_scope": "Declared named work and retained logical payloads; incomplete Python temporary/allocation coverage"}


def rational(value):
    return Fraction(value["numerator"], value["denominator"])


def reader_fixture():
    config = CONFIG["reader"]
    histories = [History(tuple(tuple(o) for o in row), (config["past_action"],)) for row in config["histories"]]
    T = [Transition(histories[row["history"]], row["action"], tuple(row["outcome"]), index)
         for index, row in enumerate(config["transitions"])]
    kwargs = {key: config[key] for key in ("W", "S", "K", "actions", "observation_alphabets")}
    return histories, T, config["predicates"], kwargs


class FabricatedInterface:
    interface_contract = "FABRICATED_PROTOCOL_FIXTURE"

    def __init__(self, primitive_outcomes=None, reset_outcomes=None, interrupt=False):
        self.primitives = iter(primitive_outcomes) if primitive_outcomes else None
        self.resets = iter(reset_outcomes) if reset_outcomes else None
        self.interrupt = interrupt
        self.calls = 0

    def reset(self):
        self.calls += 1
        return (next(self.resets) if self.resets else 0,)

    def step(self, action):
        self.calls += 1
        if self.interrupt:
            raise OSError("declared fabricated interrupted primitive")
        return (next(self.primitives) if self.primitives else 0,)


class DeniedBrierMeter(Meter):
    def charge(self, category, units=1, bits=1):
        if category == CONFIG["acquisition"]["pending_validation"]["deny_first_category"] and self.work_limit is None:
            self.work_limit = self.work
        return super().charge(category, units, bits)


def acquire(name):
    base = CONFIG["acquisition"]
    case = base[name]
    meter = DeniedBrierMeter() if name == "pending_validation" else Meter()
    kwargs = {key: base[key] for key in ("W", "S", "actions", "observation_alphabets")}
    kwargs["K"] = case["K"]
    learner = N1(meter=meter, **kwargs)
    interface = FabricatedInterface(case.get("primitive_outcomes"), case.get("reset_outcomes"), case.get("interrupt_first_primitive", False))
    run = Acquisition(interface, learner, arm="FULL", L=base["L"], V=base["V"], q=base["q"],
                      B_env=case["B_env"], meter=meter, snapshot_reservation_bytes=base["snapshot_reservation_bytes"],
                      block_id="fabricated045-" + name)
    result = run.run()
    return run, learner, interface, result, kwargs


class PrescribedReaderTests(unittest.TestCase):
    def test_exact_partition_fit_never_searches_and_preserves_input(self):
        histories, T, Phi, kwargs = reader_fixture()
        before = canonical([r.state() for r in T])
        session = DiagnosticSession()
        reader = PrescribedReader(meter=session.meter, **kwargs)
        with patch.object(N1, "_search", side_effect=AssertionError("forbidden feature search")), patch.object(N1, "append", side_effect=AssertionError("forbidden incremental fit")):
            result = reader.fit(T, Phi[:1])
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(reader.predict(histories[1], 0)["probabilities"][(1,)], Fraction(2, 3))
        self.assertEqual(reader.predict(histories[0], 0)["probabilities"][(1,)], Fraction(1, 3))
        self.assertEqual(canonical([r.state() for r in T]), before)
        self.assertEqual(reader.construction_log, [])
        self.assertEqual(reader.inventory, [])
        self.assertEqual(reader.source_table_sha256, table_sha256(T, session.meter))
        self.assertIsNot(reader.T[0], T[0])
        with self.assertRaisesRegex(ValueError, "fit once"):
            reader.fit(T, Phi[:1])
        CASE_RESULTS["prescribed_partition"] = {"status": "PASSED", "same_T_sha256": reader.source_table_sha256,
                                                 "goal_probabilities": ["2/3", "1/3"], "feature_search_calls": 0}

    def test_all_deletions_hold_remaining_partition_and_same_T(self):
        histories, T, Phi, kwargs = reader_fixture()
        session = DiagnosticSession()
        readers = partition_controls(T, Phi, session, **kwargs)
        self.assertEqual(set(readers), {"SELECTED", "DELETE_0", "DELETE_1", "ORDER0", "ORDER1", "ORDER2"})
        self.assertEqual(readers["DELETE_0"].Phi, readers["SELECTED"].Phi[1:])
        self.assertEqual(readers["DELETE_1"].Phi, readers["SELECTED"].Phi[:1])
        self.assertEqual(len({r.source_table_sha256 for r in readers.values()}), 1)
        # Complementary predicates are redundant on this fixed table: either
        # single deletion preserves the learned partition's forecast.
        for name in ("SELECTED", "DELETE_0", "DELETE_1"):
            self.assertEqual(readers[name].predict(histories[1], 0)["probabilities"][(1,)], Fraction(2, 3))
        self.assertEqual(readers["ORDER0"].predict(histories[1], 0)["probabilities"][(1,)], Fraction(1, 2))
        for name in ("ORDER1", "ORDER2"):
            self.assertEqual(readers[name].predict(histories[1], 0)["probabilities"][(1,)], Fraction(2, 3))
        results = {name: choose_goal(reader, histories[1], (1,), session) for name, reader in readers.items()}
        self.assertTrue(all(result["status"] == "AVAILABLE" for result in results.values()))
        CASE_RESULTS["all_predicate_deletions"] = {"status": "PASSED", "all_T_hashes_identical": True,
            "readers": {name: {"action": row["action"], "probability": row["goal_probability"]} for name, row in results.items()},
            "redundant_predicate_single_deletion_can_mask_effect": True, "meter": session.meter.state()}
        CASE_RESULTS["order_0_1_2"] = {"status": "PASSED", "goal_probabilities": {"ORDER0": "1/2", "ORDER1": "2/3", "ORDER2": "2/3"},
            "same_T_sha256": readers["ORDER0"].source_table_sha256, "all_readers_prescribed_before_results": True}

    def test_empty_partition_equals_order0_including_unseen(self):
        histories, T, _, kwargs = reader_fixture()
        meter = Meter()
        selected = PrescribedReader(meter=meter, **kwargs)
        selected.fit(T, [])
        order0 = GenericReader(0, observation_alphabets=kwargs["observation_alphabets"], actions=kwargs["actions"], meter=meter)
        order0.fit(T)
        for history in histories + [History.initial((1,))]:
            for action in range(5):
                self.assertEqual(selected.predict(history, action, log=False), order0.predict(history, action, log=False))

    def test_invalid_prescribed_grammar_is_rejected(self):
        _, T, _, kwargs = reader_fixture()
        invalid = [(0, (0, 0, 0, 3), (1, 0, 0)), (0, (0, 0, 0, 0), (1, 1, 0)),
                   (0, (0, 0, 0, 0), (1, 0, 5)), (0, (1, 0, 0), (0, 0, 0, 0))]
        for predicate in invalid:
            with self.subTest(predicate=predicate), self.assertRaises(ValueError):
                PrescribedReader(**kwargs).fit(T, [predicate])

    def test_fit_refusal_is_nonnumeric_and_does_not_retry(self):
        histories, T, Phi, kwargs = reader_fixture()
        meter = Meter()
        reader = PrescribedReader(meter=meter, **kwargs)
        meter.work_limit = meter.work
        result = reader.fit(T, Phi[:1])
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(reader.predict(histories[0], 0)["status"], "COMPUTATION_INCOMPLETE")
        with self.assertRaises(ValueError):
            reader.fit(T, Phi[:1])


class ChooserTests(unittest.TestCase):
    def test_exact_five_action_maximum_and_stable_ties(self):
        histories, T, Phi, kwargs = reader_fixture()
        session = DiagnosticSession()
        reader = PrescribedReader(meter=session.meter, **kwargs)
        reader.fit(T, Phi[:1])
        upper = choose_goal(reader, histories[1], (1,), session)
        lower = choose_goal(reader, histories[0], (1,), session)
        self.assertEqual(upper["action"], 0)  # 2/3 beats four unseen 1/2 forecasts.
        self.assertEqual(lower["action"], 1)  # first of four unseen tied actions.
        self.assertEqual([r["action"] for r in lower["predictions"]], list(range(5)))
        self.assertEqual(len(reader.T), 2)
        CASE_RESULTS["exact_five_action_chooser"] = {"status": "PASSED", "seen_max_action": 0,
            "unseen_tie_action": 1, "all_five_predictions": True, "fitted_T_unchanged": True}

    def test_nonnumeric_required_forecast_blocks_decision_after_all_requests(self):
        histories, T, Phi, kwargs = reader_fixture()
        session = DiagnosticSession()
        reader = PrescribedReader(meter=session.meter, **kwargs)
        reader.fit(T, Phi[:1])
        original = reader.predict
        calls = []
        def predict(history, action, log=False):
            calls.append(action)
            return {"status": "COMPUTATION_INCOMPLETE", "probabilities": None} if action == 3 else original(history, action, log=log)
        with patch.object(reader, "predict", side_effect=predict):
            result = choose_goal(reader, histories[1], (1,), session)
        self.assertEqual(calls, list(range(5)))
        self.assertEqual(result["status"], "DECISION_UNAVAILABLE")
        self.assertIsNone(result["action"])
        CASE_RESULTS["nonnumeric_unavailability"] = {"status": "PASSED", "all_action_requests": calls,
            "required_nonnumeric_action": 3, "selected_action": result["action"], "decision_status": result["status"]}

    def test_refused_chooser_work_stops_without_favorable_fallback(self):
        histories, T, Phi, kwargs = reader_fixture()
        session = DiagnosticSession()
        reader = PrescribedReader(meter=session.meter, **kwargs)
        reader.fit(T, Phi[:1])
        session.meter.work_limit = session.meter.work
        result = choose_goal(reader, histories[1], (1,), session)
        self.assertEqual(result["status"], "DECISION_UNAVAILABLE")
        self.assertEqual(result["unattempted_actions"], list(range(5)))
        self.assertIsNone(result["action"])
        CASE_RESULTS["accounting_refusal"] = {"status": "PASSED", "chooser_status": result["status"],
            "unattempted_actions": result["unattempted_actions"], "cause": result["cause"], "budget_refilled": False}

    def test_five_opaque_action_contract_is_explicit(self):
        session = DiagnosticSession()
        reader = PrescribedReader(actions=(0, 1), meter=session.meter)
        reader.fit([], [])
        with self.assertRaisesRegex(ValueError, "indices 0 through 4"):
            choose_goal(reader, History.initial((0,)), (0,), session)

    def test_chooser_rejects_separate_unmatched_meter(self):
        histories, T, Phi, kwargs = reader_fixture()
        reader = PrescribedReader(**kwargs)
        reader.fit(T, Phi[:1])
        with self.assertRaisesRegex(ValueError, "same meter"):
            choose_goal(reader, histories[1], (1,), DiagnosticSession())

    def test_float_forecast_is_unavailable_under_exact_rational_contract(self):
        histories, T, Phi, kwargs = reader_fixture()
        session = DiagnosticSession()
        reader = PrescribedReader(meter=session.meter, **kwargs)
        reader.fit(T, Phi[:1])
        with patch.object(reader, "predict", return_value={"status": "UNSEEN_KEY", "probabilities": {(0,): 0.5, (1,): 0.5}}):
            result = choose_goal(reader, histories[0], (1,), session)
        self.assertEqual(result["status"], "DECISION_UNAVAILABLE")
        self.assertIsNone(result["action"])


class ReplayAndBrierTests(unittest.TestCase):
    def run_case(self, name):
        run, learner, interface, result, kwargs = acquire(name)
        calls_before = interface.calls
        session = DiagnosticSession()
        report, boundaries = replay_acquisition(result["state"], learner.state(), session)
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(interface.calls, calls_before)
        self.assertEqual(report["environment_calls_issued_by_replay"], 0)
        return run, learner, result, kwargs, session, report, boundaries

    def test_count_only_raw_gain_is_not_gated_credit(self):
        run, _, _, kwargs, session, report, boundaries = self.run_case("constant_complete")
        self.assertEqual(len(boundaries), 1)
        result = trial_decomposition(boundaries[0], CONFIG["acquisition"]["V"], session, **kwargs)
        self.assertEqual(result["status"], "AVAILABLE")
        # Old action0 count1 gives (2/3,1/3), new count3 gives (4/5,1/5).
        # Action1 unchanged; mean improvement = ((2/9)-(2/25))/2 = 16/225.
        self.assertEqual(rational(result["mean_count_effect"]), Fraction(16, 225))
        self.assertEqual(rational(result["mean_partition_effect"]), 0)
        self.assertEqual(rational(result["mean_raw_gain"]), Fraction(16, 225))
        self.assertEqual(rational(result["gated_credit"]), 0)
        self.assertTrue(result["identity_verified"])
        self.assertEqual(result["T1_P10_sha256"], result["T1_P11_sha256"])
        finalizations = [i for i, row in enumerate(report["trace"]) if row["operation"] == "FINALIZE_CREDIT"]
        delayed = [i for i, row in enumerate(report["trace"]) if row.get("phase") == "DELAYED_VALIDATION"]
        self.assertLess(finalizations[0], min(delayed))
        self.assertEqual(len(boundaries[0]["post"]["T"]), 4)
        self.assertEqual(run.state()["learner_transition_count"], 6)
        CASE_RESULTS["count_only_credit_gate"] = {"status": "PASSED", "replay": report, "decomposition": result}

    def test_positive_fresh_predicate_exact_sequential_identity(self):
        _, _, _, kwargs, session, report, boundaries = self.run_case("fresh_predicate")
        result = trial_decomposition(boundaries[0], CONFIG["acquisition"]["V"], session, **kwargs)
        self.assertTrue(result["fresh_predicate"])
        self.assertEqual(result["status"], "AVAILABLE")
        self.assertEqual(rational(result["gated_credit"]), Fraction(*CONFIG["acquisition"]["fresh_predicate"]["expected_credit"]))
        self.assertEqual(rational(result["mean_count_effect"]) + rational(result["mean_partition_effect"]), Fraction(7, 144))
        # Independent direct sum of squared errors, separate from brier().
        for row in result["validation_rows"]:
            original = next(e for e in boundaries[0]["validation_events"] if e["index"] == row["event_index"])
            for label, prediction in row["predictions"].items():
                direct = sum((rational(p["probability"]) - int(p["outcome"] == original["outcome"])) ** 2 for p in prediction["probabilities"])
                self.assertEqual(direct, rational(row["brier"][label]))
        CASE_RESULTS["fresh_predicate_brier_identity"] = {"status": "PASSED", "replay": report, "decomposition": result}

    def test_partial_validation_keeps_prefix_and_no_full_credit(self):
        _, _, _, kwargs, session, report, boundaries = self.run_case("constant_partial")
        result = trial_decomposition(boundaries[0], CONFIG["acquisition"]["V"], session, **kwargs)
        self.assertEqual(result["status"], "INCOMPLETE_VALIDATION")
        self.assertEqual(len(result["validation_rows"]), 1)
        self.assertIsNone(result["mean_raw_gain"])
        self.assertIsNone(result["gated_credit"])
        self.assertTrue(result["identity_verified"])
        CASE_RESULTS["partial_validation"] = {"status": "PASSED", "replay": report, "decomposition": result}

    def test_reset_arrival_precedes_trial_update(self):
        _, _, _, _, _, report, _ = self.run_case("reset_arrival")
        resets = [r for r in report["trace"] if r["operation"] == "OBSERVE_RESET"]
        self.assertEqual(resets[0]["observed_constants"][0], [0])
        self.assertEqual(resets[1]["observed_constants"][0], [0, 1])
        self.assertEqual(resets[1]["table_size"], 1)
        CASE_RESULTS["reset_arrival"] = {"status": "PASSED", "replay": report}

    def test_pending_validation_is_not_silently_added(self):
        _, learner, result, kwargs, session, report, boundaries = self.run_case("pending_validation")
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(len(learner.T), 4)
        self.assertEqual(report["pending_validation_event_indices"], [7])
        self.assertEqual(len(boundaries[0]["post"]["T"]), 4)
        controls = partition_controls(learner.T, learner.Phi, session, **kwargs)
        self.assertTrue(all(len(reader.T) == 4 for reader in controls.values()))
        self.assertFalse(any(r.get("phase") == "DELAYED_VALIDATION" for r in report["trace"]))
        CASE_RESULTS["pending_validation"] = {"status": "PASSED", "replay": report, "all_reader_T_sizes": [len(r.T) for r in controls.values()]}

    def test_issued_interruption_has_no_fabricated_transition_or_token(self):
        _, learner, _, _, _, report, _ = self.run_case("pending_issued")
        self.assertEqual(learner.T, [])
        self.assertEqual(learner.observed[1], set())
        self.assertTrue(report["pending_issued_preserved"])
        CASE_RESULTS["pending_issued"] = {"status": "PASSED", "replay": report}

    def test_replay_rejects_history_snapshot_phase_and_pending_tampering(self):
        _, learner, _, result, _ = acquire("constant_complete")
        mutations = [lambda state: state["events"][5]["before"]["observations"].__setitem__(0, [1]),
                     lambda state: state["trials"][2].__setitem__("before_snapshot_sha256", "0" * 64),
                     lambda state: state["events"][7].__setitem__("phase", "TRIAL"),
                     lambda state: state["events"][7].__setitem__("assimilated", False)]
        for mutation in mutations:
            state = copy.deepcopy(result["state"])
            mutation(state)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                replay_acquisition(state, learner.state(), DiagnosticSession())
        CASE_RESULTS["replay_tamper"] = {"status": "PASSED", "distinct_mutations_rejected": 4}

    def test_source_frozen_forecast_tamper_is_rejected(self):
        _, _, _, kwargs, session, _, boundaries = self.run_case("constant_complete")
        altered = copy.deepcopy(boundaries[0])
        altered["validation_events"][0]["predictions"]["before"]["probabilities"][0]["probability"] = {"numerator": 1, "denominator": 2}
        with self.assertRaisesRegex(ValueError, "logged frozen forecast"):
            trial_decomposition(altered, CONFIG["acquisition"]["V"], session, **kwargs)

    def test_recomputed_diagnostic_does_not_retroactively_award_unavailable_credit(self):
        _, _, _, kwargs, session, _, boundaries = self.run_case("fresh_predicate")
        altered = copy.deepcopy(boundaries[0])
        altered["trial"]["credit_status"] = "UNAVAILABLE"
        altered["trial"]["credit"] = None
        result = trial_decomposition(altered, CONFIG["acquisition"]["V"], session, **kwargs)
        self.assertEqual(rational(result["gated_credit"]), Fraction(7, 144))
        self.assertIsNone(result["operative_priority_credit"])
        self.assertIsNone(result["source_credit"])
        self.assertTrue(result["reconstructed_gated_credit_is_new_diagnostic_only"])

    def test_decomposition_nonnumeric_component_remains_unavailable(self):
        _, _, _, kwargs, session, _, boundaries = self.run_case("constant_complete")
        original = PrescribedReader.predict
        def predict(reader, history, action, log=False):
            return {"status": "COMPUTATION_INCOMPLETE", "probabilities": None} if action == 1 else original(reader, history, action, log=log)
        with patch.object(PrescribedReader, "predict", predict):
            result = trial_decomposition(boundaries[0], CONFIG["acquisition"]["V"], session, **kwargs)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIsNone(result["mean_count_effect"])
        self.assertIsNone(result["mean_raw_gain"])
        self.assertIsNone(result["gated_credit"])
        self.assertIsNone(result["validation_rows"][0]["count_effect"])

    def test_decomposition_global_refusal_stops_after_first_prediction(self):
        _, _, _, kwargs, _, _, boundaries = self.run_case("constant_complete")
        class PredictionDenial(Meter):
            def __init__(self):
                super().__init__()
                self.denied = False
                self.after = []
            def charge(self, category, units=1, bits=1):
                if self.denied:
                    self.after.append(category)
                if category == "n1.prediction_fraction" and not self.denied:
                    self.work_limit = self.work
                    self.denied = True
                return super().charge(category, units, bits)
        meter = PredictionDenial()
        result = trial_decomposition(boundaries[0], CONFIG["acquisition"]["V"], DiagnosticSession(meter), **kwargs)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertEqual(set(result["partial_predictions"]), {"P00"})
        self.assertEqual(meter.after, [])

    def test_replay_rejects_warmup_word_and_empty_interior_trial(self):
        _, learner, _, result, _ = acquire("constant_complete")
        state = copy.deepcopy(result["state"])
        state["trials"][0]["word"] = [1]
        with self.assertRaisesRegex(ValueError, "warmup word"):
            replay_acquisition(state, learner.state(), DiagnosticSession())
        state = copy.deepcopy(result["state"])
        for event in state["events"]:
            if event["trial_id"] == 0:
                event["trial_id"] = 1
        with self.assertRaisesRegex(ValueError, "empty-event trial"):
            replay_acquisition(state, learner.state(), DiagnosticSession())


if __name__ == "__main__":
    unittest.main()
