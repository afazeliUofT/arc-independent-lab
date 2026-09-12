"""Fabricated conformance fixtures only; no target world or target outcomes."""
import itertools
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from accounting043 import Limit, Meter
from reference_n1_043 import N1, GenericReader, History, evaluate, tree_size, tree_tokens


def contrasting_histories():
    return (History.initial((0,)).advance(0, (0,)),
            History.initial((1,)).advance(0, (0,)))


class InterruptMeter(Meter):
    def __init__(self):
        super().__init__()
        self.category = None
        self.remaining = 0

    def charge(self, category, units=1, bits=1):
        if category == self.category:
            if self.remaining == 0:
                self.category = None
                raise Limit('COMPUTATION_INCOMPLETE')
            self.remaining -= 1
        return super().charge(category, units, bits)


class N1Conformance(unittest.TestCase):
    def test_literal_inventory_and_typed_missing(self):
        learner = N1()
        for i in range(5):
            learner.observe_reset((i,))
            learner.observe_action(i)
        learner.resume()
        self.assertEqual(38, sum(tree_size(x) == 1 for x in learner.inventory))
        self.assertEqual(3002, len(learner.inventory))
        self.assertEqual(3002, len(set(learner.inventory)))
        self.assertEqual(learner.inventory, sorted(learner.inventory, key=lambda x: (tree_size(x), tree_tokens(x))))
        missing_equal = (0, (0, 0, 0, 1), (0, 0, 0, 2))
        missing_constant = (0, (0, 0, 0, 1), (1, 0, 0))
        self.assertTrue(evaluate(missing_equal, History.initial((0,))))
        self.assertFalse(evaluate(missing_constant, History.initial((0,))))
        # Same typed term comparisons are ordered and retain self equality.
        self.assertIn((0, (0, 1, 0, 1), (0, 1, 0, 1)), learner.inventory)
        self.assertNotIn((0, (0, 0, 0, 0), (1, 0, -1)), learner.inventory)

    def test_greedy_bitsets_match_literal_pair_oracle(self):
        learner = N1(W=1, S=3, K=2, observation_alphabets=((0, 1),), actions=(0, 1))
        first, second = contrasting_histories()
        learner.append(first, 1, (0,), search=False)
        learner.append(second, 1, (1,), search=False)
        learner._ensure_inventory()
        literal_gains = []
        for expr in learner.inventory:
            gain = sum(evaluate(expr, a.history) != evaluate(expr, b.history)
                       for a, b in itertools.combinations(learner.T, 2)
                       if a.history.current == b.history.current and a.action == b.action and a.outcome != b.outcome)
            literal_gains.append((gain, expr))
        expected = min(((-gain, tree_size(expr), tree_tokens(expr), expr) for gain, expr in literal_gains if gain > 0))[-1]
        learner.resume()
        self.assertEqual([expected], learner.Phi)
        self.assertEqual(1, learner.construction_log[0]['gain'])
        self.assertEqual('OBSERVED_SINGLE_OUTCOME', learner.predict(first, 1)['status'])
        self.assertEqual(Fraction(2, 3), learner.predict(first, 1)['probabilities'][(0,)])
        self.assertEqual(Fraction(2, 3), learner.predict(second, 1)['probabilities'][(1,)])

    def test_complete_pass_required_and_resumable(self):
        meter = InterruptMeter()
        learner = N1(W=1, S=3, K=2, observation_alphabets=((0, 1),), actions=(0, 1), meter=meter)
        first, second = contrasting_histories()
        learner.append(first, 1, (0,), search=False)
        learner.append(second, 1, (1,), search=False)
        meter.category, meter.remaining = 'n1.candidate_access_and_selected_test', 5
        stopped = learner.resume()
        self.assertEqual('COMPUTATION_INCOMPLETE', stopped['status'])
        self.assertEqual([], learner.Phi)
        self.assertEqual(5, learner.cursor['next'])
        self.assertEqual('OBSERVED_CONFLICT', learner.predict(first, 1)['status'])
        learner.resume()
        self.assertEqual(1, len(learner.Phi))
        self.assertTrue(learner.counts_ready)

    def test_stale_cursor_and_dirty_counts_do_not_predict_stale_probabilities(self):
        meter = InterruptMeter()
        learner = N1(W=1, S=3, K=2, observation_alphabets=((0, 1),), actions=(0, 1), meter=meter)
        first, second = contrasting_histories()
        learner.append(first, 1, (0,), search=False)
        learner.append(second, 1, (1,), search=False)
        meter.category, meter.remaining = 'n1.candidate_access_and_selected_test', 2
        learner.resume()
        old_version = learner.table_version
        meter.category, meter.remaining = 'n1.count_scan', 0
        result = learner.append(first, 1, (0,))
        self.assertTrue(result['appended'])
        self.assertEqual(old_version + 1, learner.table_version)
        self.assertFalse(learner.counts_ready)
        self.assertEqual('COMPUTATION_INCOMPLETE', learner.predict(first, 1)['status'])
        self.assertIsNone(learner.cursor)
        self.assertEqual('DISCARDED_CURSOR', learner.search_log[-1]['event'])
        learner.resume()
        self.assertTrue(learner.counts_ready)
        self.assertEqual(2, learner.predict(first, 1)['counts'][(0,)])

    def test_snapshots_are_independent_and_unseen_keys_uniform(self):
        learner = N1(W=1, S=1, K=0, observation_alphabets=((0, 1),), actions=(0, 1))
        history = History.initial((0,))
        learner.append(history, 0, (0,))
        frozen = learner.snapshot()
        original = frozen.predict(history, 0, log=False)
        learner.append(history, 0, (1,))
        self.assertEqual(original, frozen.predict(history, 0, log=False))
        self.assertEqual({(0,): Fraction(1, 2), (1,): Fraction(1, 2)}, frozen.predict(history, 1)['probabilities'])
        self.assertEqual([0], sorted(frozen.observed[0]))
        self.assertEqual([0, 1], sorted(learner.observed[0]))
        self.assertNotEqual(learner.owner, frozen.owner)
        frozen.close()
        # Refusing a copy after its reservation must not leave an owner claiming
        # that an actual returned snapshot exists.
        interrupted_meter = InterruptMeter()
        interrupted = N1(W=0, S=1, K=0, observation_alphabets=((0, 1),), actions=(0, 1), meter=interrupted_meter)
        interrupted.append(history, 0, (0,), search=False)
        owners_before = dict(interrupted_meter.owners)
        interrupted_meter.category, interrupted_meter.remaining = 'n1.snapshot_copy_bytes', 0
        with self.assertRaises(Limit):
            interrupted.snapshot()
        self.assertEqual(owners_before, interrupted_meter.owners)
        self.assertEqual([], interrupted_meter.state()['open_prepaid_cleanup_owners'])
        # A prepaid release works at an exhausted work cap, cannot be reused,
        # and does not refund successful work.
        lease = interrupted_meter.prepay_release('temporary-fixture')
        interrupted_meter.reserve('temporary-fixture', 17)
        spent = interrupted_meter.work
        interrupted_meter.work_limit = spent
        interrupted_meter.release_prepaid(lease)
        self.assertEqual(spent, interrupted_meter.work)
        self.assertNotIn('temporary-fixture', interrupted_meter.owners)
        with self.assertRaises(ValueError):
            interrupted_meter.release_prepaid(lease)

    def test_fixed_readers_receive_same_table_and_missing_boundaries(self):
        learner = N1(W=1, S=1, K=0, observation_alphabets=((0, 1),), actions=(0, 1))
        first, second = contrasting_histories()
        learner.append(first, 1, (0,), search=False)
        learner.append(second, 1, (1,), search=False)
        readers = [GenericReader(k, observation_alphabets=((0, 1),), actions=(0, 1)) for k in (0, 1, 2)]
        for reader in readers:
            self.assertEqual('COMPLETE', reader.fit(learner.T)['status'])
            self.assertEqual([x.state() for x in learner.T], [x.state() for x in reader.T])
            self.assertEqual(len(learner.T), reader.meter.calls.get('n1.count_scan'))
        self.assertEqual(1, len({reader.source_table_sha256 for reader in readers}))
        self.assertEqual('OBSERVED_CONFLICT', readers[0].predict(first, 1)['status'])
        self.assertEqual('OBSERVED_SINGLE_OUTCOME', readers[1].predict(first, 1)['status'])
        self.assertEqual('OBSERVED_SINGLE_OUTCOME', readers[2].predict(first, 1)['status'])
        self.assertEqual('UNSEEN_KEY', readers[1].predict(History.initial((0,)), 1)['status'])

    def test_all_conflicting_pairs_retained_in_outcome_masks(self):
        learner = N1(W=0, S=1, K=2, observation_alphabets=((0, 1),), actions=(0, 1))
        history = History.initial((0,))
        for outcome in (0, 1, 0, 1):
            learner.append(history, 0, (outcome,))
        self.assertEqual('GRAMMAR_LIMITED', learner.search_status)
        self.assertEqual([], learner.Phi)
        self.assertEqual(1, len(learner.groups))
        masks = dict(learner.groups[0]['outcomes'])
        self.assertEqual(0b0101, masks[(0,)])
        self.assertEqual(0b1010, masks[(1,)])
        self.assertEqual(4, masks[(0,)].bit_count() * masks[(1,)].bit_count())

    def test_new_block_archives_old_empirical_evidence(self):
        learner = N1(W=1, S=1, K=2, observation_alphabets=((0, 1),), actions=(0, 1))
        first, second = contrasting_histories()
        learner.append(first, 1, (0,))
        learner.predict(first, 1)
        learner.new_block('second')
        self.assertEqual([], learner.T)
        archived = learner.archives[0]
        self.assertEqual(1, len(archived['transitions']))
        self.assertEqual('UNSEEN_KEY', learner.predict(first, 1)['status'])
        self.assertEqual([], archived['Phi'])
        self.assertEqual([], archived['construction_log'])
        self.assertEqual(1, len(archived['prediction_log']))
        learner.append(first, 1, (0,))
        learner.append(second, 1, (1,))
        learner.predict(first, 1)
        self.assertEqual(1, len(learner.Phi))
        self.assertEqual([], archived['Phi'])
        self.assertEqual([], archived['construction_log'])
        self.assertEqual(1, len(archived['prediction_log']))


if __name__ == '__main__':
    unittest.main()
