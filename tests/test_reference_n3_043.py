"""Predeclared development conformance; no calibration world or target panel."""
import sys
from fractions import Fraction
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from accounting043 import Limit, Meter
from reference_n1_043 import N1
from reference_n3_043 import Acquisition, Scheduler, brier


class ConstantInterface:
    interface_contract = "FABRICATED_PROTOCOL_FIXTURE"
    def __init__(self):
        self.calls = []

    def reset(self):
        self.calls.append(None)
        return (0,)

    def step(self, action):
        self.calls.append(action)
        return (0,)


def scheduler(arm="FULL", actions=(0, 1), L=3, q=4, meter=None):
    value = Scheduler(actions, L, q, arm, meter or Meter())
    for index, action in enumerate(actions):
        value.add_completed((action,), index, warmup=True)
    return value


def acquisition(B_env, arm="FULL", meter=None, V=2, envelope=10_000_000):
    meter = meter or Meter()
    learner = N1(W=1, S=1, K=0, observation_alphabets=((0, 1),), actions=(0, 1), meter=meter)
    interface = ConstantInterface()
    run = Acquisition(interface, learner, arm=arm, L=3, V=V, q=4, B_env=B_env,
                      meter=meter, snapshot_reservation_bytes=envelope)
    return run, learner, interface, meter


class SchedulerTests(unittest.TestCase):
    def test_four_operators_and_multi_parent_dedup(self):
        value = scheduler()
        operators = {detail["operator"] for _, detail in value._mutations((0, 1))}
        self.assertEqual(operators, {"INSERT", "DELETE", "REPLACE", "SWAP"})
        selected = value.select(1)
        self.assertEqual(selected["word"], (0, 0))
        mixed = next(row for row in value.queue if row["word"] == (0, 1))
        self.assertEqual(mixed["parents"], [0, 1])
        self.assertEqual(mixed["selected_parent"], 0)
        self.assertEqual(sum(row["word"] == (0, 1) for row in value.queue), 1)

    def test_max_parent_mean_then_child_then_parent_ties(self):
        value = scheduler(arm="MACRO_OFF")
        value.add_completed((0,), 2, Fraction(-1, 2))
        value.add_completed((1,), 3, Fraction(1, 3))
        selected = value.select(1)
        self.assertEqual(selected["word"], (0, 1))
        self.assertEqual(selected["selected_parent"], 1)
        self.assertEqual(selected["operative_score"], Fraction(1, 3))
        # Mandatory qth coverage ignores the positive priority.
        self.assertEqual(value.select(4)["word"], (0, 0))

    def test_full_promotion_only_and_shadow_null_priority(self):
        values = [scheduler(arm=arm) for arm in ("FULL", "MACRO_OFF", "FEEDBACK_NULL", "COVERAGE")]
        for value in values:
            value.add_completed((0, 1, 0), 2, Fraction(1, 5))
        self.assertIn((0, 1), [row["word"] for row in values[0].M])
        for value in values[1:]:
            self.assertEqual([row["word"] for row in value.M], [(0,), (1,)])
        self.assertEqual(values[2].select(1)["operative_score"], 0)
        self.assertEqual(values[2].F[-1]["utility_sum"], Fraction(1, 5))

    def test_null_and_direct_coverage_identical_until_finite_exhaustion(self):
        null, direct = scheduler(arm="FEEDBACK_NULL"), scheduler(arm="COVERAGE")
        for t in range(1, 13):
            left, right = null.select(t), direct.select(t)
            self.assertIsNotNone(left)
            self.assertEqual(left["word"], right["word"])
            null.add_completed(left["word"], t + 1, Fraction(-t, 7))
            direct.add_completed(right["word"], t + 1, Fraction(-t, 7))
        self.assertIsNone(null.select(13))
        self.assertIsNone(direct.select(13))
        self.assertGreater(null.meter.work, direct.meter.work)


