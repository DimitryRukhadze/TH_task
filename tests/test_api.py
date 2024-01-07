import pytest
import json

from django.utils import timezone

from apps.tasks.models import Task, CW


CORRECT_TASK_PAYLOAD = [
    {"code": "00-IJM-001", "description": "long_str"},
    {"code": "112219-MRIP-MRBR", "description": "long_str"},
    {"code": "AC76-160609", "description": "long_str", "due_months": 6},
    {"code": "AC76-170424", "description": "long_str"}
]


WRONG_TASK_PAYLOAD = [
    {"code": 1, "description": "long_str"},
    {"code": "112219-MRIP-MRBR", "description": 22},
    {"code": "AC76-160609", "description": "long_str", "due_months": "6"},
]

# Пытался перевести код тестов на эту фикстуру, но не преуспел. Из за этого использую глобальные переменные
@pytest.fixture
def correct_task_payload(scope='class'):
    task_payload = [
        {"code": "00-IJM-001", "description": "long_str"},
        {"code": "112219-MRIP-MRBR", "description": "long_str"},
        {"code": "AC76-160609", "description": "long_str"},
        {"code": "AC76-170424", "description": "long_str"}
        ]
    return task_payload


def bulk_tasks(payload):
    tasks = [Task(**fields) for fields in payload]
    return tasks


