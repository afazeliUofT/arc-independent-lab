#!/usr/bin/env python3
"""Outcome-blind development reference for frozen035 N1 and fixed-order readers.

No environment, target panel, network, model, or experiment entry point exists here.
EQ=0, NOT=1, AND=2, OR=3.  A term is (0,type,field,lag), a
constant (1,type,token); observation type=0, action type=1.  Tree size
counts Boolean nodes, so an entire typed equality is one leaf.  Literal
ordered trees are retained even when their truth values coincide.
"""
from __future__ import annotations

import copy
import hashlib
import itertools
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from accounting043 import Limit, Meter, rational_operation

MISSING = -1


@dataclass(frozen=True)
class History:
    observations: tuple[tuple[int, ...], ...]
    actions: tuple[int, ...] = ()

    def __post_init__(self):
        if not self.observations or len(self.observations) != len(self.actions) + 1:
            raise ValueError("history must have one more observation than actions")

    @classmethod
    def initial(cls, observation):
        return cls((tuple(observation),), ())

    def advance(self, action, observation):
        return History(self.observations + (tuple(observation),), self.actions + (action,))

    @property
    def current(self):
        return self.observations[-1]

    def state(self):
        return {"observations": self.observations, "actions": self.actions}


@dataclass(frozen=True)
class Transition:
    history: History
    action: int
    outcome: tuple[int, ...]
    index: int

    def state(self):
        return {"history": self.history.state(), "action": self.action,
                "outcome": self.outcome, "index": self.index}


def tree_size(expression):
    if expression[0] == 0:
        return 1
    return 1 + sum(tree_size(child) for child in expression[1:])


def tree_tokens(expression):
    """Numeric prefix serialization; all constructor arities are fixed."""
    if expression[0] == 0:
        return (0,) + expression[1] + expression[2]
    return (expression[0],) + tuple(x for c in expression[1:] for x in tree_tokens(c))


def _term(history, operand):
    if operand[0] == 1:
        return operand[2]
    _, typ, field, lag = operand
    if typ == 0:
        return history.observations[-1-lag][field] if lag < len(history.observations) else MISSING
    return history.actions[-lag] if lag <= len(history.actions) else MISSING


def evaluate(expression, history, meter=None):
    """Simple literal evaluator, also the independent bitset conformance oracle."""
    if meter:
        meter.charge("n1.expression_node")
    op = expression[0]
    if op == 0:
        if meter:
            meter.charge("n1.term_access", 2)
            meter.charge("n1.token_equality", bits=max(1, max(abs(_term(history, x)).bit_length() for x in expression[1:])))
        return _term(history, expression[1]) == _term(history, expression[2])
    if op == 1:
        return not evaluate(expression[1], history, meter)
    left = evaluate(expression[1], history, meter)
    right = evaluate(expression[2], history, meter)  # no short-circuit accounting
    return (left and right) if op == 2 else (left or right)


