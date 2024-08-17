# DND Game API

## Описание
DND Game API предоставляет интерфейс для управления и взаимодействия с игрой Dungeons & Dragons (DND). Это API позволяет пользователям создавать игры, добавлять игроков, управлять игровыми сессиями и выполнять игровые действия. 

## Полезность
API может быть полезен для разработчиков, создающих приложения или игры, основанные на DND, а также для тех, кто хочет автоматизировать процесс игры, интегрируя его с другими системами или интерфейсами.

## Установка и развертывание локально

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL_репозитория>
   cd <папка_репозитория>
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/Mac
   venv\Scripts\activate  # Для Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите сервер:**
   ```bash
   python services/controle_game_api/main.py
   ```

5. **API будет доступен по адресу:**
   ```
   http://localhost:8000
   ```

## Описание методов API

![API Methods](readme_source/APIMETHODS.jpg)

### 1. Создание игры
- **Метод:** `POST /game/create`
- **Описание:** Создает новую игру.
- **Input:**
  ```json
  {
    "n_ai": 2,
    "n_players": 4
  }
  ```
- **Output:**
  ```json
  {
    "message": "Game created successfully",
    "admin_uuid": "some-uuid"
  }
  ```

### 2. Удаление игры
- **Метод:** `POST /game/delete`
- **Описание:** Удаляет текущую игру.
- **Input:**
  ```json
  {
    "admin_uuid": "some-uuid"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Game deleted successfully"
  }
  ```

### 3. Добавление игрока
- **Метод:** `POST /player/add`
- **Описание:** Добавляет нового игрока в игру.
- **Input:**
  ```json
  {
    "generate_auto": false,
    "is_ai": false,
    "name": "Player1",
    "character_class": "Warrior",
    "race": "Human",
    "backstory": "A brave warrior."
  }
  ```
- **Output:**
  ```json
  {
    "message": "Player added successfully",
    "uuid": "player-uuid",
    "character": { ... }
  }
  ```

### 4. Получение состояния игры
- **Метод:** `POST /game/get_state`
- **Описание:** Получает текущее состояние игры.
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "Game state retrieved successfully",
    "adventure_data": { ... }
  }
  ```

### 5. Выполнение хода игрока
- **Метод:** `POST /game/make_turn_player`
- **Описание:** Выполняет ход для игрока.
- **Input:**
  ```json
  {
    "player_uuid": "player-uuid",
    "action": "attack",
    "task": { ... },
    "task_answer": "some answer"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Turn made successfully",
    "adventure_data": { ... },
    "task_status": { ... }
  }
  ```

### 6. Генерация задания
- **Метод:** `POST /game/generate_task`
- **Описание:** Генерирует новое задание.
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "Task generated successfully",
    "task": { ... }
  }
  ```

