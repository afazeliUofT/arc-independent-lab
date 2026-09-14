"""Frozen finite kernel checks; no learner, model, environment or profile run."""
import itertools
import importlib.util
from fractions import Fraction
from pathlib import Path
import sys
import unittest


def load_source(name, filename):
    path = Path(__file__).resolve().parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


reference = load_source("kernel_test_accounting043", "accounting043.py")
kernel = load_source("kernel_test_accounting048", "accounting048.py")
canonical043, nodes043 = reference.canonical, reference._nodes
Codec, Ledger, Limit, Owner, Schema = kernel.Codec, kernel.Ledger, kernel.Limit, kernel.Owner, kernel.Schema
MAX_SCHEMA_DEPTH, MAX_WIDTH = kernel.MAX_SCHEMA_DEPTH, kernel.MAX_WIDTH
codec_owners, compile_schema = kernel.codec_owners, kernel.compile_schema


CASE_MATRIX = (
    ("test_global_simultaneous_owners", "Global acquisition plus diagnostic sum; atomic refusal"),
    ("test_independent_copies_have_distinct_owners", "No implicit sharing deduction"),
    ("test_work_escrow_is_not_spent", "Unused capacity release never refunds spent work"),
    ("test_first_cause_and_prepaid_cleanup", "Latched cause; no scientific work after refusal; idempotent cleanup"),
    ("test_terminal_slots_are_bounded", "Finite slot/code vocabulary; immutable idempotent terminal commits"),
    ("test_undeclared_metadata_rejected", "Closed channels/operations/owners and initialization reserve"),
    ("test_codec_exact043_edge_fixtures", "Fraction, set/map tags, Unicode, DEL, surrogates, empty structures"),
    ("test_codec_structural_bound_reference", "Finite independent043 length/node oracle at boundary values"),
    ("test_codec_refuse_before_normalize", "Insufficient overlapping-owner capacity refuses before traversal"),
    ("test_codec_workspace_refusal", "Deliberately insufficient validation workspace"),
    ("test_codec_invalid_input_before_normalize", "Wrong type, width, integer width, record and cyclic value"),
    ("test_codec_live_overlap_and_output_lifetime", "Observe all owners during normalization; retained source/output"),
    ("test_codec_work_refusal_cleanup", "Mid-codec work refusal preserves first cause/source and drops temporaries"),
    ("test_schema_is_closed_and_finite", "Unknown/irrelevant/overdeep/ambiguous schema rejection"),
    ("test_actual_ordering_branch_work", "Executed set ordering receives comparison charges; list does not"),
)


def fixture_codec(schema, work=100_000_000, memory=100_000_000, **kwargs):
    ledger = Ledger(work, memory, codec_owners("c"))
    return ledger, Codec(ledger, schema, "c", **kwargs)


