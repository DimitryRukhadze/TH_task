import pytest
import json

from apps.tasks.models import Task


CORRECT_PAYLOAD = [
    {'code': '00-IJM-001', 'description': 'long_str'},
    {'code': '112219-MRIP-MRBR', 'description': 'long_str'},
    {'code': 'AC76-160609', 'description': 'long_str'},
    {'code': 'AC76-170424', 'description': 'long_str'}
]

WRONG_PAYLOAD = [
    {'code': 1, 'description': 'long_str'},
    {'code': '112219-MRIP-MRBR', 'description': 22},
    {'code': 'AC76-160609', 'description': 'long_str', 'due_months': '6'},
]


def bulk_tasks(payload):
    tasks = [Task(**fields) for fields in payload]
    return tasks


@pytest.mark.django_db
class TestTasks:

    def test_get_all_tasks(self, client):
        tasks = bulk_tasks(CORRECT_PAYLOAD)
        Task.objects.bulk_create(tasks)

        response = client.get('/api/tasks')
        assert response.status_code == 200
        for task in tasks:
            assert Task.objects.get(pk=task.pk)

        Task.objects.all().delete()

    @pytest.mark.parametrize(
        'task_attrs',
        CORRECT_PAYLOAD
    )
    def test_get_task(self, client, task_attrs):

        task = Task.objects.create(code=task_attrs['code'], description=task_attrs['description'])

        response = client.get(f'/api/tasks/{task.pk}')
        false_response = client.get(f'/api/tasks/{task.pk + 100}')
        response_obj_data = json.loads(response.content.decode())
        assert response.status_code == 200
        assert false_response.status_code == 404
        assert task.pk == response_obj_data['pk']

        for task_field in task._meta.get_fields():
            if task_field in response_obj_data.keys():
                assert task.task_field == response_obj_data[task_field]

    def test_create_tasks(self, client):
        response_single_task = client.post('/api/tasks/', payload=CORRECT_PAYLOAD[:1])
        assert response_single_task.status_code == 201
        assert response_single_task[0] == Task.objects.get(pk=response_single_task[0].pk)

        response_bulk_tasks = client.post('/api/tasks/', payload=CORRECT_PAYLOAD)
        assert response_bulk_tasks.response == 201

        for obj in response_bulk_tasks:
            assert obj == Task.objects.get(pk=obj.pk)

    @pytest.mark.parametrize(
        'task_attrs',
        WRONG_PAYLOAD
    )
    def test_create_tasks_fails(self, client, task_attrs):
        response_single_task = client.post('/api/tasks/', payload=WRONG_PAYLOAD[:1])
        assert response_single_task.status_code == 400

        response_bulk_tasks = client.post('/api/tasks/', payload=WRONG_PAYLOAD)
        assert response_bulk_tasks.status_code == 400

    @pytest.mark.parametrize(
        'task_attrs,task_update',
        [
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'description': 'updated long str'}),
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'due_months': 2}),
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'code': '112219-MRIP-MRBR'}),
        ]
    )
    def test_update_task(self, client, task_attrs, task_update):
        task = Task.objects.create(**task_attrs)
        response = client.put(f'/api/task/{task.pk}', payload=task_update)
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
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'description': 3209867}),
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'due_months': '2'}),
            ({'code': '00-IJM-001', 'description': 'long_str'}, {'code': 112219}),
        ]
    )
    def test_update_task_fails(self, client, task_attrs, task_update):
        task = Task.objects.create(**task_attrs)
        response = client.put(f'/api/task/{task.pk}', payload=task_update)
        assert response.status_code == 400
        assert Task.objects.get(task.pk) == task

    def test_bulk_delete_tasks(self, client):
        tasks = bulk_tasks(CORRECT_PAYLOAD)
        Task.objects.bulk_create(tasks)
        response = client.delete('/api/task', payload=[task.id for task in tasks])
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'task_attrs',
        CORRECT_PAYLOAD
    )
    def test_delete_task(self, client, task_attrs):
        task = Task.objects.create(**task_attrs)
        response = client.delete(f'/api/task/{task.pk}')
        assert response.status_code == 200
        response = client.delete(f'/api/task/{task.pk}')
        assert response.status_code == 204

    def test_get_deleted_tasks(self, client):
        tasks = bulk_tasks(CORRECT_PAYLOAD)
        Task.objects.bulk_create(tasks)
        Task.objects.all().delete()

        response = client.get('/api/tasks/deleted')
        assert response.status_code == 200
        for task in tasks:
            assert Task.objects.get(pk=task.pk)


@pytest.mark.django_db
def test_get_all_cws(client):
    response = client.get('/api/cws')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_cw(client):
    response = client.get('/api/cws', {'cw_pk': 1})
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_cws_by_task(client):
    response = client.get('/api/cws/by_task', {'task_code': 'code_str'})
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_cw(client):
    payload = {
        'task': 'RT120',
        'perform_date': '2014-02-22'
    }
    response = client.post('/api/cws/create', data=payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_cws(client):

    response = client.delete('/api/cws/delete')
    assert response.status_code == 200