### 7. Получение всех заданий
- **Метод:** `POST /game/get_all_tasks`
- **Описание:** Получает все задания.
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "All tasks retrieved successfully",
    "tasks": [ ... ]
  }
  ```

### 8. Получение подсказки
- **Метод:** `POST /game/get_hint`
- **Описание:** Получает подсказку для задания.
- **Input:**
  ```json
  {
    "task_uuid": "task-uuid",
    "code": "some code"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Hint retrieved successfully",
    "hint": "some hint",
    "current_task": { ... },
    "code": "some code"
  }
  ```

### 9. Объяснение решения
- **Метод:** `POST /game/explain_solution`
- **Описание:** Объясняет решение для задания.
- **Input:**
  ```json
  {
    "task_uuid": "task-uuid",
    "code": "some code"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Solution explained successfully",
    "explanation": "some explanation",
    "current_task": { ... },
    "code": "some code"
  }
  ```

### 10. Генерация изображения для игрока
- **Метод:** `POST /game/make_player_image`
- **Описание:** Генерирует изображение для игрока.
- **Input:**
  ```json
  {
    "player_uuid": "player-uuid"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Player image made successfully",
    "image_url": "url_to_image",
    "filename": "image_filename"
  }
  ```

### 11. Генерация сцены изображения
- **Метод:** `POST /game/make_scene_image`
- **Описание:** Генерирует изображение для сцены на основе описания.
- **Input:**
  ```json
  {
    "scene_description": "A dark forest with towering trees."
  }
  ```
- **Output:**
  ```json
  {
    "message": "Image made successfully",
    "image_url": "url_to_image",
    "filename": "image_filename"
  }
  ```

### 12. Генерация музыки для сцены
- **Метод:** `POST /game/make_scene_music`
- **Описание:** Генерирует музыку для сцены на основе описания.
- **Input:**
  ```json
  {
    "scene_description": "A lively tavern filled with laughter."
  }
  ```
- **Output:**
  ```json
  {
    "message": "Music made successfully",
    "music_url": "url_to_music",
    "filename": "music_filename"
  }
  ```

### 13. Создание приключения
- **Метод:** `POST /game/create_adventure`
- **Описание:** Создает новое приключение для текущей игры.
- **Input:**
  ```json
  {
    "admin_uuid": "some-uuid",
    "dm_intro": "Welcome to the adventure!",
    "create_image": true,
    "create_music": false
  }
  ```
- **Output:**
  ```json
  {
    "message": "Adventure created successfully",
    "adventure_data": { ... }
  }
  ```

### 14. Получение доступных голосов
- **Метод:** `GET /game/get_voices`
- **Описание:** Получает список доступных голосов для TTS (Text-to-Speech).
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "Voices retrieved successfully",
    "voices": [ "Voice1", "Voice2", ... ]
  }
  ```

### 15. Создание TTS для AI
- **Метод:** `POST /game/make_tts_ai`
- **Описание:** Создает TTS для AI игрока на основе последнего хода.
- **Input:**
  ```json
  {
    "player_uuid": "ai-player-uuid",
    "voice_name": "Voice1"
  }
  ```
- **Output:**
  ```json
  {
    "message": "TTS AI made successfully",
    "adventure_data": {
      "tts_path": "path_to_tts",
      "tts_base64": "base64_encoded_audio"
    }
  }
  ```

### 16. Выполнение хода DM
- **Метод:** `POST /game/make_turn_dm`
- **Описание:** Выполняет ход для DM (Dungeon Master).
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "Turn DM made successfully",
    "adventure_data": {
      "role": "dm",
      "text": "DM's narrative text.",
      "uuid": "dm-uuid",
      "features": { ... }
    }
  }
  ```

### 17. Получение состояния игры
- **Метод:** `POST /game/get_state`
- **Описание:** Получает текущее состояние игры, включая информацию о игроках и заданиях.
- **Input:** (нет)
- **Output:**
  ```json
  {
    "message": "Game state retrieved successfully",
    "adventure_data": {
      "players": [ ... ],
      "last_turn": { ... },
      "current_quest": { ... },
      "players_not_turned": [ ... ],
      "players_turned": [ ... ]
    }
  }
  ```

### 18. Получение параметров хода
- **Метод:** `POST /game/get_turn_params`
- **Описание:** Получает параметры для выполнения хода игрока.
- **Input:**
  ```json
  {
    "player_uuid": "player-uuid"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Turn params retrieved successfully",
    "adventure_data": {
      "task": { ... },
      "seconds_to_solve": "",
      "difficulty": "easy"
    }
  }
  ```

### 19. Получение задания по UUID
- **Метод:** `POST /game/get_task`
- **Описание:** Получает задание по его UUID.
- **Input:**
  ```json
  {
    "task_uuid": "task-uuid"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Task retrieved successfully",
    "task": { ... }
  }
  ```

### 20. Выполнение задания
- **Метод:** `POST /game/execute_task`
- **Описание:** Выполняет задание, предоставляя код и проверяя его.
- **Input:**
  ```json
  {
    "code": "print('Hello, World!')",
    "task_uuid": "task-uuid"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Code executed successfully",
    "success": true,
    "errors1": [],
    "errors2": [],
    "current_task": { ... },
    "code": "print('Hello, World!')"
  }
  ```

## Заключение
DND Game API предоставляет мощный инструмент для управления игровыми сессиями Dungeons & Dragons, позволяя разработчикам и игрокам взаимодействовать с игрой через удобный интерфейс.