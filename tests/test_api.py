import pytest
import json

from django.utils import timezone

from apps.tasks.models import Task, CW


CORRECT_TASK_PAYLOAD = [
    {"code": "00-IJM-001", "description": "long_str"},
    {"code": "112219-MRIP-MRBR", "description": "long_str", "due_months": 0},
    {"code": "AC76-160609", "description": "long_str", "due_months": 6},
    {"code": "AC76-170424", "description": "long_str", "due_months": 0}
]


WRONG_TASK_PAYLOAD = [
    {"code": 1, "description": "long_str"},
    {"code": "112219-MRIP-MRBR", "description": 22},
    {"code": "AC76-160609", "description": "long_str", "due_months": "6"},
]


def bulk_tasks(payload):
    tasks = [Task(**fields) for fields in payload]
    return tasks


@pytest.mark.django_db
def test_get_all_tasks(client):
    tasks = bulk_tasks(CORRECT_TASK_PAYLOAD)
    Task.objects.bulk_create(tasks)

    response = client.get('/api/tasks/')
    assert response.status_code == 200
    for task in tasks:
        assert Task.objects.get(pk=task.pk)


@pytest.mark.parametrize(
    'task_attrs',
    CORRECT_TASK_PAYLOAD
)
@pytest.mark.django_db
def test_get_task(client, task_attrs):

    task = Task.objects.create(
        code=task_attrs['code'],
        description=task_attrs['description']
        )

    response = client.get(f'/api/tasks/{task.pk}/')
    false_response = client.get(f'/api/tasks/{task.pk + 100}/')
    response_obj_data = json.loads(response.content)
    assert response.status_code == 200
    assert false_response.status_code == 404
    assert task.pk == response_obj_data['pk']

    for task_field in task._meta.get_fields():
        if task_field in response_obj_data.keys():
            assert task.task_field == response_obj_data[task_field]


@pytest.mark.parametrize(
    'task_attrs',
    CORRECT_TASK_PAYLOAD
)
@pytest.mark.django_db
def test_create_task(client, task_attrs):
    task_attrs = [task_attrs]
    response_single_task = client.post(
        '/api/tasks/',
        json.dumps(task_attrs),
        content_type='application/json'
    )

    assert response_single_task.status_code == 200
    response_body_values = json.loads(response_single_task.content)[0].values()

    for value in task_attrs[0].values():
        assert value in response_body_values


@pytest.mark.django_db
def test_bulk_create_tasks(client):
    response_bulk_tasks = client.post(
        '/api/tasks/',
        json.dumps(CORRECT_TASK_PAYLOAD),
        content_type='application/json'
    )
    assert response_bulk_tasks.status_code == 200


@pytest.mark.parametrize(
    'task_attrs',
    WRONG_TASK_PAYLOAD
)
@pytest.mark.django_db
def test_create_tasks_fails(client, task_attrs):
    response_single_task = client.post(
        '/api/tasks/',
        json.dumps(WRONG_TASK_PAYLOAD[:1]),
        content_type='application/json'
    )
    assert response_single_task.status_code == 422

    response_bulk_tasks = client.post(
        '/api/tasks/',
        json.dumps(WRONG_TASK_PAYLOAD[1:]),
        content_type='application/json'
    )
    assert response_bulk_tasks.status_code == 422


@pytest.mark.parametrize(
    'task_update',
    [
        {"description": "updated long str"},
        {"due_months": 2},
        {"code": "112219-MRIP-MRBR"},
    ]
)
@pytest.mark.django_db
def test_update_task(client, task_update):
    obj_attrs = {"code": "00-IJM-001", "description": "long_str"}
    task = Task.objects.create(**obj_attrs)
    obj_attrs.update(task_update)

    response = client.put(
        f'/api/tasks/{task.pk}/',
        json.dumps(obj_attrs),
        content_type='application/json'
    )

    assert response.status_code == 200
    updated_task_attrs = json.loads(response.content)

    for field, value in updated_task_attrs.items():
        if field in obj_attrs.keys():
            assert value == obj_attrs[field]