def _plain(value):
    if isinstance(value, History):
        return value.state()
    if isinstance(value, Transition):
        return value.state()
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if isinstance(value, tuple):
        return [_plain(x) for x in value]
    if isinstance(value, list):
        return [_plain(x) for x in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    return value


class N1:
    """Versioned exact greedy historical-predicate learner on supplied traces.

    Computation stops are explicit.  append's ``appended`` field distinguishes a
    retained completed transition from one whose initial reservation failed.
    A memory stop retains a conservative reservation until close/resume; the
    complete-state logical-byte report is only exact after a successful seal.
    """
    _next_owner = itertools.count()

    def __init__(self, W=2, S=3, K=4, observation_alphabets=((0, 1, 2, 3, 4),),
                 actions=(0, 1, 2, 3, 4), meter=None, owner=None):
        if W < 0 or S < 1 or K < 0 or not observation_alphabets or not actions:
            raise ValueError("invalid N1 bounds/interface")
        self.W, self.S, self.K = W, S, K
        self.observation_alphabets = tuple(tuple(x) for x in observation_alphabets)
        self.actions = tuple(actions)
        if any(not a or any(type(x) is not int or x < 0 for x in a) or len(set(a)) != len(a)
               for a in self.observation_alphabets) or len(set(self.actions)) != len(self.actions) or any(type(x) is not int or x < 0 for x in self.actions):
            raise ValueError("nonnegative unique token indices required")
        self.meter = meter or Meter()
        self.owner = owner or "n1-" + str(next(self._next_owner))
        self.T: list[Transition] = []
        self.Phi: list[tuple] = []
        self.observed = [set(), set()]
        self.inventory: list[tuple] = []
        self.inventory_tag = None
        self.truth: dict[tuple, int] = {}
        self.truth_version = -1
        self.table_version = 0
        self.phi_version = 0
        self.counts_version = (0, 0)
        self.counts: dict[tuple, dict[tuple, int]] = {}
        self.groups: list[dict] = []
        self.groups_version = None
        self.cursor = None
        self.search_status = "COMPLETE"
        self.construction_log = []
        self.search_log = []
        self.prediction_log = []
        self.archives = []
        self.block = 0
        self._bytes = 0
        self._last_sealed_bytes = None
        self._reservation_is_exact = False
        self._seal()

    @property
    def counts_ready(self):
        return self.counts_version == (self.table_version, self.phi_version)

    def _versions(self):
        return (self.table_version, self.phi_version, tuple(sorted(self.observed[0])), tuple(sorted(self.observed[1])))

    def _reserve(self, extra):
        self.meter.reserve(self.owner, self._bytes + max(0, extra))
        self._bytes += max(0, extra)
        self._reservation_is_exact = False

    def _seal(self):
        data = self.state()
        self._bytes = self.meter.retain(self.owner, data)
        self._last_sealed_bytes = self._bytes
        self._reservation_is_exact = True

    def logical_bytes(self):
        return self._bytes

    def retained_memory_report(self):
        return {"owner_reserved_bytes": self.meter.owners.get(self.owner, 0),
                "last_successfully_sealed_payload_bytes": self._last_sealed_bytes,
                "reservation_is_exact_payload_size": self._reservation_is_exact,
                "scope": "Canonical logical payload/reservation; not Python RSS or arena sharing"}

    def close(self):
        self.meter.release(self.owner)

    def _validate_observation(self, observation):
        obs = tuple(observation)
        if len(obs) != len(self.observation_alphabets):
            raise ValueError("observation width differs from declared interface")
        for value, alphabet in zip(obs, self.observation_alphabets):
            self.meter.charge("n1.validate_token", len(alphabet))
            if type(value) is not int or value not in alphabet:
                raise ValueError("observation outside declared alphabet")
        return obs

    def observe_observation(self, observation):
        obs = self._validate_observation(observation)
        self._reserve(128 + len(obs) * 32)
        for token in obs:
            self.meter.charge("n1.constant_encounter")
            self.observed[0].add(token)
        self._seal()

    observe_reset = observe_observation

    def observe_action(self, action):
        self.meter.charge("n1.validate_action", len(self.actions))
        if type(action) is not int or action not in self.actions:
            raise ValueError("action outside declared alphabet")
        self._reserve(160)
        self.meter.charge("n1.constant_encounter")
        self.observed[1].add(action)
        self._seal()

    def _discard_cursor(self, why):
        if self.cursor is not None:
            self.meter.charge("n1.cursor_archive")
            self.search_log.append({"event": "DISCARDED_CURSOR", "reason": why,
                                    "cursor": copy.deepcopy(self.cursor)})
            self.cursor = None

    def append(self, history, action, outcome, search=True):
        start = len(self.Phi)
        appended = False
        try:
            if not isinstance(history, History):
                raise TypeError("History required")
            obs = self._validate_observation(outcome)
            if action not in self.actions:
                raise ValueError("action outside declared alphabet")
            # These are encounters in this completed record, never future batch tokens.
            for hobs in history.observations:
                self._validate_observation(hobs)
            if any(a not in self.actions for a in history.actions):
                raise ValueError("history action outside declared alphabet")
            record = Transition(history, action, obs, len(self.T))
            size = len(self.meter.encode(record.state()))
            self._reserve(size + 2048)
            # Precharge one indivisible append/encounter commit, so a refused charge
            # cannot leave a retained transition with only half its constants recorded.
            encounter_count = sum(map(len, history.observations)) + len(history.actions) + 1 + len(obs)
            self.meter.charge("n1.append_record", 8)
            self.meter.charge("n1.constant_encounter", encounter_count)
            self.meter.charge("n1.cursor_archive", int(self.cursor is not None))
            self.T.append(record)
            self.table_version += 1
            appended = True
            if self.cursor is not None:
                self.search_log.append({"event": "DISCARDED_CURSOR", "reason": "transition_table_changed", "cursor": copy.deepcopy(self.cursor)})
                self.cursor = None
            for hobs in history.observations:
                self.observed[0].update(hobs)
            self.observed[1].update(history.actions + (action,))
            self.observed[0].update(obs)
            self.truth.clear()
            self.truth_version = self.table_version
            self.groups_version = None
            self.rebuild_counts()
            if search:
                self._search()
            else:
                self.search_status = "FEATURE_SEARCH_NOT_REQUESTED"
            self._seal()
        except Limit as error:
            self.search_status = getattr(error, "status", str(error))
        return {"status": self.search_status, "appended": appended,
                "new_predicates": self.Phi[start:], "counts_ready": self.counts_ready}

    def _key(self, history, action):
        self.meter.charge("n1.key_construction", 3 + len(self.Phi))
        return (history.current, tuple(evaluate(p, history, self.meter) for p in self.Phi), action)

    def rebuild_counts(self):
        """Atomic replacement: dirty old tables never support a prediction."""
        self._reserve(1024 + len(self.T) * (128 + 40 * len(self.Phi) + 32 * len(self.observation_alphabets)))
        fresh = {}
        for record in self.T:
            self.meter.charge("n1.count_scan")
            key = self._key(record.history, record.action)
            self.meter.charge("n1.count_dict", 3)
            cell = fresh.setdefault(key, {})
            n = cell.get(record.outcome, 0)
            self.meter.charge("n1.count_increment", bits=max(1, n.bit_length()))
            cell[record.outcome] = n + 1
        self.meter.charge("n1.count_commit", 2)
        self.counts = fresh
        self.counts_version = (self.table_version, self.phi_version)

    def _ensure_inventory(self):
        tag = (tuple(sorted(self.observed[0])), tuple(sorted(self.observed[1])))
        if self.inventory_tag == tag:
            self.meter.charge("n1.inventory_tag_compare", sum(map(len, tag)) + 1)
            return
        terms = [[(0, 0, field, lag) for field in range(len(self.observation_alphabets)) for lag in range(self.W + 1)],
                 [(0, 1, 0, lag) for lag in range(1, self.W + 1)]]
        nleaves = sum(len(terms[t]) * (len(terms[t]) + len(tag[t])) for t in (0, 1))
        numbers = {1: nleaves}
        for size in range(2, self.S + 1):
            self.meter.charge("n1.grammar_cardinality", size, bits=max(1, nleaves.bit_length()))
            numbers[size] = numbers[size - 1] + 2 * sum(numbers[a] * numbers[size-1-a] for a in range(1, size-1))
        # Upper bound for literal JSON tree storage; token width included.
        width = max([len(str(x)) for t in tag for x in t] + [len(str(self.W)), len(str(len(self.observation_alphabets))), 1])
        self._reserve(sum(numbers.values()) * (64 + 32 * self.S * width))
        by_size = {1: []}
        for typ in (0, 1):
            for left in terms[typ]:
                for right in terms[typ] + [(1, typ, token) for token in tag[typ]]:
                    self.meter.charge("n1.grammar_leaf", 12)
                    by_size[1].append((0, left, right))
        for size in range(2, self.S + 1):
            level = []
            for child in by_size[size-1]:
                self.meter.charge("n1.grammar_unary", 3)
                level.append((1, child))
            for op in (2, 3):
                for leftsize in range(1, size-1):
                    for left in by_size[leftsize]:
                        for right in by_size[size-1-leftsize]:
                            self.meter.charge("n1.grammar_binary", 4)
                            level.append((op, left, right))
            by_size[size] = level
        inventory = []
        for size, level in by_size.items():
            for expr in level:
                self.meter.charge("n1.grammar_sort_key", len(tree_tokens(expr)))
            # Stable, declared comparison upper charging; literal trees are unique by construction.
            self.meter.charge("n1.grammar_sort", max(1, len(level)) * max(1, len(level).bit_length()), bits=max(1, size))
            inventory.extend(sorted(level, key=tree_tokens))
        self.meter.charge("n1.inventory_commit")
        self.inventory, self.inventory_tag = inventory, tag
        self.truth.clear()
        self.truth_version = self.table_version
        self._discard_cursor("constant_inventory_changed")

    def _signature(self, expression):
        self.meter.charge("n1.truth_cache_lookup")
        if expression in self.truth:
            return self.truth[expression]
        n = len(self.T)
        if expression[0] == 0:
            result = 0
            for i, record in enumerate(self.T):
                self.meter.charge("n1.truth_record_access")
                if evaluate(expression, record.history, self.meter):
                    self.meter.charge("n1.truth_bitset_set", bits=max(1, n))
                    result |= 1 << i
        else:
            left = self._signature(expression[1])
            if expression[0] == 1:
                self.meter.charge("n1.truth_not", 3, bits=max(1, n))
                result = ((1 << n) - 1) ^ left
            else:
                right = self._signature(expression[2])
                self.meter.charge("n1.truth_boolean", bits=max(1, n))
                result = left & right if expression[0] == 2 else left | right
        self.meter.charge("n1.truth_cache_store")
        self.truth[expression] = result
        return result

    def _ensure_groups(self):
        version = (self.table_version, self.phi_version)
        if self.groups_version == version:
            return
        self._reserve(1024 + len(self.T) * 192)
        groups = {}
        for i, record in enumerate(self.T):
            self.meter.charge("n1.conflict_group_scan")
            key = self._key(record.history, record.action)
            self.meter.charge("n1.conflict_group_dict", 4)
            group = groups.setdefault(key, {})
            self.meter.charge("n1.conflict_group_bitset", 2, bits=max(1, len(self.T)))
            group[record.outcome] = group.get(record.outcome, 0) | (1 << i)
        selected = []
        for key, outcomes in groups.items():
            self.meter.charge("n1.conflict_group_test")
            if len(outcomes) > 1:
                self.meter.charge("n1.conflict_group_store", len(outcomes))
                selected.append({"key": key, "outcomes": tuple(sorted(outcomes.items()))})
        self.groups = selected
        self.groups_version = version

    def _gain(self, signature):
        gain = 0
        width = max(1, len(self.T))
        for group in self.groups:
            true_total = false_total = same = 0
            for outcome, mask in group["outcomes"]:
                self.meter.charge("n1.gain_bitset", 3, bits=width)
                yes = (mask & signature).bit_count()
                no = mask.bit_count() - yes
                bw = max(1, yes.bit_length(), no.bit_length(), true_total.bit_length(), false_total.bit_length())
                self.meter.charge("n1.gain_integer_add", 3, bits=bw)
                self.meter.charge("n1.gain_integer_multiply", bits=bw*bw)
                true_total += yes
                false_total += no
                same += yes * no
            bw = max(1, true_total.bit_length(), false_total.bit_length(), same.bit_length())
            self.meter.charge("n1.gain_integer_multiply", bits=bw*bw)
            self.meter.charge("n1.gain_integer_add", 2, bits=2*bw)
            gain += true_total * false_total - same
        return gain

    def _search(self):
        self._ensure_inventory()
        # Reserve every potential truth entry before any are materialized.
        self._reserve(len(self.inventory) * (80 + 32*self.S + (len(self.T) + 2)//3) + 2048)
        while True:
            self.meter.charge("n1.search_loop")
            self._ensure_groups()
            if not self.groups:
                self.cursor = None
                self.search_status = "COMPLETE"
                return
            if len(self.Phi) >= self.K:
                self.cursor = None
                self.search_status = "FEATURE_LIMITED"
                return
            if self.cursor is None or tuple(self.cursor["versions"]) != self._versions():
                self._discard_cursor("version_mismatch")
                self.cursor = {"versions": self._versions(), "next": 0, "best_gain": 0,
                               "best_index": None, "completed_candidates": 0}
            while self.cursor["next"] < len(self.inventory):
                i = self.cursor["next"]
                self.meter.charge("n1.candidate_access_and_selected_test", 1 + len(self.Phi))
                expr = self.inventory[i]
                if expr not in self.Phi:
                    gain = self._gain(self._signature(expr))
                    self.meter.charge("n1.candidate_gain_compare", bits=max(1, gain.bit_length()))
                    # Inventory order already supplies size and serialization ties.
                    if gain > self.cursor["best_gain"]:
                        self.cursor["best_gain"], self.cursor["best_index"] = gain, i
                self.meter.charge("n1.cursor_advance", 2)
                self.cursor["next"] += 1
                self.cursor["completed_candidates"] += 1
            selected = self.cursor["best_index"]
            if selected is None:
                self.search_status = "GRAMMAR_LIMITED"
                self.search_log.append({"event": "COMPLETE_NO_POSITIVE_GAIN", "versions": self._versions(),
                                        "candidate_count": len(self.inventory) - len(self.Phi)})
                self.cursor = None
                self.rebuild_counts()
                return
            predicate = self.inventory[selected]
            log = {"event": "SELECTED", "predicate": predicate, "gain": self.cursor["best_gain"],
                   "table_version": self.table_version, "old_phi_version": self.phi_version,
                   "candidate_pass_complete": True, "conflicting_groups": copy.deepcopy(self.groups)}
            self.meter.charge("n1.selection_commit", 5)
            self.Phi.append(predicate)
            self.phi_version += 1
            self.construction_log.append(log)
            self.cursor = None
            self.groups_version = None
            self.rebuild_counts()

    def resume(self):
        start = len(self.Phi)
        try:
            if not self.counts_ready:
                self.rebuild_counts()
            self._search()
            self._seal()
        except Limit as error:
            self.search_status = getattr(error, "status", str(error))
        return {"status": self.search_status, "new_predicates": self.Phi[start:], "counts_ready": self.counts_ready}

    def predict(self, history, action, log=True):
        if not self.counts_ready:
            return {"status": "COMPUTATION_INCOMPLETE", "features": None, "counts": None, "probabilities": None}
        try:
            key = self._key(history, action)
            self.meter.charge("n1.predict_lookup")
            cell = self.counts.get(key, {})
            n = 0
            for count in cell.values():
                self.meter.charge("n1.predict_count_sum", bits=max(1, count.bit_length(), n.bit_length()))
                n += count
            dimension = 1
            for alphabet in self.observation_alphabets:
                self.meter.charge("n1.outcome_cardinality", bits=max(1, dimension.bit_length())**2)
                dimension *= len(alphabet)
            probabilities = {}
            for outcome in itertools.product(*self.observation_alphabets):
                self.meter.charge("n1.prediction_fraction", 6, bits=max(1, (n + dimension).bit_length())**2)
                probabilities[outcome] = rational_operation(self.meter, "div", cell.get(outcome, 0) + 1, n + dimension)
            status = "UNSEEN_KEY" if not cell else "OBSERVED_SINGLE_OUTCOME" if len(cell) == 1 else "OBSERVED_CONFLICT"
            result = {"status": status, "features": key[1], "counts": dict(cell), "probabilities": probabilities,
                      "n": n, "outcome_space_size": dimension}
            if log:
                item = {"history": history.state(), "action": action, "table_version": self.table_version,
                        "phi_version": self.phi_version, "status": status, "counts": [[y, c] for y, c in sorted(cell.items())]}
                self._reserve(len(self.meter.encode(item)) + 128)
                self.meter.charge("n1.prediction_log_append")
                self.prediction_log.append(item)
            return result
        except Limit:
            return {"status": "COMPUTATION_INCOMPLETE", "features": None, "counts": None, "probabilities": None}

    def snapshot(self, meter=None):
        if not self.counts_ready:
            raise Limit("COMPUTATION_INCOMPLETE")
        target_meter = meter or self.meter
        state_bytes = len(target_meter.encode(self.state()))
        owner = "n1-snapshot-" + str(next(self._next_owner))
        cleanup = target_meter.prepay_release(owner)
        try:
            target_meter.reserve(owner, state_bytes)
            target_meter.charge("n1.snapshot_copy_bytes", state_bytes)
            memo = {id(self.meter): target_meter}
            duplicate = copy.deepcopy(self, memo)
            duplicate.meter, duplicate.owner = target_meter, owner
            duplicate._bytes, duplicate._reservation_is_exact = state_bytes, True
            duplicate._last_sealed_bytes = state_bytes
        except BaseException:
            target_meter.release_prepaid(cleanup)
            raise
        target_meter.discard_prepaid_release(cleanup)
        return duplicate

    def new_block(self, block):
        if block == self.block:
            raise ValueError("new block identifier required")
        archive_view = self.state()
        archive_view.pop("archives")
        archive_bytes = len(self.meter.encode(archive_view))
        self._reserve(archive_bytes + 256)
        self.meter.charge("n1.archive_copy_bytes", archive_bytes)
        archived = copy.deepcopy(archive_view)
        self.meter.charge("n1.archive_block", len(self.T) + 8)
        self.archives.append(archived)
        self.block = block
        self.T, self.counts, self.groups, self.truth = [], {}, [], {}
        self.table_version += 1
        self.truth_version = self.table_version
        self.counts_version = (self.table_version, self.phi_version)
        self.groups_version = None
        self.cursor = None
        self.search_status = "COMPLETE"
        self._seal()

    def state(self):
        return {"kind": "N1_REFERENCE_043_v1", "configuration": {"W": self.W, "S": self.S, "K": self.K,
                    "observation_alphabets": self.observation_alphabets, "actions": self.actions},
                "block": self.block, "transitions": [x.state() for x in self.T], "Phi": self.Phi,
                "observed_constants": [sorted(x) for x in self.observed], "inventory": self.inventory,
                "inventory_tag": self.inventory_tag, "truth": [[p, v] for p, v in sorted(self.truth.items(), key=lambda x: (tree_size(x[0]), tree_tokens(x[0])))],
                "truth_version": self.truth_version, "table_version": self.table_version,
                "phi_version": self.phi_version, "counts_version": self.counts_version,
                "counts": [[k, sorted(v.items())] for k, v in sorted(self.counts.items())],
                "conflicting_groups": self.groups, "groups_version": self.groups_version,
                "cursor": self.cursor, "search_status": self.search_status,
                "construction_log": self.construction_log, "search_log": self.search_log,
                "prediction_log": self.prediction_log, "archives": self.archives}


class GenericReader(N1):
    """Prescribed order-0/1/2 exact typed-window reader on the SAME active T."""
    def __init__(self, order, observation_alphabets=((0, 1, 2, 3, 4),), actions=(0, 1, 2, 3, 4), meter=None):
        if order not in (0, 1, 2):
            raise ValueError("only prespecified reader orders 0,1,2")
        self.order = order
        self._fit_complete = False
        self.source_table_sha256 = None
        super().__init__(W=order, S=1, K=0, observation_alphabets=observation_alphabets, actions=actions, meter=meter)

    def _key(self, history, action):
        self.meter.charge("reader.key_construction", 3 + self.order * (len(self.observation_alphabets) + 1))
        past = tuple(_term(history, (0, 0, field, lag)) for field in range(len(self.observation_alphabets)) for lag in range(1, self.order + 1))
        past += tuple(_term(history, (0, 1, 0, lag)) for lag in range(1, self.order + 1))
        return (history.current, past, action)

    @property
    def counts_ready(self):
        return self._fit_complete and super().counts_ready

    def fit(self, transitions):
        """One bulk count reconstruction on an explicitly frozen source table.

        This reader does not replay repeated N1 feature-search/count updates.
        Any partial fit stays nonnumeric; its retained prefix is inspectable.
        """
        if self.T or self._fit_complete:
            raise ValueError("fit once on one frozen active table")
        if not isinstance(transitions, (list, tuple)):
            raise TypeError("frozen sequence of Transition records required")
        try:
            source = [record.state() for record in transitions]
            self.meter.charge("reader.source_table_view", len(transitions))
            raw = self.meter.encode(source)
            self._reserve(len(raw) + 1024)
            self.meter.charge("reader.source_table_hash", len(raw), bits=8)
            self.source_table_sha256 = hashlib.sha256(raw).hexdigest()
            for record in transitions:
                self.meter.charge("reader.record_validation")
                if not isinstance(record, Transition):
                    raise TypeError("Transition record required")
                self._validate_observation(record.outcome)
                for observation in record.history.observations:
                    self._validate_observation(observation)
                self.meter.charge("reader.action_validation", (1 + len(record.history.actions)) * len(self.actions))
                if record.action not in self.actions or any(a not in self.actions for a in record.history.actions):
                    raise ValueError("source action outside declared alphabet")
                record_bytes = len(self.meter.encode(record.state()))
                self.meter.charge("reader.record_copy_bytes", record_bytes)
                self.meter.charge("reader.record_commit", 2 + sum(map(len, record.history.observations)) + len(record.history.actions) + len(record.outcome))
                self.T.append(copy.deepcopy(record))
                self.table_version += 1
                for observation in record.history.observations:
                    self.observed[0].update(observation)
                self.observed[0].update(record.outcome)
                self.observed[1].update(record.history.actions + (record.action,))
            self.truth_version = self.table_version
            self.rebuild_counts()
            self.search_status = "FEATURE_SEARCH_NOT_REQUESTED"
            self._fit_complete = True
            self._seal()
            return {"status": "COMPLETE", "transitions": len(self.T), "counts_ready": self.counts_ready,
                    "source_table_sha256": self.source_table_sha256}
        except Limit as error:
            self.search_status = getattr(error, "status", str(error))
            self._fit_complete = False
            return {"status": self.search_status, "transitions": len(self.T), "counts_ready": False,
                    "source_table_sha256": self.source_table_sha256}

    def state(self):
        result = super().state()
        result["kind"] = "GENERIC_HISTORY_READER_043_v1"
        result["order"] = self.order
        result["fit_complete"] = self._fit_complete
        result["source_table_sha256"] = self.source_table_sha256
        return result
