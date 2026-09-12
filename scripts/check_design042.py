#!/usr/bin/env python3
"""Finite instrument conformance only; no candidate, reader fitting or scheduler.

The role-aware transducer and hand-prepared witnesses below are evaluator checks.
They are never learner inputs. The release wrapper pins this file and all inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
from fractions import Fraction

sys.dont_write_bytecode = True

KIND = 'P3_CALIBRATION_DESIGN_CHECK_042_v1'
CODE_PATH = 'scripts/check_design042.py'
CONFIG_PATH = 'configs/P3_CALIBRATION_DESIGN_042.json'
SOURCE_PINS = {
    'docs/P2_SECOND_OPERATION_SPECIFICATIONS_035.md': '25f3148827d22abbe587a6c2ff0c5a3ff2db1883f70e678f640f16d0f07a7c69',
    'docs/P3_N1_N3_SUCCESSOR_COMPARISON_041.md': '70424ad00f17056b1508a46e385b75496a7c25f51d5bb648377995761da4cef5',
    'evidence/P3_INSTRUMENT_CHECK_PLAN_042.md': '4549e6fd21bf4f38d80300511aaa77bfe7b1464366bfc01b6556bd55dacb8f6c',
    CONFIG_PATH: 'bd892bf72027ddb3d3ebdee979e4304cad5e36766a87d240acd32d11d783ee5f',
    'docs/P3_COMPARISON_DESIGN_042.md': '597ad1981a90682eea3e8e0118bbea0c9268d2f2edb82a20bce8c1c018d593fb',
    'evidence/P3_COMPARISON_FEASIBILITY_042.md': '4e8fdaa35d82f874f141540d91b307088567969d04780454d656afd03ff0d57a',
}
ACTION_ROLES = ('SET_0', 'SET_1', 'MASK', 'PROBE_0', 'PROBE_1')
OBSERVATION_ROLES = ('CUE_0', 'CUE_1', 'NEUTRAL', 'MATCH', 'MISMATCH')
BOUNDARIES = {
    'instrument_only': True,
    'N1_or_N3_instantiated': False,
    'acquisition_scheduler_executed': False,
    'predictor_fit': False,
    'target_candidate_scores_generated': False,
    'candidate_or_experiment_started': False,
    'treatment_or_profile_executed': False,
    'native_starts': 0,
    'model_turns_sent': 0,
    'independent_scientific_verdict_created': False,
    'future_experiment_admission': False,
    'private_paper_content_read_or_published': False,
}


class DesignCheckError(Exception):
    """The argument is a fixed public-safe failure code, never exception text."""


def require(condition, code):
    if not condition:
        raise DesignCheckError(code)


def canonical(value):
    """Panel digest: UTF-8, sorted object keys, compact separators, no newline."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_public(root, name):
    require(not root.is_symlink() and root.is_dir(), 'source_root_refused')
    path = root
    for part in Path(name).parts:
        require(part not in ('', '.', '..'), 'source_relative_path_refused')
        path = path / part
        require(not path.is_symlink(), 'source_symlink_refused')
    require(path.is_file(), 'source_file_missing')
    require(path.stat().st_size <= 2 * 1024 * 1024, 'source_size_refused')
    return path.read_bytes()


def role_transition(register, role):
    """Complete five-action evaluator truth table; no fitted parameters."""
    require(register in (0, 1), 'instrument_register_domain')
    require(type(role) is int and 0 <= role < 5, 'instrument_role_domain')
    if role < 2:
        return role, role
    if role == 2:
        return register, 2
    return register, 3 if register == role - 3 else 4


