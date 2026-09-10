"""Offline proposal: finite native-item policy; no launcher or authority grant.

The source-enumerated labels below are the only native categories retained in
diagnostics. Item IDs, text, arguments and their digests never leave this class.
Pinned protocol: openai/codex 78c290807ce710180111df227df3b7a4fe845452.
"""
from __future__ import annotations

import hashlib
import json

POLICY_VERSION = "P3_EVENT_POLICY_030_OFFLINE_PROPOSAL_v1"
MAX_ITEMS = 4096
ITEM_CLASSES = {
    "userMessage": "fixed_input", "agentMessage": "text_output",
    "reasoning": "text_output", "dynamicToolCall": "broker_callback",
    "functionCallOutput": "restricted_native_output", "plan": "text_output",
    "contextCompaction": "context_lifecycle",
    "hookPrompt": "refused_instruction_source",
    "commandExecution": "refused_native_effect", "fileChange": "refused_native_effect",
    "mcpToolCall": "refused_native_effect", "collabAgentToolCall": "refused_native_effect",
    "subAgentActivity": "refused_native_effect", "webSearch": "refused_native_effect",
    "imageView": "refused_native_effect", "sleep": "refused_native_effect",
    "imageGeneration": "refused_native_effect", "enteredReviewMode": "refused_mode_change",
    "exitedReviewMode": "refused_mode_change",
}
KNOWN_NOTIFICATION_NAMES = frozenset((
    'account/login/completed', 'account/rateLimits/updated', 'account/updated',
    'app/list/updated', 'autoApprovalReview/strictReviewRequired', 'command/exec/outputDelta',
    'configWarning', 'deprecationNotice', 'error', 'externalAgentConfig/import/completed',
    'externalAgentConfig/import/progress', 'fs/changed', 'fuzzyFileSearch/sessionCompleted',
    'fuzzyFileSearch/sessionUpdated', 'guardianWarning', 'hook/completed', 'hook/started',
    'item/agentMessage/delta', 'item/autoApprovalReview/completed', 'item/autoApprovalReview/started',
    'item/commandExecution/outputDelta', 'item/commandExecution/terminalInteraction',
    'item/completed', 'item/fileChange/outputDelta', 'item/fileChange/patchUpdated',
    'item/mcpToolCall/progress', 'item/plan/delta', 'item/reasoning/summaryPartAdded',
    'item/reasoning/summaryTextDelta', 'item/reasoning/textDelta', 'item/started',
    'mcpServer/event/stream/notification', 'mcpServer/oauthLogin/completed',
    'mcpServer/startupStatus/updated', 'model/rerouted', 'model/safetyBuffering/updated',
    'model/verification', 'process/exited', 'process/outputDelta', 'project/changed',
    'rawResponse/completed', 'rawResponseItem/completed', 'remoteControl/status/changed',
    'serverRequest/resolved', 'skills/changed', 'thread/archived', 'thread/closed',
    'thread/compacted', 'thread/deleted', 'thread/environment/connected',
    'thread/environment/disconnected', 'thread/goal/cleared', 'thread/goal/updated',
    'thread/name/updated', 'thread/project/updated', 'thread/queue/changed',
    'thread/realtime/closed', 'thread/realtime/error', 'thread/realtime/item/completed',
    'thread/realtime/item/started', 'thread/realtime/item/transcript/delta',
    'thread/realtime/itemAdded', 'thread/realtime/outputAudio/delta', 'thread/realtime/sdp',
    'thread/realtime/started', 'thread/realtime/transcript/delta',
    'thread/realtime/transcript/done', 'thread/reverted', 'thread/settings/updated',
    'thread/started', 'thread/status/changed', 'thread/tokenUsage/updated',
    'thread/unarchived', 'turn/completed', 'turn/diff/updated', 'turn/moderationMetadata',
    'turn/plan/updated', 'turn/started', 'warning', 'windows/worldWritableWarning',
    'windowsSandbox/setupCompleted'))


class Violation(RuntimeError):
    """Only a fixed local code may be supplied."""


def require(condition, code):
    if not condition:
        raise Violation(code)


