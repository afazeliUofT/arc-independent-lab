#!/usr/bin/env python3
"""Offline engineering reproductions against unchanged 027 broker/protocol.

The schema projection is a source-derived Python transcription of the applicable
subset of Codex JsonSchema serde fields, not execution of Codex or Rust.
No model, authentication, network, or native Codex process is invoked.
"""
from pathlib import Path
import base64
import copy
import hashlib
import importlib.util
import json
import re
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / 'rebuild027/repository'

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

broker = module('p3_review_broker')
protocol = module('p3_review_protocol')
SHA = lambda data: hashlib.sha256(data).hexdigest()
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
SERDE_KEYS = {'$ref', 'type', 'description', 'encrypted', 'enum', 'items', 'properties',
              'required', 'additionalProperties', 'anyOf', 'oneOf', 'allOf', '$defs', 'definitions'}

def project(schema):
    """Applicable only to these simple explicitly typed input schemas."""
    result = {key: copy.deepcopy(value) for key, value in schema.items() if key in SERDE_KEYS}
    for key in ('properties', '$defs', 'definitions'):
        if key in result:
            result[key] = {name: project(value) for name, value in result[key].items()}
    if 'items' in result:
        result['items'] = project(result['items'])
    for key in ('anyOf', 'oneOf', 'allOf'):
        if key in result:
            result[key] = [project(value) for value in result[key]]
    return result

def accepts(schema, value):
    """Validator for the finite keywords in broker.TOOL_SCHEMAS; no external lib."""
    kind = schema.get('type')
    if kind == 'object':
        if type(value) is not dict: return False
        if not set(schema.get('required', [])) <= set(value): return False
        if schema.get('additionalProperties') is False and not set(value) <= set(schema.get('properties', {})): return False
        return all(accepts(schema['properties'][key], item) for key, item in value.items())
    if kind == 'array':
        return (type(value) is list and schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', float('inf'))
                and all(accepts(schema['items'], item) for item in value))
    if kind == 'string':
        return (type(value) is str and schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', float('inf'))
                and ('pattern' not in schema or re.search(schema['pattern'], value) is not None)
                and ('enum' not in schema or value in schema['enum']))
    if kind == 'integer':
        return (type(value) in (int, float) and value % 1 == 0
                and schema.get('minimum', -float('inf')) <= value <= schema.get('maximum', float('inf')))
    raise AssertionError('Unexpected schema kind')

class Fixture:
    def __init__(self, historical=False):
        self.tmp = tempfile.TemporaryDirectory(prefix='case-', dir=HERE)
        self.root = Path(self.tmp.name)
        self.packet, self.out = self.root / 'packet', self.root / 'output'
        self.packet.mkdir(); self.out.mkdir()
        self.entries = {}
        self.add('notes/evidence.txt', 'αβγ\nfixture evidence\n'.encode(), 'text')
        self.add('pages/page1.png', PNG, 'image')
        self.add('papers/full.pdf', b'%PDF-1.4 synthetic only', 'binary')
        for path in broker.REVIEW_MANIFESTS.values():
            self.add(path, b'{"scope":"synthetic engineering only"}\n', 'text')
        self.add('PACKET_INDEX.json', (json.dumps({'files':list(self.entries.values())})+'\n').encode(), 'text')
        if historical:
            closure = json.loads((ROOT / broker.CLOSURE).read_text())
            names = {e['path'] for e in closure['view_input_files']}
            names |= {broker.RAW_DIR+'/'+n for n in closure['post_run_additional_inventory']}
            names.add(broker.CLOSURE)
            for name in names: self.add(name, (ROOT/name).read_bytes(), 'text')
        raw = (json.dumps({'schema_version':1,'files':list(self.entries.values())})+'\n').encode()
        (self.packet/'BROKER_MANIFEST.json').write_bytes(raw)
        self.pin = SHA(raw)
    def add(self, name, data, kind):
        path = self.packet/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.entries[name] = {'path':name,'sha256':SHA(data),'kind':kind}
    def open(self):
        return broker.ReviewBroker(self.packet,manifest_sha256=self.pin,output_root=self.out)
    def verdict(self):
        return {'verdict':'SUSPEND_FOR_DEPENDENCY', 'applies_to':{'scope':'SYNTHETIC ONLY', **{
            key:self.entries[path]['sha256'] for key,path in broker.REVIEW_MANIFESTS.items()}},
            'summary':'Synthetic engineering fixture; no scientific verdict.',
            'dispositions':[{'subject':s,'disposition':'unreviewed','reason':'Synthetic only.',
                'evidence':[{'path':'notes/evidence.txt','sha256':self.entries['notes/evidence.txt']['sha256']}]} for s in broker.SUBJECTS],
            'strongest_objections':[], 'missing_dependencies':['No scientific reviewer ran.'],'required_corrections':[]}
    def close(self): self.tmp.cleanup()

