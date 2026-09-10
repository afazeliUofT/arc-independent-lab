"""Preopened packet verifier, independent of the request dispatcher's stop flag.

This is an engineering input-integrity observer, never a scientific reviewer.
It exposes no dispatch operation and cannot reset another broker's failed state.
"""
import importlib.util
from pathlib import Path
import sys


def _original():
    name = 'p3_review_broker'
    path = Path(__file__).with_name(name + '.py').resolve()
    if name in sys.modules:
        value = sys.modules[name]
        if Path(value.__file__).resolve() != path:
            raise RuntimeError('Original packet verifier origin differs')
        return value
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


original = _original()
ERROR_CODES = {
    'Input identity changed':'input_identity_changed',
    'Resource digest mismatch':'resource_digest_mismatch',
    'Resource opening denied':'resource_opening_refused',
    'Resource changed during read':'resource_changed_during_read',
    'Packet manifest changed':'manifest_digest_mismatch',
    'Resource must be a regular file without hardlink aliases':'file_type_or_alias_refused',
    'Resource exceeds byte bound':'file_byte_limit_exceeded',
}


class PacketObserver:
    def __init__(self, packet_root, *, manifest_sha256, output_root):
        # Original constructor opens fixed input/output directories and verifies
        # all manifest bytes. This object is never passed to model transport.
        self._reader = original.ReviewBroker(packet_root,
            manifest_sha256=manifest_sha256, output_root=output_root)
        self.before = {'manifest_sha256':self._reader.manifest_sha256,
                       'files_rehashed':len(self._reader._files)}

    def verify(self):
        try:
            receipt = self._reader.verify_inputs()
            if receipt != self.before:
                raise RuntimeError('Packet observer receipt differs')
            return receipt
        except Exception as error:
            code = ERROR_CODES.get(str(error), 'packet_verification_failed') if type(error) is original.BrokerError else 'packet_verification_failed'
            return {'status':'FAILED','verified':False,'error_code':code,
                    'manifest_sha256':self.before['manifest_sha256'],
                    'files_rehashed':None, 'original_identity_baseline_preserved':True,
                    'request_dispatcher_state_reset':False,
                    'raw_path_or_exception_saved':False,'writer_identified':False}

    def close(self):
        self._reader.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
