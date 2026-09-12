#!/usr/bin/env python3
"""Version043 deterministic development work and retained-byte accounting.

A declared abstract-operation convention, not a count of Python instructions.
Address-space/RSS and wall/CPU limits are separate process measurements. No target
experiment budget or worst-case completion guarantee is inferred by this module.
"""
from __future__ import annotations
import json
from fractions import Fraction


class Limit(RuntimeError):
    def __init__(self, status):
        self.status = status
        super().__init__(status)


def _normal(value):
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, Fraction):
        return {'$rational': [value.numerator, value.denominator]}
    if type(value) in (list, tuple):
        return [_normal(v) for v in value]
    if type(value) in (set, frozenset):
        rows = [_normal(v) for v in value]
        return {'$set': sorted(rows, key=lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=True))}
    if type(value) is dict:
        if all(type(k) is str for k in value):
            return {k: _normal(v) for k, v in value.items()}
        rows = [[_normal(k), _normal(v)] for k, v in value.items()]
        return {'$map': sorted(rows, key=lambda v: json.dumps(v[0], sort_keys=True, separators=(',', ':'), ensure_ascii=True))}
    raise TypeError('Unsupported canonical accounting value: ' + type(value).__name__)


def canonical(value):
    return json.dumps(_normal(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def _nodes(value):
    if type(value) is dict:
        return 1 + sum(_nodes(k) + _nodes(v) for k, v in value.items())
    if type(value) in (list, tuple, set, frozenset):
        return 1 + sum(_nodes(v) for v in value)
    if isinstance(value, Fraction):
        return 3
    return 1


def bits(value):
    if isinstance(value, Fraction):
        return max(1, abs(value.numerator).bit_length()) + max(1, value.denominator.bit_length())
    if type(value) is int:
        return max(1, abs(value).bit_length())
    return max(1, len(canonical(value)) * 8)


class Meter:
    """Finite additive charges and explicit owner-based retained-byte reservations.

    Owners identify actual disjoint stored copies. No implicit object sharing is
    deducted. Modules must include their complete state, temporary workspace and
    evidence, and must reserve before an externally observable action. A successful
    retain records logical canonical bytes, not actual allocator or resident bytes.
    A failed charge changes no successful-work total; refusal is recorded separately.
    """
    def __init__(self, work_limit=None, memory_limit=None):
        for x in (work_limit, memory_limit):
            if x is not None and (type(x) is not int or x < 0):
                raise ValueError('Nonnegative integer limit required')
        self.work_limit = work_limit
        self.memory_limit = memory_limit
        self.work = 0
        self.charges = {}
        self.calls = {}
        self.owners = {}
        self.retained_bytes = 0
        self.peak_retained_bytes = 0
        self.refusals = []
        self._release_leases = {}

    @property
    def used(self):
        return self.work

    def charge(self, category, units=1, bits=1):
        if type(category) is not str or not category or type(units) is not int or units < 0 or type(bits) is not int or bits < 0:
            raise ValueError('Invalid work charge')
        amount = units * max(1, bits)
        if self.work_limit is not None and self.work + amount > self.work_limit:
            self.refusals.append({'status': 'COMPUTATION_INCOMPLETE', 'category': category, 'requested': amount, 'used': self.work})
            raise Limit('COMPUTATION_INCOMPLETE')
        self.work += amount
        self.charges[category] = self.charges.get(category, 0) + amount
        self.calls[category] = self.calls.get(category, 0) + 1
        return amount

    def encode(self, value):
        # Stable codec traversal and emitted-byte charges. Its sorting work is
        # additionally bounded/charged by serialized-key lengths and key count.
        self.charge('codec.node_visit', _nodes(value))
        raw = canonical(value)
        self.charge('codec.output_byte', len(raw), bits=8)
        # An explicit conservative comparison-work convention for canonical sort.
        # This is a chosen cost rule, not a claim about CPython's exact sort trace.
        self.charge('codec.ordering_bound', max(1, len(raw).bit_length()), bits=max(1, len(raw) * 8))
        return raw

    def reserve(self, owner, bytes_count):
        if type(owner) is not str or not owner or type(bytes_count) is not int or bytes_count < 0:
            raise ValueError('Invalid retained-byte reservation')
        self.charge('memory.reservation', bits=max(1, bytes_count.bit_length()))
        after = self.retained_bytes - self.owners.get(owner, 0) + bytes_count
        if self.memory_limit is not None and after > self.memory_limit:
            self.refusals.append({'status': 'MEMORY_LIMIT', 'owner': owner, 'requested': bytes_count, 'current': self.retained_bytes})
            raise Limit('MEMORY_LIMIT')
        self.owners[owner] = bytes_count
        self.retained_bytes = after
        self.peak_retained_bytes = max(self.peak_retained_bytes, after)
        return bytes_count

    def retain(self, owner, value):
        raw = self.encode(value)
        self.reserve(owner, len(raw))
        return len(raw)

    def release(self, owner):
        self.charge('memory.release')
        self.retained_bytes -= self.owners.pop(owner, 0)

    def prepay_release(self, owner):
        """Buy one failure-cleanup lease before an allocation can exhaust work.

        The opaque token is valid only in this Meter and only once. Its paid
        disposition neither increases a work limit nor refunds consumed work.
        """
        if type(owner) is not str or not owner:
            raise ValueError('Invalid cleanup owner')
        self.charge('memory.prepaid_cleanup', 3)
        token = object()
        self._release_leases[token] = owner
        return token

    def release_prepaid(self, token):
        if token not in self._release_leases:
            raise ValueError('Unknown or consumed cleanup lease')
        owner = self._release_leases.pop(token)
        self.retained_bytes -= self.owners.pop(owner, 0)

    def discard_prepaid_release(self, token):
        if token not in self._release_leases:
            raise ValueError('Unknown or consumed cleanup lease')
        self._release_leases.pop(token)

    def state(self):
        return {'kind': 'P3_DEVELOPMENT_METER_043_v1', 'work': self.work,
                'work_limit': self.work_limit, 'memory_limit': self.memory_limit,
                'charges': dict(sorted(self.charges.items())), 'calls': dict(sorted(self.calls.items())),
                'retained_bytes': self.retained_bytes, 'peak_retained_bytes': self.peak_retained_bytes,
                'owners': dict(sorted(self.owners.items())), 'refusals': list(self.refusals),
                'open_prepaid_cleanup_owners': sorted(self._release_leases.values()),
                'scope': 'Declared abstract-operation/codec convention; not Python instruction count or RSS; implementation instrumentation and full-work coverage require separate validation.'}


def rational_operation(meter, operator, left, right=None):
    """Exact fractions with explicit schoolbook arithmetic and Euclidean charges."""
    a = Fraction(left)
    b = Fraction(0 if right is None else right)
    if operator in ('add', 'sub'):
        meter.charge('rational.cross_product', bits=bits(a.numerator) * bits(b.denominator) + bits(b.numerator) * bits(a.denominator))
        n = a.numerator * b.denominator + (b.numerator * a.denominator if operator == 'add' else -b.numerator * a.denominator)
        meter.charge('rational.integer_add', bits=max(bits(a.numerator*b.denominator), bits(b.numerator*a.denominator)))
        meter.charge('rational.denominator_product', bits=bits(a.denominator) * bits(b.denominator))
        d = a.denominator * b.denominator
    elif operator == 'mul':
        meter.charge('rational.products', bits=bits(a.numerator)*bits(b.numerator)+bits(a.denominator)*bits(b.denominator))
        n, d = a.numerator*b.numerator, a.denominator*b.denominator
    elif operator == 'div':
        if b == 0:
            raise ZeroDivisionError
        meter.charge('rational.products', bits=bits(a.numerator)*bits(b.denominator)+bits(a.denominator)*bits(b.numerator))
        n, d = a.numerator*b.denominator, a.denominator*b.numerator
    else:
        raise ValueError('Unknown rational operation')
    x, y = abs(n), abs(d)
    while y:
        meter.charge('rational.euclidean_remainder', bits=bits(x)*bits(y))
        x, y = y, x % y
    meter.charge('rational.reduced_division', bits=bits(n)*bits(max(1,x))+bits(d)*bits(max(1,x)))
    return Fraction(n, d)
