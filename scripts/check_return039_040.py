#!/usr/bin/env python3
"""Verify the pinned039 original return offline; never run a native client/model."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'ee29a58cf57783984e848df83032541c929c4658'
ARCHIVE = 'artifacts/P3_REVIEW_039_RETURN/8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b'
INDEX_SHA = '8b2bd233f9e585d4ef490dd5302ee488c14989d8badeb5ab2b3353c23c85049b'
REPORT_SHA = '8a14ad9551e6f0f1840d05889574cb7763b330046c0a51474d62ceb3926c38cc'
SOURCE_PINS = {
 'scripts/p3_focused_review_039.py':'e3ee20f21672b6a02cd3ebb54cdb44ed671c188ad3ce1f86aa5b9927b440ab3b',
 'scripts/p3_receipt_collection_032.py':'52b88345b8d707891fc33d37cd7040ca356178f400cc1396db9282951937b552',
 'scripts/p3_reviewer_session_039.py':'6ecd0c92ba7cb308d26d26157d6e9172d9e3669a0a8c140c2ce03c9c0e81e4bb',
 'configs/P3_FOCUSED_REVIEW_SCOPE_039.json':'fa94aee5482afa11f1a638ccf4759f630839cb38afaa25812746a81f428e7fd2',
 'evidence/P3_FOCUSED_REVIEW_MANIFEST_039.json':'c43d8773caee24ee1ad0b3dbc50bbb847dc02add09d87aed08575db77db64772',
}

def sha(raw): return hashlib.sha256(raw).hexdigest()

def canonical(value):
 return (json.dumps(value,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()

def object_pairs(rows):
 result={}
 for k,v in rows:
  assert k not in result, 'duplicate JSON key'
  result[k]=v
 return result

def parse(raw):
 return json.loads(raw,object_pairs_hook=object_pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))

def read(name):
 path=ROOT/name
 assert not path.is_symlink() and path.is_file(),name
 return path.read_bytes()

def load(name):
 path=ROOT/'scripts'/(name+'.py')
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return module

def verify():
 for name,digest in SOURCE_PINS.items():assert sha(read(name))==digest,name
 manifest=parse(read('evidence/P3_FOCUSED_REVIEW_MANIFEST_039.json'))
 for row in manifest['inputs']:assert sha(read(row['path']))==row['sha256'],row['path']
 archive=ROOT/ARCHIVE
 index_raw=read(ARCHIVE+'/INDEX.json');assert sha(index_raw)==INDEX_SHA
 index=parse(index_raw);inventory=parse(read(ARCHIVE+'/MANIFEST.json'))
 assert inventory['evidence_digest']==inventory['index_sha256']==INDEX_SHA
 checks=[]
 for row in inventory['files']:
  assert not row['path'].startswith('/') and '..' not in Path(row['path']).parts
  name=ARCHIVE+'/'+row['path'];raw=read(name)
  assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],name
  checks.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
 assert len(checks)==12 and len({x['path'] for x in checks})==12
 expected={Path(x['path']).relative_to(ARCHIVE).as_posix() for x in checks}|{'MANIFEST.json'}
 actual={p.relative_to(archive).as_posix() for p in archive.rglob('*') if p.is_file()}
 assert expected==actual
 present=[x for x in index['sources'] if x['status']=='PRESENT']
 missing=[x for x in index['sources'] if x['status']=='MISSING']
 assert len(present)==11 and len(missing)==1 and missing[0]['source_path'].endswith('/science_output/REVIEW_VERDICT.json')
 for row in present:
  raw=read(ARCHIVE+'/'+row['archive_path'])
  assert sha(raw)==row['sha256'] and len(raw)==row['bytes']
 run=archive/'files/delivery/P3_FOCUSED_REVIEW_039'
 raw=(run/'REPORT.json').read_bytes();assert sha(raw)==REPORT_SHA
 assert (run/'REPORT.sha256').read_bytes()==(REPORT_SHA+'\n').encode()
 report=parse(raw)
 controller=load('p3_focused_review_039')
 scope,prior,pins=controller.load_bundle()
 assert report['pins']==pins and report['authorization']==scope['authorization']
 assert sha((run/'AUTHORIZATION.md').read_bytes())==scope['authorization']['sha256']
 attempt=parse((run/'ATTEMPT.json').read_bytes())
 assert attempt['pins']==pins and attempt['reserved_native_starts']==2 and attempt['reserved_turns']==2
 collector=controller.module('p3_receipt_collection_032')
 collection=collector.collect(run,emitter_path=ROOT/'scripts/p3_reviewer_session_039.py',
  emitter_sha256=SOURCE_PINS['scripts/p3_reviewer_session_039.py'],expected_kind='P3_FINITE_REVIEWER_SESSION_039_v1',expected_modes=('synthetic','science'))
 assert collection==report['receipt_collection'] and collection['complete'] and not collection['errors']
 assert report['stages']==[collection['stages'][m] for m in ('synthetic','science')]
 syn,sci=(collection['observations'][m] for m in ('synthetic','science'))
 assert controller.admitted_synthetic(collection['stages']['synthetic']) is True
 assert controller.admitted_science(collection['stages']['science']) is False
 assert report['status']=='STOPPED_WITHOUT_COMPLETED_REVIEW' and report['reviewer_output'] is None
 assert not (run/'science_output/REVIEW_VERDICT.json').exists()
 assert sci['admission_reason']=='Unexpected reviewer dynamic tool spec'
 assert sci['thread_request_sent'] is False and sci['model_turn_request_sent'] is False and sci['verdict_submitted'] is False
 assert controller.accounting(collection['observations'],['synthetic','science'])==report['attempt_accounting']
 assert report['attempt_accounting']['cumulative_observed_native_starts']==16
 assert report['attempt_accounting']['cumulative_observed_sent_turns']==12
 for mode in ('synthetic','science'):
  stage=collection['stages'][mode]
  assert stage['host_checks']['all_noncredential_checks_pass'] is True
  assert stage['packet_before']==stage['packet_after']
  assert stage['observation']['native_process_reaped'] is True
 delivery=collection['stages']['science']['source_delivery_after']
 assert not delivery['delivery_events'] and len(delivery['missing_required_texts'])==40
 assert all(not p['full_text_delivered'] and not p['page_images_delivered'] for p in delivery['papers'])
 old_admission=controller.module('p3_reviewer_admission_022')
 broker=controller.module('p3_focused_review_broker_039')
 specs=broker.dynamic_tool_specs()
 old_admission.thread_params('gpt-5.6-sol','max','/home/afazeli2006/ARC_Independent_Lab/delivery/P3_FOCUSED_REVIEW_039/synthetic_native',
  [s for s in specs if s['name']=='read_text'],old_admission.REQUIRED_CONTROLS.copy())
 try:
  old_admission.thread_params('gpt-5.6-sol','max','/home/afazeli2006/ARC_Independent_Lab/delivery/P3_FOCUSED_REVIEW_039/science_native',specs,old_admission.REQUIRED_CONTROLS.copy())
 except old_admission.Stop as error:assert str(error)==sci['admission_reason']
 else:raise AssertionError('original scientific admission mismatch not reproduced')
 return {'kind':'P3_ORIGINAL_RETURN_VERIFICATION_040_v1','github_commit':COMMIT,
  'return_archive':ARCHIVE,'source_pins':SOURCE_PINS,'return_file_checks':checks,
  'return_manifest':{'path':ARCHIVE+'/MANIFEST.json','sha256':sha(read(ARCHIVE+'/MANIFEST.json'))},
  'source_bound_collector_reexecution_matches_original':True,'exact_controller_pins_and_stage_admission_recomputed':True,
  'all_83_frozen_release_inputs_verified':True,'original_039_report_and_receipts_modified':False,
  'scientific_verdict':'ABSENT','scientific_independent_assessment_occurred':False,
  'actual_attempt_usage':{'native_starts':2,'sent_turns':1,'completed_turn_events':0},
  'actual_cumulative_usage':{'native_starts':16,'sent_turns':12},
  '039_scope_native_ceiling_exhausted':True,'reserved_sent_turn_ceiling':13,
  'quota_or_model_absence_caused_stop':False,'local_admission_defect_reproduced_without_native_execution':True,
  'observed_boundary_breach':False,'full_boundary_or_scientific_fresh_context_proven':False,
  'current_host_privately_reinspected_here':False,'papers_or_scientific_texts_delivered_to_science_model':False,
  'native_starts_by_this_verifier':0,'model_turns_by_this_verifier':0}

if __name__=='__main__':
 print(json.dumps(verify(),indent=2,ensure_ascii=True))