def identifier(value):
    return type(value) is str and 0 < len(value) <= 256 and all(32 <= ord(c) < 127 for c in value)


def known_type(item):
    kind = item.get('type') if type(item) is dict else None
    return kind if type(kind) is str and kind in ITEM_CLASSES else 'unknown'


def _strings(value):
    return type(value) is list and len(value) <= MAX_ITEMS and all(type(x) is str for x in value)


def _metadata_text(value):
    try:
        if type(value) is not str:
            return False
        value.encode('utf-8')
        return True
    except UnicodeError:
        return False


def _argument_digest(value):
    # Transient comparison only. Never exposed in diagnostic receipts.
    return hashlib.sha256(json.dumps(value, allow_nan=False, sort_keys=True,
        separators=(',', ':')).encode()).digest()


class Lifecycle:
    """One bound turn's monotonic item registry, independent of model context."""

    def __init__(self, prompt, tools):
        self.prompt, self.tools = prompt, tools
        self._items = {}
        self.counts = {}
        self.completed = 0
        self.compactions_started = self.compactions_completed = 0
        self.callbacks_observed = 0
        self.safety_buffering_metadata = {'notifications_admitted': 0,
            'last_recommendation_present': None, 'recommendation_ever_present': False,
            'alternative_model_selected': False, 'raw_metadata_saved_or_hashed': False}

    def safety_buffering(self, params, selected_model):
        require(type(params) is dict and set(params) == {'threadId', 'turnId', 'model',
            'useCases', 'reasons', 'showBufferingUi', 'fasterModel'}, 'buffering_fields_differ')
        require(type(selected_model) is str and bool(selected_model) and
            params['model'] == selected_model, 'buffering_model_differs')
        require(type(params['showBufferingUi']) is bool, 'buffering_flag_invalid')
        for key in ('useCases', 'reasons'):
            require(type(params[key]) is list and
                all(_metadata_text(value) for value in params[key]), 'buffering_metadata_bounds')
        require(params['fasterModel'] is None or _metadata_text(params['fasterModel']),
            'buffering_recommendation_bounds')
        receipt = self.safety_buffering_metadata
        receipt['notifications_admitted'] += 1
        receipt['last_recommendation_present'] = params['fasterModel'] is not None
        receipt['recommendation_ever_present'] |= params['fasterModel'] is not None

    def validate(self, item):
        require(type(item) is dict, 'item_not_object')
        require(identifier(item.get('id')), 'item_identifier_invalid')
        kind = known_type(item)
        require(kind != 'unknown', 'unknown_item_type')
        require(not ITEM_CLASSES[kind].startswith('refused_'), ITEM_CLASSES[kind])
        if kind == 'contextCompaction':
            require(set(item) == {'type', 'id'}, 'compaction_fields_differ')
        elif kind == 'plan':
            require(set(item) == {'type', 'id', 'text'} and type(item['text']) is str,
                'plan_fields_differ')
        elif kind == 'userMessage':
            content = item.get('content')
            require(set(item) <= {'type', 'id', 'clientId', 'content'} and
                item.get('clientId') is None and type(content) is list and len(content) == 1 and
                type(content[0]) is dict and set(content[0]) <= {'type', 'text', 'text_elements'} and
                content[0].get('type') == 'text' and content[0].get('text') == self.prompt and
                content[0].get('text_elements', []) == [], 'user_input_origin_differ')
        elif kind == 'agentMessage':
            require(set(item) <= {'type', 'id', 'text', 'phase', 'memoryCitation', 'delivery'} and
                type(item.get('text')) is str and item.get('memoryCitation') is None and
                item.get('delivery') in (None, 'async') and
                item.get('phase') in (None, 'commentary', 'final'), 'agent_output_origin_differ')
        elif kind == 'reasoning':
            require(set(item) <= {'type', 'id', 'summary', 'content'} and
                _strings(item.get('summary', [])) and _strings(item.get('content', [])),
                'reasoning_fields_differ')
        elif kind == 'dynamicToolCall':
            require(set(item) <= {'type', 'id', 'namespace', 'tool', 'arguments', 'status',
                'contentItems', 'success', 'durationMs'} and type(item.get('tool')) is str and
                item['tool'] in self.tools and item.get('namespace') is None and
                type(item.get('arguments')) is dict and item.get('status') in
                ('inProgress', 'completed', 'failed'), 'dynamic_authority_or_shape_differ')
        elif kind == 'functionCallOutput':
            # The native handlers remain the source-closed pair admitted in028.
            # This output is never interpreted as a command or broker outcome.
            require(set(item) <= {'type', 'id', 'name', 'namespace', 'output'} and
                item.get('name') in ('send_user_message_async', 'test_sync_tool') and
                item.get('namespace') in (None, 'functions') and 'output' in item,
                'function_output_authority_differ')
        return kind

    def item(self, item, phase):
        kind = self.validate(item)
        item_id = item['id']
        if phase == 'snapshot':
            # RPC/turn summaries describe existing items, never start new work.
            row = self._items.get(item_id)
            if row is not None:
                require(row['kind'] == kind, 'snapshot_item_type_changed')
            return
        require(phase in ('started', 'completed'), 'item_phase_invalid')
        if phase == 'started':
            require(item_id not in self._items, 'item_start_replayed')
            require(len(self._items) < MAX_ITEMS, 'item_count_ceiling')
            if kind == 'userMessage':
                require(self.counts.get(kind, 0) == 0, 'additional_user_input')
            row = {'kind': kind, 'completed': False, 'callback': False}
            if kind == 'dynamicToolCall':
                require(item['status'] == 'inProgress', 'dynamic_start_status_differ')
                row.update(tool=item['tool'], arguments_digest=_argument_digest(item['arguments']))
            self._items[item_id] = row
            self.counts[kind] = self.counts.get(kind, 0) + 1
            self.compactions_started += kind == 'contextCompaction'
        else:
            row = self._items.get(item_id)
            require(row is not None, 'item_completed_without_start')
            require(not row['completed'], 'item_completion_replayed')
            require(row['kind'] == kind, 'item_type_changed')
            if kind == 'dynamicToolCall':
                require(row['callback'] and item['tool'] == row['tool'] and
                    _argument_digest(item['arguments']) == row['arguments_digest'] and
                    item['status'] in ('completed', 'failed'), 'dynamic_completion_unwitnessed')
            row['completed'] = True
            self.completed += 1
            self.compactions_completed += kind == 'contextCompaction'

    def delta(self, params, kind):
        item_id = params.get('itemId')
        require(identifier(item_id), 'delta_item_identifier_invalid')
        row = self._items.get(item_id)
        require(row is not None and not row['completed'] and row['kind'] == kind,
            'delta_without_matching_active_item')

    def callback(self, params):
        require(type(params) is dict and identifier(params.get('callId')),
            'callback_identity_invalid')
        row = self._items.get(params['callId'])
        require(row is not None and row['kind'] == 'dynamicToolCall' and
            not row['completed'] and not row['callback'], 'callback_without_fresh_dynamic_start')
        require(params.get('tool') == row['tool'] and params.get('namespace') is None and
            type(params.get('arguments')) is dict and
            _argument_digest(params['arguments']) == row['arguments_digest'],
            'callback_differs_from_dynamic_start')
        # Consume before the broker executes, including an invalid/recoverable call.
        row['callback'] = True
        self.callbacks_observed += 1

    def receipt(self):
        return {'version': POLICY_VERSION, 'item_ceiling': MAX_ITEMS,
            'item_starts_by_known_type': dict(self.counts), 'items_completed': self.completed,
            'items_still_active': len(self._items) - self.completed,
            'context_compactions_started': self.compactions_started,
            'context_compactions_completed': self.compactions_completed,
            'dynamic_callbacks_observed': self.callbacks_observed,
            'safety_buffering_metadata': dict(self.safety_buffering_metadata),
            'metadata_size_bounded_by_protocol_frame': True,
            'resets_context_independent_controls': False,
            'raw_ids_text_arguments_or_digests_saved': False}

    def clear(self):
        self._items.clear()