class OpaqueWorld:
    """Only reset() and step(opaque_action) return ordinary one-token tuples.

    Private evaluator mappings and register are not a proposed learner interface.
    No learner exists in this module. Calls count structural validation work only.
    """
    def __init__(self, action_map, observation_map, initial, counters):
        require(sorted(action_map) == list(range(5)), 'action_bijection')
        require(sorted(observation_map) == list(range(5)), 'observation_bijection')
        self._inverse_actions = {opaque: role for role, opaque in enumerate(action_map)}
        self._observations = tuple(observation_map)
        self._initial = initial
        self._register = initial
        self._counters = counters

    def reset(self):
        self._register = self._initial
        self._counters['reset_calls'] += 1
        return (self._observations[2],)

    def step(self, action):
        require(type(action) is int and action in self._inverse_actions,
                'opaque_action_domain')
        self._register, observed_role = role_transition(
            self._register, self._inverse_actions[action])
        self._counters['primitive_calls'] += 1
        return (self._observations[observed_role],)


def trace(world, word):
    observations = [world.reset()]
    for action in word:
        observation = world.step(action)
        require(type(observation) is tuple and len(observation) == 1
                and type(observation[0]) is int and 0 <= observation[0] < 5,
                'ordinary_observation_interface')
        observations.append(observation)
    return tuple(word), tuple(observations)


def typed_window(history, order):
    """Proof terms only; not the future executable retained-byte encoding.

    Each row is (type, field, lag, present/missing, opaque token). Action fields
    are None, observations field zero. A typed MISSING cannot equal a token or
    the other type's MISSING. The predicted action is outside this window.
    """
    actions, observations = history
    require(type(order) is int and 0 <= order <= 2, 'window_order_domain')
    require(len(observations) == len(actions) + 1, 'history_shape')
    rows = []
    for lag in range(order + 1):
        available = lag < len(observations)
        rows.append(('observation', 0, lag, 'TOKEN' if available else 'MISSING',
                     observations[-1-lag][0] if available else None))
    for lag in range(1, order + 1):
        available = lag <= len(actions)
        rows.append(('action', None, lag, 'TOKEN' if available else 'MISSING',
                     actions[-lag] if available else None))
    return tuple(rows)


def preparation_last_role(b, endpoint):
    if endpoint < 3:
        return endpoint
    return 3 + (1 - b if endpoint == 3 else b)


def short_endpoint_role(initial, endpoint):
    if endpoint < 3:
        return endpoint
    return 3 + (initial if endpoint == 3 else 1 - initial)


