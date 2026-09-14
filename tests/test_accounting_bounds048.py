import importlib.util
from pathlib import Path
from fractions import Fraction
import sys
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "accounting_bounds048.py"
SPEC = importlib.util.spec_from_file_location("accounting_bounds048", MODULE_PATH)
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class AccountingBounds048Tests(unittest.TestCase):
    def compare(self, domain):
        slow = m.reference_bounds(domain)
        states = slow.pop("reference_count_vectors")
        self.assertEqual(slow, m.algebraic_bounds(domain), repr(domain))
        self.assertEqual(m.transition_table_bound(domain),
                         m.reference_transition_table_bound(domain), repr(domain))
        return slow, states

    def test_finite_small_domain_reference(self):
        for actions in (1, 2, 3):
            budgets = sorted({0, 1, 2 * actions - 1, 2 * actions, 2 * actions + 1, 10, 20, 40})
            for length in (1, 2, 3, 4):
                for validation in (1, 2, 3):
                    for budget in budgets:
                        self.compare(m.Domain(actions, length, validation, budget))

    def test_actual042_reference_and_terminal_multiplicities(self):
        bounds, states = self.compare(m.Domain())
        expected = {
            "completed_scored_trials": 50, "scored_trial_records": 51,
            "total_trial_records": 56, "event_bearing_scored_boundaries": 50,
            "replay_boundary_table_partition_copies": 100,
            "decomposition_reader_attempts": 150,
            "completed_validation_events": 100,
            "decomposition_validation_forecasts": 300,
            "acquisition_snapshot_attempts": 100,
            "scheduler_selection_attempts": 51,
            "mutation_assemblies_noncoverage_arms": 39,
            "mutation_assemblies_coverage_arm": 0,
            "recipe_records": 55, "macro_records": 45,
            "raw_mutations_per_assembly": 27720,
            "raw_insertion_word_tokens": 10, "nonempty_word_vocabulary": 3905,
        }
        self.assertEqual(bounds, expected)
        self.assertEqual(m.transition_table_bound(m.Domain()), 245)
        self.assertGreater(states, 1)

    def test_whole_trial_reservation_precedes_first_event(self):
        for budget in (4, 5, 6):
            b, _ = self.compare(m.Domain(2, 2, 2, budget))
            self.assertEqual((b["scored_trial_records"], b["event_bearing_scored_boundaries"]), (1, 0))
        for budget in (7, 8):
            b, _ = self.compare(m.Domain(2, 2, 2, budget))
            self.assertEqual((b["completed_scored_trials"], b["event_bearing_scored_boundaries"]), (0, 1))
            self.assertEqual(b["completed_validation_events"], budget - 7)
        b, _ = self.compare(m.Domain(2, 2, 2, 9))
        self.assertEqual((b["completed_scored_trials"], b["scored_trial_records"], b["event_bearing_scored_boundaries"]), (1, 2, 1))

    def test_exhausted_vocabulary_and_coverage(self):
        b, _ = self.compare(m.Domain(1, 2, 1, 6))
        self.assertEqual((b["completed_scored_trials"], b["scored_trial_records"], b["scheduler_selection_attempts"]), (1, 1, 2))
        self.assertEqual(b["mutation_assemblies_coverage_arm"], 0)
        self.assertEqual(m.algebraic_bounds(m.Domain(max_word=1))["scored_trial_records"], 0)

    def test_reduced_result_and_unreduced_rational_caps(self):
        caps = m.reduced_credit_caps()
        self.assertEqual(caps["reduced_credit_denominator"], 30517578125000000000)
        self.assertEqual((caps["denominator_bits"], caps["absolute_numerator_bits"]), (65, 66))
        for a in range(-3, 4):
            for b in range(1, 5):
                for c in range(-3, 4):
                    for d in range(1, 5):
                        for op in ("add", "sub", "mul", "div"):
                            if op == "div" and c == 0:
                                continue
                            bound_n, bound_d = m.unreduced_rational_caps(op, (abs(a), b), (abs(c), d))
                            if op == "add":
                                raw_n, raw_d = a * d + c * b, b * d
                            elif op == "sub":
                                raw_n, raw_d = a * d - c * b, b * d
                            elif op == "mul":
                                raw_n, raw_d = a * c, b * d
                            else:
                                raw_n, raw_d = a * d, b * c
                            self.assertLessEqual(abs(raw_n), bound_n)
                            self.assertLessEqual(abs(raw_d), bound_d)
                            reduced = Fraction(raw_n, raw_d)
                            self.assertLessEqual(abs(reduced.numerator), bound_n)
                            self.assertLessEqual(reduced.denominator, max(1, bound_d))


if __name__ == "__main__":
    unittest.main()
