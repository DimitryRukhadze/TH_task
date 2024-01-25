import pytest
import json
from copy import deepcopy
from datetime import datetime

from django.utils import timezone

from apps.tasks.models import Task, Requirements, CW


CORRECT_TASK_PAYLOAD = [
    {"code": "00-IJM-001", "description": "long_str"},
    {"code": "112219-MRIP-MRBR", "description": ""},
    {"code": "AC76-160609", "description": "long_str"},
    {"code": "AC76-170424", "description": "long_str"}
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
    'task,payload,result',
    [
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M"}, 200),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "tol_pos_mos": 12}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "tol_pos_mos": 12, "tol_mos_unit": "D"}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_pos_mos": 12, "tol_mos_unit": "D"}, 200),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_pos_mos": 12}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_mos_unit": "D"}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_pos_mos": 12, "tol_neg_mos": 12, "tol_mos_unit": "D"}, 200),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_pos_mos": 12, "tol_neg_mos": 12}, 400),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_neg_mos": 12, "tol_mos_unit": "D"}, 200),
        (Task(code='00-IJM-001', description='long_str'), {"is_active": True, "due_months": 6, "due_months_unit": "M", "tol_neg_mos": 12}, 400),
    ]
)
@pytest.mark.django_db
def test_create_requirements(client, task, payload, result):
    task = task
    task.save()
    curr_payload = deepcopy(payload)
    curr_payload["task"] = task.pk

    response = client.post(
        f'/api/tasks/{task.pk}/requirements/',
        json.dumps(curr_payload),
        content_type='application/json'
    )

    assert response.status_code == result

    if response.status_code == 200:
        resp_dict = json.loads(response.content)
        curr_payload["pk"] = curr_payload["task"]
        curr_payload.pop("task")
        for key, value in resp_dict.items():
            if key in curr_payload:
                assert curr_payload[key] == value


@pytest.mark.parametrize(
    'task,requirement_1,requirement_2,payload,result',
    [
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": True},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "due_months": 5},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "due_months_unit": "M"},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": True, "tol_pos_mos": 12},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "tol_pos_mos": 12, "tol_mos_unit": "D"},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "due_months_unit": "M", "tol_pos_mos": 12},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": True, "due_months_unit": "M", "tol_mos_unit": "D"},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": True, "due_months_unit": "M", "tol_pos_mos": 12, "tol_neg_mos": 12, "tol_mos_unit": "D"},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "due_months_unit": "M", "tol_pos_mos": 12, "tol_neg_mos": 12},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": False, "due_months_unit": "M", "tol_neg_mos": 12, "tol_mos_unit": "D"},
            200
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            {"is_active": True, "due_months_unit": "M", "tol_neg_mos": 12},
            200
            ),
    ]
)
@pytest.mark.django_db
def test_update_requirements(client, task, requirement_1, requirement_2, payload, result):
    task = task
    task.save()

    req_1 = requirement_1
    req_1.task = task

    if payload.get("is_active"):
        req_1.is_active = True
    req_1.save()

    req_2 = requirement_2
    req_2.task = task
    req_2.save()

    response_2 = client.put(
        f'/api/tasks/{task.pk}/requirements/{req_2.pk}/',
        json.dumps(payload),
        content_type='application/json'
    )
    response_1 = client.get(
        f'/api/tasks/{task.pk}/requirements/{req_1.pk}/'
    )
    assert response_2.status_code == result

    updated_contents_1 = json.loads(response_1.content)
    updated_contents_2 = json.loads(response_2.content)

    for key, value in payload.items():
        if updated_contents_2.get(key) and updated_contents_1.get(key):
            assert value == updated_contents_2[key]
            assert not updated_contents_2[key] == updated_contents_1[key]
            assert not value == updated_contents_1[key]


@pytest.mark.parametrize(
    'task,requirement,result_1,result_2',
    [
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            200,
            404
            ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            200,
            404
            ),
    ]
)
@pytest.mark.django_db
def test_delete_requirements(client, task, requirement, result_1, result_2):
    task = task
    task.save()

    req = requirement
    req.task = task
    req.save()

    response = client.delete(f"/api/tasks/{task.pk}/requirements/{req.pk}/")
    assert response.status_code == result_1
    deleted_req = Requirements.objects.get(pk=req.pk)
    assert not deleted_req.is_active
    assert deleted_req.is_deleted

    response = client.delete(f"/api/tasks/{task.pk}/requirements/{req.pk}/")
    assert response.status_code == result_2
    deleted_req = Requirements.objects.get(pk=req.pk)
    assert not deleted_req.is_active
    assert deleted_req.is_deleted


@pytest.mark.parametrize(
    "task,requirement,cw_1,cw_2,expected_ndd",
    [
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            None,
            datetime.strptime("2019-07-01")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-07-01")),
            datetime.strptime("2020-01-01")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-07-01")),
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            None,
            datetime.strptime("2019-01-07")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-01-07")),
            datetime.strptime("2019-01-14")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-07-01")),
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit=D),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-07-07")),
            datetime.strptime("2020-01-01")
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit=D),
            CW(perform_date=datetime.strptime("2019-01-01")),
            CW(perform_date=datetime.strptime("2019-06-")),
            datetime.strptime("2020-01-01")
        ),
    ]
)
@pytest.mark.django_db
def test_cnt_next_due():
    pass