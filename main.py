# You can use streamlit app only for singleplayer mode

CAN_CHANGE_MODELS = False
from pprint import pprint

import streamlit as st
import os
import requests
import json
from typing import Dict, Tuple
from dotenv import load_dotenv

import sys
import random
from PIL import Image
import base64
import requests
from io import BytesIO

from source.models.init_models import setup_models, reload_models
from source.shell.game_setup import Story, BossFight

from source.shell.game_run import DND_Game
from source.shell.game_task_generator.game_task_generator import GameTask

load_dotenv('.env')

admin_uuid = ['dcdc4443-4047-48fd-a909-0105dfb16c8d']
tasker = GameTask()

st.set_page_config(page_title="CodeDungeons", page_icon="⚔️", layout="wide")

RAG = setup_models.get("RAG")
LLM = setup_models.get("LLM")
CHAT_MODEL = setup_models.get("CHAT_MODEL")
IMAGE_MODEL = setup_models.get("IMAGE_MODEL")
MUSIC_MODEL = setup_models.get("MUSIC_MODEL")
TTS = setup_models.get("TTS")


def set_fantasy_theme():
    st.markdown("""
    <style>
        body { color: #e0e0e0; background-color: #1a1a2e; font-family: 'Cinzel', serif; }
        .stButton>button { color: #ffd700; background-color: #4a0e0e; border: 2px solid #ffd700; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { color: #e0e0e0; background-color: #2a2a4e; }
        .stHeader { color: #ffd700; text-shadow: 2px 2px 4px #000000; }
        .sidebar .sidebar-content { background-color: #16213e; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

def display_image(image_path: str):
    try:
        image = Image.open(image_path)
        st.image(image, caption="Adventure Image", use_column_width=False, width=400)
    except Exception:
        st.info("Картинка будет загружена позже.")

def display_music(music_path: str):
    try:
        with open(music_path, "rb") as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode()
        st.markdown(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading music: {e}")


def manage_models():
    st.write('Model Management Panel')
    st.subheader("Available Models")

    # Define the model data
    model_data = {
        'LLM': {'yandex': 'GPT-3', 'openai': 'GPT-4o'},
        'Image': {'openai': 'DALL-E-3', 'yandex': 'YandexArt'},
        'Music': {'suno': 'Suno MusicGen'},
        'RAG': {'openai': 'OpenAI Embeddings', 'ollama': 'Ollama Embeddings'},
        'TTS': {'openai': 'OpenAI TTS', 'elevenlabs': "eleven_multilingual_v2"}
    }

    # Create a DataFrame for display
    data = []
    for model_type, options in model_data.items():
        options_str = ", ".join([f"{k}: {v}" for k, v in options.items()])
        data.append({"Model Type": model_type, "Available Options": options_str})

    # Display the table using Streamlit's dataframe
    st.dataframe(data, use_container_width=True, hide_index=True)

    # Form for selecting models
    with st.form(key='model_selection_form'):
        st.subheader("Select Models")
        
        selected_llm = st.selectbox("LLM", 
                                    [f"{k}: {v}" for k, v in model_data['LLM'].items()],
                                    format_func=lambda x: x.split(': ')[1])
        selected_image = st.selectbox("Image Model", 
                                      [f"{k}: {v}" for k, v in model_data['Image'].items()],
                                      format_func=lambda x: x.split(': ')[1])
        selected_music = st.selectbox("Music Model", 
                                      [f"{k}: {v}" for k, v in model_data['Music'].items()],
                                      format_func=lambda x: x.split(': ')[1])
        selected_rag = st.selectbox("RAG Model", 
                                    [f"{k}: {v}" for k, v in model_data['RAG'].items()],
                                    format_func=lambda x: x.split(': ')[1])
        selected_tts = st.selectbox("TTS Model", 
                                    [f"{k}: {v}" for k, v in model_data['TTS'].items()],
                                    format_func=lambda x: x.split(': ')[1])

        admin_uuid_key = st.text_input("Admin UUID Key", value="")
        submit_button = st.form_submit_button("Apply Model Selection")
        st.markdown("""
        <div style="
            background-color: rgba(70, 70, 70, 0.8);
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 20px;
            color: #e0e0e0;
            font-size: 16px;
            margin-bottom: 20px;  /* Added margin for spacing */
        ">
            <p>Для использования моделей нужно прописать соответствующие переменные API ключей и других значений.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background-color: rgba(70, 70, 70, 0.8);
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 20px;
            color: #e0e0e0;
            font-size: 16px;
            margin-bottom: 20px;  /* Added margin for spacing */
        ">
            <p>Было решено отключить возможность изменения моделей без ключа админа.</p>
            <p>Для изменения моделей необходимо развернуть приложение локально и изменить флаг <strong>CAN_CHANGE_MODELS</strong> на True в самом начале кода. 
            Код рабочий и был протестирован много раз. Пробный вызов модели можно осуществить в Настройках.</p>
            <p>Спасибо за понимание!</p>
        </div>
        """, unsafe_allow_html=True)

    if submit_button:
        if (admin_uuid_key in admin_uuid) or CAN_CHANGE_MODELS:
            llm_provider, model = selected_llm.split(': ')
            os.environ['LLM_PROVIDER'] = llm_provider
        
            imgen_provider, model = selected_image.split(': ')
            os.environ['IMGEN_PROVIDER'] = imgen_provider

            music_provider, model = selected_music.split(': ')
            os.environ['MUSIC_PROVIDER'] = music_provider

            rag_provider, model = selected_rag.split(': ')
            os.environ['RAG_PROVIDER'] = rag_provider

            tts_provider, model = selected_tts.split(': ')
            os.environ['TTS_PROVIDER'] = tts_provider

            reload_models()
            # Here you can add logic to apply the selected models
            st.success("Model selection applied successfully!")

        else:
            st.info("Неверный ключ администратора для изменения моделей.")

def players_turn():
    ai_players = [player for player in st.session_state.current_game.game_setup.party if player.player_type == "ai"]
    player = [player for player in st.session_state.current_game.game_setup.party if player.player_type == "player"][-1]

    if "voice_name" not in st.session_state:
        st.session_state.voice_name = random.choice(st.session_state.current_game.get_available_voices())

    # Ход AI игроков
    for player in ai_players:
        action = st.session_state.current_game.make_single_turn(
            player,
            is_ai=True
        )
        if st.session_state.generate_tts:
            filepath, base64 = st.session_state.current_game.make_tts(
                player=player,
                text=action.message,
                voice_name=st.session_state.voice_name
            )

def set_background_image(image_source):
    """
    Set the background image for the Streamlit app.
    
    :param image_source: Either a URL string or an uploaded image file
    """

    image = Image.open(image_source)
    
    # Convert the image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Set the background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_str}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add this near the top of the main function
start_image_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "image_storage", "start_image.png")
st.session_state.image_path = start_image_source

start_music_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "music_storage", "start_music.mp3")
st.session_state.music_path = start_music_source

def main():
    set_background_image(
        st.session_state.image_path.split('.')[0] + "_blurred." + st.session_state.image_path.split('.')[1]
    )
    set_fantasy_theme()

    # Add this at the beginning of the main function
    st.sidebar.markdown(
        """
        <h1 style="
            color: #a0a0a0;
            font-family: 'Luminari', 'Dragon Hunter', 'Papyrus', fantasy;
            text-align: center;
            margin-bottom: 20px;
        ">AI Arrow</h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h1 class="fantasy-title">CodeDungeons</h1>
        <style>
        .fantasy-title {
            font-family: 'Luminari', 'Dragon Hunter', 'Papyrus', fantasy;
            font-size: 4rem;
            text-align: center;
            color: #FFD700;
            text-shadow: 
                0 0 10px #FF6600,
                0 0 20px #FF6600,
                0 0 30px #FF6600,
                0 0 40px #FF6600;
            letter-spacing: 0.1em;
            margin-bottom: 30px;
            animation: glow 1.5s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from {
                text-shadow: 
                    0 0 10px #FF6600,
                    0 0 20px #FF6600,
                    0 0 30px #FF6600,
                    0 0 40px #FF6600;
            }
            to {
                text-shadow: 
                    0 0 20px #FF6600,
                    0 0 30px #FF6600,
                    0 0 40px #FF6600,
                    0 0 50px #FF6600,
                    0 0 60px #FF6600;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )



    st.sidebar.markdown("### Настройки генерации")
    st.session_state.generate_image = st.sidebar.checkbox("Генерировать изображение", value=True)
    st.session_state.generate_audio = st.sidebar.checkbox("Генерировать аудио", value=False)
    st.session_state.generate_tts = st.sidebar.checkbox("Генерировать озвучку", value=False)

    if 'current_game' not in st.session_state:
        st.session_state.current_game = None

    
    st.sidebar.markdown("### Навигация")
    page = st.sidebar.radio(label='', options=["Играть", "Информация о группе", "Управление моделями", "Настройки"], label_visibility="collapsed")

    if page == "Настройки":
        st.sidebar.header("Настройки")
        st.header("Настройки и основные сведения")

        if 'image_path' in st.session_state:
            st.markdown(f"<small>Текущая картинка: {st.session_state.image_path}</small>", unsafe_allow_html=True)
        if 'music_path' in st.session_state:
            st.markdown(f"<small>Текущая музыка: {st.session_state.music_path}</small>", unsafe_allow_html=True)

        if st.session_state.current_game:
            st.session_state.voice_name = st.selectbox("Выберите голос для озвучки", st.session_state.current_game.get_available_voices())

        st.markdown(f"Поле для тестового запроса LLM. Провайдер LLM: {os.environ.get('LLM_PROVIDER')}")
        llm_prompt = st.text_input("Введите prompt для LLM", value="")
        if st.button("Тестовый запрос", key="llm_test_button"):
            result = LLM.api_call(
                prompt=llm_prompt,
                max_tokens=20,
            )
            st.write(result)

        st.write(
            {
                "LLM_PROVIDER": os.environ.get("LLM_PROVIDER"),
                "IMGEN_PROVIDER": os.environ.get("IMGEN_PROVIDER"),
                "MUSIC_PROVIDER": os.environ.get("MUSIC_PROVIDER"),
                "RAG_PROVIDER": os.environ.get("RAG_PROVIDER"),
                "TTS_PROVIDER": os.environ.get("TTS_PROVIDER")
            }
        )

        # show st.session_state.current_game
        if st.session_state.current_game:
            st.write("Текущая игра: ", st.session_state.current_game.__dict__)

        if st.session_state.current_game:
            st.write("Настройка игры: ", st.session_state.current_game.game_setup.__dict__)

    if page == "Информация о группе":
        st.sidebar.header("Управление группой")
        st.header("Информация о группе")

        if not st.session_state.current_game:
            st.sidebar.info("Сначала нужно создать группу.")

        if st.session_state.current_game:
            images = [
                'https://polinka.top/pics1/uploads/posts/2024-01/1706530799_polinka-top-p-fantasticheskii-peizazh-krasivo-1.jpg',
                'https://gas-kvas.com/grafic/uploads/posts/2024-01/gas-kvas-com-p-kosmicheskie-miri-oboi-5.jpg',
                'https://kartinki.pics/uploads/posts/2022-02/1645840669_51-kartinkin-net-p-fantasticheskie-kartinki-54.jpg',
            ]

            for player in st.session_state.current_game.game_setup.party:
                bg_color = 'rgba(0, 0, 70, 0.7)' if player.player_type == "player" else 'rgba(70, 30, 0, 0.7)'
                border_color = '#00ffff' if player.player_type == "player" else '#ffd700'

                st.markdown(
                    f"""
                    <div style="
                        background-image: url('{random.choice(images)}');
                        background-size: cover;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    ">
                        <div style="
                            background-color: {bg_color};
                            border: 2px solid {border_color};
                            border-radius: 8px;
                            padding: 15px;
                        ">
                            <h3 style="color: {border_color};">{player.name}</h3>
                            <p style="color: #e0e0e0;"><strong>Тип:</strong> {player.player_type.capitalize()}</p>
                            <p style="color: #e0e0e0;"><strong>Класс:</strong> {player.character_class}</p>
                            <p style="color: #e0e0e0;"><strong>Раса:</strong> {player.race}</p>
                            <details>
                                <summary style="color: #e0e0e0; cursor: pointer;">Предыстория</summary>
                                <p style="color: #a0a0a0; font-style: italic;">{player.backstory}</p>
                            </details>
                            <p style="color: #a0a0a0; font-size: 12px;">UUID: {player.uuid}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if page == "Играть":
        st.sidebar.header("Управление игрой")
        if st.sidebar.button("Создать новую игру"):
            st.session_state.current_game = DND_Game()
            st.success("Новая игра создана!\nТеперь создайте свою команду.")


        if st.session_state.current_game:
            number_of_players = st.sidebar.slider("Выберите количество ИИ-игроков", min_value=1, max_value=5, value=1)

            if st.sidebar.button("🧙‍♂️ Сгенерировать новую группу"):
                with st.spinner("Призываем отважных искателей приключений..."):
                    st.session_state.current_game.game_setup.add_to_party(
                        st.session_state.current_game.game_setup.generate_character(
                            is_ai=False,
                            generate_auto=True
                        )
                    )
                    for i in range(number_of_players):
                        st.session_state.current_game.game_setup.add_to_party(
                            st.session_state.current_game.game_setup.generate_character(
                                is_ai=True,
                                generate_auto=True
                            )
                        )

                st.success("Ваша группа собрана!\nТеперь создайте приключение.")

        if st.session_state.current_game and len(st.session_state.current_game.game_setup.party) != 0:
            if st.sidebar.button("🗺️ Начать новое приключение"):
                with st.spinner("Готовим эпическое задание..."):
                    adventure = st.session_state.current_game.game_setup.create_new_adventure(
                        create_image=st.session_state.generate_image,
                        create_music=st.session_state.generate_audio
                    )

                    st.session_state.current_game.current_quest = Story(
                        turn_start=0,
                        vector_store=st.session_state.current_game.game_setup.vector_store,
                        game_setup=st.session_state.current_game.game_setup,
                        start_story=adventure.get("dm_intro", "")
                    )

                    image_path = adventure.get("current_image_path", None)
                    music_path = adventure.get("current_music_path", None)

                    # Set blurred image as background
                    if image_path:
                        st.session_state.image_path = image_path
                        set_background_image(
                            image_path.split('.')[0] + "_blurred." + image_path.split('.')[1]
                        )
                    
                    if music_path:
                        st.session_state.music_path = music_path

                    display_image(st.session_state.image_path)
                    display_music(st.session_state.music_path)

                st.success("Приключение создано!\nМожно начинать!")

        if st.session_state.current_game and st.session_state.current_game.current_quest:
            st.header("Информация о приключении")

            with st.form(key=f'player_action_form_{st.session_state.current_game.current_quest.turn_start}'):
                st.subheader("Ход игрока")
                st.markdown("### Редактор кода")
                code = """def main():
    # Вот так выглядит функция, который будет выполняться
    # Когда вы делаете проверку кода (вторая кнопка).
    # Без параметров!
    pass

# def main(-needed amount of parameters-):
    # Вот так выглядит функция, который будет выполняться
    # Когда вы делаете ход (первая кнопка).
    # С нужным количеством параметров!
    # pass
"""
                answer = st.text_area(
                    "Введите ваш код:",
                    height=150,
                    max_chars=None,
                    key=f"code_editor_{st.session_state.current_game.current_quest.turn_start}",
                    help="Напишите здесь свой код для выполнения задания.",
                    on_change=None,
                    args=None,
                    kwargs=None,
                    placeholder="def main():\n    # Ваш код здесь. Функция должна называться 'main'.\n    pass",
                    value=code,
                )
                st.markdown(
                    "<small>Напишите здесь свой Python-код.</small><br>"
                    "Важно: <br>"
                    "<small><li>Когда вы делаете ход, вызывается функция <strong>'main' с аргументами.</strong><br>"
                    "<li>Когда вы проверяете код, вызывается функция <strong>'main' без аргументов.</strong><br>"
                    "<li>Рекомендую перед ходом очищать форму с помощью любой кнопки, кроме 'Сделать ход', тогда проблем никогда не возникнет!</small>",
                    unsafe_allow_html=True
                )
                st.markdown("### Действие")
                action = st.text_input("Ваше действие:")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    submit_button = st.form_submit_button("🎲 Сделать ход")
                    st.markdown("<small>Отправить код и действие.</small>", unsafe_allow_html=True)
                with col2:
                    submit_button_2 = st.form_submit_button("🔍 Выполнить код")
                    st.markdown("<small>Запустить код и получить результат.</small>", unsafe_allow_html=True)
                with col3:
                    submit_button_3 = st.form_submit_button("💡 Получить подсказку")
                    st.markdown("<small>Получить полезную подсказку.</small>", unsafe_allow_html=True)
                with col4:
                    submit_button_4 = st.form_submit_button("🔍 Посмотреть параметры задания")
                    st.markdown("<small>Посмотреть параметры задания.</small>", unsafe_allow_html=True)

            if submit_button_2:
                if len(st.session_state.current_game.current_quest.tasks) != 0:
                    executed = tasker.execute_task(
                        code=answer,
                    )
                    result = executed.result
                    error = executed.error
                    
                    output_html = f"""
                    <div style="
                        background-color: rgba(30, 30, 50, 0.9);
                        border: 2px solid #4a86e8;
                        border-radius: 10px;
                        padding: 20px;
                        margin-bottom: 20px;
                    ">
                        <h3 style="color: #4a86e8; margin-bottom: 15px;">Результат выполнения</h3>
                        <div style="
                            background-color: rgba(0, 50, 0, 0.3);
                            border: 1px solid #4a86e8;
                            border-radius: 5px;
                            padding: 10px;
                        ">
                            <p style="color: #a8d08d; margin: 0;">Вывод:</p>
                            <p style="color: #e0e0e0; margin: 5px 0 0 0;">{result if result else 'Нет вывода'}</p>
                        </div>
                        <div style="
                            background-color: rgba(50, 0, 0, 0.3);
                            border: 1px solid #4a86e8;
                            border-radius: 5px;
                            padding: 10px;
                            margin-top: 10px;
                        ">
                            <p style="color: #ea9999; margin: 0;">Ошибка:</p>
                            <p style="color: #e0e0e0; margin: 5px 0 0 0;">{error if error else 'Нет ошибки'}</p>
                        </div>
                    </div>
                    """
                    st.markdown(output_html, unsafe_allow_html=True)
                else:
                    st.info("Вы не можете выполнить код в этом задании.")
            
            if submit_button_3:
                if len(st.session_state.current_game.current_quest.tasks) != 0:
                    hint = tasker.get_hint(
                        code=answer,
                        task=st.session_state.current_task
                    )
                    
                    st.markdown(f"""
                    <div style="
                        background-color: rgba(0, 0, 70, 0.7);
                        border: 2px solid #00ffff;
                        border-radius: 10px;
                        padding: 20px;
                        margin-bottom: 20px;
                    ">
                        <h3 style="color: #00ffff;">Магическая подсказка</h3>
                        <p style="color: #e0e0e0; font-style: italic;">{hint}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Вы не можете получить подсказку в этом задании.")

            if submit_button_4:
                if len(st.session_state.current_game.current_quest.tasks) != 0:
                    task = st.session_state.current_task
                    
                    quest = st.session_state.current_game.current_quest
                    hp = quest.hp
                    n_tasks = quest.n_tasks

                    last_turn_status = None
                    if st.session_state.task_status:
                        last_turn_status = st.session_state.task_status

                    quest_parameters_html = f"""
                    <div style="
                        background-color: rgba(0, 0, 70, 0.7);
                        border: 2px solid #00ffff;
                        border-radius: 10px;
                        padding: 20px;
                        margin-bottom: 20px;
                    ">
                        <h4 style="color: #00ffff;">Параметры задания</h4>
                        <p style="color: #e0e0e0; margin: 5px 0;">HP Босса: <span style="color: #FFD700;">{hp}</span></p>
                        <p style="color: #e0e0e0; margin: 5px 0;">Количество заданий: <span style="color: #FFD700;">{n_tasks}</span></p>
                        <hr>
                        <h4 style="color: #00ffff;">Статус задания</h4>
                        <p style="color: #e0e0e0; margin: 5px 0;">Урон, нанесенный вами в прошлом ходу: <span style="color: #FFD700;">{last_turn_status.get("damage", "Неизвестно")}</span></p>
                        <p style="color: #e0e0e0; margin: 5px 0;">Решено ли было задание: <span style="color: #FFD700;">{last_turn_status.get("solved", "Неизвестно")}</span></p>
                        <p style="color: #e0e0e0; margin: 5px 0;">Замечание: <span style="color: #FFD700;">{last_turn_status.get("message", "Неизвестно")}</span></p>
                    </div>
                    """
                    st.markdown(quest_parameters_html, unsafe_allow_html=True)
                else:
                    st.info("Вы не можете посмотреть параметры задания в этом задании.")

            player = list(filter(lambda x: x.player_type != "ai", st.session_state.current_game.game_setup.party))[0]
            # Обработка хода ирока
            if submit_button:
                with st.spinner("Обработка вашего хода..."):
                    if "current_task" not in st.session_state:
                        st.session_state.current_task = None

                    task_dict = {
                        "task": st.session_state.current_task,
                        "answer": answer,
                    }
                    pprint("answer")
                    pprint(answer)
                    action = st.session_state.current_game.make_single_turn(
                        player,
                        is_ai=False,
                        action=action,
                        task_dict=task_dict
                    )

                    # Запись статуса задания
                    st.session_state.task_status = action.task_status

                # Ходы ИИ
                players_turn()
                action = st.session_state.current_game.dm_single_turn()

                if st.session_state.generate_image:
                    image_path, url = st.session_state.current_game.game_setup.generate_image_for_scene(
                        action.message
                    )
                    if image_path:
                        st.session_state.image_path = image_path
                        
                if st.session_state.generate_audio:
                    music_path, url = st.session_state.current_game.game_setup.generate_music_for_scene(
                        action.message
                    )
                    if music_path:
                        st.session_state.music_path = music_path

                display_image(st.session_state.image_path)
                if st.session_state.image_path:
                    set_background_image(
                        st.session_state.image_path.split('.')[0] + "_blurred." + st.session_state.image_path.split('.')[1]
                    )
                display_music(st.session_state.music_path)

            # История ходов
            st.header("Журнал приключения")
            for i, turns in enumerate(st.session_state.current_game.game_setup.story_progression[::-1]):
                for j, turn in enumerate(turns[::-1]):
                    with st.container():
                        images = [
                            'https://polinka.top/pics1/uploads/posts/2024-01/1706530799_polinka-top-p-fantasticheskii-peizazh-krasivo-1.jpg',
                            'https://gas-kvas.com/grafic/uploads/posts/2024-01/gas-kvas-com-p-kosmicheskie-miri-oboi-5.jpg',
                            'https://kartinki.pics/uploads/posts/2022-02/1645840669_51-kartinkin-net-p-fantasticheskie-kartinki-54.jpg',
                        ]
                        # Определяем стиль для DM
                        is_dm = turn.get('role', '').lower() == 'dm'
                        bg_color = 'rgba(70, 30, 0, 0.8)' if is_dm else 'rgba(0, 0, 0, 0.6)'
                        border_color = '#ffd700' if is_dm else '#a0a0a0'

                        # Выводим квест только после последнего хода DM
                        if is_dm and j == 0 and len(st.session_state.current_game.current_quest.tasks) != 0:
                            st.session_state.current_task = st.session_state.current_game.current_quest.tasks[-1]
                            task = st.session_state.current_task
                            
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: rgba(70, 30, 0, 0.7);
                                    border: 2px solid #ffd700;
                                    border-radius: 10px;
                                    padding: 20px;
                                    margin-bottom: 20px;
                                ">
                                    <h3 style="color: #ffd700;">Ваше задание</h3>
                                    <p style="color: #e0e0e0; font-size: 18px;"><strong>Задание:</strong> {task.task_name}</p>
                                    <p style="color: #e0e0e0; font-size: 16px;"><strong>Сложность:</strong> {task.task_difficulty}</p>
                                    <p style="color: #e0e0e0; font-size: 16px;"><strong>Описание:</strong> {task.task_description}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            f"""
                            <div style="
                                background-image: url('{random.choice(images)}');
                                background-size: cover;
                                padding: 20px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                            ">
                                <div style="
                                    background-color: {bg_color};
                                    border: 2px solid {border_color};
                                    border-radius: 8px;
                                    padding: 15px;
                                ">
                                    <h3 style="color: #ffd700;">{turn.get('name', 'Неизвестно')}</h3>
                                    <p style="color: #e0e0e0; font-size: 16px;">{turn.get('message', '')}</p>
                                    <p style="color: #a0a0a0; font-size: 12px;">TTS: {"/storage/voice_storage/" + turn.get('name', '') + "_" + st.session_state.get("voice_name") + ".mp3" if not is_dm else ""}</p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Add BossFight task information if applicable
                
                # Добавляем разграничительную черту после каждой грппы ходов, кроме последней
                if i < len(st.session_state.current_game.game_setup.story_progression) - 1:
                    st.markdown("<hr style='border: 1px solid #4a4a4a; margin: 20px 0;'>", unsafe_allow_html=True)


        if st.sidebar.button("🔄 Сбросить игру"):
            st.session_state.current_game = None
            st.success("Игра сброшена. Готовы к новому приключению!")
            st.rerun()

            # Отображение пути до текущей картинки и музыки ниже кнопки сброса

    elif page == "Управление моделями":
        manage_models()


if __name__ == "__main__":
    main()