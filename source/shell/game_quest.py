import os
import sys
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(project_root + '/.env')

SHORT_PROMPTS = os.getenv("SHORT_PROMPTS") == "True"

from source.models.init_models import setup_models
from source.shell.game_task_generator.game_task_generator import GameTask

from source.shell.game_task_generator.game_task_generator import CodewarsTask

LLM = setup_models.get("LLM")

import time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Story:
    max_turns = 1

    def __init__(self, turn_start: int, vector_store, game_setup, start_story: str = None):
        self.turn_start = turn_start
        self.tasks = []
        self.tasker = GameTask()
        self.difficulty = 0
        if not start_story:
            self.description, self.prompt = self.create_description(vector_store, game_setup)
        else:
            self.description = start_story

    def to_dict(self):
        return {
            "turn_start": self.turn_start,
            "tasks": self.tasks,
            "difficulty": self.difficulty,
            "description": self.description,
        }

    def get_task_by_uuid(self, uuid: str):
        retrieved = list(filter(lambda x: x.uuid == uuid, self.tasks))
        if len(retrieved) == 0:
            return None
        return retrieved[0]

    def create_description(self, vector_store, game_setup):
        logging.info("game_quest - create_description - Начало создания описания")
        last_context = game_setup.story_progression[-1][-5:]
        last_context = list(map(lambda x: x.get('message'), last_context))

        context = vector_store.similarity_search(game_setup.game_uuid, " ".join(last_context), k=3)

        # Код для настройки квестов
        if SHORT_PROMPTS:
            dm_prompt = (f"Как Мастер Подземелий, создайте сцену для D&D:\n"
            f"Используйте релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
            f"Учтите недавние события: {' '.join(last_context)}.\n"
            f"Опишите новую локацию или изменения в текущей.\n"
            f"3. Введите новый вызов или загадку для персонажей.\n"
            f"Ответ должен быть в 4-5 предложениях.")
        else:
            dm_prompt = (f"Как Мастер Подземелий, создайте следующую сцену для приключения D&D:\n"
                        f"1. Учтите недавние события: {' '.join(last_context)}\n"
                        f"2. Используйте релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
                        f"3. Опишите новую локацию или изменения в текущей (1-2 предложения)\n"
                        f"4. Представьте новый вызов или загадку для персонажей (не боевой)\n"
                        f"5. Введите или развейте второстепенного персонажа\n"
                        f"6. Намекните на дальнейшее развитие сюжета\n"
                        f"7. Создайте атмосферу, используя описания звуков, запахов или погоды\n"
                        f"Будьте креативны, увлекательны и погрузите игроков в мир D&D. Ответ должен быть на 200-300 слов.")

        # DM генерирует квест и задает игрокам
        dm_response = LLM.api_call(
            dm_prompt,
            max_tokens=300,
        )

        logging.info("game_quest - create_description - Описание создано")
        return dm_response, dm_prompt
    
    def next_step_description(self, vector_store, game_setup, quest_ended: str):
        logging.info("game_quest - next_step_description - Начало следующего шага описания")
        last_context = game_setup.story_progression[-1][-5:]
        last_context = list(map(lambda x: x.get('message'), last_context))

        context = vector_store.similarity_search(game_setup.game_uuid, " ".join(last_context), k=3)

        if SHORT_PROMPTS:
            dm_prompt = (f"Как Мастер Подземелий, создайте сцену для D&D:\n"
            f"Используйте релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
            f"Учтите недавние события: {' '.join(last_context)}.\n"
            f"Опишите новую локацию или изменения в текущей.\n"
            f"3. Введите новый вызов или загадку для персонажей.\n"
            f"Ответ должен быть в 4-5 предложениях.")
        else:   
            dm_prompt = (f"Как Мастер Подземелий, продолжите историю приключения D&D, сосредоточившись на развитии сюжета. Исходя из последних событий:\n"
                    f"1. Учтите недавние события: {' '.join(last_context)}\n"
                    f"2. Используйте релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
                    f"3. Опишите следующий этап сюжета, включая:\n"
                    f"   1. Взаимодействие игроков с окружающим миром.\n"
                    f"   2. Выборы, которые делают игроки, и их последствия.\n"
                    f"   3. Новые элементы, которые могут повлиять на их приключение.\n"
                    f"4. Создайте атмосферу, используя описания звуков, запахов или погоды.\n"
                    f"5. Результат предыдущего шага: {quest_ended}"
            )    
        
        dm_response = LLM.api_call(
            dm_prompt,
            max_tokens=300,
        )

        logging.info("game_quest - next_step_description - Следующий шаг описания завершен")
        return dm_response, dm_prompt