@pytest.mark.parametrize(
    'task_update',
    [
        {"description": 3209867},
        {"due_months": "2"},
        {"code": 112219}
    ]
)
@pytest.mark.django_db
def test_update_task_fails(client, task_update):
    obj_attrs = {"code": "00-IJM-001", "description": "long_str"}
    task = Task.objects.create(**obj_attrs)

    obj_attrs.update(task_update)
    response = client.put(
        f'/api/tasks/{task.pk}/',
        json.dumps(task_update),
        content_type='application/json'
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    'task_attrs',
    CORRECT_TASK_PAYLOAD
)
@pytest.mark.django_db
def test_delete_task(client, task_attrs):
    task = Task.objects.create(**task_attrs)
    response = client.delete(
        f'/api/tasks/{task.pk}/',
    )
    assert response.status_code == 200
    deleted_task = Task.objects.get(pk=task.pk)
    assert task.pk == deleted_task.pk
    assert deleted_task.is_deleted


@pytest.mark.parametrize(
    'num,result',
    [
        (0, 200),
        (-1, 400),
        (1, 200)
    ]
)
@pytest.mark.django_db
def test_create_cw_for_task(client, num, result):
    today = timezone.now().date()
    perf_date = today - timezone.timedelta(days=num)

    task = Task.objects.create(code='00-IJM-001', description='long_str')

    today_cws_payload = {"perform_date": perf_date.strftime("%Y-%m-%d")}
    response = client.post(
        f'/api/tasks/{task.pk}/cws/',
        json.dumps(today_cws_payload),
        content_type='application/json'
    )

    assert response.status_code == result


@pytest.mark.django_db
def test_get_cws_for_task(client):
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)

    task = Task.objects.create(code='00-IJM-001', description='long_str')
    today_cws_payload = {'task': task, 'perform_date': today}
    past_cws_payload = {'task': task, 'perform_date': yesterday}

    bulk_cws_payload = [today_cws_payload, past_cws_payload]

    cws = [CW(**fields) for fields in bulk_cws_payload]

    CW.objects.bulk_create(cws)

    response = client.get(f'/api/tasks/{task.pk}/cws/')
    assert response.status_code == 200

    for obj_repr in json.loads(response.content):
        assert obj_repr['task']['pk'] == task.pk


@pytest.mark.django_db
def test_delete_cws(client):
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    another_prev_date = today - timezone.timedelta(days=10)

    task = Task.objects.create(code='00-IJM-001', description='long_str')
    today_cws_payload = {'task': task, 'perform_date': today}
    past_cws_payload = {'task': task, 'perform_date': yesterday}
    prev_cws_payload = {'task': task, 'perform_date': another_prev_date}

    bulk_cws_payload = [today_cws_payload, past_cws_payload, prev_cws_payload]
    cws = [CW(**fields) for fields in bulk_cws_payload]

    CW.objects.bulk_create(cws)

    for cw in cws:
        response = client.delete(f'/api/tasks/{task.pk}/cws/{cw.pk}/')
        assert response.status_code == 200
        response = client.delete(f'/api/tasks/{task.pk}/cws/{cw.pk}/')
        assert response.status_code == 404


@pytest.mark.django_db
def test_update_cw(client):
    today = timezone.now().date()

    task = Task.objects.create(code='00-IJM-001', description='long_str')
    today_cws_attrs = {
        "task": task,
        "perform_date": today
        }

    cw = CW.objects.create(**today_cws_attrs)

    update_payload = {
        'perform_date': (
            cw.perform_date - timezone.timedelta(days=1)
            ).strftime("%Y-%m-%d")
        }

    response = client.put(
        f'/api/tasks/{task.pk}/cws/{cw.pk}/',
        json.dumps(update_payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    updated_cw = json.loads(response.content)
    assert updated_cw['perform_date'] == update_payload['perform_date']
