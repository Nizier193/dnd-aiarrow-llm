import os
import sys
import time
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(project_root + '/.env')

SHORT_PROMPTS = os.getenv('SHORT_PROMPTS') == "True"

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table
from rich import box

from PIL import (       
    Image,
    ImageEnhance,   
)

from source.shell.game_setup import make_blur
from source.shell.game_setup import Character  # Add this import

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from source.models.init_models import setup_models
from source.models.soundgen.openai_TTS import Voices

from source.shell.game_quest import Story, BossFight
from source.shell.game_setup import DND_GameSetup
from source.shell.game_setup import GameConfig
import random

LLM = setup_models.get('LLM')
TTS = setup_models.get('TTS')
IMAGE_MODEL = setup_models.get('IMAGE_MODEL')
RAG_MODEL = setup_models.get('RAG')
SOUND_MODEL = setup_models.get('MUSIC_MODEL')

def log(message, tag):
    console.print(f"[bold cyan][{tag}][/bold cyan] {message}")

import os

console = Console()

class GameResponse:
    def __init__(self, role: str, message: str, features: str = None, uuid: str = None, task_status: dict = None, name: str = None):
        self.role = role
        self.message = message
        self.features = features
        self.uuid = uuid
        self.task_status = task_status
        self.name = name
    def to_dict(self):
        return {
            "role": self.role,
            "message": self.message,
            "features": self.features,
            "uuid": self.uuid,
            "task_status": self.task_status,
            "name": self.name
        }

