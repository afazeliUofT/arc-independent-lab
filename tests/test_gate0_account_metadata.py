"""Real synthetic pipe tests and receipt refusal; no Codex/model/network executes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

m = load('gate0_account_metadata')
p = load('gate0_client_preflight')

CHILD = r'''
import json,sys
expected=['initialize','config/read','configRequirements/read','account/read']
index=0
for line in sys.stdin:
 q=json.loads(line)
 if 'id' not in q: continue
 assert q['method']==expected[index];index+=1
 if q['method']=='account/read':
  assert q['params']=={'refreshToken':False}
  r={'requiresOpenaiAuth':True,'account':{'type':'chatgpt','email':'SECRET_EMAIL','planType':'pro'},'unexpected':'SECRET_TOKEN'}
 elif q['method']=='config/read':
  r={'config':{'cli_auth_credentials_store':'file','features':{'plugins':False},'secret':'SECRET_CONFIG'},'origins':{},'layers':[]}
 elif q['method']=='configRequirements/read':r={'requirements':None}
 else:r={'userAgent':'synthetic'}
 print(json.dumps({'id':q['id'],'result':r}),flush=True)
'''

class AccountMetadataCases(unittest.TestCase):
    def test_enumerations_and_no_refresh_request_match_exact_embedded_interface(self):
        outer=json.loads((ROOT/'artifacts/GATE0_CODEX_INTERFACE/20260907_001/schemas/experimental.json').read_bytes())
        response=json.loads(outer['v2/GetAccountResponse.json'])
        self.assertEqual(set(m.PLAN_TYPES),set(response['definitions']['PlanType']['enum']))
        kinds={a['properties']['type']['enum'][0] for a in response['definitions']['Account']['oneOf']}
        self.assertEqual(set(m.ACCOUNT_KINDS),kinds)
        request=json.loads(outer['v2/GetAccountParams.json'])
        self.assertEqual(request['properties']['refreshToken']['type'],'boolean')

    def test_real_transport_only_four_requests_no_refresh_no_raw_secrets(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'delivery',prefix='account-test-') as d:
            result=p.observe({'argv':[sys.executable,'-I','-B','-c',CHILD]},Path(d),{'features.plugins':False},account_status=True)
        self.assertEqual(result['requests_sent'],['initialize','config/read','configRequirements/read','account/read'])
        self.assertEqual(result['status'],'OBSERVED_CONTAINED_ACCOUNT_METADATA_ONLY')
        self.assertEqual(result['contained_account']['account_kind'],'chatgpt')
        self.assertEqual(result['account_configuration']['configured_backend'],'file')
        self.assertNotIn('SECRET',json.dumps(result))
        self.assertFalse(result['contained_account']['authoritative_allowance_observed'])
        self.assertFalse(result['thread_or_model_request_sent'])

    def test_absent_account_is_only_contained_not_host_logout(self):
        r=m.safe_account({'requiresOpenaiAuth':True,'account':None})
        self.assertFalse(r['account_present'])
        self.assertFalse(r['host_login_status_verified'])
        self.assertFalse(r['live_authentication_verified'])

    def test_error_records_only_numeric_code_and_fixed_categories(self):
        child="import json; print(json.dumps({'id':1,'error':{'code':-32000,'message':'keyring credential SECRET_TOKEN'}}),flush=True)"
        with tempfile.TemporaryDirectory(dir=ROOT/'delivery',prefix='account-test-') as d:
            r=p.observe({'argv':[sys.executable,'-I','-B','-c',child]},Path(d),{},account_status=True)
        self.assertEqual(r['status'],'STOPPED_WITHOUT_REVIEW')
        self.assertEqual(r['protocol_error']['code'],-32000)
        self.assertTrue(r['protocol_error']['categories_observed']['keyring'])
        self.assertNotIn('SECRET',json.dumps(r))

    def test_unknown_account_provider_and_plan_do_not_leak_or_authorize(self):
        for value in ('SECRET',{'a':'SECRET'},None,True):
            r=m.safe_account({'account':{'type':value,'email':'SECRET','planType':'SECRET'},'requiresOpenaiAuth':'SECRET'})
            self.assertFalse(r['response_shape_recognized'])
            self.assertNotIn('SECRET',json.dumps(r))
        r=m.safe_account({'requiresOpenaiAuth':True,'account':{'type':'chatgpt','planType':'SECRET'}})
        self.assertFalse(r['reported_plan_type_recognized'])
        self.assertIsNone(r['reported_plan_type'])

    def test_backend_default_is_labelled_inference_and_unknowns_redacted(self):
        for value in ('SECRET',{},None,False):
            r=m.safe_account_config({'config':{'cli_auth_credentials_store':value},'layers':[],'origins':{}})
            self.assertIsNone(r['configured_backend'])
            self.assertTrue(r['default_is_source_inference_not_runtime_attestation'])
            self.assertNotIn('SECRET',json.dumps(r))

    def receipt(self,run):
        r={'model_called_by_protocol':False,'formal_verdict':None,
           'driver_sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in m.DRIVER_NAMES}}
        raw=json.dumps(r).encode();(run/'REPORT.json').write_bytes(raw)
        (run/'REPORT.sha256').write_text(hashlib.sha256(raw).hexdigest()+'\n')
        return r

    def test_repeated_completed_step_returns_same_report_without_subprocess(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=ROOT/'delivery',prefix='account-test-') as d:
            run=Path(d);self.receipt(run)
            with patch.object(p.subprocess,'Popen',side_effect=AssertionError('Must not execute')):
                self.assertEqual(m.existing_report(run,p),run/'REPORT.json')
                self.assertEqual(m.existing_report(run,p),run/'REPORT.json')

    def test_partial_tampered_or_different_driver_receipt_stops(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'delivery',prefix='account-test-') as d:
            run=Path(d)
            with self.assertRaises(OSError): m.existing_report(run,p)
            r=self.receipt(run);(run/'REPORT.json').write_text('{}')
            with self.assertRaises(p.Stop):m.existing_report(run,p)
            r=self.receipt(run);r['driver_sources']={};raw=json.dumps(r).encode()
            (run/'REPORT.json').write_bytes(raw);(run/'REPORT.sha256').write_text(hashlib.sha256(raw).hexdigest()+'\n')
            with self.assertRaises(p.Stop):m.existing_report(run,p)

    def test_symlinked_receipt_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'delivery',prefix='account-test-') as d:
            run=Path(d);self.receipt(run);(run/'REPORT.json').rename(run/'other.json');(run/'REPORT.json').symlink_to(run/'other.json')
            with self.assertRaises(p.Stop):m.existing_report(run,p)

if __name__=='__main__':unittest.main(verbosity=2)
