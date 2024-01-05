import pytest
import json

from apps.tasks.models import Task


def bulk_create_tasks():
    tasks = [
        Task(code='00-IJM-001', description='long_str'),
        Task(code='112219-MRIP-MRBR', description='long_str'),
        Task(code='AC76-160609', description='long_str'),
        Task(code='AC76-170424', description='long_str')
    ]
    return Task.objects.bulk_create(tasks)


# @pytest.mark.parametrize(
#     'task_object',
#     [
#         {'code': '00-IJM-001', 'description': 'long_str'},
#         {'code': '112219-MRIP-MRBR', 'description': 'long_str'},
#         {'code': 'AC76-160609', 'description': 'long_str'},
#         {'code': 'AC76-170424', 'description': 'long_str'},
#     ]
# )
@pytest.mark.django_db
class TestTasks:
    def test_get_all_tasks(self, client):
        tasks = bulk_create_tasks()
        response = client.get('/api/tasks')
        assert response.status_code == 200
        for task in tasks:
            assert Task.objects.get(pk=task.pk)

        Task.objects.all().delete()

    @pytest.mark.parametrize(
        'task_attrs',
        [
            {'code': '00-IJM-001', 'description': 'long_str'},
            {'code': '112219-MRIP-MRBR', 'description': 'long_str'},
            {'code': 'AC76-160609', 'description': 'long_str'},
            {'code': 'AC76-170424', 'description': 'long_str'},
        ]
    )
    def test_get_task(self, client, task_attrs):
        false_response = client.get('/api/tasks', {'task_id': 300})
        false_response_data = json.loads(false_response.content.decode())
        assert not false_response_data

        task = Task.objects.create(code=task_attrs['code'], description=task_attrs['description'])
        response = client.get('/api/tasks', {'task_id': task.pk})
        response_obj_data = json.loads(response.content.decode())[0]
        assert response.status_code == 200

        for task_field in task._meta.get_fields():
            if task_field in response_obj_data.keys():
                assert task.task_field == response_obj_data[task_field]

    def test_create_tasks(self, client):
        payload = [
            {
                'code': 'RT120',
                'description': 'very long string',
            }
        ]
        response = client.post('/api/tasks/create', data=payload)
        assert response.status_code == 201

    def test_get_task_with_cw(self, client):
        response = client.get('/api/tasks/with_cws', {'task_id': 1})
        assert response.status_code == 200

    def test_get_deleted_tasks(self, client):
        response = client.get('/api/tasks/deleted')
        assert response.status_code == 200

    def test_delete_tasks(self, client):
        data = ['pk_1', 'pk_2']
        response = client.put('/api/task/delete', payload=data)
        assert response.status_code == 200

    def test_update_task(self, client):
        data = {
            'field': 'value'
        }
        response = client.put('/api/task/update', payload=data)
        assert response.status_code == 200


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
