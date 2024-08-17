import os
import time
import threading
import pygame
import pygame.mixer
import speech_recognition as sr
from rich.console import Console
from rich.panel import Panel
import logging  # Импортируем модуль logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

def log(message, log_type):
    # Функция для вывода сообщений в консоль
    console.print(Panel(f"[bold]{message}[/bold]", title=f"[{log_type}]", border_style="cyan"))

class GameSounds():
    # Путь к папке с голосовыми файлами
    TTS_PATH = os.path.join(os.path.dirname(__file__), "voice_storage")

    def __init__(self):
        logger.info("Initializing GameSounds")  # Логирование
        # Инициализация звуков и распознавания речи
        self.sounds = {
            "beep": os.path.join(self.TTS_PATH, "test.mp3")
        }
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        self.bg_music_channel = pygame.mixer.Channel(0)
        self.tts_channel = pygame.mixer.Channel(1)
        self.sfx_channel = pygame.mixer.Channel(2)
        self.stop_bg_music = threading.Event()
        self.stop_tts = threading.Event()
        self.bg_music_thread = None
        self.tts_thread = None

    def play_background_music(self, music_file):
        logger.info(f"Playing background music: {music_file}")  # Логирование
        def music_player():
            try:
                bg_music = pygame.mixer.Sound(music_file)
                self.bg_music_channel.play(bg_music, loops=-1)
                log(f"Начало воспроизведения фоновой музыки: {music_file}", "ФОНОВАЯ МУЗЫКА")
                while not self.stop_bg_music.is_set():
                    pygame.time.wait(100)
                self.bg_music_channel.stop()
                log("Остановка фоновой музыки", "ФОНОВАЯ МУЗЫКА")
            except Exception as e:
                log(f"Ошибка воспроизведения фоновой музыки: {str(e)}", "ОШИБКА")

        self.stop_bg_music.clear()
        self.bg_music_thread = threading.Thread(target=music_player)
        self.bg_music_thread.start()

    def stop_background_music(self):
        logger.info("Stopping background music")  # Логирование
        if self.bg_music_thread and self.bg_music_thread.is_alive():
            self.stop_bg_music.set()
            self.bg_music_thread.join()

    def play_tts(self, tts_file):
        logger.info(f"Playing TTS: {tts_file}")  # Логирование
        def tts_player():
            try:
                tts_sound = pygame.mixer.Sound(tts_file)
                self.tts_channel.play(tts_sound)
                log(f"Начало воспроизведения TTS: {tts_file}", "TTS")
                while self.tts_channel.get_busy() and not self.stop_tts.is_set():
                    pygame.time.wait(100)
                self.tts_channel.stop()
                log("Остановка TTS", "TTS")
            except Exception as e:
                log(f"Ошибка воспроизведения TTS: {str(e)}", "ОШИБКА")

        self.stop_tts.clear()
        self.tts_thread = threading.Thread(target=tts_player)
        self.tts_thread.start()

    def stop_tts(self):
        logger.info("Stopping TTS")  # Логирование
        if self.tts_thread and self.tts_thread.is_alive():
            self.stop_tts.set()
            self.tts_thread.join()

    def play_sound(self, sound_name):
        logger.info(f"Playing sound: {sound_name}")  # Логирование
        try:
            sound = pygame.mixer.Sound(self.sounds[sound_name])
            self.sfx_channel.play(sound)
            log(f"Воспроизведен звук {sound_name}", "ВОСПРОИЗВЕДЕНИЕ ЗВУКА")
        except Exception as e:
            raise Exception(f"Ошибка воспроизведения аудио файла: {str(e)}")

    def recognize_speech(self, duration: int):
        logger.info("Recognizing speech")  # Логирование
        try:
            with sr.Microphone() as source:
                console.print("[yellow]Настройка под окружающий шум...[/yellow]")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                console.print(f"[green]Слушаю в течение {duration} секунд...[/green]")
                audio = self.recognizer.listen(source, timeout=duration)
                
                console.print("[yellow]Распознавание речи...[/yellow]")
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                
                log(f"Распознанный текст: {text}", "РАСПОЗНАВАНИЕ РЕЧИ")
                return text
        except sr.WaitTimeoutError:
            log("Время ожидания истекло. Речь не обнаружена.", "ТАЙМАУТ")
        except sr.UnknownValueError:
            log("Речь не распознана", "ОШИБКА РАСПОЗНАВАНИЯ")
        except sr.RequestError as e:
            log(f"Ошибка сервиса распознавания речи: {e}", "ОШИБКА СЕРВИСА")
        except Exception as e:
            log(f"Неизвестная ошибка: {e}", "ОШИБКА")
        
        return None