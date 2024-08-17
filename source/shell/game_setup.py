import os
import sys
import random
import string
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавление корневой директории проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Импорт необходимых библиотек
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter

# Импорт пользовательских модулей
from source.shell.game_quest import Story, BossFight
from source.models.init_models import setup_models
from source.shell.settings import names, classes, races

#
import uuid

# Инициализация моделей
LLM = setup_models.get('LLM')
TTS = setup_models.get('TTS')
IMAGE_MODEL = setup_models.get('IMAGE_MODEL')
RAG_MODEL = setup_models.get('RAG')
SOUND_MODEL = setup_models.get('MUSIC_MODEL')

console = Console()

# Функция для логирования сообщений
def log(message, tag):
    console.print(f"[bold blue][{tag}][/bold blue] {message}")

# Класс для хранения конфигурации игры

root_slash = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
class GameConfig:
    TURN_LIMIT = 10
    TTS_PATH = os.path.join(project_root, "storage", "voice_storage")
    MUSIC_PATH = os.path.join(project_root, "storage", "music_storage")
    IMAGE_PATH = os.path.join(project_root, "storage", "image_storage")

# Функция для создания размытого и затемненного изображения
def make_blur(filename, filepath=GameConfig.IMAGE_PATH):
    logger.info("Starting make_blur function")  # Логирование
    # Construct the full path to the image
    image_path = os.path.join(filepath, filename)
    
    # Open the image
    with Image.open(image_path) as img:
        # Apply Gaussian blur
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Make the image darker
        enhancer = ImageEnhance.Brightness(blurred_img)
        darkened_img = enhancer.enhance(0.3)  # Reduce brightness by 30%
        
        # Generate the output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_blurred{ext}"
        output_path = os.path.join(filepath, output_filename)
        
        # Save the blurred and darkened image
        darkened_img.save(output_path)
    
    log(f"Blurred and darkened image saved as {output_filename}", "IMAGE")

def generate_image_for_player(
        player_description,
        filepath=os.path.join(GameConfig.IMAGE_PATH, f"player.png")
    ):
    logger.info("Starting generate_image_for_player function")  # Логирование
    prompt = f"Generate an image for the player: {player_description}"
    filepath, image_url = IMAGE_MODEL.api_call(
        prompt,
        filepath
    )

    return filepath, image_url

class Character:
    def __init__(self, name, player_type, character_class, race, backstory):
        logger.info("Initializing Character")  # Логирование
        self.name = name
        self.player_type = player_type  # "player" or "ai"
        self.character_class = character_class
        self.race = race
        self.backstory = backstory

        self.uuid = str(uuid.uuid4())

    def is_ai(self):
        logger.info("Checking if character is AI")  # Логирование
        return self.player_type == "ai"