def fraction(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def static_checks(config):
    require(config['kind'] == 'P3_CALIBRATION_DESIGN_042_v1', 'config_kind')
    require(config['parameters'] == {
        'W': 2, 'S': 3, 'K': 4, 'L': 5, 'V': 2, 'q': 4,
        'B_env_acquisition': 285}, 'config_parameter_contract')
    require(config['world']['action_roles'] == list(ACTION_ROLES)
            and config['world']['observation_roles'] == list(OBSERVATION_ROLES),
            'config_role_order')
    require(config['panel']['action_permutation_ranks'] == list(range(120))
            and config['panel']['initial_register_values'] == [0, 1]
            and config['panel']['observation_permutation_rank_multiplier'] == 37
            and config['panel']['observation_permutation_rank_offset'] == 11
            and config['panel']['observation_permutation_modulus'] == 120,
            'config_panel_membership')
    require(config['resource_admission']['B_comp'] is None
            and config['resource_admission']['B_mem'] is None
            and config['resource_admission']['target_execution_admitted'] is False,
            'config_no_resource_admission')

    permutations = tuple(itertools.permutations(range(5)))
    require(len(permutations) == 120, 'permutation_count')
    obs_ranks = [(37 * r + 11) % 120 for r in range(120)]
    require(sorted(obs_ranks) == list(range(120)), 'observation_rank_marginal_balance')
    counters = {'reset_calls': 0, 'primitive_calls': 0}
    checked = {
        'opaque_instances': 0, 'planned_decisions': 0,
        'distinct_target_windows': 0, 'order1_support_cells': 0,
        'order2_support_cells': 0, 'unique_goal_action_witnesses': 0,
        'inherently_ambiguous_probe_pairs': 0,
        'two_step_isolation_cases': 0,
        'cue_isolated_neutral_cases': 0,
    }
    panel = []
    representatives = {}
    for rank, action_map in enumerate(permutations):
        observation_rank = obs_ranks[rank]
        observation_map = permutations[observation_rank]
        for initial in (0, 1):
            world = OpaqueWorld(action_map, observation_map, initial, counters)
            require(world.reset() == (observation_map[2],), 'paid_reset_observation')
            require(world.step(action_map[3 + initial]) == (observation_map[3],),
                    'paid_reset_initial_register')
            world.step(action_map[1-initial])
            require(world.reset() == (observation_map[2],)
                    and world.step(action_map[3 + initial]) == (observation_map[3],),
                    'reset_restores_after_overwrite')
            empty = trace(world, ())
            missing = typed_window(empty, 2)
            require(missing == (
                ('observation', 0, 0, 'TOKEN', observation_map[2]),
                ('observation', 0, 1, 'MISSING', None),
                ('observation', 0, 2, 'MISSING', None),
                ('action', None, 1, 'MISSING', None),
                ('action', None, 2, 'MISSING', None)), 'typed_missing_reset_window')
            once = trace(world, (action_map[0],))
            require(typed_window(once, 2) == (
                ('observation', 0, 0, 'TOKEN', observation_map[0]),
                ('observation', 0, 1, 'TOKEN', observation_map[2]),
                ('observation', 0, 2, 'MISSING', None),
                ('action', None, 1, 'TOKEN', action_map[0]),
                ('action', None, 2, 'MISSING', None)), 'typed_lags_after_one_action')
            require(typed_window(trace(world, ()), 2) == missing,
                    'lags_do_not_cross_reset')

            query_rows = []
            windows = set()
            for b in (0, 1):
                for endpoint in range(5):
                    roles = (1-b,) + (2,) * 5 + (preparation_last_role(b, endpoint), b, 2)
                    word = tuple(action_map[role] for role in roles)
                    history = trace(world, word)
                    require(len(word) == 9 and len(word) > 5 + 2,
                            'whole_history_absence_length')
                    require(history[1][-3] == (observation_map[endpoint],),
                            'preparation_endpoint')
                    expected2 = (
                        ('observation', 0, 0, 'TOKEN', observation_map[2]),
                        ('observation', 0, 1, 'TOKEN', observation_map[b]),
                        ('observation', 0, 2, 'TOKEN', observation_map[endpoint]),
                        ('action', None, 1, 'TOKEN', action_map[2]),
                        ('action', None, 2, 'TOKEN', action_map[b]))
                    require(typed_window(history, 2) == expected2, 'target_order2_window')
                    expected1 = (expected2[0], expected2[1], expected2[3])
                    require(typed_window(history, 1) == expected1, 'target_order1_window')
                    windows.add(expected2)
                    cue_vector = tuple(history[1][-2][0] == observation_map[c] for c in (0, 1))
                    require(cue_vector == (b == 0, b == 1), 'cue_witness_target_separation')

                    # The five outcomes are truth-table checks, not a candidate's
                    # chosen action, forecast, empirical target score or training.
                    possible = []
                    for opaque_action in range(5):
                        trace(world, word)
                        possible.append(world.step(opaque_action)[0])
                    for goal in (3, 4):
                        good = [a for a, output in enumerate(possible)
                                if output == observation_map[goal]]
                        expected_action = action_map[3 + (b if goal == 3 else 1-b)]
                        require(good == [expected_action], 'unique_goal_producing_probe')
                        require(1 + len(word) + 1 == 11, 'logical_evaluation_call_count')
                        query_rows.append([b, endpoint, goal, list(word), observation_map[goal]])
                        checked['unique_goal_action_witnesses'] += 1
                        checked['planned_decisions'] += 1

                    short_role = short_endpoint_role(initial, endpoint)
                    prefix2 = (action_map[short_role], action_map[b], action_map[2])
                    before2 = trace(world, prefix2)
                    require(typed_window(before2, 2) == expected2,
                            'order2_short_word_same_before_window')
                    for probe in (0, 1):
                        before2 = trace(world, prefix2)
                        support_outcome2 = world.step(action_map[3 + probe])
                        require(len(prefix2) + 1 == 4 <= config['parameters']['L'],
                                'order2_support_length')
                        require(support_outcome2 == (observation_map[3 if b == probe else 4],),
                                'order2_support_observation')
                        checked['order2_support_cells'] += 1
                    if rank == 0 and initial == 0 and b == 1 and endpoint == 4:
                        representatives['long_and_order2_short_support'] = {
                            'world_action_rank': rank, 'world_observation_rank': observation_rank,
                            'initial_register': initial, 'final_setter_value': b,
                            'preparation_endpoint_role': OBSERVATION_ROLES[endpoint],
                            'long_opaque_word': list(word),
                            'short_opaque_probe_word': list(prefix2) + [action_map[3+b]],
                            'identical_before_window': expected2,
                            'witness_only_not_a_selected_or_executed_learner_action': True,
                        }
                prefix1 = (action_map[b], action_map[2])
                before1 = trace(world, prefix1)
                require(typed_window(before1, 1) == (
                    ('observation', 0, 0, 'TOKEN', observation_map[2]),
                    ('observation', 0, 1, 'TOKEN', observation_map[b]),
                    ('action', None, 1, 'TOKEN', action_map[2])),
                    'order1_short_word_same_before_window')
                for probe in (0, 1):
                    trace(world, prefix1)
                    require(world.step(action_map[3+probe]) ==
                            (observation_map[3 if b == probe else 4],), 'order1_support_observation')
                    require(len(prefix1) + 1 == 3 <= config['parameters']['L'],
                            'order1_support_length')
                    checked['order1_support_cells'] += 1

            require(len(windows) == 10 and len(query_rows) == 20, 'balanced_window_count')
            require(len({tuple(row[:3]) for row in query_rows}) == 20,
                    'balanced_query_membership')
            checked['distinct_target_windows'] += len(windows)
            checked['opaque_instances'] += 1
            panel.append([rank, observation_rank, initial, list(action_map),
                          list(observation_map), query_rows])

            # Exhaust every possible two-action suffix from either register.
            # A previous cue + current neutral uniquely identifies its setter.
            for start in (0, 1):
                for first_role, second_role in itertools.product(range(5), repeat=2):
                    middle, previous_role = role_transition(start, first_role)
                    final_register, current_role = role_transition(middle, second_role)
                    vector = (previous_role == 0, previous_role == 1)
                    checked['two_step_isolation_cases'] += 1
                    if current_role == 2 and vector in ((True, False), (False, True)):
                        require(second_role == 2 and first_role in (0, 1),
                                'cue_isolation_requires_setter_then_mask')
                        require(final_register == (0 if vector[0] else 1),
                                'cue_isolation_register')
                        checked['cue_isolated_neutral_cases'] += 1
            for probe in (0, 1):
                histories = []
                outputs = []
                words = []
                for b in (0, 1):
                    prefix = (action_map[b],) + (action_map[2],) * 3
                    histories.append(typed_window(trace(world, prefix), 2))
                    outputs.append(world.step(action_map[3 + probe])[0])
                    words.append(list(prefix) + [action_map[3+probe]])
                require(histories[0] == histories[1] and outputs[0] != outputs[1],
                        'inherent_order2_aliasing')
                require(all(len(w) == 5 for w in words), 'aliasing_word_length')
                checked['inherently_ambiguous_probe_pairs'] += 1
                if rank == 0 and initial == 0 and probe == 0:
                    representatives['inherent_order2_aliasing'] = {
                        'opaque_probe_words': words,
                        'identical_before_window': histories[0],
                        'different_opaque_observations': outputs,
                        'scope': 'No expression of this complete W2 window separates this pair.',
                    }
            if rank == 0 and initial == 0:
                representatives['typed_reset_boundary_window'] = missing
                representatives['order1_short_support'] = {
                    'opaque_probe_word': [action_map[1], action_map[2], action_map[4]],
                    'before_window': typed_window(trace(world, (action_map[1], action_map[2])), 1),
                    'length': 3,
                }
                representatives['cue_predicate_representability'] = {
                    'predicates': [
                        {'operator': 'EQUAL', 'term': ['observation', 0, 1],
                         'constant_type': 'observation', 'opaque_constant': observation_map[b],
                         'boolean_leaf_size': 1} for b in (0, 1)],
                    'slot_count': 2, 'available_slot_bound': 4,
                    'grammar_size_bound': 3,
                    'eligibility': 'Conditional on those cue tokens having been encountered.',
                    'supplied_to_a_learner': False,
                    'selected_by_a_learner': False,
                    'claim': 'Representability and target-cell isolation only; no greedy-selection or count-support claim.',
                }

    require(checked == {
        'opaque_instances': 240, 'planned_decisions': 4800,
        'distinct_target_windows': 2400, 'order1_support_cells': 960,
        'order2_support_cells': 4800, 'unique_goal_action_witnesses': 4800,
        'inherently_ambiguous_probe_pairs': 480,
        'two_step_isolation_cases': 12000, 'cue_isolated_neutral_cases': 960,
    }, 'structural_count_totals')
    warmup_cost = 5 * (1 + 1)
    cost2 = 5**2 * (1 + 2 + 2)
    cost3 = 5**3 * (1 + 3 + 2)
    cost4 = 5**4 * (1 + 4 + 2)
    require(warmup_cost + cost2 + cost3 == 885, 'coverage_through_three_identity')
    require(warmup_cost + cost2 + cost3 + cost4 == 5260,
            'coverage_through_four_identity')
    require(warmup_cost + cost2 + 25 * (1 + 3 + 2) == 285,
            'early_coverage_prefix_identity')
    # Direct formula at zero counts; no predictor is fitted or called.
    unseen_distribution = [Fraction(0 + 1, 0 + 5) for _ in range(5)]
    require(sum(unseen_distribution) == 1
            and all(value == Fraction(1, 5) for value in unseen_distribution),
            'unseen_key_uniformity_identity')
    all_actions_goal_probability = [Fraction(1, 5)] * 5
    require(len(set(all_actions_goal_probability)) == 1,
            'all_action_keys_unseen_tie_identity')
    # Positive pure-cell sufficiency is an exact inequality, not a learned score.
    require(Fraction(2, 6) > Fraction(1, 5) > Fraction(1, 6),
            'one_observation_support_inequality')
    return {
        'structural_counts': checked,
        'expanded_panel': {
            'scope': 'Fixed finite planned input panel, not candidate outcomes or independent world laws.',
            'instance_row_fields': ['action_permutation_rank', 'observation_permutation_rank',
                'initial_register', 'action_role_to_opaque', 'observation_role_to_opaque', 'queries'],
            'query_row_fields': ['final_setter_value', 'preparation_endpoint_role_index',
                'goal_role_index', 'nine_opaque_history_actions', 'opaque_goal_token'],
            'role_index_orders': {'actions': ACTION_ROLES, 'observations': OBSERVATION_ROLES},
            'rows': panel,
            'rows_sha256': sha(canonical(panel)),
            'digest_serialization': 'UTF-8 JSON; sorted object keys; compact separators; no newline.',
            'contains_candidate_choices_or_scores': False,
            'action_observation_orders_fully_crossed': False,
            'marginal_action_permutations': 120,
            'marginal_observation_permutations': 120,
        },
        'representative_witnesses': representatives,
        'coverage_cost_identities': {
            'scope': 'Algebraic completed-word costs only; no acquisition scheduler executed.',
            'warmup_calls': warmup_cost,
            'all_length_two_calls': cost2,
            'all_length_three_calls': cost3,
            'all_length_four_calls': cost4,
            'through_length_three_calls': 885,
            'through_length_four_calls': 5260,
            'declared_early_prefix': {'warmup_words': 5, 'length_two_words': 25,
                                    'length_three_words': 25, 'calls': 285},
            'each_planned_evaluation_decision_calls': 11,
            'support_bounds_are_sufficient_not_necessary': True,
            'presumes_complete_work_and_sufficient_other_resources': True,
        },
        'unseen_key_identity': {
            'formula': '(0+1)/(0+5)',
            'distribution': [fraction(v) for v in unseen_distribution],
            'all_five_action_keys_unseen_means_goal_probability_tie': True,
            'tie_action_opaque_index_by_declared_rule': 0,
            'one_unseen_action_key_does_not_make_other_action_keys_uniform': True,
            'candidate_predictor_constructed_or_fit': False,
        },
        'structural_transducer_calls': {
            **counters,
            'scope': 'Checker truth-table and witness validation work, not acquisition or evaluation experiment usage.',
        },
    }


def verify(root: Path, packet: Path) -> dict:
    """Return complete public evidence; never open packet or write any output."""
    del packet  # Private packet integrity belongs to the caller's sealed wrapper.
    result = {'kind': KIND, 'integrity_verified': False, 'boundaries': dict(BOUNDARIES)}
    try:
        root = Path(root)
        sources = []
        config = None
        for name, expected in SOURCE_PINS.items():
            raw = read_public(root, name)
            require(sha(raw) == expected, 'source_hash_mismatch')
            sources.append({'path': name, 'sha256': expected, 'bytes': len(raw)})
            if name == CONFIG_PATH:
                config = json.loads(raw)
        code = read_public(root, CODE_PATH)
        require(sha(Path(__file__).read_bytes()) == sha(code), 'executing_checker_differs_from_root')
        require(type(config) is dict, 'configuration_object_required')
        structural = static_checks(config)
        result.update(structural)
        result.update({
            'integrity_verified': True,
            'status': 'STRUCTURAL_CHECKS_PASSED_NOT_SCIENTIFIC_VERDICT',
            'source_inputs': sources,
            'checker': {'path': CODE_PATH, 'sha256': sha(code), 'bytes': len(code),
                        'trust_anchor': 'External checkpoint release manifest pins these executable bytes.'},
            'private_packet_scope': 'Not read here; verified by the caller before and after this checker.',
            'limitations': [
                'A finite transducer and predetermined input panel were checked; no mechanism was implemented or run.',
                'No fitted count reader, selected predicate, acquisition schedule, target candidate outcome or compute profile exists here.',
                'Representability witnesses are evaluator proofs; they are never supplied to a learner and do not guarantee selection or support.',
                'Long whole histories are absent by length, but their target windows have short-word support; substantive recombination and retention are not tested.',
                'Operation and memory budgets remain unmeasured; no grid, independent verdict or future experiment admission follows.',
                'Self-reported source hashes require the separately trusted release wrapper; this checker does not attest operating-system isolation.',
            ],
        })
    except DesignCheckError as error:
        result.update(status='STRUCTURAL_CHECK_STOPPED', failure_class=str(error))
    except (OSError, UnicodeError, json.JSONDecodeError):
        result.update(status='STRUCTURAL_CHECK_STOPPED', failure_class='source_io_or_parse_failure')
    except (KeyError, TypeError, ValueError):
        result.update(status='STRUCTURAL_CHECK_STOPPED', failure_class='configuration_shape_failure')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--packet', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.root, args.packet)
    sys.stdout.buffer.write(canonical(result) + b'\n')
    return 0 if result['integrity_verified'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