def request(tool,args):
    return json.dumps({'id':1,'method':'item/tool/call','params':{'tool':tool,'arguments':args,
        'callId':'call1','threadId':'thread1','turnId':'turn1'}},ensure_ascii=False).encode()

rows = []
def case(label, tool, make_args, historical=False, before=None):
    f = Fixture(historical)
    try:
        args = make_args(f)
        with f.open() as b:
            if before: before(b, f)
            direct_error = None
            try:
                result = b.dispatch(tool,args)
            except Exception as exc:
                direct_error = type(exc).__name__+': '+str(exc)
            direct_stopped = b._failed
        # Fresh instance distinguishes exact broker failure from lossy protocol.
        protocol_output = f.root / 'output_protocol'
        protocol_output.mkdir()
        with broker.ReviewBroker(f.packet, manifest_sha256=f.pin, output_root=protocol_output) as b:
            if before: before(b, f)
            p = protocol.DynamicToolBoundary(b,thread_id='thread1',turn_id='turn1')
            protocol_error = None
            try: p.handle(request(tool,args))
            except Exception as exc: protocol_error = type(exc).__name__+': '+str(exc)
            rows.append({'case':label,'tool':tool,
                'original_schema_accepts':accepts(broker.TOOL_SCHEMAS[tool],args),
                'projected_schema_accepts':accepts(project(broker.TOOL_SCHEMAS[tool]),args),
                'request_bytes':len(request(tool,args)), 'direct_error':direct_error,
                'broker_permanently_stopped':direct_stopped, 'protocol_error':protocol_error,
                'protocol_stopped':p.stopped,'receipts_retained':len(p.receipts)})
    finally: f.close()

def changed_verdict(f, field, value):
    v=f.verdict(); v[field]=value; return v

