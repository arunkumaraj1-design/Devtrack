import json
import os
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTERS_FILE = os.path.join(BASE_DIR, 'reporters.json')
ISSUES_FILE = os.path.join(BASE_DIR, 'issues.json')


def _load(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return []


def _save(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def reporters_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            reporter = Reporter(data.get('id'), data.get('name'), data.get('email'), data.get('team'))
            reporter.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        arr = _load(REPORTERS_FILE)
        arr.append(reporter.to_dict())
        _save(REPORTERS_FILE, arr)
        return JsonResponse(reporter.to_dict(), status=201)

    if request.method == 'GET':
        qid = request.GET.get('id')
        arr = _load(REPORTERS_FILE)
        if qid:
            try:
                rid = int(qid)
            except ValueError:
                return JsonResponse({'error': 'Invalid id'}, status=400)
            for r in arr:
                if r.get('id') == rid:
                    return JsonResponse(r, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)
        return JsonResponse(arr, safe=False, status=200)

    return HttpResponseNotAllowed(['GET', 'POST'])


def issues_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        priority = data.get('priority')
        try:
            if priority == 'critical':
                issue = CriticalIssue(data.get('id'), data.get('title'), data.get('description'), data.get('status'), priority, data.get('reporter_id'))
            elif priority == 'low':
                issue = LowPriorityIssue(data.get('id'), data.get('title'), data.get('description'), data.get('status'), priority, data.get('reporter_id'))
            else:
                issue = Issue(data.get('id'), data.get('title'), data.get('description'), data.get('status'), priority, data.get('reporter_id'))
            issue.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        arr = _load(ISSUES_FILE)
        arr.append(issue.to_dict())
        _save(ISSUES_FILE, arr)
        response_data = issue.to_dict()
        response_data['message'] = issue.describe()
        return JsonResponse(response_data, status=201)

    if request.method == 'GET':
        qid = request.GET.get('id')
        qstatus = request.GET.get('status')
        arr = _load(ISSUES_FILE)
        if qid:
            try:
                iid = int(qid)
            except ValueError:
                return JsonResponse({'error': 'Invalid id'}, status=400)
            for it in arr:
                if it.get('id') == iid:
                    return JsonResponse(it, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)
        if qstatus:
            filtered = [it for it in arr if it.get('status') == qstatus]
            return JsonResponse(filtered, safe=False, status=200)
        return JsonResponse(arr, safe=False, status=200)

    return HttpResponseNotAllowed(['GET', 'POST'])
