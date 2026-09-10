"""Proposed stage evidence collection; no process launch or model authority.

Session termination and each later check are separate facts. Source cache metadata
is observed separately from the exact sealed bytes supplied to the native client.
This module is inactive until a new controller scope is explicitly approved.
"""
from pathlib import Path
import os
import stat


META_FIELDS = ('device', 'inode', 'bytes', 'mode', 'mtime_ns', 'ctime_ns')


def observe_path(path):
    """No-follow metadata only, including for the existing credential file."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Noncanonical metadata path')
    if len(path.parts) < 2:
        raise ValueError('Metadata path cannot be root')
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=fd)
            os.close(fd)
            fd = child
        info = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Metadata path type differs')
    except FileNotFoundError:
        return {'present': False}
    finally:
        os.close(fd)
    return {'present': True, 'metadata': {
        'device': info.st_dev, 'inode': info.st_ino, 'bytes': info.st_size,
        'mode': stat.S_IMODE(info.st_mode), 'mtime_ns': info.st_mtime_ns,
        'ctime_ns': info.st_ctime_ns}}


def collect_postchecks(facts, metadata, preflight, identity_path, cache_inputs):
    """Collect every independent predicate; a failed check never hides the rest.

``facts`` must come from the unchanged admitted inventory. ``metadata`` remains
an explicit dependency for the controller's source closure; no credential content
operation is delegated to it. Exception strings and cache bytes are never saved.
"""
    result = {'config_comparisons': [], 'failures': [],
              'credential_contents_checked': False,
              'cache_source_change_is_writer_attribution': False}

    def failure(code):
        row = {'phase': 'postcheck', 'code': code}
        if row not in result['failures']:
            result['failures'].append(row)

    def check(name, operation):
        try:
            value = operation()
            passed = value is True
        except Exception:
            passed = False
        result[name] = passed
        if not passed:
            failure(name)

    origins_ok = True
    for item in facts['origins']:
        if item['path'] == str(facts['auth']):
            continue
        before = {key: item[key] for key in ('present', 'metadata') if key in item}
        row = {'path': item['path'], 'before': before}
        try:
            after = observe_path(item['path'])
            row.update(after=after, observed=True, unchanged=after == before)
            row['changed_fields'] = (['present'] if after['present'] != before['present']
                else [field for field in META_FIELDS
                      if after.get('metadata', {}).get(field) != before.get('metadata', {}).get(field)])
        except Exception:
            row.update(after=None, observed=False, unchanged=False,
                       changed_fields=[], error_code='metadata_observation_failed')
        origins_ok &= row['unchanged']
        result['config_comparisons'].append(row)
    result['config_metadata_unchanged'] = bool(origins_ok)
    if not origins_ok:
        failure('config_metadata_unchanged')

    # Every source path is still observed. Changing it after capture is distinct
    # from altering the sealed input, and never identifies the responsible actor.
    try:
        observations = cache_inputs.observe_sources()
        result['cache_source_observations'] = observations
        result['cache_source_observations_collected'] = (type(observations) is list and
            len(observations) == 2 and
            {row.get('name') for row in observations if type(row) is dict} ==
                {'models_cache.json', 'cloud-config-bundle-cache.json'} and
            all(row.get('observation_succeeded') is True for row in observations))
        if not result['cache_source_observations_collected']:
            failure('cache_source_observations_unavailable')
    except Exception:
        result['cache_source_observations'] = None
        result['cache_source_observations_collected'] = False
        failure('cache_source_observations_unavailable')
    try:
        receipt = cache_inputs.verify()
        result['cache_input_verification'] = receipt
        result['cache_inputs_intact'] = (type(receipt) is dict and
                                        receipt.get('all_inputs_intact') is True)
    except Exception:
        result['cache_input_verification'] = None
        result['cache_inputs_intact'] = False
    if not result['cache_inputs_intact']:
        failure('cache_inputs_intact')

    for predicate, path_key, expected_key in (
        ('runtime_unchanged', 'runtime', 'runtime_before'),
        ('bwrap_unchanged', 'bwrap', 'bwrap_before'),
        ('host_installation_id_unchanged', 'identifier', 'identifier_before')):
        def signature_matches(path_key=path_key, expected_key=expected_key):
            observed = observe_path(facts[path_key])
            expected_meta = {k: facts[expected_key][k] for k in META_FIELDS}
            if not observed['present'] or observed['metadata'] != expected_meta:
                return False
            return preflight.signature(facts[path_key]) == facts[expected_key]
        check(predicate, signature_matches)

    def private_identity_matches():
        path = Path(identity_path)
        if not observe_path(path)['present']:
            return False
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            expected = facts['identifier_bytes']
            return os.read(fd, len(expected) + 1) == expected
        finally:
            os.close(fd)
    check('private_installation_id_matches', private_identity_matches)
    try:
        result['credential_metadata_after'] = observe_path(facts['auth'])
        result['credential_metadata_observed'] = result['credential_metadata_after']['present']
    except Exception:
        result['credential_metadata_after'] = None
        result['credential_metadata_observed'] = False
    if not result['credential_metadata_observed']:
        failure('credential_metadata_observation_failed')
    result['all_noncredential_checks_pass'] = not result['failures']
    result['source_metadata_changes_are_not_silently_waived_input_changes'] = True
    return result


def summarize_stage_failures(observation, checks, packet_after, *, mode):
    failures = []
    expected = 'VERDICT_SUBMITTED' if mode == 'science' else 'SYNTHETIC_REFUSAL_OBSERVED'
    if observation.get('status') != expected:
        failures.append({'phase': 'session', 'code': 'required_outcome_not_observed'})
    if observation.get('native_process_reaped') is not True:
        failures.append({'phase': 'cleanup', 'code': 'native_process_not_reaped'})
    failures.extend(checks.get('failures', []))
    if checks.get('all_noncredential_checks_pass') is not True and not checks.get('failures'):
        failures.append({'phase': 'postcheck', 'code': 'protected_input_check_failed'})
    if mode == 'science' and packet_after is None:
        failures.append({'phase': 'packet', 'code': 'packet_after_check_failed'})
    return failures


def finalize_stage(run, mode, observation, *, host_checks_call, packet_check_call,
                   base_fields, write_json):
    """Persist SESSION first, collect later facts independently, then persist STAGE.