class Accounting048Tests(unittest.TestCase):
    def test_global_simultaneous_owners(self):
        owners = (Owner("a", "acquisition"), Owner("d", "diagnostic"))
        ledger = Ledger(100_000, 100_000, owners)
        available = ledger.memory_limit - ledger.metadata_bytes
        each = available * 3 // 4
        ledger.reserve_bundle((("a", each),))
        with self.assertRaises(Limit) as caught:
            ledger.reserve_bundle((("d", each),))
        self.assertEqual(caught.exception.status, "MEMORY_LIMIT")
        self.assertEqual(ledger.owned("a"), each)
        self.assertEqual(ledger.owned("d"), 0)
        self.assertEqual(ledger.retained_bytes, ledger.metadata_bytes + each)

    def test_independent_copies_have_distinct_owners(self):
        ledger = Ledger(100_000, 100_000, (Owner("a", "acquisition"), Owner("b", "acquisition")))
        ledger.reserve_bundle((("a", 300), ("b", 300)))
        self.assertEqual(ledger.retained_bytes - ledger.metadata_bytes, 600)
        ledger.cleanup("a")
        self.assertEqual(ledger.owned("b"), 300)
        with self.assertRaises(ValueError):
            ledger.reserve_bundle((("a", 1),))

    def test_work_escrow_is_not_spent(self):
        ledger = Ledger(1000, 100_000, (Owner("stage", "diagnostic"),))
        initial = ledger.spent
        ledger.reserve_work("stage", 100)
        self.assertEqual(ledger.spent, initial + 1)
        self.assertEqual(ledger.escrowed, 100)
        ledger.spend("diagnostic", "science", 40, escrow_owner="stage")
        self.assertEqual(ledger.spent, initial + 41)
        self.assertEqual(ledger.escrowed, 60)
        ledger.cleanup("stage")
        self.assertEqual(ledger.spent, initial + 41)
        self.assertEqual(ledger.escrowed, 0)
        self.assertEqual(ledger.channel_spent("diagnostic"), 41)

    def test_first_cause_and_prepaid_cleanup(self):
        ledger = Ledger(100, 100_000, (Owner("a", "acquisition"),))
        ledger.reserve_bundle((("a", 100),))
        ledger.spend("acquisition", "science", ledger.work_limit - ledger.spent)
        with self.assertRaises(Limit):
            ledger.spend("acquisition", "science")
        cause, spent = ledger.refusal, ledger.spent
        for operation in (lambda: ledger.spend("diagnostic", "science", 0),
                          lambda: ledger.reserve_bundle((("a", 0),)),
                          lambda: ledger.reserve_work("a", 0),
                          lambda: ledger.release_work("a")):
            with self.assertRaises(Limit) as caught:
                operation()
            self.assertIs(caught.exception.cause, cause)
        ledger.cleanup("a")
        ledger.cleanup("a")
        ledger.commit_terminal(0, "REFUSED", 1)
        ledger.commit_terminal(0, "REFUSED", 1)
        self.assertIs(ledger.refusal, cause)
        self.assertEqual(ledger.spent, spent)
        self.assertEqual(ledger.retained_bytes, ledger.metadata_bytes)

    def test_terminal_slots_are_bounded(self):
        ledger = Ledger(100, 100_000, (), terminal_slots=1)
        before = ledger.spent
        ledger.commit_terminal(0, "COMPLETED", 7)
        ledger.commit_terminal(0, "COMPLETED", 7)
        for args in ((1, "COMPLETED", 0), (0, "ARBITRARY", 0), (0, "REFUSED", 7)):
            with self.assertRaises(ValueError):
                ledger.commit_terminal(*args)
        self.assertEqual(len(ledger.terminals), 1)
        self.assertEqual(ledger.spent, before)

    def test_undeclared_metadata_rejected(self):
        ledger = Ledger(100, 100_000, (Owner("a", "acquisition"),))
        with self.assertRaises(ValueError):
            ledger.reserve_bundle((("new", 1),))
        with self.assertRaises(ValueError):
            ledger.spend("arbitrary", "science", 1)
        with self.assertRaises(ValueError):
            ledger.spend("acquisition", "unregistered", 1)
        with self.assertRaises(ValueError):
            Ledger(1, 1, ())
        self.assertEqual(len(ledger.owner_specs), 1)

    def test_codec_exact043_edge_fixtures(self):
        scalar = Schema("union", choices=(Schema("scalar"), Schema("int", bits=1024), Schema("string", chars=100)))
        fixtures = (
            (Schema("scalar"), None), (Schema("scalar"), False),
            (Schema("int", bits=1024), -(1 << 1000)),
            (Schema("string", chars=100), '\x00\x1f\x7f\b\f\n\r\t"\\é\U0001f680\ud800'),
            (Schema("fraction", bits=16), Fraction(-7, 8)),
            (Schema("list", width=6, item=scalar), [True, None, -1, "a", "\x7f"]),
            (Schema("tuple", width=2, item=Schema("int", bits=4)), (2, -3)),
            (Schema("set", width=5, item=scalar), frozenset(("10", 2, 10, None))),
            (Schema("set", width=0, item=Schema("scalar")), set()),
            (Schema("map", width=3, key=scalar, value=Schema("fraction", bits=8)), {2: Fraction(2, 3), "a": Fraction(5, 7)}),
            (Schema("map", width=3, key=Schema("string", chars=5), value=Schema("scalar")), {"é": None, "z": False}),
            (Schema("map", width=0, key=Schema("int", bits=8), value=Schema("scalar")), {}),
            (Schema("record", fields=(("a", Schema("fraction", bits=8)), ("b", Schema("list", width=0, item=scalar)))), {"b": [], "a": Fraction(1, 2)}),
        )
        for schema, value in fixtures:
            with self.subTest(kind=schema.kind, type=type(value).__name__):
                ledger, codec = fixture_codec(schema)
                output = codec.encode(value)
                self.assertEqual(output.raw, canonical043(value))
                self.assertLessEqual(len(output.raw), codec.bound.output)
                output.close()
                ledger.cleanup(output.source_owner)
        self.assertEqual(canonical043(Fraction(-7, 8)), b'{"$rational":[-7,8]}')

    def test_codec_structural_bound_reference(self):
        item = Schema("union", choices=(Schema("int", bits=3), Schema("string", chars=2)))
        values = (-7, 0, 7, "", "\U0001f680\U0001f680", "\ud800\x7f")
        schema = Schema("list", width=2, item=item)
        bound = compile_schema(schema)
        for width in range(3):
            for row in itertools.product(values, repeat=width):
                value = list(row)
                self.assertLessEqual(len(canonical043(value)), bound.output)
                self.assertLessEqual(nodes043(value), bound.nodes)
        nested = Schema("map", width=2, key=Schema("tuple", width=2, item=Schema("int", bits=3)),
                        value=Schema("set", width=2, item=Schema("fraction", bits=4)))
        value = {(7, -7): {Fraction(-7, 8), Fraction(15, 1)}, (): set()}
        ledger, codec = fixture_codec(nested)
        output = codec.encode(value)
        self.assertEqual(output.raw, canonical043(value))
        self.assertLessEqual(len(output.raw), compile_schema(nested).output)
        self.assertLessEqual(nodes043(value), compile_schema(nested).nodes)

    def test_codec_refuse_before_normalize(self):
        ledger, codec = fixture_codec(Schema("list", width=128, item=Schema("string", chars=4096)), memory=100_000)
        with self.assertRaises(Limit) as caught:
            codec.encode([])
        self.assertEqual(caught.exception.status, "MEMORY_LIMIT")
        self.assertFalse(codec.normalization_started)
        self.assertEqual(ledger.charged("acquisition", "codec.validate"), 0)
        self.assertTrue(all(ledger.owned(owner.name) == 0 for owner in ledger.owner_specs))

    def test_codec_workspace_refusal(self):
        ledger, codec = fixture_codec(Schema("scalar"), workspace_bytes=0)
        with self.assertRaises(Limit) as caught:
            codec.encode(None)
        self.assertEqual(caught.exception.status, "WORKSPACE_LIMIT")
        self.assertFalse(codec.normalization_started)
        self.assertEqual(ledger.charged("acquisition", "codec.validate"), 0)

    def test_codec_invalid_input_before_normalize(self):
        cycle = []
        cycle.append(cycle)
        fixtures = (
            (Schema("int", bits=3), True), (Schema("int", bits=3), 8),
            (Schema("string", chars=2), "abc"),
            (Schema("list", width=1, item=Schema("scalar")), [None, None]),
            (Schema("list", width=1, item=Schema("scalar")), cycle),
            (Schema("record", fields=(("a", Schema("scalar")),)), {"b": None}),
            (Schema("fraction", bits=3), Fraction(1, 8)),
        )
        for schema, value in fixtures:
            ledger, codec = fixture_codec(schema)
            with self.assertRaises(Limit) as caught:
                codec.encode(value)
            self.assertEqual(caught.exception.status, "SCHEMA_LIMIT")
            self.assertFalse(codec.normalization_started)
            self.assertEqual(ledger.charged("acquisition", "codec.normalize"), 0)
            self.assertGreater(ledger.owned("c.source"), 0)
            self.assertTrue(all(ledger.owned("c." + suffix) == 0 for suffix in ("validation", "normalized", "ordering", "json_text", "encoded")))

    def test_codec_live_overlap_and_output_lifetime(self):
        class InspectCodec(Codec):
            def _normal(inner, value):
                self.assertTrue(all(inner.ledger.owned(name) > 0 for name in inner.names))
                self.assertGreaterEqual(inner.ledger.retained_bytes,
                                        inner.ledger.metadata_bytes + sum(size for _, size in inner.reservations))
                return super()._normal(value)
        schema = Schema("list", width=2, item=Schema("int", bits=8))
        ledger = Ledger(100_000, 100_000, codec_owners("c"))
        ledger.reserve_bundle((("c.source", 1000),))
        output = InspectCodec(ledger, schema, "c").encode([1, 2])
        self.assertEqual(ledger.owned("c.source"), 1000)
        self.assertGreater(ledger.owned("c.encoded"), 0)
        self.assertEqual(ledger.owned("c.normalized"), 0)
        output.close()
        output.close()
        self.assertEqual(output.raw, b"")
        self.assertEqual(ledger.owned("c.encoded"), 0)
        self.assertEqual(ledger.owned("c.source"), 1000)

    def test_codec_work_refusal_cleanup(self):
        ledger, codec = fixture_codec(Schema("string", chars=100), work=100)
        retained_error = None
        try:
            codec.encode("a" * 100)
        except Limit as error:
            retained_error = error
        self.assertIsNotNone(retained_error)
        self.assertEqual(retained_error.status, "COMPUTATION_INCOMPLETE")
        self.assertIsNone(retained_error.__context__)
        self.assertIsNone(retained_error.__cause__)
        traceback = retained_error.__traceback__
        while traceback is not None:
            self.assertNotIn(traceback.tb_frame.f_code.co_name,
                             ("_normal", "_json", "_measure", "_charge", "spend", "refuse"))
            traceback = traceback.tb_next
        self.assertTrue(codec.normalization_started)
        self.assertGreater(ledger.owned("c.source"), 0)
        self.assertTrue(all(ledger.owned(name) == 0 for name in codec.names[1:]))
        spent = ledger.spent
        ledger.cleanup("c.source")
        ledger.commit_terminal(0, "REFUSED")
        self.assertEqual(ledger.spent, spent)

    def test_schema_is_closed_and_finite(self):
        overdeep = Schema("scalar")
        for _ in range(MAX_SCHEMA_DEPTH):
            overdeep = Schema("list", width=1, item=overdeep)
        invalid = (Schema("unknown"), Schema("scalar", bits=2),
                   Schema("int", bits=0), Schema("list", width=MAX_WIDTH + 1, item=Schema("scalar")),
                   Schema("union", choices=(Schema("int", bits=3), Schema("int", bits=4))),
                   Schema("record", fields=(("a", Schema("scalar")), ("a", Schema("scalar")))), overdeep)
        for schema in invalid:
            with self.assertRaises(ValueError):
                compile_schema(schema)
        for width in (245, 3002, 27720, 65536):
            bound = compile_schema(Schema("list", width=width, item=Schema("scalar")))
            self.assertEqual(bound.nodes, 1 + width)

    def test_actual_ordering_branch_work(self):
        integer = Schema("int", bits=8)
        list_ledger, list_codec = fixture_codec(Schema("list", width=3, item=integer))
        set_ledger, set_codec = fixture_codec(Schema("set", width=3, item=integer))
        self.assertEqual(list_codec.encode([10, 2, 1]).raw, canonical043([10, 2, 1]))
        self.assertEqual(set_codec.encode({10, 2, 1}).raw, canonical043({10, 2, 1}))
        self.assertEqual(list_ledger.charged("acquisition", "codec.compare"), 0)
        self.assertGreater(set_ledger.charged("acquisition", "codec.compare"), 0)


if __name__ == "__main__":
    unittest.main()
