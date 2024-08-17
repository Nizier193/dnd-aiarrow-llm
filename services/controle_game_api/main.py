import os
import sys

# Adjust the path to include the directory containing the 'source' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Now try to import from source
from source.shell.game_setup import Character
from source.shell.game_run import DND_Game
from source.shell.game_quest import Story, BossFight
from source.shell.game_setup import GameConfig
from source.shell.game_task_generator.game_task_generator import GameTask, CodewarsTask

from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from pydantic import BaseModel

import random
import uuid

tasker = GameTask()

# Две задачи для любых действий
custom_tasks = [
    tasker.get_task() for i in range(2)
]
app = FastAPI()

# Глобальная переменная для хранения текущей игры
global current_game, admin_uuid, max_n_ai, max_n_players
current_game = None
admin_uuid = None

max_n_ai = 0
max_n_players = 0

class GameModel(BaseModel):
    n_ai: int
    n_players: int

templates = Jinja2Templates(directory="services/controle_game_api/")  # Укажите директорию для шаблонов

@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    global current_game

    game_info = {}
    tasks = [task.to_dict() for task in custom_tasks]

    if current_game is not None:
        game_info = {
            "admin_uuid": admin_uuid,
            "max_n_ai": max_n_ai,
            "max_n_players": max_n_players,
            "current_n_ai": current_game.game_setup.get_n_ai(),
            "current_n_players": current_game.game_setup.get_n_players(),
            "players": [player.__dict__ for player in current_game.game_setup.party],
        }
        tasks = [task.to_dict() for task in current_game.current_quest.tasks] + [task.to_dict() for task in custom_tasks]
    
    return templates.TemplateResponse("game_info.html", {"request": request, "game_info": game_info, "tasks": tasks})


@app.post('/game/create')
def create_game(game_model: GameModel):
    # Создание игры
    # Передать количество AI и игроков: n_ai, n_players
    # Возвращает UUID админа для управления игрой

    global current_game, admin_uuid, max_n_ai, max_n_players
    if current_game is not None:
        return JSONResponse(content={"message": "Game already created and is running."}, status_code=400)   
    else:
        current_game = DND_Game()
        admin_uuid = str(uuid.uuid4())
        max_n_ai = game_model.n_ai
        max_n_players = game_model.n_players
        return JSONResponse(content={"message": f"Game created successfully", "admin_uuid": admin_uuid}, status_code=200)

class GameDeleteModel(BaseModel):
    admin_uuid: str