@pytest.mark.django_db
class TestTasks:

    def test_get_all_tasks(self, client, correct_task_payload):
        tasks = bulk_tasks(correct_task_payload)
        Task.objects.bulk_create(tasks)

        response = client.get('/api/tasks')
        assert response.status_code == 200
        for task in tasks:
            assert Task.objects.get(pk=task.pk)

        Task.objects.all().delete()

    @pytest.mark.parametrize(
        'task_attrs',
        CORRECT_TASK_PAYLOAD
    )
    def test_get_task(self, client, task_attrs):

        task = Task.objects.create(code=task_attrs['code'], description=task_attrs['description'])

        response = client.get(f'/api/tasks/{task.pk}')
        false_response = client.get(f'/api/tasks/{task.pk + 100}')
        response_obj_data = json.loads(response.content)
        assert response.status_code == 200
        assert false_response.status_code == 404
        assert task.pk == response_obj_data['pk']

        for task_field in task._meta.get_fields():
            if task_field in response_obj_data.keys():
                assert task.task_field == response_obj_data[task_field]

    def test_create_tasks(self, client):
        response_single_task = client.post('/api/tasks', payload=CORRECT_TASK_PAYLOAD[:1])
        assert response_single_task.status_code == 200
        assert response_single_task[0] == Task.objects.get(pk=response_single_task[0].pk)

        response_bulk_tasks = client.post('/api/tasks', payload=CORRECT_TASK_PAYLOAD[1:])
        assert response_bulk_tasks.status_code == 200

        for obj in response_bulk_tasks:
            assert obj == Task.objects.get(pk=obj.pk)

    @pytest.mark.parametrize(
        'task_attrs',
        WRONG_TASK_PAYLOAD
    )
    def test_create_tasks_fails(self, client, task_attrs):
        response_single_task = client.post('/api/tasks/', json=WRONG_TASK_PAYLOAD[:1])
        assert response_single_task.status_code == 400

        response_bulk_tasks = client.post('/api/tasks/', json=WRONG_TASK_PAYLOAD[1:])
        assert response_bulk_tasks.status_code == 400

    @pytest.mark.parametrize(
        'task_attrs,task_update',
        [
            ({"code": "00-IJM-001", "description": "long_str"}, {"description": "updated long str"}),
            ({"code": "00-IJM-001", "description": "long_str"}, {"due_months": 2}),
            ({"code": "00-IJM-001", "description": "long_str"}, {"code": "112219-MRIP-MRBR"}),
        ]
    )
    def test_update_task(self, client, task_attrs, task_update):
        task = Task.objects.create(**task_attrs)
        task_attrs.update(task_update)
        response = client.put(f'/api/task/{task.pk}', json=task_attrs)
        assert response.status_code == 200

        updated_task = Task.objects.get(task.pk)
        assert updated_task != task

        task_attrs.update(task_update)
        attr_keys = task_attrs.keys()

        for field in updated_task._meta.get_fields():
            if field in attr_keys:
                assert task.field == task_attrs[field]

    @pytest.mark.parametrize(
        'task_attrs,task_update',
        [
            ({"code": "00-IJM-001", "description": "long_str"}, {"description": 3209867}),
            ({"code": "00-IJM-001", "description": "long_str"}, {"due_months": "2"}),
            ({"code": "00-IJM-001", "description": "long_str"}, {"code": 112219}),
        ]
    )
    def test_update_task_fails(self, client, task_attrs, task_update):
        task = Task.objects.create(**task_attrs)
        response = client.put(f'/api/task/{task.pk}', payload=task_update)
        assert response.status_code == 400
        assert Task.objects.get(task.pk) == task

    def test_bulk_delete_tasks(self, client):
        tasks = bulk_tasks(CORRECT_TASK_PAYLOAD)
        Task.objects.bulk_create(tasks)
        response = client.delete('/api/task', payload=[task.id for task in tasks])
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'task_attrs',
        CORRECT_TASK_PAYLOAD
    )
    def test_delete_task(self, client, task_attrs):
        task = Task.objects.create(**task_attrs)
        response = client.delete(f'/api/task/{task.pk}')
        assert response.status_code == 200
        response = client.delete(f'/api/task/{task.pk}')
        assert response.status_code == 204

    def test_get_deleted_tasks(self, client, correct_task_payload):
        tasks = bulk_tasks(correct_task_payload)
        Task.objects.bulk_create(tasks)
        Task.objects.all().delete()

        response = client.get('/api/tasks/deleted')
        assert response.status_code == 200
        for task in tasks:
            assert Task.objects.get(pk=task.pk)

    def test_create_cws_for_task(self, client):
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)
        yesterday = today - timezone.timedelta(days=1)

        task = Task.objects.create(code='00-IJM-001', description='long_str')
        today_cws_payload = {"task": task.pk, "perform_date": today}
        past_cws_payload = {"task": task.pk, "perform_date": yesterday}
        future_cws_payload = {"task": task.pk, "perform_date": tomorrow}

        response = client.post(f'/api/tasks/{task.pk}/cws', payload=today_cws_payload)
        assert response.status_code == 200
        response = client.post(f'/api/tasks/{task.pk}/cws', payload=today_cws_payload)
        assert response.status_code == 400
        response = client.post(f'/api/tasks/{task.pk}/cws', payload=past_cws_payload)
        assert response.status_code == 200
        response = client.post(f'/api/tasks/{task.pk}/cws', payload=future_cws_payload)
        assert response.status_code == 400

    def test_get_cws_for_task(self, client):
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        task = Task.objects.create(code='00-IJM-001', description='long_str')
        today_cws_payload = {'task': task.pk, 'perform_date': today}
        past_cws_payload = {'task': task.pk, 'perform_date': yesterday.date}

        bulk_cws_payload = [today_cws_payload, past_cws_payload]

        CW.objects.bulk_create(bulk_cws_payload)

        response = client.get(f'/api/tasks/{task.pk}/cws')
        assert response.status_code == 200

        for obj_repr in json.loads(response.content):
            assert obj_repr['pk'] == task.pk

    def test_bulk_delete_cws(self, client):
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        another_prev_date = today - timezone.timedelta(days=10)

        task = Task.objects.create(code='00-IJM-001', description='long_str')
        today_cws_payload = {'task': task.pk, 'perform_date': today}
        past_cws_payload = {'task': task.pk, 'perform_date': yesterday.date}
        prev_cws_payload = {'task': task.pk, 'perform_date': another_prev_date}

        bulk_cws_payload = [today_cws_payload, past_cws_payload, prev_cws_payload]

        cws = CW.objects.bulk_create(bulk_cws_payload)

        response = client.delete(f'/api/tasks/{task.pk}/cws', payload=[cw.pk for cw in cws])
        assert response.status_code == 200
        response = client.delete(f'/api/tasks/{task.pk}/cws', payload=[cw.pk for cw in cws])
        assert response.status_code == 400

    def test_delete_cws(self, client):
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        another_prev_date = today - timezone.timedelta(days=10)

        task = Task.objects.create(code='00-IJM-001', description='long_str')
        today_cws_payload = {'task': task.pk, 'perform_date': today}
        past_cws_payload = {'task': task.pk, 'perform_date': yesterday.date}
        prev_cws_payload = {'task': task.pk, 'perform_date': another_prev_date}

        bulk_cws_payload = [today_cws_payload, past_cws_payload, prev_cws_payload]

        cws = CW.objects.bulk_create(bulk_cws_payload)

        for cw in cws:
            response = client.delete(f'/api/tasks/{task.pk}/cws/{cw.pk}')
            assert response.status_code == 200
            response = client.delete(f'/api/tasks/{task.pk}/cws/{cw.pk}')
            assert response.status_code == 400

    def test_update_cws(self, client):
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        another_prev_date = today - timezone.timedelta(days=10)

        task = Task.objects.create(code='00-IJM-001', description='long_str')
        today_cws_payload = {'task': task.pk, 'perform_date': today}
        yesterday_cws_payload = {'task': task.pk, 'perform_date': yesterday.date}
        prev_cws_payload = {'task': task.pk, 'perform_date': another_prev_date}

        bulk_cws_payload = [today_cws_payload, yesterday_cws_payload, prev_cws_payload]

        cws = CW.objects.bulk_create(bulk_cws_payload)

        for cw in cws:
            update_payload = {'perform_date': cw.perform_date - timezone.timedelta(days=1)}
            response = client.update(f'/api/tasks/{task.pk}/cws/{cw.pk}', payload=update_payload)
            assert response.status_code == 200
            assert cw.perform_date == update_payload['perform_date']
