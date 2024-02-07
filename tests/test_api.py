import pytest
import json
from copy import deepcopy
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.utils import timezone

from apps.tasks.models import Task, Requirements, CW
from apps.tasks.interval_maths import cnt_next_due


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


MATH_TESTS = [
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            None,
            "2019-07-01",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            "2020-01-01",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='M'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            None,
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            None,
            "2019-01-07",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-01-07", "%Y-%m-%d")),
            "2019-01-13",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=False, due_months=6, due_months_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-01", "%Y-%m-%d")),
            None,
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            "2020-01-01",
            -12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            "2020-01-01",
            12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            "2019-12-19",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            "2020-01-01",
            -12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-07-13", "%Y-%m-%d")),
            "2020-01-13",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-19", "%Y-%m-%d")),
            "2020-01-01",
            12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            "2020-01-01",
            -31
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            "2020-01-01",
            30
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            "2019-12-01",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            "2020-01-01",
            -31
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-01", "%Y-%m-%d")),
            "2020-02-01",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=1, tol_mos_unit="M"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-06-01", "%Y-%m-%d")),
            "2020-01-01",
            30
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.91, tol_neg_mos=20.25, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-08", "%Y-%m-%d")),
            "2020-01-01",
            -38
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.91, tol_neg_mos=20.25, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-05-25", "%Y-%m-%d")),
            "2020-01-01",
            37
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.91, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-08", "%Y-%m-%d")),
            "2020-01-01",
            -38
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_pos_mos=20.91, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-05-25", "%Y-%m-%d")),
            "2019-11-25",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=20.25, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-08-08", "%Y-%m-%d")),
            "2020-02-08",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=6, due_months_unit='M', tol_neg_mos=20.25, tol_mos_unit="P"),
            CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2019-05-25", "%Y-%m-%d")),
            "2020-01-01",
            37
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=30, due_months_unit='D', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-03-14", "%Y-%m-%d")),
            "2020-04-01",
            -12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=80, due_months_unit='D', tol_pos_mos=12, tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-04-09", "%Y-%m-%d")),
            "2020-07-10",
            12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-18", "%Y-%m-%d")),
            "2021-01-14",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-11", "%Y-%m-%d")),
            "2021-01-26",
            -12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-18", "%Y-%m-%d")),
            "2021-01-26",
            12
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_neg_mos=12, tol_mos_unit='D'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-11", "%Y-%m-%d")),
            "2021-02-07",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12.25, tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            "2021-01-26",
            22
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12.25, tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            "2021-01-26",
            -22
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            "2021-01-26",
            -22
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_pos_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            "2021-01-04",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-08-21", "%Y-%m-%d")),
            "2021-02-17",
            None
        ),
        (
            Task(code='00-IJM-001', description='long_str'),
            Requirements(is_active=True, due_months=180, due_months_unit='D', tol_neg_mos=12.25, tol_mos_unit='P'),
            CW(perform_date=datetime.strptime("2020-02-01", "%Y-%m-%d")),
            CW(perform_date=datetime.strptime("2020-07-08", "%Y-%m-%d")),
            "2021-01-26",
            22
        ),
    ]


def bulk_tasks(payload):
    return [Task(**fields) for fields in payload]


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
        )[0].values()
    print(response_body_values)
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
    )

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
    print("FAILED TO RESPOND")

    assert response.status_code == 200
    updated_task_attrs = json.loads(response.content)

    for field, value in updated_task_attrs.items():
        if field in obj_attrs.keys():
            assert value == obj_attrs[field]


