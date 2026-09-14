#!/usr/bin/env python3
"""Bounded 048 kernel prerequisite; NOT a completed 047 correction.

Only the ledger and a closed-schema codec are guarded here. No learner, adapter,
transport, complete-work projector, scientific budget or admission is supplied.
Bytes are declared logical ownership envelopes, never Python allocator/RSS bytes.
The caller must own/admit the input before this API; the codec cannot retroactively
guard input construction. Schema compilation is bounded apparatus preparation.
Python frames/integers/counters use the declared finite apparatus convention below;
this is not an interpreter-instruction or physical-memory accounting instrument.

Work prices: one per visited/validated/normalized/measured node or moved slot;
eight per examined string code point and emitted ASCII byte. Each actual
json.dumps invocation receives the 043 ordering convention
max(1, L.bit_length()) * max(1, 8*L), with its actual output length L, before
execution. This is an explicit cost convention, not an imputed sort trace.
The extra stable sort actually compares keys, charging examined code points and
its reached key-wrapper construction. No unused escrow is reported as spent work.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cmp_to_key
import json

CHANNELS = ("acquisition", "diagnostic", "apparatus")
OPERATIONS = ("apparatus.init", "memory.reserve", "work.reserve", "work.release",
              "science", "codec.validate", "codec.character", "codec.normalize",
              "codec.slot", "codec.measure", "codec.json_visit", "codec.output",
              "codec.ordering043", "codec.compare", "codec.move")
TERMINAL_CODES = ("COMPLETED", "REFUSED", "INVALID_SCHEMA_VALUE", "CLOSED")
MAX_UNITS = (1 << 63) - 1
MAX_OWNERS = 4096
MAX_TERMINALS = 16
MAX_SCHEMA_DEPTH = 20
MAX_SCHEMA_DECLARATIONS = 512
MAX_WIDTH = 65536
MAX_STRING = 4096
MAX_BITS = 1024


def _uint(value):
    if type(value) is not int or not 0 <= value <= MAX_UNITS:
        raise ValueError("Expected a bounded nonnegative integer")
    return value


@dataclass(frozen=True, slots=True)
class Owner:
    name: str
    channel: str


@dataclass(frozen=True, slots=True)
class Refusal:
    status: str
    channel: str
    operation: str
    owner_index: int
    requested: int


class Limit(RuntimeError):
    def __init__(self, cause):
        self.cause = cause
        self.status = cause.status
        super().__init__(cause.status)


@dataclass(slots=True)
class Terminal:
    code: str | None = None
    value: int = 0


class Ledger:
    """One global allowance; all names, counters and terminal slots are finite.

    Cleanup and one commit per terminal slot are prepaid during initialization.
    Cleanup releases ownership/unused escrow only; spent work is monotonic.
    A latched refusal forbids every subsequent scientific debit or reservation.
    Terminal/cleanup methods remain usable and idempotent after refusal. Caller
    retention of exceptions or exported reports needs a separate guarded owner.
    No method creates an unbounded refusal history or registers names dynamically.
    """
    def __init__(self, work_limit, memory_limit, owners, terminal_slots=2):
        self.work_limit = _uint(work_limit)
        self.memory_limit = _uint(memory_limit)
        if type(owners) is not tuple or len(owners) > MAX_OWNERS:
            raise ValueError("Declare a finite tuple of owners")
        if type(terminal_slots) is not int or not 0 <= terminal_slots <= MAX_TERMINALS:
            raise ValueError("Invalid terminal capacity")
        names = set()
        for owner in owners:
            if (type(owner) is not Owner or type(owner.name) is not str or
                    not owner.name or len(owner.name) > 80 or
                    not owner.name.isascii() or type(owner.channel) is not str or owner.channel not in CHANNELS or
                    owner.name in names):
                raise ValueError("Invalid/duplicate owner declaration")
            names.add(owner.name)
        # Fixed owner/counter/first-cause/terminal metadata envelope. These are
        # declared logical slots (not sizeof); counters cannot exceed 63 bits.
        self.metadata_bytes = (512 + 64 * len(CHANNELS) * len(OPERATIONS) +
                               sum(256 + len(o.name) for o in owners) +
                               128 * terminal_slots)
        self.prepaid_work = 1 + 3 * len(owners) + 3 * terminal_slots
        if self.metadata_bytes > memory_limit or self.prepaid_work > work_limit:
            raise ValueError("Ledger initialization cannot prepay apparatus")
        self.owner_specs = owners
        self._owned = [0] * len(owners)
        self._escrow = [0] * len(owners)
        self._closed = [False] * len(owners)
        self._work = [0] * len(CHANNELS)
        self._charges = [[0] * len(OPERATIONS) for _ in CHANNELS]
        self.terminals = tuple(Terminal() for _ in range(terminal_slots))
        self.refusal = None
        self._work[2] = self.prepaid_work
        self._charges[2][0] = self.prepaid_work
        self.peak_retained_bytes = self.metadata_bytes

    @property
    def spent(self):
        return sum(self._work)

    @property
    def escrowed(self):
        return sum(self._escrow)

    @property
    def retained_bytes(self):
        return self.metadata_bytes + sum(self._owned)

    def owned(self, owner):
        return self._owned[self._index(owner)]

    def channel_spent(self, channel):
        return self._work[CHANNELS.index(channel)]

    def charged(self, channel, operation):
        return self._charges[CHANNELS.index(channel)][OPERATIONS.index(operation)]

    def _index(self, owner):
        for index, spec in enumerate(self.owner_specs):
            if spec.name == owner:
                return index
        raise ValueError("Undeclared owner")

    def _active(self):
        if self.refusal is not None:
            raise Limit(self.refusal)

    def refuse(self, status, channel, operation, owner_index=-1, requested=0):
        self._active()
        if status not in ("MEMORY_LIMIT", "COMPUTATION_INCOMPLETE", "SCHEMA_LIMIT", "WORKSPACE_LIMIT"):
            raise ValueError("Undeclared refusal status")
        if channel not in CHANNELS or operation not in OPERATIONS:
            raise ValueError("Undeclared refusal metadata")
        if type(owner_index) is not int or not -1 <= owner_index < len(self.owner_specs):
            raise ValueError("Invalid refusal owner")
        self.refusal = Refusal(status, channel, operation, owner_index, _uint(requested))
        raise Limit(self.refusal)

    def spend(self, channel, operation, amount=1, escrow_owner=None):
        self._active()
        ci, oi = CHANNELS.index(channel), OPERATIONS.index(operation)
        amount = _uint(amount)
        if escrow_owner is None:
            if self.spent + self.escrowed + amount > self.work_limit:
                self.refuse("COMPUTATION_INCOMPLETE", channel, operation, requested=amount)
        else:
            index = self._index(escrow_owner)
            if self.owner_specs[index].channel != channel or self._closed[index]:
                raise ValueError("Wrong-channel or closed escrow")
            if amount > self._escrow[index]:
                self.refuse("COMPUTATION_INCOMPLETE", channel, operation, index, amount)
            self._escrow[index] -= amount
        self._work[ci] += amount
        self._charges[ci][oi] += amount

    def reserve_work(self, owner, amount):
        self._active()
        index, amount = self._index(owner), _uint(amount)
        if self._closed[index]:
            raise ValueError("Owner already cleaned")
        channel = self.owner_specs[index].channel
        self.spend(channel, "work.reserve")
        if self.spent + self.escrowed - self._escrow[index] + amount > self.work_limit:
            self.refuse("COMPUTATION_INCOMPLETE", channel, "work.reserve", index, amount)
        self._escrow[index] = amount

    def release_work(self, owner):
        self._active()
        index = self._index(owner)
        self.spend(self.owner_specs[index].channel, "work.release")
        self._escrow[index] = 0

    def reserve_bundle(self, reservations):
        """Atomically admit a fixed tuple of distinct owner sizes, before expansion."""
        self._active()
        if type(reservations) is not tuple or len(reservations) > len(self.owner_specs):
            raise ValueError("Invalid reservation tuple")
        after = self.retained_bytes
        seen = 0
        for owner, size in reservations:
            index, size = self._index(owner), _uint(size)
            if self._closed[index] or seen & (1 << index):
                raise ValueError("Closed or duplicate owner")
            seen |= 1 << index
            self.spend(self.owner_specs[index].channel, "memory.reserve")
            after += size - self._owned[index]
        if after > self.memory_limit:
            # No owner-size mutation occurs on failure; the attempted guard work
            # remains spent. Global demand includes all channels simultaneously.
            # requested is a saturated lower bound if global addition exceeds
            # the 63-bit metadata domain, never a claim of exact overflow size.
            self.refuse("MEMORY_LIMIT", "apparatus", "memory.reserve", requested=min(after, MAX_UNITS))
        for owner, size in reservations:
            self._owned[self._index(owner)] = size
        self.peak_retained_bytes = max(self.peak_retained_bytes, after)

    def cleanup(self, owner):
        index = self._index(owner)
        self._owned[index] = 0
        self._escrow[index] = 0
        self._closed[index] = True

    def commit_terminal(self, slot, code, value=0):
        if type(slot) is not int or not 0 <= slot < len(self.terminals):
            raise ValueError("Undeclared terminal slot")
        if code not in TERMINAL_CODES:
            raise ValueError("Undeclared terminal code")
        value = _uint(value)
        terminal = self.terminals[slot]
        if terminal.code is not None and (terminal.code, terminal.value) != (code, value):
            raise ValueError("Terminal slot already committed")
        terminal.code, terminal.value = code, value


@dataclass(frozen=True, slots=True)
class Schema:
    """Closed acyclic tree. Irrelevant fields MUST remain at their defaults."""
    kind: str
    bits: int = 0
    chars: int = 0
    width: int = 0
    item: Schema | None = None
    key: Schema | None = None
    value: Schema | None = None
    fields: tuple = ()
    choices: tuple = ()


@dataclass(frozen=True, slots=True)
class Bound:
    output: int
    nodes: int
    keys: int
    depth: int


_KINDS = {
    "scalar": frozenset((type(None), bool)), "int": frozenset((int,)),
    "string": frozenset((str,)), "fraction": frozenset((Fraction,)),
    "list": frozenset((list,)), "tuple": frozenset((tuple,)),
    "set": frozenset((set, frozenset)), "map": frozenset((dict,)),
    "record": frozenset((dict,)),
}


def _types(schema):
    if schema.kind == "union":
        result = frozenset()
        for child in schema.choices:
            result = result | _types(child)
        return result
    return _KINDS[schema.kind]


def compile_schema(schema):
    """Literal structural recurrence uses schema metadata only, never values."""
    declarations = 0

    def walk(s, depth):
        nonlocal declarations
        declarations += 1
        if type(s) is not Schema or depth > MAX_SCHEMA_DEPTH or declarations > MAX_SCHEMA_DECLARATIONS:
            raise ValueError("Schema tree is not within finite declaration limits")
        if s.kind not in _KINDS and s.kind != "union":
            raise ValueError("Unknown schema kind")
        allowed = {"scalar": (), "int": ("bits",), "string": ("chars",),
                   "fraction": ("bits",), "list": ("width", "item"),
                   "tuple": ("width", "item"), "set": ("width", "item"),
                   "map": ("width", "key", "value"), "record": ("fields",),
                   "union": ("choices",)}[s.kind]
        for name, default in (("bits", 0), ("chars", 0), ("width", 0),
                              ("item", None), ("key", None), ("value", None),
                              ("fields", ()), ("choices", ())):
            if name not in allowed and getattr(s, name) != default:
                raise ValueError("Unexpected schema metadata")
        for name, maximum in (("bits", MAX_BITS), ("chars", MAX_STRING), ("width", MAX_WIDTH)):
            if type(getattr(s, name)) is not int or not 0 <= getattr(s, name) <= maximum:
                raise ValueError("Invalid scalar schema bound")
        if type(s.fields) is not tuple or type(s.choices) is not tuple:
            raise ValueError("Schema sequences must be tuples")
        if s.kind == "scalar":
            out = Bound(5, 1, 0, 1)
        elif s.kind == "int":
            if not s.bits:
                raise ValueError("Integer width must be positive")
            out = Bound(s.bits + 1, 1, 0, 1)
        elif s.kind == "string":
            out = Bound(12 * s.chars + 2, 1, 0, 1)
        elif s.kind == "fraction":
            if not s.bits:
                raise ValueError("Fraction width must be positive")
            out = Bound(17 + 2 * (s.bits + 1), 3, 0, 2)
        elif s.kind in ("list", "tuple", "set"):
            child = walk(s.item, depth + 1)
            n = s.width
            out = Bound((11 if s.kind == "set" else 2) + n * child.output + max(0, n - 1),
                        1 + n * child.nodes, n * child.keys + (n * child.output if s.kind == "set" else 0),
                        child.depth + (2 if s.kind == "set" else 1))
        elif s.kind == "map":
            key, val = walk(s.key, depth + 1), walk(s.value, depth + 1)
            n = s.width
            # Tagged-pair representation dominates the string-key object form.
            out = Bound(11 + n * (3 + key.output + val.output) + max(0, n - 1),
                        1 + n * (key.nodes + val.nodes),
                        n * (key.keys + val.keys + key.output), 3 + max(key.depth, val.depth))
        elif s.kind == "record":
            if len(s.fields) > MAX_WIDTH:
                raise ValueError("Too many record fields")
            previous = set()
            output, nodes, keys, subdepth = 2, 1, 0, 0
            for row in s.fields:
                if type(row) is not tuple or len(row) != 2:
                    raise ValueError("Malformed record field")
                name, child_schema = row
                if type(name) is not str or len(name) > MAX_STRING or name in previous:
                    raise ValueError("Invalid/duplicate record field")
                previous.add(name)
                child = walk(child_schema, depth + 1)
                output += len(json.dumps(name, ensure_ascii=True)) + 1 + child.output
                nodes += 1 + child.nodes
                keys += child.keys
                subdepth = max(subdepth, child.depth)
            out = Bound(output + max(0, len(s.fields) - 1), nodes, keys, 1 + subdepth)
        else:
            if not 1 <= len(s.choices) <= 8:
                raise ValueError("Invalid union width")
            kinds = frozenset()
            bounds = []
            for child in s.choices:
                bounds.append(walk(child, depth + 1))
                child_types = _types(child)
                if kinds & child_types:
                    raise ValueError("Union alternatives must have disjoint exact types")
                kinds |= child_types
            out = Bound(max(b.output for b in bounds), max(b.nodes for b in bounds),
                        max(b.keys for b in bounds), 1 + max(b.depth for b in bounds))
        if max(out.output, out.nodes, out.keys, out.depth) > MAX_UNITS // 1024:
            raise ValueError("Schema expansion exceeds finite metadata capacity")
        return out

    return walk(schema, 1)


_CODEC_SUFFIXES = ("source", "validation", "normalized", "ordering", "json_text", "encoded")


def codec_owners(prefix, channel="acquisition"):
    return tuple(Owner(prefix + "." + suffix, channel) for suffix in _CODEC_SUFFIXES)


@dataclass(slots=True)
class Encoded:
    raw: bytes
    ledger: Ledger
    output_owner: str
    source_owner: str

    def close(self):
        """Drop this handle's output before its prepaid owner release."""
        self.raw = b""
        self.ledger.cleanup(self.output_owner)