class AcquisitionTests(unittest.TestCase):
    def test_unknown_reset_contract_is_not_inferred_from_methods(self):
        interface = ConstantInterface()
        interface.interface_contract = None
        meter = Meter()
        learner = N1(W=0, S=1, K=0, observation_alphabets=((0,),), actions=(0,), meter=meter)
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_INTERFACE"):
            Acquisition(interface, learner, arm="COVERAGE", L=1, V=1, q=2,
                        B_env=4, meter=meter, snapshot_reservation_bytes=100_000)
        self.assertEqual(interface.calls, [])

    def test_interrupted_issued_action_preserves_pending_encounter_without_outcome(self):
        class InterruptedInterface(ConstantInterface):
            def step(self, action):
                self.calls.append(action)
                raise OSError("fabricated interface interruption")

        meter = Meter()
        learner = N1(W=0, S=1, K=0, observation_alphabets=((0,),), actions=(0,), meter=meter)
        interface = InterruptedInterface()
        run = Acquisition(interface, learner, arm="COVERAGE", L=1, V=1, q=2,
                          B_env=4, meter=meter, snapshot_reservation_bytes=100_000)
        result = run.run()
        self.assertEqual(result["status"], "ENVIRONMENT_INTERRUPTED")
        self.assertEqual(interface.calls, [None, 0])
        self.assertEqual(learner.T, [])
        self.assertTrue(result["state"]["encounter_inventory_pending"])
        self.assertEqual(run.events[-1]["status"], "INTERRUPTED")
        self.assertIsNone(run.events[-1]["outcome"])

    def test_exact_brier_sign_and_nonnumeric(self):
        p = {"status": "OBSERVED_SINGLE_OUTCOME", "probabilities": {(0,): Fraction(3, 4), (1,): Fraction(1, 4)}}
        self.assertEqual(brier(p, (0,), Meter()), Fraction(1, 8))
        self.assertEqual(brier(p, (1,), Meter()), Fraction(9, 8))
        self.assertIsNone(brier({"status": "COMPUTATION_INCOMPLETE"}, (0,), Meter()))

    def test_paid_warmup_and_trial_only_reservation_with_partial_validation(self):
        run, learner, interface, _ = acquisition(8)
        result = run.run()
        self.assertEqual(result["status"], "ENVIRONMENT_LIMIT")
        self.assertEqual(interface.calls, [None, 0, None, 1, None, 0, 0, 1])
        self.assertEqual(run.t, 1)
        record = run.trials[2]
        self.assertEqual(record["status"], "COMPLETED")
        self.assertEqual(record["credit_status"], "INCOMPLETE")
        self.assertIsNone(record["credit"])
        self.assertEqual(len(record["validation"]), 1)
        self.assertEqual(len(learner.T), 5)
        self.assertEqual(run.pending_validation, [])
        self.assertTrue(run.events[-1]["assimilated"])
        self.assertEqual(run.scheduler.F[-1]["utility_count"], 0)

    def test_complete_validation_frozen_snapshots_and_fresh_predicate_gate(self):
        run, learner, interface, _ = acquisition(9)
        result = run.run()
        record = run.trials[2]
        self.assertEqual(record["credit_status"], "AVAILABLE")
        self.assertEqual(record["credit"], 0)
        self.assertEqual(len(learner.T), 6)
        self.assertEqual(run.t, 2)  # failed next trial reservation is still logged
        self.assertEqual(len(interface.calls), 9)
        self.assertTrue(record["finalized_before_validation_assimilation"])
        rows = [event for event in run.events if event["phase"] == "VALIDATION"]
        self.assertEqual([event["action"] for event in rows], [1, 0])
        self.assertTrue(all(event["predictions"]["before"]["probabilities"] for event in rows))
        # Count-only improvement can be positive while the literal gate is zero.
        self.assertTrue(any(row["brier_difference"]["numerator"] > 0 for row in record["validation"]))
        self.assertFalse(result["target_scores_generated"])

    def test_no_partial_word_when_full_trial_does_not_fit(self):
        run, learner, interface, _ = acquisition(6)
        result = run.run()
        self.assertEqual(result["status"], "ENVIRONMENT_LIMIT")
        self.assertEqual(len(interface.calls), 4)
        self.assertEqual(len(learner.T), 2)
        self.assertEqual(run.t, 1)

    def test_response_storage_preflight_stops_before_environment_call(self):
        run, _, interface, meter = acquisition(9)
        meter.memory_limit = meter.retained_bytes
        result = run.run()
        self.assertEqual(result["status"], "MEMORY_LIMIT")
        self.assertEqual(interface.calls, [])

    def test_snapshot_envelope_failure_preserves_physically_completed_trial(self):
        run, learner, interface, _ = acquisition(9, envelope=0)
        result = run.run()
        self.assertEqual(result["status"], "SNAPSHOT_ENVELOPE_EXCEEDED")
        self.assertEqual(len(interface.calls), 7)
        self.assertEqual(run.trials[2]["status"], "COMPLETED")
        self.assertEqual(run.trials[2]["credit_status"], "INCOMPLETE")
        self.assertNotIn((0, 0), [row["word"] for row in run.scheduler.F])
        self.assertTrue(run.trials[2]["library_update_pending"])
        self.assertEqual(len(learner.T), 4)

    def test_exhausted_work_does_not_issue_an_action_or_refill(self):
        run, _, interface, meter = acquisition(9)
        meter.work_limit = meter.work
        result = run.run()
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(interface.calls, [])
        with self.assertRaises(ValueError):
            run.run()

    def test_denied_score_debit_keeps_validation_pending_without_later_science(self):
        class DenialMeter(Meter):
            def __init__(self):
                super().__init__()
                self.denied = False
                self.after_denial = []

            def charge(self, category, units=1, bits=1):
                if self.denied:
                    self.after_denial.append(category)
                if category == "n3_brier_outcome" and not self.denied:
                    self.denied = True
                    self.work_limit = self.work + 1
                return super().charge(category, units, bits)

        meter = DenialMeter()
        run, learner, interface, _ = acquisition(9, meter=meter)
        result = run.run()
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(len(interface.calls), 8)
        self.assertEqual(len(learner.T), 4)
        self.assertEqual(len(run.pending_validation), 1)
        self.assertTrue(run.trials[2]["library_update_pending"])
        self.assertEqual([row["word"] for row in run.scheduler.F], [(0,), (1,)])
        self.assertFalse(any(category.startswith("n1.") or category.startswith("n3_") for category in meter.after_denial))

    def test_fresh_predicate_is_credited_only_from_its_trial(self):
        class ScriptedInterface(ConstantInterface):
            def __init__(self):
                super().__init__()
                self.outputs = iter((0, 0, 0, 1, 0, 0))

            def step(self, action):
                self.calls.append(action)
                return (next(self.outputs),)

        meter = Meter()
        learner = N1(W=1, S=1, K=1, observation_alphabets=((0, 1),), actions=(0, 1), meter=meter)
        run = Acquisition(ScriptedInterface(), learner, arm="FULL", L=3, V=2, q=4,
                          B_env=9, meter=meter, snapshot_reservation_bytes=10_000_000)
        run.run()
        record = run.trials[2]
        self.assertEqual(len(record["new_predicates"]), 1)
        self.assertEqual(record["credit_status"], "AVAILABLE")
        self.assertEqual(record["credit"], Fraction(7, 144))
        self.assertIn((0, 0), [row["word"] for row in run.scheduler.M])

    def test_snapshot_nonnumeric_after_global_denial_cannot_issue_validation(self):
        class PredictionDenial(Meter):
            def charge(self, category, units=1, bits=1):
                if category == "n1.prediction_fraction" and self.work_limit is None:
                    self.work_limit = self.work + 1
                return super().charge(category, units, bits)

        run, learner, interface, _ = acquisition(9, meter=PredictionDenial())
        result = run.run()
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(len(interface.calls), 7)
        self.assertEqual(len(learner.T), 4)
        self.assertEqual(run.trials[2]["validation"], [])
        self.assertEqual([row["word"] for row in run.scheduler.F], [(0,), (1,)])

    def test_library_update_denial_does_not_start_validation_assimilation(self):
        class LibraryDenial(Meter):
            def charge(self, category, units=1, bits=1):
                if category == "n3_utility_accumulate" and self.work_limit is None:
                    self.work_limit = self.work
                return super().charge(category, units, bits)

        run, learner, interface, _ = acquisition(9, meter=LibraryDenial())
        result = run.run()
        self.assertEqual(result["status"], "COMPUTATION_INCOMPLETE")
        self.assertEqual(len(interface.calls), 9)
        self.assertEqual(len(learner.T), 4)
        self.assertEqual(len(run.pending_validation), 2)
        self.assertEqual(run.trials[2]["credit_status"], "AVAILABLE")
        self.assertTrue(run.trials[2]["library_update_pending"])


if __name__ == "__main__":
    unittest.main()
