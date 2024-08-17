import requests
import json  # Добавлено для работы с json

BASE_URL = "http://localhost:8000"

def setup_game():
    # Создание игры
    create_game_response = requests.post(f"{BASE_URL}/game/create", json={"n_ai": 1, "n_players": 1})
    print("Create Game Response:", json.dumps(create_game_response.json(), indent=4))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert create_game_response.status_code == 200
    admin_uuid = create_game_response.json()["admin_uuid"]

    # Создание приключения
    create_adventure_response = requests.post(f"{BASE_URL}/game/create_adventure", 
                                              json={"admin_uuid": admin_uuid, "dm_intro": "Test adventure", "create_image": False, "create_music": False})
    print("Create Adventure Response:", json.dumps(create_adventure_response.json(), indent=4))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert create_adventure_response.status_code == 200

    return admin_uuid

def teardown_game(admin_uuid):
    # Удаление игры
    delete_game_response = requests.post(f"{BASE_URL}/game/delete", json={"admin_uuid": admin_uuid})
    assert delete_game_response.status_code == 200

def test_task_api():
    admin_uuid = setup_game()

    # Тест /game/get_all_tasks
    get_all_tasks_response = requests.post(f"{BASE_URL}/game/get_all_tasks")
    print("Get All Tasks Response:", json.dumps(get_all_tasks_response.json(), indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert get_all_tasks_response.status_code == 200
    all_tasks_data = get_all_tasks_response.json()
    print("Get All Tasks Response:", json.dumps(all_tasks_data, indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert "tasks" in all_tasks_data
    assert isinstance(all_tasks_data["tasks"], list)

    # Тест /game/get_custom_task
    get_custom_task_response = requests.post(f"{BASE_URL}/game/get_task")
    print("Custom Task Response:", json.dumps(get_custom_task_response.json(), indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert get_custom_task_response.status_code == 200
    custom_task_data = get_custom_task_response.json()
    print("Custom Task Response:", json.dumps(custom_task_data, indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert "task" in custom_task_data
    assert isinstance(custom_task_data["task"], dict)
    assert "task_uuid" in custom_task_data["task"]

    task_uuid = custom_task_data["task"]["task_uuid"]

    # Тест /game/execute_code
    execute_code_response = requests.post(f"{BASE_URL}/game/execute_code", 
                                          json={"task_uuid": task_uuid, "code": input("Enter code: ")})
    print("Execute Code Response:", json.dumps(execute_code_response.json(), indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert execute_code_response.status_code == 200
    execute_code_data = execute_code_response.json()
    print("Execute Code Response:", json.dumps(execute_code_data, indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert "success" in execute_code_data
    assert "errors1" in execute_code_data
    assert "errors2" in execute_code_data

    # Тест /game/get_hint
    get_hint_response = requests.post(f"{BASE_URL}/game/get_hint", 
                                      json={"task_uuid": task_uuid, "code": "# Incomplete code"})
    print("Hint Data:", json.dumps(get_hint_response.json(), indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert get_hint_response.status_code == 200
    hint_data = get_hint_response.json()
    print("Hint Data:", json.dumps(hint_data, indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert "hint" in hint_data

    # Тест /game/explain_solution
    explain_solution_response = requests.post(f"{BASE_URL}/game/explain_solution", 
                                              json={"task_uuid": task_uuid, "code": input("Enter code: ")})
    print("Explanation Data:", json.dumps(explain_solution_response.json(), indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert explain_solution_response.status_code == 200
    explanation_data = explain_solution_response.json()
    print("Explanation Data:", json.dumps(explanation_data, indent=4, ensure_ascii=False))  # Изменено
    print("=" * 40)  # Добавлено разделение
    assert "explanation" in explanation_data

    teardown_game(admin_uuid)

if __name__ == "__main__":
    test_task_api()
    print("All tests passed successfully!")