class Codec:
    """Single-use prepared codec. Keep source owner until caller drops its input.

    All six independent envelopes coexist at admission. The ordering envelope
    includes canonical key text, four output envelopes for overlapping scalar
    arithmetic/JSON chunk workspace, and 64 logical bytes per source node/frame
    for bounded reference arrays, pair/list slots and measure/sort workspace. Validation has
    a preallocated depth stack of input references, never recursive input copies.
    Normalized containers remain live through ASCII-byte creation. On success
    source/output owners stay live and all temporary objects are dropped before
    their prepaid release. New invocations require newly declared owner slots.
    """
    def __init__(self, ledger, schema, prefix, channel="acquisition", workspace_bytes=None):
        self.ledger, self.schema, self.prefix, self.channel = ledger, schema, prefix, channel
        self.bound = compile_schema(schema)
        self._routes = {}

        def prepare(s):
            if s.kind == "union":
                self._routes[id(s)] = tuple((_types(child), child) for child in s.choices)
                for child in s.choices:
                    prepare(child)
            elif s.kind in ("list", "tuple", "set"):
                prepare(s.item)
            elif s.kind == "map":
                prepare(s.key)
                prepare(s.value)
            elif s.kind == "record":
                for _, child in s.fields:
                    prepare(child)
        prepare(schema)
        self.names = tuple(prefix + "." + s for s in _CODEC_SUFFIXES)
        for name in self.names:
            index = ledger._index(name)
            if ledger.owner_specs[index].channel != channel:
                raise ValueError("Codec owner channel mismatch")
        self.validation_bytes = 256 * (self.bound.depth + MAX_SCHEMA_DEPTH + 1)
        self.workspace_bytes = self.validation_bytes if workspace_bytes is None else _uint(workspace_bytes)
        b = self.bound
        self.reservations = tuple(zip(self.names, (b.output, self.validation_bytes,
                                  b.output, b.keys + 4 * b.output + 64 * (b.nodes + b.depth + 1), b.output, b.output)))
        self.used = False
        self.normalization_started = False
        self._stack = None

    def _charge(self, operation, amount=1):
        self.ledger.spend(self.channel, operation, amount)

    def _invalid(self):
        self.ledger.refuse("SCHEMA_LIMIT", self.channel, "codec.validate")

    def _validate(self, value, schema, level=0):
        self._charge("codec.validate")
        # The entire stack was allocated only after all owner reservations.
        self._stack[level] = value
        kind = schema.kind
        if kind == "union":
            for types, choice in self._routes[id(schema)]:
                self._charge("codec.validate")
                if type(value) in types:
                    return self._validate(value, choice, level + 1)
            self._invalid()
        if type(value) not in _KINDS[kind]:
            self._invalid()
        if kind == "int":
            if value.bit_length() > schema.bits:
                self._invalid()
        elif kind == "string":
            if len(value) > schema.chars:
                self._invalid()
        elif kind == "fraction":
            if value.numerator.bit_length() > schema.bits or value.denominator.bit_length() > schema.bits:
                self._invalid()
        elif kind in ("list", "tuple", "set"):
            if len(value) > schema.width:
                self._invalid()
            for child in value:
                self._validate(child, schema.item, level + 1)
        elif kind == "map":
            if len(value) > schema.width:
                self._invalid()
            for key, val in value.items():
                self._validate(key, schema.key, level + 1)
                self._validate(val, schema.value, level + 1)
        elif kind == "record":
            if len(value) != len(schema.fields):
                self._invalid()
            # Validate exact key types/lengths before any membership comparison;
            # this refuses hostile custom keys without invoking their methods.
            for key in value:
                self._charge("codec.validate")
                if type(key) is not str or len(key) > MAX_STRING:
                    self._invalid()
                self._charge("codec.character", 8 * len(key))
            for name, child_schema in schema.fields:
                self._charge("codec.character", 8 * len(name))
                if name not in value:
                    self._invalid()
                self._validate(value[name], child_schema, level + 1)
        self._stack[level] = None

    def _compare(self, a, b):
        for index in range(min(len(a), len(b))):
            self._charge("codec.compare", 8)
            if a[index] != b[index]:
                return -1 if a[index] < b[index] else 1
        self._charge("codec.compare")
        return (len(a) > len(b)) - (len(a) < len(b))

    def _order(self, rows):
        # Stable builtin ordering avoids a new quadratic full-domain algorithm.
        # Key wrappers/reference workspace are already owned. Comparisons are
        # charged as reached; CPython's internal pointer moves are apparatus,
        # not represented as an invented exact move trace.
        self._charge("codec.slot", len(rows))
        rows.sort(key=cmp_to_key(lambda a, b: self._compare(a[0], b[0])))
        return rows

    def _normal(self, value):
        self._charge("codec.normalize")
        if value is None or type(value) in (bool, int, str):
            return value
        if type(value) is Fraction:
            self._charge("codec.slot", 4)
            return {"$rational": [value.numerator, value.denominator]}
        if type(value) in (list, tuple):
            rows = []
            for child in value:
                normalized = self._normal(child)
                self._charge("codec.slot")
                rows.append(normalized)
            return rows
        if type(value) in (set, frozenset):
            rows = []
            for child in value:
                normalized = self._normal(child)
                key = self._json(normalized)
                self._charge("codec.slot", 2)
                rows.append((key, normalized))
            self._order(rows)
            self._charge("codec.slot", len(rows) + 1)
            return {"$set": [row[1] for row in rows]}
        string_keys = True
        for key in value:
            self._charge("codec.normalize")
            if type(key) is not str:
                string_keys = False
                break
        if string_keys:
            result = {}
            for key, child in value.items():
                normalized = self._normal(child)
                self._charge("codec.slot")
                result[key] = normalized
            return result
        rows = []
        for key, child in value.items():
            normal_key, normal_val = self._normal(key), self._normal(child)
            key_text = self._json(normal_key)
            self._charge("codec.slot", 4)
            rows.append((key_text, [normal_key, normal_val]))
        self._order(rows)
        self._charge("codec.slot", len(rows) + 1)
        return {"$map": [row[1] for row in rows]}

    def _measure(self, value):
        self._charge("codec.measure")
        if value is None:
            return 4, 1
        if type(value) is bool:
            return (4 if value else 5), 1
        if type(value) is int:
            # Exact decimal-length calculation executes bounded divisions here;
            # its operand/result scratch is in the ordering envelope. Actual
            # JSON integer conversion is charged by the JSON-output convention.
            magnitude = abs(value)
            digits = 1
            while magnitude >= 10:
                self._charge("codec.measure", max(1, magnitude.bit_length()))
                magnitude //= 10
                digits += 1
            return digits + (1 if value < 0 else 0), 1
        if type(value) is str:
            length = 2
            for char in value:
                self._charge("codec.character", 8)
                code = ord(char)
                if char in ('"', "\\", "\b", "\f", "\n", "\r", "\t"):
                    length += 2
                elif code < 32 or 127 <= code <= 65535:
                    length += 6
                elif code > 65535:
                    length += 12
                else:
                    length += 1
            return length, 1
        size, nodes = 2 + max(0, len(value) - 1), 1
        if type(value) is list:
            for child in value:
                child_size, child_nodes = self._measure(child)
                size, nodes = size + child_size, nodes + child_nodes
        else:
            for key, child in value.items():
                key_size, key_nodes = self._measure(key)
                child_size, child_nodes = self._measure(child)
                size += key_size + child_size + 1
                nodes += key_nodes + child_nodes
        return size, nodes

    def _json(self, normalized):
        length, nodes = self._measure(normalized)
        self._charge("codec.json_visit", nodes)
        self._charge("codec.output", 8 * length)
        self._charge("codec.ordering043", max(1, length.bit_length()) * max(1, 8 * length))
        text = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
        if len(text) != length:
            raise AssertionError("Codec length recurrence mismatch")
        return text

    def encode(self, value):
        self.ledger._active()
        if self.used:
            raise ValueError("Codec is single use")
        self.used = True
        if self.workspace_bytes < self.validation_bytes:
            self.ledger.refuse("WORKSPACE_LIMIT", self.channel, "codec.validate", requested=self.validation_bytes)
        # The input is caller-created; this guard admits its retained envelope
        # alongside every disjoint codec copy before any traversal/normalization.
        reservations = ((self.names[0], max(self.bound.output, self.ledger.owned(self.names[0]))),) + self.reservations[1:]
        self.ledger.reserve_bundle(reservations)
        normalized = text = raw = None
        success = safe_release = False
        error_cause = None
        try:
            self._stack = [None] * (self.bound.depth + MAX_SCHEMA_DEPTH + 1)
            self._validate(value, self.schema)
            self.normalization_started = True
            normalized = self._normal(value)
            text = self._json(normalized)
            if len(text) > self.bound.output:
                raise AssertionError("Schema output envelope violated")
            self._charge("codec.output", 8 * len(text))
            raw = text.encode("ascii")
            result = Encoded(raw, self.ledger, self.names[5], self.names[0])
            success = True
            return result
        except Limit as error:
            # A live traceback retains lower-frame rows and JSON intermediates.
            # Remove it before releasing temporary owners, then leave this
            # handler before raising the new bounded cause-only exception.
            error_cause = error.cause
            error.__traceback__ = None
            error.__context__ = None
            error.__cause__ = None
            safe_release = True
        finally:
            normalized = text = raw = None
            self._stack = None
            if success or safe_release:
                for name in self.names[1:5]:
                    self.ledger.cleanup(name)
                if not success:
                    self.ledger.cleanup(self.names[5])
            # Unexpected Python exceptions preserve reservations because their
            # surviving traceback may own codec intermediates. No RSS guarantee
            # or automatic recovery from process failure is asserted.
            # Source owner deliberately survives success AND refusal: the
            # caller still holds value. Only its caller may release that owner.
        if error_cause is not None:
            raise Limit(error_cause) from None
