import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

def post_request(endpoint, data=None):
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    return response.json()

def get_request(endpoint, data=None):
    response = requests.get(f"{BASE_URL}{endpoint}")
    return response.json()

def print_response(method_name, response):
    print(f"\n--- {method_name} ---")
    print(json.dumps(response, indent=2))
    print("-" * 40)

def test_game_api():
    # Создание игры
    game_data = {"n_ai": 2, "n_players": 2}
    create_game_response = post_request("/game/create", game_data)
    print_response("Create Game", create_game_response)
    admin_uuid = create_game_response["admin_uuid"]

    # Добавление игроков
    players = []

    # Игрок 1 (генеративно)
    player1_data = {
        "generate_auto": False,
        "is_ai": True,
        "name": "Nizier", "character_class": "Wizard", "race": "Elf",
        "backstory": "A curious elf wizard from the Enchanted Forest."
    }
    player1_response = post_request("/player/add", player1_data)
    players.append(player1_response["uuid"])
    print_response("Add Player 1 (Auto-generated)", player1_response)

    # Игрок 2 (вручную)
    player2_data = {
        "generate_auto": False,
        "is_ai": False,
        "name": "Alice", "character_class": "Wizard", "race": "Elf",
        "backstory": "A curious elf wizard from the Enchanted Forest."
    }
    player2_response = post_request("/player/add", player2_data)
    players.append(player2_response["uuid"])
    print_response("Add Player 2 (Manual)", player2_response)

    # Создание приключения
    adventure_data = {
        "admin_uuid": admin_uuid,
        "dm_intro": "You find yourselves in a mysterious forest...",
        "create_image": False,
        "create_music": False
    }
    create_adventure_response = post_request("/game/create_adventure", adventure_data)
    print_response("Create Adventure", create_adventure_response)

    # Цикл ходов (3 раза)
    for turn in range(30):
        print(f"\n=== Turn {turn + 1} ===")

        # Получение состояния игры
        game_state = post_request("/game/get_state")
        print_response("Get Game State", game_state)

        # Ходы игроков
        for player_uuid in players:  # Human players
            # Получение информации о ходе
            turn_params = post_request("/game/get_turn_params", {"player_uuid": player_uuid})
            print_response(f"Get Turn Params for Player {player_uuid}", turn_params)

            # Ход игрока (симуляция)
            player_turn_data = {
                "player_uuid": player_uuid,
            }
            player_turn_response = post_request("/game/make_turn_ai", player_turn_data)
            print_response(f"Make Turn for Player {player_uuid}", player_turn_response)

            available_voices = get_request("/game/get_voices").get("voices") # list of voices
            print_response(f"Available Voices for Player {player_uuid}", available_voices)

            tts_response = post_request("/game/make_tts_ai", {"player_uuid": player_uuid, "voice_name": random.choice(available_voices)})
            print_response(f"Make TTS for Player {player_uuid}", tts_response)

        # Ход ДМ
        dm_turn_response = post_request("/game/make_turn_dm")
        print_response("Make DM Turn", dm_turn_response)

        # Генерация картинки
        image_response = post_request("/game/make_image", {"scene_description": "A mysterious forest with ancient ruins"})
        print_response("Generate Image", image_response)

        # Генерация музыки
        music_response = post_request("/game/make_music", {"scene_description": "Eerie and mystical forest ambiance"})
        print_response("Generate Music", music_response)

        time.sleep(1)  # Небольшая пауза между ходами

    # Удаление игры
    delete_game_response = post_request("/game/delete", {"admin_uuid_passed": admin_uuid})
    print_response("Delete Game", delete_game_response)

test_game_api()

delete_game_response = post_request("/game/delete_game", {"admin_uuid_passed": "023d2bc8-ec41-4357-b535-9820bffd781c"})
print_response("Delete Game", delete_game_response)

