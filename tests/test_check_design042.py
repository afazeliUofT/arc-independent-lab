"""Check the material source-admission risks, without instantiating a learner."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('instrument042', ROOT / 'scripts/check_design042.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class SourceAdmission(unittest.TestCase):
    def setUp(self):
        scratch = ROOT.parent / 'work042'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='instrument_source_', dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in [*CHECK.SOURCE_PINS, CHECK.CODE_PATH]:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def assert_rejected(self, code):
        result = CHECK.verify(self.root, self.root / 'private_packet_not_available')
        self.assertIs(result['integrity_verified'], False)
        self.assertEqual(result['failure_class'], code)
        self.assertNotIn(str(self.root), str(result))
        self.assertNotIn('expanded_panel', result)
        self.assertEqual(result['boundaries']['native_starts'], 0)
        self.assertIs(result['boundaries']['predictor_fit'], False)

    def test_each_mutated_scientific_source_stops_before_enumeration(self):
        for name in CHECK.SOURCE_PINS:
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n')
                self.assert_rejected('source_hash_mismatch')
                path.write_bytes(original)

    def test_missing_source_is_categorical_without_filesystem_details(self):
        (self.root / CHECK.CONFIG_PATH).unlink()
        self.assert_rejected('source_file_missing')

    def test_source_symlink_and_different_executable_are_rejected(self):
        path = self.root / CHECK.CONFIG_PATH
        path.unlink()
        path.symlink_to(ROOT / CHECK.CONFIG_PATH)
        self.assert_rejected('source_symlink_refused')
        path.unlink()
        shutil.copyfile(ROOT / CHECK.CONFIG_PATH, path)
        script = self.root / CHECK.CODE_PATH
        script.write_bytes(script.read_bytes() + b'\n')
        self.assert_rejected('executing_checker_differs_from_root')


if __name__ == '__main__':
    unittest.main()
