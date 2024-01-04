import pytest


@pytest.mark.django_db
def test_get_all_tasks(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_task(client):
    response = client.get('/api/tasks', {'task_id': 1})
    assert response.status_code == 200
