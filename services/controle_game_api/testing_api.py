import requests

url = "http://localhost:8000/game/make_player_image"
data = {
    "player_description": "Имя: Герой\nКласс: Воин\nРаса: Человек\nИстория: Сражался с драконами."
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())