class BossFight:
    max_turns = 3
    LLM_damage = 10
    player_damage = 15
    hp = 100

    def __init__(self, turn_start: int, n_tasks: int, difficulty: int, vector_store, game_setup):
        self.turn_start = turn_start
        self.n_tasks = n_tasks
        self.difficulty = difficulty

        # Увеличиваем количество ходов, если сложность боя 3
        self.max_turns = self.max_turns + 1 if difficulty == 3 else self.max_turns

        self.tasks_type = "code"
        self.tasker = GameTask()
        self.tasks = [] # list[CodewarsTask]
        self.make_tasks()
        self.description, self.prompt = self.create_description(vector_store, game_setup)
        
    def to_dict(self):
        return {
            "turn_start": self.turn_start,
            "n_tasks": self.n_tasks,
            "difficulty": self.difficulty,
            "tasks_type": self.tasks_type,
            "tasker": self.tasker.to_dict(),
        }

    def create_description(self, vector_store, game_setup):
        logging.info("game_quest - create_description - Начало создания описания битвы с боссом")
        last_context = game_setup.story_progression[-1][-5:]
        last_context = list(map(lambda x: x.get('message'), last_context))

        context = vector_store.similarity_search(game_setup.game_uuid, " ".join(last_context), k=3)

        if SHORT_PROMPTS:
            dm_prompt = (
            f"Как Мастер Подземелий, создайте атмосферную сцену битвы с боссом для D&D. "
            f"Недавние события: {' '.join(last_context)}\n"
            f"Релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
            f"Опишите босса: его имя, физическое описание и способности. "
            f"Укажите его мотивацию и цели, а также арену сражения. "
            f"Сделайте описание динамичным и захватывающим, чтобы игроки почувствовали напряжение битвы."
        )
        else:
            dm_prompt = (
            f"Как Мастер Подземелий, создайте эпический сценарий битвы с боссом для приключения D&D. Исходя из последних событий."
            f"Недавние события: {' '.join(last_context)}\n"
            f"Релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
            f"Проанализируйте ситуацию и создайте захватывающую встречу с боссом. Включите следующее:\n"
            f"1. Имя и титул босса (1-2 предложения)\n"
            f"2. Физическое описание и способности (2-3 предложения)\n"
            f"3. Мотивация и цели босса (1-2 предложения)\n"
            f"4. Поле боя или арена, где происходит сражение (1-2 предложения)\n"
            f"Убедитесь, что босс и встреча тематически соответствуют тону и сеттингу приключения."
            f"Описание должно включать в себя описание сцены, где происходит битва."
        )

        return LLM.api_call(dm_prompt, 500), dm_prompt
    
    def next_step_description(self, vector_store, game_setup, quest_ended: str):
        logging.info("game_quest - next_step_description - Начало следующего шага битвы с боссом")
        last_context = game_setup.story_progression[-1][-5:]
        last_context = list(map(lambda x: x.get('message'), last_context))

        context = vector_store.similarity_search(game_setup.game_uuid, " ".join(last_context), k=3)
        if SHORT_PROMPTS:
            dm_prompt = (
                f"Как Мастер Подземелий, продолжите сцену битвы с боссом в D&D. "
                f"Релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
                f"Недавние события: {' '.join(last_context)}. "
                f"Босс: у него осталось {self.hp} HP. "
                f"Опишите его действия и реакции игроков, а также изменения на поле боя. "
                f"Сделайте описание динамичным и захватывающим."
            )

        else:
            dm_prompt = (
                f"Как Мастер Подземелий, продолжите эпическую сцену битвы с боссом в приключении D&D. "
                f"Недавние события: {' '.join(last_context)}\n"
                f"Релевантный лор: {' '.join([doc.page_content for doc in context])}\n"
                f"Опишите следующий этап сражения, учитывая следующие аспекты:\n"
                f"1. Действия босса: какие атаки или способности он использует?\n"
                f"2. Реакция игроков: как они противостоят боссу и его действиям?\n"
                f"3. Изменения на поле боя: как меняется окружение в ходе битвы?\n"
                f"4. Напряженные моменты: опишите критические ситуации или повороты в сражении.\n"
                f"5. Атмосфера: передайте настроение и накал битвы.\n"
                f"Сделайте описание динамичным и захватывающим, чтобы игроки почувствовали себя в центре эпического сражения."
                f"У босса осталось {self.hp} HP. Сложность битвы: {self.difficulty} (от 1 до 3)"
                f"Результат предыдущего боя: {quest_ended}"
            )

        return LLM.api_call(
            dm_prompt, 
            max_tokens=500,
        ), dm_prompt
    
    def make_tasks(self):
        self.tasks = [self.make_quest_to_solve() for _ in range(self.n_tasks)]
    
    # Генерация задачи для игрока, в зависимости от типа задачи
    def make_quest_to_solve(self):
        return self.tasker.get_task(self.difficulty)
    
    def get_task_by_uuid(self, uuid: str):
        retrieved = list(filter(lambda x: x.uuid == uuid, self.tasks))
        if len(retrieved) == 0:
            return None
        return retrieved[0]

    # Каждый из персонажей атакует босса один раз за ход
    def attack(self, is_ai: bool = False, player_answer: str = None, task: CodewarsTask = None):
        logging.info("game_quest - attack - Начало атаки")
        if is_ai:
            self.hp -= self.LLM_damage * self.difficulty
            logging.info("game_quest - attack - Атака завершена")
            return self.LLM_damage * self.difficulty, self.hp
        else:
            result = self.tasker.run_task(
                code=player_answer,
                task=task,
            )
            
            if result:
                self.hp -= self.player_damage * task.task_difficulty
                logging.info("game_quest - attack - Атака завершена")
                return self.player_damage * task.task_difficulty, self.hp
            else:
                logging.info("game_quest - attack - Атака завершена")
                return 0, self.hp