# Основной класс для настрой�� игры D&D
class DND_GameSetup():
    def __init__(self):
        logger.info("Initializing DND_GameSetup")  # Логирование
        self.party = []
        self.current_image_url = None
        self.current_music_url = None
        self.story_progression: list[list[dict]] = []
        self.vector_store = RAG_MODEL

        # Создание необходимых директорий
        for dir in [GameConfig.TTS_PATH, GameConfig.MUSIC_PATH, GameConfig.IMAGE_PATH]:
            if not os.path.exists(dir):
                os.makedirs(dir)

    # Получение количества игроков
    def get_n_players(self):
        logger.info("Getting number of players")  # Логирование
        return len(list(filter(lambda x: x.player_type == "player", self.party)))

    # Получение количества AI
    def get_n_ai(self):
        logger.info("Getting number of AI characters")  # Логирование
        return len(list(filter(lambda x: x.player_type == "ai", self.party)))

    # Получение имен всех игроков
    def get_player_names(self):
        logger.info("Getting player names")  # Логирование
        return [character.name for character in self.party]
    
    # Получение информации о конкрето�� игроке по имени
    def get_player(self, name):
        logger.info(f"Getting player with name: {name}")  # Логирование
        return next((character for character in self.party if character.name == name), None)

    # Генерация изображения для сцены
    def generate_image_for_scene(
            self,
            scene_description,
            filepath=os.path.join(GameConfig.IMAGE_PATH, "background.png")
    ):
        logger.info("Starting generate_image_for_scene function")
        prompt = f"Generate an image for the scene: {scene_description}"
        try:
            filepath, image_url = IMAGE_MODEL.api_call(
                prompt,
                filepath
            )
            if filepath and image_url:
                make_blur(filepath)
                return filepath, image_url
            else:
                logger.error("IMAGE_MODEL.api_call returned None or incomplete data")
                return None, None
        except Exception as e:
            logger.error(f"Error in generate_image_for_scene: {str(e)}")
            return None, None

    # Генерация музыки для сцены
    def generate_music_for_scene(
            self,
            scene_description,
            filepath=os.path.join(GameConfig.MUSIC_PATH, "background_music.mp3")
    ):
        logger.info("Starting generate_music_for_scene function")  # Логирование
        prompt = f"Generate music for the scene: {scene_description}"
        filepath, music_url = SOUND_MODEL.api_call(
            prompt,
            filepath
        )

        return filepath, music_url

    # Создание нового приключения
    def create_new_adventure(
            self,
            create_image=True,
            create_music=True,
            dm_intro=None
    ):
        logger.info("Creating new adventure")  # Логирование
        party_members = [
            f"Name {character.name} - Class {character.character_class}"
            for character in self.party
        ]

        log("Creating new adventure with DM.", "GAME")
        if dm_intro is None:
            dm_intro = LLM.api_call(
                f"""You are the Dungeon Master. Create an exciting and unique D&D adventure.

                1. Setting:
                - Describe the world or region where the adventure takes place
                - Mention any important historical or cultural context

                2. Characters:
                Introduce the following party members:
                {', '.join(party_members)}

                3. Opening Scene:
                - Set the initial location where the party meets
                - Describe the atmosphere and any notable features

                4. Initial Challenge or Mystery:
                - Present a problem or quest that will drive the story forward
                - Provide some hints or clues for the players to investigate

                5. Immediate Goal:
                - Give the party a clear, short-term objective to pursue

                Remember:
                - Be creative and engaging in your descriptions
                - Do not introduce any new characters beyond those listed
                - Aim for a balance of action, mystery, and role-playing opportunities

                Provide your response in a narrative format, ready to be presented to the players.
                Answer in Russian.
                """,
                500)

        image_filepath, initial_image_url = (self.generate_image_for_scene(dm_intro) 
                                             if create_image else (None, None))
        music_filepath, initial_music_url = (self.generate_music_for_scene(dm_intro) 
                                             if create_music else (None, None))

        self.current_image_url = initial_image_url
        self.current_music_url = initial_music_url

        log(f"Initial music URL: {initial_music_url}", "MUSIC")
        log(f"Initial image URL: {initial_image_url}", "IMAGE")

        console.print(Panel(
            Text(dm_intro, style="italic"),
            title="[bold red]Dungeon Master Introduction[/bold red]",
            border_style="red",
            expand=False
        ))

        # Нужно переделать в такой формат:
        # story_progression = [[{}, {}], [{}, {}]]

        self.story_progression = [
            [
                {
                    "role": "DM",
                    "message": dm_intro,
                    "features": "intro",
                    "name": "Dungeon Master"
                }
            ]
        ]

        return {
            "turn": 1,
            "story_progression": [
                [
                    # Первый ход игры.
                    {
                        "role": "DM",
                        "message": dm_intro,
                        "features": "intro"
                    },
                ],
                # [], - второй ход игры.
                # [], - третий ход игры.
                # и т.д.
            ],
            "party_members": self.party,
            "current_image_url": initial_image_url,
            "current_music_url": initial_music_url,
            "current_image_path": image_filepath,
            "current_music_path": music_filepath,
            "dm_intro": dm_intro
        }

    # Генерация группы персонажей
    def generate_party(
            self,
            n=2,
            n_ai=2,
    ):
        logger.info("Generating party")  # Логирование
        party = list()
        console.print(Panel("Character Generation", style="bold magenta", expand=False))
        console.print(f"Game with [green]{n}[/green] players and [yellow]{n_ai}[/yellow] AI characters.")

        for i in range(n):
            generated = self.generate_character(
                is_ai=False
            )
            party.append(generated)

        for i in range(n_ai):
            generated = self.generate_character(
                is_ai=True
            )
            party.append(generated)

        console.print(Panel("Character Generation Complete", style="bold magenta", expand=False))
        self.party = party
        return party
        

    # Генерация одельного персонажа
    def generate_character(
            self,
            is_ai=False,
            player_data=None,
            generate_auto=True
    ):
        logger.info("Generating character")  # Логирование
        current_names = self.get_player_names()
        # Генерация игроков - Людей/AI.
        def generate_unique_name():
            name = random.choice(names)
            return name if name not in current_names else ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Форма для генерации персонажа.
        if not player_data:
            if is_ai:
                name = generate_unique_name()
                class_ = random.choice(classes)
                race = random.choice(races)
                console.print(Panel(
                    f"[bold]AI Character Created[/bold]\nName: {name}\nClass: {class_}\nRace: {race}",
                    style="yellow",
                    expand=False
                ))
            else:
                if generate_auto:
                    name = generate_unique_name()
                    class_ = random.choice(classes)
                    race = random.choice(races)
                    console.print(Panel(
                        f"[bold]Player Character Created[/bold]\nName: {name}\nClass: {class_}\nRace: {race}",
                        style="green",
                        expand=False
                    ))
                else:
                    name = next(name for name in iter(lambda: console.input("[bold]Enter character name: [/bold]"), None) if name not in current_names)
                    class_ = console.input("[bold]Enter character class: [/bold]")
                    race = console.input("[bold]Enter character race: [/bold]")
                    console.print(Panel(
                        f"[bold]Player Character Created[/bold]\nName: {name}\nClass: {class_}\nRace: {race}",
                        style="green",
                        expand=False
                    ))
        else:
            name = player_data.get("name")
            class_ = player_data.get("class")
            race = player_data.get("race")

        generate_character_prompt = f"""
            Сгенерируй, пожалуйста историю для персонажа D&D.

            Его характеристики:
            Имя: {name}
            Класс: {class_}
            Раса: {race}

            Сделай это по шаблону:
            1. Красивое предложение-представление героя в ентези стиле. (1 предложение)
            2. История главного героя. (3 предложения)
            3. Лучшие качества. (1 предложение)
            4. Любимая фраза. (1 предложение)

            Будь креативным и фантастичным.
            """

        print(setup_models)
        backstory = LLM.api_call(generate_character_prompt, 300) if generate_auto else player_data.get("backstory")

        console.print(Panel(
            Text(backstory, style="italic"),
            title="Character Backstory",
            style="cyan",
            expand=False
        ))

        return Character(
            name=name,
            player_type="player" if not is_ai else "ai",
            character_class=class_,
            race=race,
            backstory=backstory,
        )
    
    # Добавление персонажа в группу
    def add_to_party(self, character: Character):
        logger.info(f"Adding character {character.name} to party")  # Логирование
        """
        Adds a character to the party.

        Args:
            character (Character): A Character object.

        Returns:
            list: The updated party list containing all characters.
        """
        self.party.append(character)
        console.print(Panel(
            f"[bold]{character.name}[/bold] added to the party!",
            style="green" if not character.is_ai() else "yellow",
            expand=False
        ))
        return self.party
    
    # Отображение информации о группе
    def display_party(self):
        logger.info("Displaying party information")  # Логирование
        table = Table(title="Party Members", box=box.ROUNDED)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Class", style="green")
        table.add_column("Race", style="yellow")

        for character in self.party:
            table.add_row(
                character.name,
                "Player" if not character.is_ai() else "AI",
                character.character_class,
                character.race
            )

        console.print(table)