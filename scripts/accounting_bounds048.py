#!/usr/bin/env python3
"""Finite static call-graph arithmetic; imports/executes no scientific adapter.

This is NOT a schema bound, complete accounting ruler, profile, or admission.
The reference enumerates all feasible counts of distinct completed words by
length. The algebra instead fills shortest word lengths. Both overapproximate
the scheduler's attainable word order; neither predicts a target trajectory.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Domain:
    actions: int = 5
    max_word: int = 5
    validation: int = 2
    environment: int = 285
    cadence: int = 4
    predicates: int = 4

    def __post_init__(self):
        values = asdict(self)
        if any(type(v) is not int for v in values.values()):
            raise ValueError("integer domain required")
        if min(self.actions, self.max_word, self.validation) < 1:
            raise ValueError("positive action, word and validation bounds required")
        if self.environment < 0 or self.cadence < 2 or self.predicates < 0:
            raise ValueError("invalid environment, cadence or predicate bound")


def _finish(domain, completed, records, event_bearing, validation_events,
            reference_states=None):
    a, length = domain.actions, domain.max_word
    warmup_complete_possible = domain.environment >= 2 * a
    # A record is appended before the warm-up's whole-word call reservation.
    warmup_records = min(a, domain.environment // 2 + 1)
    selection_attempts = completed + 1 if warmup_complete_possible else 0
    recipes = a + event_bearing if warmup_complete_possible else warmup_records
    vocabulary = sum(a ** size for size in range(1, length + 1))
    macros = min(vocabulary, a + domain.predicates * length * (length - 1) // 2)
    assemblies = selection_attempts - selection_attempts // domain.cadence
    result = {
        "completed_scored_trials": completed,
        "scored_trial_records": records,
        "total_trial_records": max(warmup_records, a + records if warmup_complete_possible else 0),
        "event_bearing_scored_boundaries": event_bearing,
        "replay_boundary_table_partition_copies": 2 * event_bearing,
        "decomposition_reader_attempts": 3 * event_bearing,
        "completed_validation_events": validation_events,
        "decomposition_validation_forecasts": 3 * validation_events,
        "acquisition_snapshot_attempts": 2 * event_bearing,
        "scheduler_selection_attempts": selection_attempts,
        "mutation_assemblies_noncoverage_arms": assemblies,
        "mutation_assemblies_coverage_arm": 0,
        "recipe_records": recipes,
        "macro_records": macros,
        "raw_mutations_per_assembly": recipes * (
            (length + 1) * macros + length + length * macros + max(0, length - 1)),
        "raw_insertion_word_tokens": 2 * length,
        "nonempty_word_vocabulary": vocabulary,
    }
    if reference_states is not None:
        result["reference_count_vectors"] = reference_states
    return result


def algebraic_bounds(domain=Domain()):
    """Greedy shortest-word lower costs, followed by terminal-stage arithmetic."""
    a, limit, v = domain.actions, domain.max_word, domain.validation
    remaining = domain.environment - 2 * a
    if remaining < 0:
        return _finish(domain, 0, 0, 0, 0)
    capacities = [(size, a ** size) for size in range(2, limit + 1)]
    word_count = sum(capacity for _, capacity in capacities)

    def minimum_full_cost(count):
        total = 0
        for size, capacity in capacities:
            take = min(count, capacity)
            total += take * (1 + size + v)
            count -= take
        if count:
            raise ValueError("count exceeds remaining distinct vocabulary")
        return total

    def maximum_count(discount):
        # A final word can omit its V validation calls, but the whole trial's
        # RESET+word allowance must fit before even its first call is issued.
        lo, hi = 0, word_count
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if minimum_full_cost(mid) - discount <= remaining:
                lo = mid
            else:
                hi = mid - 1
        return lo

    completed = maximum_count(0)
    events = maximum_count(v)
    records = min(word_count, completed + 1)
    validation_events = completed * v
    if events:
        prefix = v * (events - 1)
        last = min(v, remaining - (minimum_full_cost(events) - v))
        validation_events = max(validation_events, prefix + last)
    return _finish(domain, completed, records, events, validation_events)


def reference_bounds(domain=Domain()):
    """Slow independent finite count-vector enumeration of reservation stages.

    Complete warm-up consumes two calls per action. For each distinct word
    length, enumerate how many scored words completed RESET, the word, and all
    V validation calls. Then enumerate every possible next unused word length:
    its record can exist before reservation; events require RESET+word capacity;
    completed validation is limited by the remaining calls. Global refusals can
    only truncate these stages. No N1, N3, world or scientific outcomes are used.
    """
    a, v = domain.actions, domain.validation
    remaining = domain.environment - 2 * a
    if remaining < 0:
        return _finish(domain, 0, 0, 0, 0, 0)
    sizes = tuple(range(2, domain.max_word + 1))
    capacities = tuple(a ** size for size in sizes)
    counts = [0] * len(sizes)
    best_completed = best_records = best_events = best_validation = states = 0

    def visit(index, spent, completed):
        nonlocal best_completed, best_records, best_events, best_validation, states
        if index < len(sizes):
            price = 1 + sizes[index] + v
            for count in range(min(capacities[index], (remaining - spent) // price) + 1):
                counts[index] = count
                visit(index + 1, spent + price * count, completed + count)
            return
        states += 1
        best_completed = max(best_completed, completed)
        best_records = max(best_records, completed)
        best_events = max(best_events, completed)
        best_validation = max(best_validation, v * completed)
        for size, used, capacity in zip(sizes, counts, capacities):
            if used == capacity:
                continue
            best_records = max(best_records, completed + 1)
            available = remaining - spent
            if available >= 1 + size:
                best_events = max(best_events, completed + 1)
                best_validation = max(best_validation,
                    v * completed + min(v, available - (1 + size)))

    visit(0, 0, 0)
    return _finish(domain, best_completed, best_records, best_events, best_validation, states)


def transition_table_bound(domain=Domain()):
    """Conservative retained-transition bound, including terminal partial work.

    After warm-up, each event-bearing trial costs one RESET and contributes at
    most L+V primitive responses. Maximizing min((L+V)*b, remaining-b) over
    integer b only requires the two integers adjacent to its linear crossing.
    The bound ignores word uniqueness and scheduler attainability. Source and
    replay boundary tables each obey it; it does not count their many copies.
    """
    a, remaining = domain.actions, domain.environment - 2 * domain.actions
    if remaining < 0:
        return min(a, domain.environment // 2)
    primitives_per_trial = domain.max_word + domain.validation
    below = remaining // (primitives_per_trial + 1)
    candidates = (below, min(remaining, below + 1))
    return a + max(min(primitives_per_trial * b, remaining - b) for b in candidates)


def reference_transition_table_bound(domain=Domain()):
    """Independent finite enumeration of every possible later RESET count."""
    if domain.environment < 2 * domain.actions:
        # Every warm-up primitive follows its own paid RESET.
        return min(domain.actions, domain.environment // 2)
    remaining = domain.environment - 2 * domain.actions
    best = 0
    for resets in range(remaining + 1):
        primitive_slots = (domain.max_word + domain.validation) * resets
        calls_left_after_resets = remaining - resets
        best = max(best, min(primitive_slots, calls_left_after_resets))
    return domain.actions + best


def reduced_credit_caps(transitions=245, outcome_tokens=5, validation=2):
    """Reduced-result caps only, never blanket temporary-operand widths.

    A Brier denominator divides D^2. A sum of V differences of two Brier
    scores has a common denominator no greater than D^(4V); division by V
    adds that factor. Each score is in [0,2], so mean differences are [-2,2].
    """
    if any(type(x) is not int for x in (transitions, outcome_tokens, validation)):
        raise ValueError("integer bounds required")
    if transitions < 0 or outcome_tokens < 1 or validation < 1:
        raise ValueError("invalid credit bounds")
    d = transitions + outcome_tokens
    denominator = validation * d ** (4 * validation)
    return {"forecast_denominator": d, "reduced_credit_denominator": denominator,
            "reduced_credit_absolute_numerator": 2 * denominator,
            "denominator_bits": denominator.bit_length(),
            "absolute_numerator_bits": (2 * denominator).bit_length()}


def unreduced_rational_caps(operation, left, right):
    """Input-derived caps (|numerator|, positive denominator), before reduction.

    This bounds mathematical cross products; it does not price library gcd,
    equality, serialization, or every interpreter temporary. Those remain
    pending parts of the corrected ruler. Division excludes a zero divisor.
    """
    an, ad = left
    bn, bd = right
    if any(type(x) is not int or x < 0 for x in (an, ad, bn, bd)) or not ad or not bd:
        raise ValueError("nonnegative numerator and positive denominator caps required")
    if operation in ("add", "sub"):
        return an * bd + bn * ad, ad * bd
    if operation == "mul":
        return an * bn, ad * bd
    if operation == "div" and bn:
        return an * bd, ad * bn
    raise ValueError("supported operation and nonzero divisor cap required")


FROZEN_CASE_MATRIX = {
    "small_domain_actions": [1, 2, 3],
    "small_domain_max_word": [1, 2, 3, 4],
    "small_domain_validation": [1, 2, 3],
    "small_domain_environment_expression": "sorted(set([0,1,2*A-1,2*A,2*A+1,10,20,40]))",
    "actual_domain": asdict(Domain()),
    "terminal_controls": "A2,L2,V2 at B4..9; A1,L2,V1 at B6",
    "transition_bounds": "closed linear crossing vs every integer later RESET count, on all small domains and actual042",
    "rational_grid": "a,c in [-3,3], b,d in [1,4]; add/sub/mul and nonzero div",
    "execution_scope": "static finite arithmetic only; no scientific adapter imports",
}