case('valid_bootstrap_read','read_text',lambda f:{'path':'PACKET_INDEX.json','offset':0,'length':10000})
case('undisclosed_upper_bound','read_text',lambda f:{'path':'PACKET_INDEX.json','offset':0,'length':200000})
case('undisclosed_lower_bound','read_text',lambda f:{'path':'PACKET_INDEX.json','offset':0,'length':0})
case('integer_numeric_representation','read_text',lambda f:{'path':'PACKET_INDEX.json','offset':0.0,'length':1000})
case('missing_required_offset','read_text',lambda f:{'path':'PACKET_INDEX.json','length':1000})
case('canonical_unknown_path','read_text',lambda f:{'path':'PACKET_INDEx.json','offset':0,'length':1000})
case('noncanonical_dot_path','read_text',lambda f:{'path':'./PACKET_INDEX.json','offset':0,'length':1000})
case('offset_past_end','read_text',lambda f:{'path':'PACKET_INDEX.json','offset':100000,'length':1000})
case('wrong_resource_kind','read_text',lambda f:{'path':'papers/full.pdf','offset':0,'length':1000})
case('valid_page_image','read_page_image',lambda f:{'path':'pages/page1.png'})
case('valid_full_file_hash','hash_file',lambda f:{'path':'papers/full.pdf'})
case('valid_fixed_audit','run_observer_audit',lambda f:{},historical=True)
case('repeated_fixed_audit','run_observer_audit',lambda f:{},historical=True,before=lambda b,f:b.dispatch('run_observer_audit',{}))
case('valid_dependency_verdict','submit_verdict',lambda f:f.verdict())
case('whitespace_only_summary','submit_verdict',lambda f:changed_verdict(f,'summary',' '))
case('undisclosed_text_length','submit_verdict',lambda f:changed_verdict(f,'summary','x'*30001))
case('missing_dispositions','submit_verdict',lambda f:changed_verdict(f,'dispositions',[]))
case('duplicate_dispositions','submit_verdict',lambda f:changed_verdict(f,'dispositions',[f.verdict()['dispositions'][0]]*6))
case('missing_audit_prerequisite','submit_verdict',lambda f:changed_verdict(f,'verdict','GO'))
case('request_vs_schema_byte_ceiling','submit_verdict',lambda f:changed_verdict(f,'strongest_objections',['x'*30000]*20))

# Pin original source and constrain source-derived projection to supplied simple
# schemas below the native compaction threshold, so compaction is not elided.
projected = {name:project(schema) for name,schema in broker.TOOL_SCHEMAS.items()}
for value in projected.values():
    assert len(json.dumps(value,separators=(',',':')).encode()) <= 5000
success_cases = {'valid_bootstrap_read','valid_page_image','valid_full_file_hash',
                 'valid_fixed_audit','valid_dependency_verdict'}
for row in rows:
    if row['case'] in success_cases:
        assert row['direct_error'] is None and row['protocol_error'] is None
        assert row['receipts_retained'] == 1 and not row['protocol_stopped']
    elif row['case'] == 'request_vs_schema_byte_ceiling':
        assert row['direct_error'] is None and row['protocol_error'] == 'ProtocolStop: Request byte limit/type'
        assert row['original_schema_accepts'] and row['request_bytes'] > protocol.MAX_REQUEST_BYTES
    else:
        assert row['direct_error'] is not None and row['broker_permanently_stopped']
        assert row['protocol_error'] == 'ProtocolStop: Broker or protocol validation failed'
        assert row['protocol_stopped'] and row['receipts_retained'] == 0
assert all(row['projected_schema_accepts'] for row in rows if row['case'] != 'missing_required_offset')
losses=[]
def lost(schema, path):
    for key in schema:
        if key not in SERDE_KEYS: losses.append({'schema_path':path,'keyword':key,'value':schema[key]})
    for name, child in schema.get('properties',{}).items(): lost(child,path+'.'+name)
    if 'items' in schema: lost(schema['items'],path+'[]')
for name,schema in broker.TOOL_SCHEMAS.items(): lost(schema,name)
report={'kind':'P3_BROKER_CONTRACT_OFFLINE_AUDIT_028_v1','science_review':False,
    'model_called':False,'native_codex_called':False,'authentication_accessed':False,
    'actual_027_failed_request_known':False,
    'source_derived_projection_not_native_execution':True,
    'broker_sha256':SHA((ROOT/'scripts/p3_review_broker.py').read_bytes()),
    'protocol_sha256':SHA((ROOT/'scripts/p3_review_protocol.py').read_bytes()),
    'projected_schemas':projected,'dropped_schema_keywords':losses,'observations':rows,
    'all_expected_outcome_assertions_passed':True,
    'historical_auditor_execution':'Only unchanged fixed arithmetic auditor, with synthetic fixture wrapper; no new experiment.'}
(HERE/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'observations':len(rows),'cases':[{k:r[k] for k in ('case','projected_schema_accepts','direct_error','protocol_error')} for r in rows]},indent=2))