@app.post('/game/delete')
def delete_game(game_delete_model: GameDeleteModel):
    # Удаление игры
    # Передать UUID админа для управления игрой
    # Возвращает сообщение об удалении игры

    global current_game, admin_uuid, max_n_ai, max_n_players
    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)  
    else:
        if str(admin_uuid) == game_delete_model.admin_uuid:
            current_game = None
            admin_uuid = None
            max_n_ai = 0
            max_n_players = 0
            return JSONResponse(content={"message": "Game deleted successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "You are not admin of this game."}, status_code=400)

class PlayerModel(BaseModel):
    generate_auto: bool
    is_ai: bool

    name: str
    character_class: str
    race: str
    backstory: str

def check_if_can_add_player(is_ai: bool, n_ai: int, n_players: int):
    if is_ai:
        if n_ai < max_n_ai:
            return True
        else:
            return False
    else:
        if n_players < max_n_players:
            return True
        else:
            return False

@app.post('/player/add')
def add_player(player: PlayerModel):
    global current_game, max_n_ai, max_n_players

    current_n_ai = current_game.game_setup.get_n_ai()
    current_n_players = current_game.game_setup.get_n_players()

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    else:
        if check_if_can_add_player(player.is_ai, current_n_ai, current_n_players):
            if player.generate_auto:
                generated = current_game.game_setup.generate_character(
                    is_ai=player.is_ai,
                    generate_auto=True,
                )
            else:
                generated = Character(
                    player_type="ai" if player.is_ai else "player",

                    name=player.name,
                    character_class=player.character_class,
                    race=player.race,
                    backstory=player.backstory,
                )
            
            current_game.game_setup.add_to_party(generated)

            return JSONResponse(content={"message": "Player added successfully", "uuid": generated.uuid, "character": generated.__dict__}, status_code=200)

        return JSONResponse(content={"message": "Can't add player. Game is full."}, status_code=400)

class AdventureModel(BaseModel):
    admin_uuid: str

    dm_intro: str = None
    create_image: bool = True
    create_music: bool = False

@app.post('/game/create_adventure')
def create_adventure(adventure_model: AdventureModel):
    global current_game, admin_uuid

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    if str(admin_uuid) != adventure_model.admin_uuid:
        return JSONResponse(content={"message": "You are not admin of this game."}, status_code=400)
    
    adventure = current_game.game_setup.create_new_adventure(
        create_image=adventure_model.create_image,
        create_music=adventure_model.create_music,  
        dm_intro=adventure_model.dm_intro,
    )
    current_game.current_quest = Story(
        turn_start=0,
        vector_store=current_game.game_setup.vector_store,
        game_setup=current_game.game_setup,
        start_story=adventure_model.dm_intro,
    )
    players = [
        player.__dict__ for player in current_game.game_setup.party
    ]
    adventure_data = {
        "players": players,
        "n_ai": current_game.game_setup.get_n_ai(),
        "n_players": current_game.game_setup.get_n_players(),

        "dm_intro": adventure_model.dm_intro,

        "image_url": current_game.game_setup.current_image_url,
        "music_url": current_game.game_setup.current_music_url,
    }
    return JSONResponse(content={"message": "Adventure created successfully", "adventure_data": adventure_data}, status_code=200)


@app.post('/game/get_state')
def get_game_state():
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    players = [
        player.__dict__ for player in current_game.game_setup.party
    ]
    # Последний ход игрока в последнем ходе игры
    last_turn = current_game.game_setup.story_progression[-1][-1]
    quest = current_game.current_quest.to_dict()

    # Игроки которые не делали ход
    players_not_turned = [
        player.__dict__ for player in current_game.game_setup.party
        if player.uuid not in [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]
    ]
    # Игроки которые делали ход
    players_turned = [
        player.__dict__ for player in current_game.game_setup.party
        if player.uuid in [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]
    ]

    adventure_data = {
        "players": players,
        "last_turn": last_turn,
        "current_quest": quest,
        "players_not_turned": players_not_turned,
        "players_turned": players_turned,
    }
    print(adventure_data)
    return JSONResponse(content={"message": "Game state retrieved successfully", "adventure_data": adventure_data}, status_code=200)

class TurnParamsModel(BaseModel):
    player_uuid: str

@app.post('/game/get_turn_params')
def get_turn_params(turn_params_model: TurnParamsModel):
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)

    players_not_turned_uuids = [
        player.uuid for player in current_game.game_setup.party
        if player.uuid not in [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]
    ]
    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    if turn_params_model.player_uuid not in [player.uuid for player in current_game.game_setup.party]:
        return JSONResponse(content={"message": "Player not found."}, status_code=400)
    if turn_params_model.player_uuid not in players_not_turned_uuids:
        return JSONResponse(content={"message": "Player already turned."}, status_code=400)

    current_tasks = current_game.current_quest.tasks

    # Таск выбирается случайным образом
    # // TODO: Выбрать таск подходящий под игрока.
    task = random.choice(current_tasks if len(current_tasks) > 0 else [{}])
    seconds_to_solve = ""
    difficulty = current_game.current_quest.difficulty
    if isinstance(task, CodewarsTask):
        task = task.to_dict()

    turn_params = {
        "task": task,
        "seconds_to_solve": seconds_to_solve,
        "difficulty": difficulty,
    }
    return JSONResponse(content={"message": "Turn params retrieved successfully", "adventure_data": turn_params}, status_code=200)

class TurnModelPlayer(BaseModel):
    player_uuid: str
    action: str

    task: dict
    task_answer: str

@app.post('/game/make_turn_player')
def make_turn_player(turn_model: TurnModelPlayer):
    global current_game

    ai_uuids = [player.uuid for player in current_game.game_setup.party if player.is_ai()]

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    if turn_model.player_uuid not in [player.uuid for player in current_game.game_setup.party]:
        return JSONResponse(content={"message": "Player not found."}, status_code=400)
    if turn_model.player_uuid in [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]:
        return JSONResponse(content={"message": "Player already turned."}, status_code=400)
    if turn_model.player_uuid in ai_uuids:
        return JSONResponse(content={"message": "Player is AI."}, status_code=400)

    task_dict = {
        "task": turn_model.task,
        "answer": turn_model.task_answer,
    }
    response = current_game.make_single_turn(
        player=list(filter(lambda x: x.uuid == turn_model.player_uuid, current_game.game_setup.party))[0],
        is_ai=False,
        action=turn_model.action,
        task_dict=task_dict,
    )

    return JSONResponse(content={
        "message": "Turn made successfully",
        "adventure_data": {
            "role": response.role,
            "text": response.message,
            "uuid": response.uuid,
            "features": response.features,
        },
        "task_status": {
            "hp": response.task_status.get("hp", None),
            "damage": response.task_status.get("damage", None),
            "solved": response.task_status.get("solved", None),
            "message": response.task_status.get("message", None),
        }
    }, status_code=200)

class TurnModelAI(BaseModel):
    player_uuid: str

@app.post('/game/make_turn_ai')
def make_turn_ai(turn_model: TurnModelAI):
    global current_game

    player_uuids = [player.uuid for player in current_game.game_setup.party if not player.is_ai()]

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    if turn_model.player_uuid not in [player.uuid for player in current_game.game_setup.party]:
        return JSONResponse(content={"message": "Player not found."}, status_code=400)
    if turn_model.player_uuid in [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]:
        return JSONResponse(content={"message": "Player already turned."}, status_code=400)
    if turn_model.player_uuid in player_uuids:
        return JSONResponse(content={"message": "Player is not AI."}, status_code=400)

    response = current_game.make_single_turn(
        player=list(filter(lambda x: x.uuid == turn_model.player_uuid, current_game.game_setup.party))[0],
        is_ai=True,
    )

    return JSONResponse(content={
        "message": "Turn made successfully",
        "adventure_data": {
            "role": response.role,
            "text": response.message,
            "uuid": response.uuid,
            "features": response.features,
        }}, status_code=200)


@app.post('/game/get_all_tasks')
def get_all_tasks():
    global current_game, custom_tasks

    custom_tasks = [task.to_dict() for task in custom_tasks]
    if current_game is not None:
        game_tasks = [task.to_dict() for task in current_game.current_quest.tasks]
    else:
        game_tasks = []

    return JSONResponse(content={"message": "All tasks retrieved successfully", "tasks": game_tasks + custom_tasks}, status_code=200)

class GetTaskModel(BaseModel):
    task_uuid: str

@app.post('/game/get_task')
def get_task(get_task_model: GetTaskModel):
    global current_game

    task_uuid = get_task_model.task_uuid
    game_tasks = []
    if current_game is not None:
        game_tasks = current_game.current_quest.tasks
        task_uuids = [task.uuid for task in game_tasks]

    task_uuids = [task.uuid for task in custom_tasks] + task_uuids

    if task_uuid not in task_uuids:
        return JSONResponse(content={"message": "Task not found."}, status_code=400)
    
    task = list(filter(lambda x: x.uuid == task_uuid, custom_tasks + game_tasks))[0]

    # CodewarsTask: task_uuid, task_name, task_difficulty, task_description, task_check_data
    return JSONResponse(content={"message": "Task retrieved successfully", "task": task.to_dict()}, status_code=200)

@app.post('/game/generate_task')
def generate_task():
    global custom_tasks

    task = tasker.get_task()
    custom_tasks.append(task)

    return JSONResponse(content={"message": "Task generated successfully", "task": task.to_dict()}, status_code=200)


class ExecuteTaskModel(BaseModel):
    code: str

    task_uuid: str = None
    custom_task: dict = None

@app.post('/game/execute_task')
def execute_task(execute_task_model: ExecuteTaskModel):
    global current_game, custom_tasks
    
    if (
        execute_task_model.task_uuid is None and
        execute_task_model.custom_task is None
    ):
        return JSONResponse(content={"message": "Task not found."}, status_code=400)

    if execute_task_model.task_uuid is not None:
        game_tasks = []
        game_task_uuids = []
        if current_game is not None:
            game_tasks = current_game.current_quest.tasks
            game_task_uuids = [task.uuid for task in game_tasks]

        game_task_uuids = [task.uuid for task in custom_tasks] + game_task_uuids

        if execute_task_model.task_uuid not in game_task_uuids:
            return JSONResponse(content={"message": "Task not found."}, status_code=400)
        
        current_task = list(filter(lambda x: x.uuid == execute_task_model.task_uuid, custom_tasks + game_tasks))[0]
    else:
        if (
            execute_task_model.custom_task.get('name') is None or
            execute_task_model.custom_task.get('difficulty') is None or
            execute_task_model.custom_task.get('description') is None or
            execute_task_model.custom_task.get('task_check_data') is None
        ):
            return JSONResponse(content={"message": "Custom task is not valid."}, status_code=400)

        current_task = CodewarsTask(
            task_name=execute_task_model.custom_task.get('name'),
            task_difficulty=execute_task_model.custom_task.get('difficulty'),
            task_description=execute_task_model.custom_task.get('description'),
            task_check_data=execute_task_model.custom_task.get('task_check_data'),
        )

    success, errors1, errors2 = tasker.check_task(
        code=execute_task_model.code,
        task=current_task,
    )

    # Преобразование ошибок в сериализуемый формат
    errors1_serialized = [(str(e[0]), e[1].__str__()) for e in errors1]
    errors2_serialized = [(str(e[0]), e[1].__str__()) for e in errors2]

    return JSONResponse(content={
        "message": "Code executed successfully",
        "success": success,
        "errors1": errors1_serialized,
        "errors2": errors2_serialized,
        "current_task": current_task.to_dict(),
        "code": execute_task_model.code,
    }, status_code=200)

# Получение подсказки
class GetHintModel(BaseModel):
    task_uuid: str
    code: str

# Метод для получения подсказки для задания
@app.post('/game/get_hint')
def get_hint(get_hint_model: GetHintModel):
    global current_game, custom_tasks

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    custom_tasks_uuids = [task.uuid for task in custom_tasks]
    all_tasks_uuids = custom_tasks_uuids + [task.uuid for task in current_game.current_quest.tasks]
    
    if get_hint_model.task_uuid not in all_tasks_uuids:
        return JSONResponse(content={"message": "Task not found."}, status_code=400)
    
    current_task = list(filter(lambda x: x.uuid == get_hint_model.task_uuid, current_game.current_quest.tasks + custom_tasks))[0]

    hint = tasker.get_hint(
        code=get_hint_model.code,
        task=current_task,
    )

    return JSONResponse(content={"message": "Hint retrieved successfully", "hint": hint, "current_task": current_task.to_dict(), "code": get_hint_model.code}, status_code=200)

class ExplainSolutionModel(BaseModel):
    task_uuid: str
    code: str

@app.post('/game/explain_solution')
def explain_solution(explain_solution_model: ExplainSolutionModel):
    global current_game, custom_tasks

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    custom_tasks_uuids = [task.uuid for task in custom_tasks]
    all_tasks_uuids = custom_tasks_uuids + [task.uuid for task in current_game.current_quest.tasks]
    
    if explain_solution_model.task_uuid not in all_tasks_uuids:
        return JSONResponse(content={"message": "Task not found."}, status_code=400)
    
    current_task = list(filter(lambda x: x.uuid == explain_solution_model.task_uuid, current_game.current_quest.tasks + custom_tasks))[0]

    explanation = tasker.explain_solution(
        solution=explain_solution_model.code,
        task=current_task,
    )

    return JSONResponse(content={
        "message": "Solution explained successfully", 
        "explanation": explanation, 
        "current_task": current_task.to_dict(), 
        "code": explain_solution_model.code
    }, status_code=200)

@app.get('/game/get_voices')
def get_voices():
    global current_game

    available_voices = current_game.get_available_voices()
    print("Available voices:")
    print(available_voices)
    print()

    return JSONResponse(content={"message": "Voices retrieved successfully", "voices": available_voices}, status_code=200)

class MakeTTSAI(BaseModel):
    player_uuid: str
    voice_name: str

@app.post('/game/make_tts_ai')
def make_tts_ai(make_tts_ai_model: MakeTTSAI):
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    if make_tts_ai_model.player_uuid not in [player.uuid for player in current_game.game_setup.party]:
        return JSONResponse(content={"message": "Player not found."}, status_code=400)
    
    ai_turns = [turn for turn in current_game.game_setup.story_progression[-1] if turn.get("role") == "ai"]
    try:
        current_turn = [turn for turn in ai_turns if turn.get('uuid') == make_tts_ai_model.player_uuid][0]

        tts_path, tts_base64 = current_game.make_tts(
            text=current_turn.get('message'),
            player=list(filter(lambda x: x.uuid == make_tts_ai_model.player_uuid, current_game.game_setup.party))[0],
            voice_name=make_tts_ai_model.voice_name,
        )
    except Exception as e:
        return JSONResponse(content={"message": "TTS AI error", "error": str(e)}, status_code=200)

    return JSONResponse(content={
        "message": "TTS AI made successfully", 
        "adventure_data": {
            "tts_path": tts_path,
            "tts_base64": tts_base64,
        }}, status_code=200)   


@app.post('/game/make_turn_dm')
def make_turn_dm():
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    players_uuids_turned = [turn.get('uuid') for turn in current_game.game_setup.story_progression[-1]]
    players_uuids = [player.uuid for player in current_game.game_setup.party]

    if len(players_uuids_turned) < len(players_uuids):
        return JSONResponse(content={"message": "Not all players turned or somehow more than players in game."}, status_code=400)
    
    response = current_game.dm_single_turn()

    return JSONResponse(content={
        "message": "Turn DM made successfully", 
        "adventure_data": {
            "role": response.role,
            "text": response.message,
            "uuid": response.uuid,
            "features": response.features,
        }}, status_code=200)

class MakeImageModel(BaseModel):
    scene_description: str

@app.post('/game/make_scene_image')
def make_scene_image(make_image_model: MakeImageModel):
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    # Use current_game.current_quest.description to generate image in ui
    filename, image_url = current_game.game_setup.generate_image_for_scene(scene_description=make_image_model.scene_description)

    return JSONResponse(content={"message": "Image made successfully", "image_url": image_url, "filename": filename}, status_code=200)

class MakeMusicModel(BaseModel):
    scene_description: str

@app.post('/game/make_scene_music')
def make_scene_music(make_music_model: MakeMusicModel):
    global current_game

    if current_game is None:
        return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
    
    # Use current_game.current_quest.description to generate music in ui
    filename, music_url = current_game.game_setup.generate_music_for_scene(scene_description=make_music_model.scene_description)

    return JSONResponse(content={"message": "Music made successfully", "music_url": music_url, "filename": filename}, status_code=200)

from source.shell.game_setup import generate_image_for_player
class MakePlayerImageModel(BaseModel):
    player_uuid: str = None
    player_description: str = None

@app.post('/game/make_player_image')
def make_player_image(make_player_image_model: MakePlayerImageModel):
    global current_game

    if make_player_image_model.player_description:
        # Генерация изображения игрока по описанию
        filename, image_url = generate_image_for_player(player_description=make_player_image_model.player_description)

        return JSONResponse(content={"message": "Player image made successfully", "image_url": image_url, "filename": filename}, status_code=200)
    
    if make_player_image_model.player_uuid:
        # Генерация изображения игрока по uuid
        if not current_game:
            return JSONResponse(content={"message": "Game not created yet."}, status_code=400)
        if make_player_image_model.player_uuid not in [player.uuid for player in current_game.game_setup.party]:
            return JSONResponse(content={"message": "Player not found."}, status_code=400)
        
        player = list(filter(lambda x: x.uuid == make_player_image_model.player_uuid, current_game.game_setup.party))[0]
        player_description = f"""
        Имя: {player.name}
        Класс: {player.class_name}
        Раса: {player.race}
        История: {player.backstory}
        """

        filename, image_url = generate_image_for_player(player_description=player_description)

        return JSONResponse(content={"message": "Player image made successfully", "image_url": image_url, "filename": filename}, status_code=200)

    return JSONResponse(content={"message": "Player uuid and player description not found."}, status_code=400)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)