Durability-write failures still propagate: an unwritten receipt is never reported
as preserved. No successful postcheck can change or select the reviewer outcome.
"""
    reserved = {'stage', 'observation', 'host_checks', 'packet_after', 'failures',
                'primary_session_reason', 'postcheck_exception_categories'}
    if mode not in ('synthetic', 'science') or reserved.intersection(base_fields):
        raise ValueError('Invalid stage receipt construction')
    run = Path(run)
    write_json(run / (mode + '_SESSION.json'), observation)
    exceptions = []
    try:
        checks = host_checks_call()
        if type(checks) is not dict:
            raise ValueError('Invalid host check receipt')
    except Exception:
        checks = {'all_noncredential_checks_pass': False,
                  'failures': [{'phase': 'postcheck', 'code': 'postcheck_collection_failed'}]}
        exceptions.append('postcheck_collection_failed')
    try:
        packet_after = packet_check_call()
    except Exception:
        packet_after = None
        exceptions.append('packet_after_check_failed')
    result = {**base_fields, 'stage': mode, 'observation': observation,
              'primary_session_reason': observation.get('primary_failure', observation.get('reason')),
              'host_checks': checks, 'packet_after': packet_after,
              'postcheck_exception_categories': exceptions,
              'failures': summarize_stage_failures(observation, checks, packet_after, mode=mode)}
    if mode == 'science' and packet_after is not None and packet_after != base_fields.get('packet_before'):
        result['failures'].append({'phase': 'packet', 'code': 'packet_receipts_differ'})
    write_json(run / (mode + '_STAGE.json'), result)
    return result
