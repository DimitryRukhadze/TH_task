import pytest
import json
import datetime

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
    response_body_values = json.loads(
        response_single_task.content
        )['items'][0].values()

    for value in task_attrs[0].values():
        assert value in response_body_values


@pytest.mark.django_db
def test_fail_create_cw_for_deleted_task(client):
    perf_date = timezone.now().date()
    task = Task.objects.create(code='00-IJM-001', description='long_str')

    today_cws_payload = {"perform_date": perf_date.strftime("%Y-%m-%d")}
    task.delete()

    response = client.post(
        f'/api/tasks/{task.pk}/cws/',
        json.dumps(today_cws_payload),
        content_type='application/json'
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_bulk_create_tasks(client):
    response_bulk_tasks = client.post(
        '/api/tasks/',
        json.dumps(CORRECT_TASK_PAYLOAD),
        content_type='application/json'
    )
    assert response_bulk_tasks.status_code == 200

    created_tasks = json.loads(
        response_bulk_tasks.content
    )['items']

    for init_payload, res_payload in zip(CORRECT_TASK_PAYLOAD, created_tasks):
        for key in init_payload.keys():
            if key in res_payload.keys():
                assert init_payload[key] == res_payload[key]


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
    response = client.delete(
        f'/api/tasks/{task.pk}/',
    )
    assert response.status_code == 404


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


@pytest.mark.parametrize(
        'due_months,perf_date,res_date',
        [
            (6, '2023-12-01', '2024-06-01'),
            (5, '2023-12-01', '2024-05-01'),
            (4, '2023-12-01', '2024-04-01'),
        ]
)
@pytest.mark.django_db
def test_due_date_count_for_cw_create(client, due_months, perf_date, res_date):

    task = Task.objects.create(
        code='00-IJM-001',
        description='long_str',
        due_months=due_months
    )

    cw_payload = {
        "task": task.pk,
        "perform_date": perf_date
    }
    response = client.post(
        f'/api/tasks/{task.pk}/cws/',
        json.dumps(cw_payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert json.loads(response.content)['next_due_date'] == res_date


@pytest.mark.parametrize(
        'due_months,perf_date,update_date,res_date',
        [
            (6, '2023-12-01', '2024-01-01', '2024-07-01'),
            (5, '2023-12-01', '2024-01-01', '2024-06-01'),
            (4, '2023-12-01', '2024-01-01', '2024-05-01'),
        ]
)
@pytest.mark.django_db
def test_due_date_count_for_cw_update(
        client,
        due_months,
        perf_date,
        update_date,
        res_date
        ):

    task = Task.objects.create(
        code='00-IJM-001',
        description='long_str',
        due_months=due_months
    )

    cw_payload = {
        "task": task,
        "perform_date": perf_date
    }

    cw = CW.objects.create(**cw_payload)

    update_payload = {
        "perform_date": update_date
    }

    response = client.put(
        f'/api/tasks/{task.pk}/cws/{cw.pk}/',
        json.dumps(update_payload),
        content_type='application/json'
    )
    print(json.loads(response.content))

    assert response.status_code == 200
    assert json.loads(response.content)['next_due_date'] == res_date


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

    for obj_repr in json.loads(response.content)["items"]:
        assert obj_repr["task"]["pk"] == task.pk


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


@pytest.mark.parametrize(
    'num,result',
    [
        (0, 400),
        (-1, 200),
        (1, 400)
    ]
)
@pytest.mark.django_db
def test_update_cw(client, num, result):
    init_cw_date = datetime.date(2023, 12, 12)

    task = Task.objects.create(code='00-IJM-001', description='long_str')
    today_cws_attrs = {
        "task": task,
        "perform_date": init_cw_date
        }

    cw = CW.objects.create(**today_cws_attrs)

    update_payload = {
        'perform_date': (
            cw.perform_date - timezone.timedelta(days=num)
            ).strftime("%Y-%m-%d")
        }

    response = client.put(
        f'/api/tasks/{task.pk}/cws/{cw.pk}/',
        json.dumps(update_payload),
        content_type='application/json'
    )

    assert response.status_code == result
    updated_cw = json.loads(response.content)
    if response.status_code == 200:
        assert updated_cw['perform_date'] == update_payload['perform_date']


@pytest.mark.django_db
def test_get_tasks_with_next_due_date():
    today = timezone.now().date()
    next_due_date = datetime.date(2023, 12, 12)

    task = Task.objects.create(code='00-IJM-001', description='long_str')
    cw_payload = {
            "task": task,
            "perform_date": today,
            "next_due_date": next_due_date
        }

    cw = CW.objects.create(**cw_payload)

    assert cw.next_due_date == cw_payload["next_due_date"]

    cw.next_due_date = None
    cw.save()

    assert not cw.next_due_date