@pytest.mark.parametrize(
    'task_update',
    [
        {"description": 3209867},
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
    'payload,result',
    [
        ({"perform_date": "2020-01-01"}, 201),
        ({"perform_date": "2030-01-01"}, 400),
        ({"perform_date": "2020-01-01"}, 201)
    ]
)
@pytest.mark.django_db
def test_create_cw_for_task(client, payload, result):

    task = Task.objects.create(code='00-IJM-001', description='long_str')

    response = client.post(
        f'/api/tasks/{task.pk}/cws/',
        json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == result

    if response.status_code == 201:
        new_cw_date = datetime.strptime(payload["perform_date"], "%Y-%m-%d") - relativedelta(days=30)

        new_response = client.post(
            f'/api/tasks/{task.pk}/cws/',
            json.dumps({"perform_date": datetime.strftime(new_cw_date, "%Y-%m-%d")}),
            content_type='application/json'
        )

        assert json.loads(new_response.content).get("message") == "Perfrom date is before or equal previous CW"


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

    print(json.loads(response.content))

    assert response.status_code == result

    if response.status_code == 200:
        resp_dict = json.loads(response.content)
        for key, value in resp_dict.items():
            if key in curr_payload:
                print(key, curr_payload[key])
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
    "task,requirement,cw_1,cw_2,expected_ndd,adj",
    MATH_TESTS
)
@pytest.mark.django_db
def test_cnt_next_due(client, task, requirement, cw_1, cw_2, expected_ndd, adj):
    task = task
    task.save()

    req = requirement
    req.task = task
    req.save()

    next_due_date = ''

    if cw_1:
        cw_1.task = task
        cw_1.save()
        cnt_next_due(task.pk)
        response = client.get(f'/api/tasks/{task.pk}/cws/')
        content = json.loads(response.content)
        next_due_date = content['items'][-1]['next_due_date']

    if cw_2:
        cw_2.task = task
        cw_2.save()
        cnt_next_due(task.pk)
        response = client.get(f'/api/tasks/{task.pk}/cws/')
        content = json.loads(response.content)
        next_due_date = content['items'][-1]['next_due_date']

    assert next_due_date == expected_ndd


@pytest.mark.parametrize(
    "task,requirement,cw_1,cw_2,expected_ndd,adj",
    MATH_TESTS
)
@pytest.mark.django_db
def test_cnt_adj(client, task, requirement, cw_1, cw_2, expected_ndd, adj):
    task = task
    task.save()

    req = requirement
    req.task = task
    req.save()

    if cw_1:
        cw_1.task = task
        cw_1.save()
        cnt_next_due(task.pk)
        response = client.get(f'/api/tasks/{task.pk}/cws/')
        content = json.loads(response.content)
        cw_adj = content['items'][-1]['adj_mos']

    if cw_2:
        cw_2.task = task
        cw_2.save()
        cnt_next_due(task.pk)
        response = client.get(f'/api/tasks/{task.pk}/cws/')
        content = json.loads(response.content)
        cw_adj = content['items'][-1]['adj_mos']

    assert cw_adj == adj


@pytest.mark.parametrize(
        "task,requirement,cw_1,cw_2,expected",
        [
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=6000),
                7000.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7000),
                8000.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7040),
                8000.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=6960),
                8000.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=6960),
                8000.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7060),
                8060.0,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7040.01),
                8040.01,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7040),
                8000,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=40, tol_neg_hrs=40, tol_hrs_unit="H"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=6059.99),
                7059.99,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=10.98, tol_neg_hrs=10.98, tol_hrs_unit="P"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=7109.8),
                8000,
            ),
            (
                Task(code='00-IJM-001', description='long_str'),
                Requirements(is_active=True, due_hrs=1000, tol_pos_hrs=10.98, tol_neg_hrs=10.98, tol_hrs_unit="P"),
                CW(perform_date=datetime.strptime("2019-01-01", "%Y-%m-%d"), perform_hrs=6000),
                CW(perform_date=datetime.strptime("2020-01-01", "%Y-%m-%d"), perform_hrs=6890.2),
                8000,
            ),
        ]
)
@pytest.mark.django_db
def test_cnt_due_hrs(client, task, requirement, cw_1, cw_2, expected):
    task = task
    task.save()

    requirement = requirement
    requirement.task = task
    requirement.save()

    cw_1 = cw_1
    cw_1.task = task
    cw_1.save()

    cnt_next_due(task.pk)

    if cw_2:
        cw_2.task = task
        cw_2.save()

    cnt_next_due(task.pk)

    response = client.get(f'/api/tasks/{task.pk}/cws/')
    print(json.loads(response.content))
    latest_cw = json.loads(response.content)["items"][-1]

    assert response.status_code == 200
    assert latest_cw["next_due_hrs"] == expected
