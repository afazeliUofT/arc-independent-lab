#!/usr/bin/env python3
"""Offline lifecycle tests using generated pipe fixtures and the real broker.

No native client, model, account/credential access or network operation. Any
verdict here is an explicitly synthetic dependency-transport fixture.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import p3_reviewer_session_030 as session
import p3_event_policy_030 as policy
import test_p3_reviewer_session_028 as prior

SECRET = 'UNRETAINED_NATIVE_ITEM_SECRET_030_6dfc249a'
REPORTS = []


def notice(kind, lifecycle_phase='started', identity='item-test', **fields):
    return {'method': 'item/' + lifecycle_phase, 'params': {'threadId': 'thread-test',
        'turnId': 'turn-test', 'startedAtMs' if lifecycle_phase == 'started' else 'completedAtMs': 1,
        'item': {'type': kind, 'id': identity, **fields}}}


def dynamic(call, phase='started'):
    p = call['params']
    return notice('dynamicToolCall', phase, p['callId'], namespace=None,
        tool=p['tool'], arguments=p['arguments'],
        status='inProgress' if phase == 'started' else 'completed',
        contentItems=None, success=None if phase == 'started' else True, durationMs=None)


def compaction(identity='compact-test'):
    return [notice('contextCompaction', 'started', identity),
            notice('contextCompaction', 'completed', identity)]


def buffering(faster=None):
    return {'method': 'model/safetyBuffering/updated', 'params': {
        'threadId': 'thread-test', 'turnId': 'turn-test', 'model': 'gpt-5.6-sol',
        'useCases': [SECRET], 'reasons': [SECRET], 'showBufferingUi': True,
        'fasterModel': faster}}


class PolicyTests(unittest.TestCase):
    def events(self):
        e = session._Events('synthetic prompt')
        e.thread_id, e.turn_id = 'thread-test', 'turn-test'
        return e

    def assert_secret_absent(self, value):
        data = json.dumps(value)
        self.assertNotIn(SECRET, data)
        self.assertNotIn(hashlib.sha256(SECRET.encode()).hexdigest(), data)

    def test_complete_source_discriminant_and_notification_catalogs(self):
        source = ROOT / 'artifacts/P3_EVENT_FORENSICS/20260910_029/source/codex-rs'
        items = (source / 'app-server-protocol/src/protocol/v2/item.rs').read_text()
        enum = items.split('pub enum ThreadItem {', 1)[1].split('\n}\n', 1)[0]
        variants = re.findall(r'^    ([A-Z][A-Za-z]+)(?: \{|\()', enum, re.M)
        self.assertEqual(len(variants), 19)
        self.assertEqual(set(policy.ITEM_CLASSES), {x[0].lower() + x[1:] for x in variants})
        common = (source / 'app-server-protocol/src/protocol/common.rs').read_text()
        definitions = common.split('server_notification_definitions! {', 1)[1].split(
            '/// Server notification envelope', 1)[0]
        methods = set(re.findall(r'=> "([^"]+)"', definitions)) | {'account/login/completed'}
        self.assertEqual(len(methods), 81)
        self.assertEqual(methods, policy.KNOWN_NOTIFICATION_NAMES)

    def test_compaction_full_schema_keeps_binding_registry_and_counters(self):
        e = self.events()
        e.request_ids.add(103)
        e.started_thread_seen = e.started_turn_seen = True
        for event in compaction():
            e.accept(event)
        self.assertEqual((e.thread_id, e.turn_id), ('thread-test', 'turn-test'))
        self.assertEqual(e.request_ids, {103})
        self.assertTrue(e.started_thread_seen and e.started_turn_seen)
        self.assertFalse(e.finished_turn or e.startup_window_open)
        receipt = e.lifecycle.receipt()
        self.assertEqual(receipt['context_compactions_started'], 1)
        self.assertEqual(receipt['context_compactions_completed'], 1)
        self.assertEqual(receipt['items_still_active'], 0)
        self.assertFalse(receipt['resets_context_independent_controls'])

    def test_prior_text_and_fixed_input_types_keep_exact_origin_controls(self):
        valid = [
            ('userMessage', {'clientId': None, 'content': [{'type': 'text',
                'text': 'synthetic prompt', 'text_elements': []}]}),
            ('agentMessage', {'text': SECRET, 'phase': 'final',
                'memoryCitation': None, 'delivery': None}),
            ('reasoning', {'summary': [SECRET], 'content': [SECRET]}),
            ('functionCallOutput', {'name': 'test_sync_tool',
                'namespace': 'functions', 'output': SECRET}),
        ]
        for kind, fields in valid:
            e = self.events()
            e.accept(notice(kind, **fields))
            e.accept(notice(kind, 'completed', **fields))
            self.assertEqual(e.lifecycle.receipt()['items_completed'], 1)
            self.assert_secret_absent(e.lifecycle.receipt())
        invalid = [
            notice('userMessage', clientId=None,
                content=[{'type': 'text', 'text': SECRET}]),
            notice('agentMessage', text=SECRET, memoryCitation={'entries': [SECRET]}),
            notice('functionCallOutput', name='exec_command', namespace='functions', output=SECRET),
            notice('reasoning', summary=SECRET),
        ]
        for event in invalid:
            e = self.events()
            with self.assertRaises(session.Stop): e.accept(event)
            self.assert_secret_absent([e.event_failure, e.last_event_observation])

    def test_all_twelve_prohibited_effect_classes_record_exact_known_category(self):
        prohibited = [k for k, v in policy.ITEM_CLASSES.items() if v.startswith('refused_')]
        self.assertEqual(len(prohibited), 12)
        for kind in prohibited:
            e = self.events()
            # Discriminant test, deliberately not a claim of full prohibited schemas.
            with self.subTest(kind=kind), self.assertRaises(session.Stop):
                e.accept(notice(kind, secret=SECRET))
            self.assertEqual(e.last_event_observation['item_type'], kind)
            self.assertEqual(e.last_event_observation['phase'], 'started')
            self.assertEqual(e.event_failure['code'], policy.ITEM_CLASSES[kind])
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_unknown_and_malformed_types_never_echo_unknown_values(self):
        for kind in (SECRET, [], None, True):
            e = self.events()
            with self.subTest(kind_type=type(kind).__name__), self.assertRaises(session.Stop):
                e.accept(notice(kind))
            self.assertEqual(e.last_event_observation['item_type'], 'unknown')
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_foreign_or_malformed_ids_cannot_hide_known_rejected_type(self):
        base = notice('contextCompaction')
        for path, value in ((('threadId',), SECRET), (('turnId',), None),
                (('item', 'id'), ''), (('item', 'id'), 5), (('item', 'id'), 'x\n'),
                (('item', 'id'), 'x' * 257), (('item', 'id'), SECRET + '\u0080')):
            e = self.events()
            event = copy.deepcopy(base)
            target = event['params']
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path, value_type=type(value).__name__), self.assertRaises(session.Stop):
                e.accept(event)
            self.assertEqual(e.last_event_observation['item_type'], 'contextCompaction')
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_compaction_extra_fields_and_missing_timestamp_stop(self):
        variants = [notice('contextCompaction', hidden=SECRET), notice('contextCompaction')]
        del variants[1]['params']['startedAtMs']
        for event in variants:
            e = self.events()
            with self.assertRaises(session.Stop):
                e.accept(event)
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_replayed_start_completion_or_changed_type_stop(self):
        cases = [
            [notice('contextCompaction'), notice('contextCompaction')],
            compaction() + [notice('contextCompaction', 'completed', 'compact-test')],
            [notice('contextCompaction', 'completed')],
            [notice('contextCompaction'), notice('reasoning', 'completed')],
            compaction() + [notice('contextCompaction', identity='compact-test')],
        ]
        for events in cases:
            e = self.events()
            with self.assertRaises(session.Stop):
                for event in events:
                    e.accept(event)

    def test_plan_text_deltas_require_active_plan_without_tool_authority(self):
        e = self.events()
        start = notice('plan', text=SECRET)
        e.accept(start)
        delta = {'method': 'item/plan/delta', 'params': {'threadId': 'thread-test',
            'turnId': 'turn-test', 'itemId': 'item-test', 'delta': SECRET}}
        e.accept(delta)
        e.accept(notice('plan', 'completed', text=SECRET))
        self.assertEqual(e.lifecycle.receipt()['dynamic_callbacks_observed'], 0)
        with self.assertRaises(session.Stop):
            e.accept(delta)
        self.assert_secret_absent([e.last_event_observation, e.event_failure, e.lifecycle.receipt()])

    def test_broker_callback_requires_matching_original_dynamic_start(self):
        call = prior.fixtures.tool_call(101, session.SYNTHETIC_READ)
        for mutation in ('missing', 'tool', 'arguments', 'callId', 'namespace', 'replay'):
            e = self.events()
            if mutation != 'missing':
                e.accept(dynamic(call))
            params = copy.deepcopy(call['params'])
            if mutation == 'tool': params['tool'] = 'hash_file'
            if mutation == 'arguments': params['arguments']['length'] = 99
            if mutation == 'callId': params['callId'] = SECRET
            if mutation == 'namespace': params['namespace'] = SECRET
            if mutation == 'replay': e.callback(params)
            with self.subTest(mutation=mutation), self.assertRaises(session.Stop):
                e.callback(params)
            self.assert_secret_absent(e.event_failure)

    def test_dynamic_completion_needs_callback_and_registry_survives_compaction(self):
        e = self.events()
        call = prior.fixtures.tool_call(101, session.SYNTHETIC_READ)
        e.accept(dynamic(call))
        with self.assertRaises(session.Stop):
            e.accept(dynamic(call, 'completed'))
        e = self.events()
        e.accept(dynamic(call))
        e.callback(call['params'])
        for event in compaction(): e.accept(event)
        e.accept(dynamic(call, 'completed'))
        self.assertEqual(e.lifecycle.receipt()['dynamic_callbacks_observed'], 1)
        with self.assertRaises(session.Stop): e.callback(call['params'])

    def test_snapshot_is_not_replayed_lifecycle_event(self):
        e = self.events()
        for event in compaction(): e.accept(event)
        before = e.lifecycle.receipt()
        snapshot = {'id': 'turn-test', 'status': 'completed',
            'items': [{'id': 'compact-test', 'type': 'contextCompaction'}]}
        e.turn(snapshot, expected='turn-test')
        self.assertEqual(before, e.lifecycle.receipt())
        with self.assertRaises(session.Stop):
            e.turn({**snapshot, 'items': [{'id': 'compact-test', 'type': 'plan', 'text': SECRET}]})

    def test_existing_turn_replay_and_resolution_replay_remain_terminal(self):
        e = self.events()
        turn = {'method': 'turn/started', 'params': {'threadId': 'thread-test',
            'turn': {'id': 'turn-test', 'status': 'inProgress', 'items': []}}}
        e.accept(turn)
        for event in compaction(): e.accept(event)
        with self.assertRaises(session.Stop): e.accept(turn)
        e = self.events()
        e.request_ids.add(1)
        resolution = {'method': 'serverRequest/resolved', 'params': {
            'threadId': 'thread-test', 'requestId': 1}}
        e.accept(resolution)
        with self.assertRaises(session.Stop): e.accept(resolution)

    def test_unreviewed_notification_families_stay_terminal_with_known_names(self):
        for method in ('thread/compacted', 'turn/plan/updated', 'model/rerouted',
                       'rawResponse/completed', SECRET):
            e = self.events()
            with self.assertRaises(session.Stop):
                e.accept({'method': method, 'params': {'threadId': 'thread-test',
                    'turnId': 'turn-test', 'payload': SECRET}})
            self.assertEqual(e.last_event_observation['method'],
                method if method in policy.KNOWN_NOTIFICATION_NAMES else 'unknown')
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_safety_buffering_metadata_is_bound_but_cannot_select_alternative_model(self):
        e = self.events()
        e.model, e.effort = 'gpt-5.6-sol', 'max'
        e.request_ids.add(101)
        for event in [buffering(SECRET), *compaction(), buffering()]:
            e.accept(event)
        self.assertEqual((e.model, e.effort), ('gpt-5.6-sol', 'max'))
        self.assertEqual(e.request_ids, {101})
        receipt = e.lifecycle.receipt()['safety_buffering_metadata']
        self.assertEqual(receipt, {'notifications_admitted': 2,
            'last_recommendation_present': False, 'recommendation_ever_present': True,
            'alternative_model_selected': False, 'raw_metadata_saved_or_hashed': False})
        self.assert_secret_absent([e.last_event_observation, e.lifecycle.receipt()])

    def test_safety_buffering_malformed_and_foreign_metadata_stops(self):
        for key, value in (
                ('threadId', SECRET), ('turnId', SECRET), ('model', SECRET),
                ('showBufferingUi', 1), ('useCases', SECRET), ('reasons', [True]),
                ('fasterModel', True),
                ('reasons', ['\ud800']), (SECRET, SECRET)):
            e = self.events()
            e.model = 'gpt-5.6-sol'
            event = buffering()
            event['params'][key] = value
            with self.subTest(field=key), self.assertRaises(session.Stop):
                e.accept(event)
            self.assertEqual(e.lifecycle.receipt()['safety_buffering_metadata']['notifications_admitted'], 0)
            self.assert_secret_absent([e.last_event_observation, e.event_failure, e.lifecycle.receipt()])

    def test_safety_buffering_passive_payload_within_frame_has_no_invented_field_caps(self):
        e = self.events()
        e.model = 'gpt-5.6-sol'
        event = buffering(SECRET * 40)
        event['params']['useCases'] = [SECRET * 40] * 80
        event['params']['reasons'] = []
        event['params']['showBufferingUi'] = False
        e.accept(event)
        self.assertEqual(e.lifecycle.receipt()['safety_buffering_metadata']['notifications_admitted'], 1)
        self.assertEqual(e.model, 'gpt-5.6-sol')
        self.assert_secret_absent([e.last_event_observation, e.lifecycle.receipt()])

    def test_unknown_nonstring_method_is_refused_without_diagnostic_exception(self):
        for method in ([SECRET], {SECRET: SECRET}, None, True):
            e = self.events()
            with self.assertRaises(session.Stop):
                e.accept({'method': method, 'params': {}})
            self.assertEqual(e.last_event_observation['method'], 'unknown')
            self.assert_secret_absent([e.last_event_observation, e.event_failure])

    def test_item_ceiling_is_monotonic_through_compaction(self):
        e = self.events()
        with mock.patch.object(policy, 'MAX_ITEMS', 2):
            for event in compaction(): e.accept(event)
            for event in compaction('compact-2'): e.accept(event)
            with self.assertRaises(session.Stop):
                e.accept(notice('contextCompaction', identity='compact-3'))
        self.assertEqual(e.event_failure['code'], 'item_count_ceiling')


class TransportTests(unittest.TestCase):
    setUp = prior.fixtures.SessionTests.setUp
    tearDown = prior.fixtures.SessionTests.tearDown

    def execute(self, *, verdict_expected=False, mode='science', cache_inputs=None, child_prefix=''):
        child = self.root / 'offline_responder_030.py'
        child.write_text(child_prefix + prior.CHILD)
        fixture = self.root / 'fixture_030.json'
        fixture.write_text(json.dumps(self.fixture))
        with session.broker_module.ReviewBroker(self.packet,
                manifest_sha256=self.manifest_sha, output_root=self.output) as broker:
            report = session.run_session({'argv': [sys.executable, '-I', '-B', str(child), str(fixture)]},
                self.run, self.requested, broker, mode=mode, prompt='synthetic prompt',
                wall_seconds=10, max_calls=12, expected_binding=prior.BINDING if mode == 'science' else None,
                cache_inputs=cache_inputs)
        self.assertTrue(report['native_process_reaped'])
        self.assertEqual(report['verdict_submitted'], verdict_expected)
        self.assertNotIn(SECRET, json.dumps(report))
        if not verdict_expected: self.assertEqual(list(self.output.iterdir()), [])
        REPORTS.append({'test': self.id(), 'engineering_fixture_only': True, 'observation': report})
        return report

    def test_sealed_descriptors_reach_transport_child_after_source_overwrite(self):
        cache_home = self.root / 'cache_home' / '.codex'
        cache_home.mkdir(parents=True)
        source = cache_home / 'models_cache.json'
        raw = b'{"fixture":"sealed synthetic cache"}'
        source.write_bytes(raw)
        call = self.verdict_call()
        self.fixture['after']['turn/start'] = [*compaction(), dynamic(call), call]
        self.fixture['after_read'] = []
        with session.cache_module.capture_cache_inputs(cache_home,
                auth_metadata={'device': 0, 'inode': 0}) as cache_inputs:
            source.write_bytes(b'{"fixture":"concurrent host update"}')
            fd = cache_inputs.pass_fds[0]
            prefix = ('import os, hashlib\nassert hashlib.sha256(os.pread(' + str(fd) +
                ', 4096, 0)).hexdigest() == ' + repr(hashlib.sha256(raw).hexdigest()) + '\n')
            report = self.execute(verdict_expected=True, cache_inputs=cache_inputs, child_prefix=prefix)
            self.assertTrue(report['cache_input_descriptors_verified'])
            self.assertEqual(report['requests_sent'].count('turn/start'), 1)
            self.assertTrue(cache_inputs.verify()['all_inputs_intact'])

    def test_closed_snapshot_refuses_before_any_child_or_turn(self):
        cache_home = self.root / 'cache_home' / '.codex'
        cache_home.mkdir(parents=True)
        cache_inputs = session.cache_module.capture_cache_inputs(cache_home,
            auth_metadata={'device': 0, 'inode': 0})
        cache_inputs.close()
        with session.broker_module.ReviewBroker(self.packet,
                manifest_sha256=self.manifest_sha, output_root=self.output) as broker:
            with mock.patch.object(session.subprocess, 'Popen', side_effect=AssertionError('Must not launch')):
                report = session.run_session({'argv': ['unused-fixture-command']}, self.run,
                    self.requested, broker, mode='science', prompt='synthetic prompt',
                    wall_seconds=10, max_calls=12, expected_binding=prior.BINDING,
                    cache_inputs=cache_inputs)
        self.assertFalse(report['client_started'])
        self.assertFalse(report['model_turn_request_sent'])
        self.assertEqual(report['status'], 'STOPPED_WITHOUT_VERDICT')

    def verdict_call(self, number=104):
        manifest = json.loads((self.packet / 'BROKER_MANIFEST.json').read_bytes())
        hashes = {}
        for name, path in session.broker_module.REVIEW_MANIFESTS.items():
            data = b'{"scope":"SYNTHETIC ENGINEERING FIXTURE ONLY"}\n'
            target = self.packet / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
            manifest['files'].append({'path': path, 'sha256': hashes[name], 'kind': 'text'})
        raw = json.dumps(manifest).encode()
        (self.packet / 'BROKER_MANIFEST.json').write_bytes(raw)
        self.manifest_sha = hashlib.sha256(raw).hexdigest()
        verdict = {'verdict': 'SUSPEND_FOR_DEPENDENCY',
            'applies_to': {'scope': 'SYNTHETIC ENGINEERING FIXTURE ONLY', **hashes},
            'summary': 'Synthetic lifecycle transport fixture; no independent scientific review.',
            'dispositions': [{'subject': subject, 'disposition': 'synthetic dependency',
                'reason': 'No scientific model called.', 'evidence': [{'path': 'CANARY.txt',
                'sha256': manifest['files'][0]['sha256']}]} for subject in session.broker_module.SUBJECTS],
            'strongest_objections': [], 'missing_dependencies': ['Synthetic fixture only'],
            'required_corrections': []}
        call = prior.fixtures.tool_call(number, verdict)
        call['params']['tool'] = 'submit_verdict'
        return call

    def test_extended_lifecycle_then_real_broker_dependency_transport(self):
        bad = prior.fixtures.tool_call(101, session.SYNTHETIC_INVALID_READ)
        read = prior.fixtures.tool_call(102, session.SYNTHETIC_READ)
        final = self.verdict_call(103)
        plan = [notice('plan', identity='plan-test', text=SECRET),
            {'method': 'item/plan/delta', 'params': {'threadId': 'thread-test',
                'turnId': 'turn-test', 'itemId': 'plan-test', 'delta': SECRET}},
            notice('plan', 'completed', 'plan-test', text=SECRET)]
        self.fixture['after']['turn/start'] = [dynamic(bad), bad]
        self.fixture['after_read'] = []
        self.fixture['after_response'] = {
            '101': [dynamic(bad, 'completed'), buffering(SECRET), *compaction(), *plan, dynamic(read), read],
            '102': [dynamic(read, 'completed'), *compaction('compact-second'), buffering(), dynamic(final), final]}
        report = self.execute(verdict_expected=True)
        self.assertEqual(report['status'], 'VERDICT_SUBMITTED', report.get('reason'))
        self.assertEqual(report['recoverable_input_errors'], 1)
        self.assertEqual(report['server_requests_dispatched'], 3)
        self.assertEqual(report['requests_sent'].count('turn/start'), 1)
        self.assertEqual(report['native_item_lifecycle']['context_compactions_completed'], 2)
        self.assertEqual(report['native_item_lifecycle']['items_still_active'], 1)
        self.assertEqual(report['native_item_lifecycle']['dynamic_callbacks_observed'], 3)
        self.assertEqual(report['native_item_lifecycle']['safety_buffering_metadata']['notifications_admitted'], 2)
        self.assertIsNone(report['native_event_failure'])
        self.assertIsNone(report['primary_failure'])
        self.assertEqual((self.output / session.broker_module.VERDICT_NAME).stat().st_mode & 0o777, 0o400)

    def test_compaction_cannot_reset_eight_argument_error_ceiling(self):
        calls = [prior.fixtures.tool_call(n, session.SYNTHETIC_INVALID_READ) for n in range(101, 110)]
        self.fixture['after']['turn/start'] = [dynamic(calls[0]), calls[0]]
        self.fixture['after_read'] = []
        self.fixture['after_response'] = {str(call['id']): [dynamic(call, 'completed'),
            *compaction('compact-' + str(i)), dynamic(calls[i + 1]), calls[i + 1]]
            for i, call in enumerate(calls[:-1])}
        report = self.execute()
        self.assertEqual(report['recoverable_input_errors'], 8)
        self.assertEqual(report['failed_broker_calls'], 9)
        self.assertEqual(report['native_item_lifecycle']['context_compactions_completed'], 8)
        self.assertEqual(report['broker_boundary_failure']['code'], 'boundary.input_error_ceiling')
        self.assertEqual(report['requests_sent'].count('turn/start'), 1)

    def test_synthetic_actual_refusal_witness_survives_compaction(self):
        invalid = prior.fixtures.tool_call(101, session.SYNTHETIC_INVALID_READ)
        read = prior.fixtures.tool_call(102, session.SYNTHETIC_READ)
        denied = prior.fixtures.tool_call(103, session.SYNTHETIC_FORBIDDEN)
        self.fixture['after']['turn/start'] = [dynamic(invalid), invalid]
        self.fixture['after_read'] = []
        self.fixture['after_response'] = {
            '101': [dynamic(invalid, 'completed'), *compaction(), dynamic(read), read],
            '102': [dynamic(read, 'completed'), dynamic(denied), denied]}
        report = self.execute(mode='synthetic')
        self.assertEqual(report['status'], 'SYNTHETIC_REFUSAL_OBSERVED')
        self.assertTrue(report['synthetic_argument_error_observed'])
        self.assertTrue(report['synthetic_allowed_read_observed'])
        self.assertTrue(report['observed_refusal'])
        self.assertEqual(report['broker_boundary_failure']['code'], 'boundary.resource_path')

    def test_exact_known_failure_before_verdict_keeps_output_absent(self):
        self.fixture['after']['turn/start'] = [*compaction(), notice('commandExecution', secret=SECRET)]
        self.fixture['after_read'] = []
        report = self.execute()
        self.assertEqual(report['native_event_failure']['code'], 'refused_native_effect')
        self.assertEqual(report['last_native_event_observation']['item_type'], 'commandExecution')
        self.assertEqual(report['last_native_event_observation']['phase'], 'started')
        self.assertTrue(report['last_native_event_observation']['thread_matches'])
        self.assertEqual(report['server_requests_dispatched'], 0)

    def test_cleanup_failure_does_not_overwrite_first_lifecycle_failure(self):
        self.fixture['after']['turn/start'] = [notice('commandExecution', secret=SECRET)]
        self.fixture['after_read'] = []
        original = session.metadata._stop_process
        def reaped_but_report_failed(*args):
            self.assertTrue(original(*args))
            return False
        # Unlike execute(), this branch deliberately records cleanup false after
        # actually reaping the fixed local responder; no native process exists.
        child = self.root / 'offline_cleanup_030.py'
        child.write_text(prior.CHILD)
        fixture = self.root / 'fixture_cleanup_030.json'
        fixture.write_text(json.dumps(self.fixture))
        with session.broker_module.ReviewBroker(self.packet,
                manifest_sha256=self.manifest_sha, output_root=self.output) as broker:
            with mock.patch.object(session.metadata, '_stop_process', side_effect=reaped_but_report_failed):
                report = session.run_session({'argv': [sys.executable, '-I', '-B', str(child), str(fixture)]},
                    self.run, self.requested, broker, mode='science', prompt='synthetic prompt',
                    wall_seconds=10, max_calls=12, expected_binding=prior.BINDING)
        self.assertEqual(report['reason'], 'Native lifecycle policy refused')
        self.assertEqual(report['primary_failure']['layer'], 'session')
        self.assertEqual(report['additional_failures'], [{
            'layer': 'cleanup', 'reason': 'Native process cleanup was not verified'}])
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertNotIn(SECRET, json.dumps(report))


if __name__ == '__main__':
    unittest.main()
