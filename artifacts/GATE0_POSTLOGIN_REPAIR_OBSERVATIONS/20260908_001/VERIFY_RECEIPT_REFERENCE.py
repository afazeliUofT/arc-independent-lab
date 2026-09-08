"""Verify supplied public receipt without invoking a native process or touching laptop paths."""
import pathlib,json,hashlib,datetime,importlib.util
R=pathlib.Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
raw=(R.parent/'upload/REPORT(6).json').read_bytes(); d=json.loads(raw)
spec=importlib.util.spec_from_file_location('metadata',R/'scripts/gate0_postlogin_metadata.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);scope,pins=mod.load_bundle()
assert sha(raw)=='ab6b731d21a3e161e43e33b6db011db93037030e56d8bd40bfbd50cd2070b9c6'
assert set(d)==mod.REPORT_KEYS and d['kind']==mod.REPORT_KIND and d['pins']==pins
prior=json.loads((R/mod.PRIOR_REPORT_PATH).read_bytes())
oldrun=scope['canonical_project']+'/delivery/'+mod.PRIOR_RUN_NAME
newrun=scope['canonical_project']+'/delivery/'+mod.RUN_NAME
expected_plan=json.loads(json.dumps(prior['mount_plan']).replace(oldrun,newrun))
assert d['mount_plan']==expected_plan
assert d['origin_inventory']==prior['origin_inventory']
assert d['cache_origins']==prior['cache_origins']
assert d['network_inputs']==prior['network_inputs']
for k in ['host_config_metadata_unchanged','host_cache_metadata_unchanged','host_runtime_unchanged','host_bwrap_unchanged','host_installation_id_unchanged','private_installation_id_matches']:assert d[k] is True
for k in ['model_requested','unattended_model_use_authorized','credential_contents_opened_hashed_or_copied_by_parent','hosted_chatgpt_allowance_verified','model_entitlement_verified','full_reviewer_boundary_verified','managed_policy_closure_verified','raw_native_logs_or_protocol_in_report']:assert d[k] is False
assert d['formal_verdict'] is None
obs=d['observation'];steps=['initialize','config/read','configRequirements/read','account/read','account/rateLimits/read','model/list']
assert obs['requests_sent']==steps and obs['responses']==[{'method':m,'received':True,'success':True} for m in steps]
assert obs['status']=='OBSERVED_POSTLOGIN_METADATA_ONLY' and obs['native_process_reaped'] is True and obs['client_started'] is True
assert obs['server_requests_dispatched']==0 and obs['thread_or_model_request_sent'] is False and obs['login_config_write_or_credit_operation_sent'] is False
assert obs['live_rate_limits_response_received'] is True
controls=obs['effective_config']['controls']
for k,v in controls.items():
 if k in ['tools.update_plan.enabled','tools.experimental_request_user_input.enabled']:continue
 assert v['present'] is True and v['equals_requested'] is True,k
assert obs['account_configuration']['projected_tool_controls']['all_two_controls_verified_false'] is True
assert d['synthetic_boundary']==mod.reuse_boundary({'bwrap_before':{'sha256':scope['bwrap_sha256']}},prior)
archive=R/'artifacts/GATE0_POSTLOGIN_REPAIR_OBSERVATIONS/20260908_001'
p=R/'evidence/GATE0_POSTLOGIN_REPAIR_017_OBSERVATION_REVIEW.json'
assert not archive.exists() and not p.exists()
archive.mkdir(parents=True)
(archive/'REPORT.json').write_bytes(raw);(archive/'SHA256SUMS').write_text(sha(raw)+'  REPORT.json\n')
rec={'kind':'GATE0_POSTLOGIN_REPAIR_017_OBSERVATION_REVIEW_v1','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'report_path':str((archive/'REPORT.json').relative_to(R)),'report_sha256':sha(raw),'published_code_commit':'e0cd916249990c1a5993a8adefba12c893f9c60d','approval_commit':'6cae5d3c8f1ac3ed2745415924eb478ee53e5951','schema_and_driver_pins_match':True,'launch_plan_matches_prior_verified_plan_with_only_run_directory_substitution':True,'all_fixed_rpc_responses_successful':True,'reported_host_checks_pass':True,'credential_metadata_unchanged':d['auth_metadata_before']==d['auth_metadata_after'],'credential_contents_checked':False,'native_process_reaped':True,'exit_minus15_is_parent_cleanup':obs['client_exit_code']==-15,'synthetic_boundary_reused_not_reexecuted':True,'account_kind':obs['contained_account']['account_kind'],'reported_plan_type':obs['contained_account']['reported_plan_type'],'live_codex_rate_limit_endpoint_response':True,'codex_rate_limit_snapshot':obs['rate_limits'],'catalog_observation':obs['model_catalog'],'model_names_discarded_by_our_literal_filter':True,'full_reviewer_boundary_verified':False,'formal_verdict':None,'unattended_model_use_authorized':False,'rerun_completed_operation_needed':False,'interpretation':'Accept successful user-supplied bounded metadata receipt; not independent remote attestation. Codex meter applies to its named bucket only. Account/read(false) is cached; successful rateLimits RPC gives separate live endpoint evidence. Model/list omitted hidden entries and may use cached metadata; literal absence is not model unavailability. Corrected native parser observed timestamp envelope successfully.'}
p.write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'accepted':True,'receipt_sha256':sha(raw),'review_sha256':sha(p.read_bytes())}))
