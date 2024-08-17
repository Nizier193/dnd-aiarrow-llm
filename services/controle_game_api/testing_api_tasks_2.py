import requests

BASE_URL = "http://localhost:8000"  # Замените на ваш URL

def test_execute_custom_task_with_custom_task():
    # Пример кода
    code = "def main(a, b):\n    return a + b"
    custom_task = {
        "name": "Sum",
        "difficulty": 1,
        "description": "A task to sum two numbers",
        "task_check_data": [
                    [[1, 2], 3],
                    [[-1, 1], 0],
                    [[0, 0], 0]
                ]
            }

    # Выполнение запроса к API
    response = requests.post(f"{BASE_URL}/game/execute_task", json={
        "code": code,
        "custom_task": custom_task
    })
    print(response.json())

    # Проверка статуса ответа
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Code executed successfully"
    assert "success" in response_data
    assert isinstance(response_data["errors1"], list)
    assert isinstance(response_data["errors2"], list)

def test_execute_custom_task_with_uuid():
    # Сначала получаем custom_task через get_custom_task
    response = requests.post(f"{BASE_URL}/game/generate_task")
    assert response.status_code == 200
    custom_task_data = response.json()["task"]
    print(custom_task_data)

    # Пример кода
    code = input("Введите код: ")

    # Выполнение запроса к API с task_uuid
    response = requests.post(f"{BASE_URL}/game/execute_task", json={
        "code": code,
        "task_uuid": custom_task_data["task_uuid"],  # Используем сгенерированный UUID
    })

    # Проверка статуса ответа
    assert response.status_code == 200
    response_data = response.json()
    print(response_data)
    assert response_data["message"] == "Code executed successfully"
    assert "success" in response_data
    assert isinstance(response_data["errors1"], list)
    assert isinstance(response_data["errors2"], list)

def test_execute_custom_task_without_task():
    # Пример кода
    code = "print('Hello, World!')"

    # Выполнение запроса к API без custom_task и task_uuid
    response = requests.post(f"{BASE_URL}/game/execute_task", json={
        "code": code,
    })

    # Проверка статуса ответа
    assert response.status_code == 400
    response_data = response.json()
    print(response_data)
    assert response_data["message"] == "Task not found."

test_execute_custom_task_with_uuid()

