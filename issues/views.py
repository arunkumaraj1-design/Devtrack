import json
import os
from pathlib import Path

from django.http import JsonResponse

from .models import CriticalIssue, Issue, LowPriorityIssue, Reporter


BASE_DIR = Path(__file__).resolve().parent.parent
REPORTERS_FILE = BASE_DIR / 'reporters.json'
ISSUES_FILE = BASE_DIR / 'issues.json'


class StorageError(Exception):
    """Raised when a JSON data file cannot be read or written safely."""


def _load(file_path):
    if not file_path.exists():
        return []
    try:
        with file_path.open('r', encoding='utf-8') as data_file:
            records = json.load(data_file)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise StorageError('Data store is unavailable or contains invalid JSON') from exc
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise StorageError('Data store must contain a JSON list of records')
    return records


def _save(file_path, records):
    temporary_path = file_path.with_name(f'.{file_path.name}.{os.getpid()}.tmp')
    try:
        with temporary_path.open('w', encoding='utf-8') as data_file:
            json.dump(records, data_file, indent=2, ensure_ascii=False)
            data_file.flush()
            os.fsync(data_file.fileno())
        os.replace(temporary_path, file_path)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise StorageError('Data store could not be saved') from exc


def _json_body(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not isinstance(payload, dict):
        return None, JsonResponse({'error': 'JSON body must be an object'}, status=400)
    return payload, None


def _next_id(records):
    existing_ids = [record.get('id') for record in records if isinstance(record.get('id'), int)]
    return max(existing_ids, default=0) + 1


def _query_id(value):
    try:
        record_id = int(value)
    except (TypeError, ValueError):
        return None
    return record_id if record_id > 0 else None


def _storage_error_response(exc):
    return JsonResponse({'error': str(exc)}, status=500)


def _method_not_allowed(allowed_methods):
    return JsonResponse(
        {'error': 'Method not allowed'},
        status=405,
        headers={'Allow': ', '.join(allowed_methods)},
    )


def reporters_view(request):
    if request.method == 'POST':
        data, error_response = _json_body(request)
        if error_response:
            return error_response

        try:
            reporters = _load(REPORTERS_FILE)
            reporter_id = data.get('id')
            if reporter_id is None:
                reporter_id = _next_id(reporters)
            reporter = Reporter(reporter_id, data.get('name'), data.get('email'), data.get('team'))
            reporter.validate()
            if any(record.get('id') == reporter.id for record in reporters):
                return JsonResponse({'error': 'Reporter ID already exists'}, status=409)
            reporters.append(reporter.to_dict())
            _save(REPORTERS_FILE, reporters)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except StorageError as exc:
            return _storage_error_response(exc)
        return JsonResponse(reporter.to_dict(), status=201)

    if request.method == 'GET':
        try:
            reporters = _load(REPORTERS_FILE)
        except StorageError as exc:
            return _storage_error_response(exc)
        query_id = request.GET.get('id')
        if query_id is not None:
            reporter_id = _query_id(query_id)
            if reporter_id is None:
                return JsonResponse({'error': 'Invalid id'}, status=400)
            for reporter in reporters:
                if reporter.get('id') == reporter_id:
                    return JsonResponse(reporter, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)
        return JsonResponse(reporters, safe=False, status=200)

    return _method_not_allowed(['GET', 'POST'])


def issues_view(request):
    if request.method == 'POST':
        data, error_response = _json_body(request)
        if error_response:
            return error_response

        try:
            issues = _load(ISSUES_FILE)
            reporters = _load(REPORTERS_FILE)
            issue_id = data.get('id')
            if issue_id is None:
                issue_id = _next_id(issues)
            priority = data.get('priority')
            issue_type = priority if isinstance(priority, str) else None
            issue_class = {
                'critical': CriticalIssue,
                'low': LowPriorityIssue,
            }.get(issue_type, Issue)
            issue = issue_class(
                issue_id,
                data.get('title'),
                data.get('description', ''),
                data.get('status'),
                priority,
                data.get('reporter_id'),
                data.get('created_at'),
            )
            issue.validate()
            if any(record.get('id') == issue.id for record in issues):
                return JsonResponse({'error': 'Issue ID already exists'}, status=409)
            if not any(record.get('id') == issue.reporter_id for record in reporters):
                return JsonResponse({'error': 'Reporter not found'}, status=404)
            issues.append(issue.to_dict())
            _save(ISSUES_FILE, issues)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except StorageError as exc:
            return _storage_error_response(exc)

        response_data = issue.to_dict()
        response_data['message'] = issue.describe()
        return JsonResponse(response_data, status=201)

    if request.method == 'GET':
        try:
            issues = _load(ISSUES_FILE)
        except StorageError as exc:
            return _storage_error_response(exc)

        query_id = request.GET.get('id')
        if query_id is not None:
            issue_id = _query_id(query_id)
            if issue_id is None:
                return JsonResponse({'error': 'Invalid id'}, status=400)
            for issue in issues:
                if issue.get('id') == issue_id:
                    return JsonResponse(issue, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)

        query_status = request.GET.get('status')
        if query_status is not None:
            if query_status not in Issue.ALLOWED_STATUSES:
                return JsonResponse({'error': 'Invalid status'}, status=400)
            issues = [issue for issue in issues if issue.get('status') == query_status]
        return JsonResponse(issues, safe=False, status=200)

    return _method_not_allowed(['GET', 'POST'])