class DND_Game():
    actions = ['будете делать?']
    tasks_type = "code"

    class Story(Story):
        pass

    class BossFight(BossFight):
        pass

    def __init__(self):
        logger.info("Initializing DND_Game")
        '''
        Чтобы инициализировать игру вручную, нужно вызвать этот метод.
        1. создать пати в game_setup.party: list[dict]
        - использовать метод game_setup.generate_character() для генерации персонажа
        - использовать метод game_setup.add_to_party() для добавления игроков
        - использовать метод game_setup.create_new_adventure() для создания нового приключения

        * Игра будет создана, далее:
        
        2. в ручном режиме запустить игру:
        - ходят игроки в произвольном порядке
        - выполняет квест, если есть квест, иначе сторителлинг

        - DM ходит после игроков
        - DM генерирует квест и задает игрокам:
        -- выбор квеста рандомно

        3. сгенерировать картинку и музыку для сцены
        - использовать метод game_setup.generate_image_for_scene(dm_response) для генерации картинки
        - использовать метод game_setup.generate_music_for_scene(dm_response) для генерации музыки

        * Картинка и музыка будут сохранены в папку GameConfig.IMAGE_PATH и GameConfig.MUSIC_PATH соответственно
        * Два экземпляра картинки будут созданы: с резким размытием и без размытия

        4. Запустить музыку используя GameSounds.play_background_music()
        - отановить музыку используя GameSounds.stop_background_music()

        5. Следующий ход
        '''

        self.game_setup = DND_GameSetup()
        self.current_quest = None
        self.current_step = 0

    def print_player_turn(self, player: Character, action, is_ai=False):
        logger.info(f"Player turn: {player.name}, Action: {action}, AI: {is_ai}")
        color = "blue" if is_ai else "green"
        title = f"[bold {color}]{'AI ' if is_ai else ''}Player {player.name}'s Turn[/bold {color}]"
        console.print(Panel(
            Text(f"{player.name} does: {action}", style="italic"),
            title=title,
            border_style=color,
            expand=False
        ))

    def print_info(self, information):
        logger.info(f"Information: {information}")
        color = "blue"
        title = f"[bold {color}]{information}[/bold {color}]"
        console.print(Panel(
            Text(f"{information}", style="italic"),
            title=title,
            border_style=color,
            expand=False
        ))

    def print_dm_response(self, dm_response):
        logger.info("Printing DM response")
        console.print(Panel(
            dm_response,
            title="[bold red]Dungeon Master[/bold red]",
            border_style="red",
            expand=False
        ))

    def print_turn_summary(self):
        logger.info("Printing turn summary")
        table = Table(title=f"[bold magenta]Turn {self.current_step} Summary[/bold magenta]", box=box.ROUNDED)
        table.add_column("Event", style="cyan")
        table.add_column("Details", style="green")

        print("story_progression", self.game_setup.story_progression)
        
        for event in self.game_setup.story_progression[-1]:  # list
            if isinstance(event, dict):
                role = event.get('role', 'Unknown')
                message = event.get('message', '')
                message = message[:50] + "..." if len(message) > 50 else message
                table.add_row(role, message)
            elif isinstance(event, str):
                table.add_row("Event", event[:50] + "..." if len(event) > 50 else event)
        
        console.print(table)

    def make_single_turn(
            self,
            player: Character,
            is_ai=False,
            action=None,
            task_dict=None,
    ) -> GameResponse:
        logger.info(f"Making single turn for player: {player.name}, AI: {is_ai}")
        player_name = player.name
        player_info = f"""
            Имя игрока: {player.name}
            Раса игрока: {player.race}
            Класс игрока: {player.character_class}
            История игрока: {player.backstory[:100]}...
            """

        context = self.game_setup.vector_store.similarity_search(player_info, k=3)

        last_context = self.game_setup.story_progression[-1][-3:]  # list[list[dict]] , последние события игры
        last_context = list(map(lambda x: x.get('message'), last_context))  # list[str]


        player_AI_prompt = (f"Имя игрока: {player_name}\n"
                        f"Информация об игроке: {player_info}\n\n"
                        f"Контекст игры: {' '.join(last_context)}\n"
                        f"Релевантная информация: {' '.join([doc.page_content for doc in context])}\n"
                        f"Что вы делаете или говорите дальше? (Ответьте на русском, как персонаж, просто опишите свои действия и реплики.)\n")

        # AI player turn
        if is_ai:
            hp = self.current_quest.__dict__.get("hp")
            damage = 0
            if self.check_quest():
                if self.current_quest.__class__ == BossFight:
                    damage, hp = self.current_quest.attack(is_ai=True)
                    player_AI_prompt += f"\n* Ваш персонаж атакует босса, нанося {damage} урона. HP босса: {hp}."

            action = LLM.api_call(player_AI_prompt, 500)
            if len(action) == 0: action = "Ничего не делает."
            self.print_player_turn(
                player,
                f"""
                Действие: {action},
                HP: {hp},
                Урон: {damage}
                """,
                is_ai=True
            )
            status = {
                "hp": hp,
                "damage": damage,
                "solved": True,
                "message": "Задание решено." if damage > 0 else "Задание не решено."
            }
            result = GameResponse(role="ai", message=action, uuid=player.uuid, name=player.name, task_status=status)
            
            # Добавляем ход игрока в последний ход игры
            self.game_setup.story_progression[-1].append(result.to_dict())
            self.game_setup.vector_store.add_texts(action)
            return result

        else:
            status = {
                "hp": self.current_quest.__dict__.get("hp"),
                "damage": 0,
                "solved": False,
                "message": "-"
            }
            damage = status.get("damage")
            hp = status.get("hp")
            if self.check_quest():
                if self.current_quest.__class__ == BossFight:
                    damage, hp = self.current_quest.attack(
                        is_ai=False,
                        player_answer=task_dict.get("answer"),
                        task=task_dict.get("task")
                    )

            if len(action) == 0: action = "Ничего не делает."   
            # Player turn - if not AI
            self.print_player_turn(
                player, 
                f"""
                Действие: {action},
                HP: {hp},
                Урон: {damage}
                Задание решено: {'Задание не решено' if damage > 0 else 'Задание решено'}
                Замечание: {status.get("message")}
                """
            )

            status["hp"] = hp
            status["damage"] = damage
            status["solved"] = damage > 0
            status["message"] = "Задание решено." if damage > 0 else "Задание не решено."

            result = GameResponse(role="player", message=action, uuid=player.uuid, task_status=status, name=player.name)
            # Добавляем ход игрока в последний ход игры
            self.game_setup.story_progression[-1].append(result.to_dict())
            self.game_setup.vector_store.add_texts(action)
            return result
        
    def get_available_voices(self):
        logger.info("Getting available voices")
        return TTS.get_available_voices()
    
    def make_tts(self, text: str, player: Character = None, voice_name: str = 'alloy'):
        logger.info(f"Generating TTS for player: {player.name}")
        audio_file = os.path.join(GameConfig.TTS_PATH, f"{player.name}.mp3")
        log(f"Generating TTS for player {player.name}", "SOUND GEN")
        filepath, base64_audio = TTS.api_call(
            voice_name,
            text,
            audio_file
        )
        # Генерация TTS для игрока. Далее запуск через GameSounds.play_tts()
        return filepath, base64_audio
    
    def start_quest(self, n_tasks: int = None):
        logger.info("Starting quest")
        # На выбор может быть два квеста.
        # 1. Story: сторителлинг, без задач
        # 2. BossFight: математические задачи или алгоритмы
        if self.current_quest:
            return False
        
        if n_tasks is None:
            n_tasks = len([p for p in self.game_setup.party if not p.is_ai()])

        quest = random.choices([Story, BossFight], weights=[0.1, 0.9])[0]
        if quest == BossFight:
            self.current_quest = quest(
                turn_start=self.current_step,
                vector_store=self.game_setup.vector_store,
                game_setup=self.game_setup,
                n_tasks=n_tasks,
                difficulty=random.randint(1, 3)
            )
        else:
            self.current_quest = quest(
                turn_start=self.current_step,
                vector_store=self.game_setup.vector_store,
                game_setup=self.game_setup,
            )

        # Для трасировки
        print("Выбран квест:", quest.__class__.__name__)
        print("Описание квеста:", self.current_quest.description)
        print("Описание промпта DM:", self.current_quest.prompt)

        return self.current_quest.description, self.current_quest.prompt

    def check_quest(self):
        logger.info("Checking current quest")
        if self.current_quest:
            return True
        return False

    def end_quest(self):
        logger.info("Ending quest")
        turns_passed = self.current_step - self.current_quest.turn_start
        if self.current_quest.__class__ == Story:
            if turns_passed >= self.current_quest.max_turns:
                self.current_quest = None
                return "Игроки продолжают свой путь в мире приключений."
            
            return "Игроки прошли один шаг истории."

        if self.current_quest.__class__ == BossFight:
            self.current_quest.make_tasks()
            
            if self.current_quest.hp <= 0:
                self.current_quest = None
                return "Игроки успешно победили босса! Поздравляем!"

            elif turns_passed >= self.current_quest.max_turns:
                # Игроки проиграли босс-баттл
                self.current_quest = None
                self.end_game()
                return "Игроки проиграли босс-баттл. Какое невезение!"
            
            return "Игроки прошли один шаг босс-баттла. Битва ещё не закончена."           

        print(self.current_quest.__class__)
        return "Игра окончена."

    def dm_single_turn(self, n_tasks: int = None, feature: str = "dm_response") -> GameResponse:
        logger.info("DM's single turn")
        # DM ход.
        
        quest_result = self.end_quest()
        self.print_info(quest_result)
        if quest_result == "Игра окончена.":
            self.end_game()

        if not self.check_quest():
            # Если квест закончился, начать новый
            # - сторителлинг
            # - босс-баттл
            dm_response, _ = self.start_quest(n_tasks=n_tasks)
        else:
            # Если квест продолжается, сгенерировать следующую сцену.
            dm_response, _ = self.current_quest.next_step_description(
                vector_store=self.game_setup.vector_store,
                game_setup=self.game_setup,
                quest_ended=quest_result # Параметр показывает, чем закончился предыдущий шаг.
            )

        result = GameResponse(role="DM", message=dm_response, features=feature, name="Dungeon Master")
        self.game_setup.vector_store.add_texts(dm_response)
        self.game_setup.story_progression.append([result.to_dict()])
        self.print_dm_response(dm_response)

        # Будет вызываться в конце хода игрока
        # Игроки могли пройти один шаг сторителлин��а или босс-баттла или проиграть квест

        # осле хода DM будут производиться действия игроков (в зависимости от квеста):
        # 1. Сражение через код или математику
        # 2. Сторителлинг
        self.current_step += 1

        return result
    

    def end_game(self):
        logger.info("Ending game")
        print(
            f"self.current_quest: {self.current_quest}\n\n",
            f"self.current_quest.description: {self.current_quest.description}\n\n",
            f"self.current_quest.prompt: {self.current_quest.prompt}\n\n",
        )

        self.game_setup = None
        self.current_quest = None
        self.current_step = 0

        console.print("[bold red]Game ended![/bold red]")
        raise Exception("Game ended")