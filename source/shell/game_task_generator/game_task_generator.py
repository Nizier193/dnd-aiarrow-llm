import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import unittest

from pprint import pprint

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain.prompts import ChatPromptTemplate

import io
import os
import uuid
import types
import json
import random

from source.models.init_models import setup_models
from source.shell.game_task_generator.tasks import tasks

CHAT_MODEL = setup_models.get("CHAT_MODEL")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')

class CodewarsTask:
    task_name: str
    task_difficulty: int
    task_description: str
    task_check_data: any

    def __init__(self, task_name: str, task_difficulty: int, task_description: str, task_check_data: any):
        self.uuid = str(uuid.uuid4())
        self.task_name = task_name
        self.task_difficulty = task_difficulty
        self.task_description = task_description
        self.task_check_data = task_check_data

    def to_dict(self):
        return {
            "task_uuid": self.uuid,
            "task_name": self.task_name,
            "task_difficulty": self.task_difficulty,
            "task_description": self.task_description,
            "task_check_data": self.task_check_data
        }

class CodewarsTaskResult:
    result: str
    error: str = None

    def __init__(self, result: str, error: str = None):
        self.result = result
        self.error = error

class GameTask:
    # Класс для генерации заданий для игры
    # Включает в себя генерацию задания, проверку задания и выдачу подсказки

    def __init__(self):
        self.chat = CHAT_MODEL

    def to_dict(self):
        # // TODO: Добавить в словарь все необходимые данные
        return {
            "chat_model": "ChatModel"
        }

    def get_task_from_codewars(self, difficulty: int = 1) -> CodewarsTask:
        logging.info("game_task_gen - get_task_from_codewars - Получение задания с Codewars")
        # Получить задание с Codewars

        # // TODO: Получить задание с Codewars с заданной сложностью

        current_task = random.choice(tasks)

        from pprint import pprint
        pprint(
            type(current_task)
        )

        return CodewarsTask(
            task_name=current_task["name"],
            task_difficulty=difficulty,
            task_description=current_task["description"],
            task_check_data=current_task["tests"]
        )
    
    def get_task_from_json(self, json_file_path: str) -> CodewarsTask:
        logging.info("game_task_gen - get_task_from_json - Получение задания из JSON файла")
        # Получить задание из JSON файла
        task_data = self.load_tasks_from_json(json_file_path)

        return CodewarsTask(
            task_name=task_data["task_name"],
            task_difficulty=task_data["task_difficulty"],
            task_description=task_data["task_description"],
            task_check_data=task_data["task_check_data"]
        )

    def get_task(self, difficulty: int = 1) -> CodewarsTask:
        logging.info("game_task_gen - get_task - Получение задания")
        # Получить задание с Codewars -> Переписать задание -> Проверить задание -> Выдать подсказку
        task = self.get_task_from_codewars(difficulty)
        task.task_description = self.rewrite_task(task)

        return task

    def execute_task(self, code: str) -> CodewarsTaskResult:
        logging.info("game_task_gen - execute_task - Выполнение задания")
        # Выполнить задание
        # Должна быть функция main() иначе не будет работать

        try:
            local_namespace = {}
            exec(code, globals(), local_namespace)
            
            if 'main' in local_namespace and callable(local_namespace['main']):
                return CodewarsTaskResult(
                    result=local_namespace['main'](),
                    error="",
                )
            else:
                return CodewarsTaskResult(
                    result="",
                    error="Функция main не определена в коде.",
                )
            
        except Exception as e:
            return CodewarsTaskResult(
                result="",
                error=str(e),
            )
        
    def check_task(self, code: str, task: CodewarsTask) -> tuple[bool, list, list]:
        logging.info("game_task_gen - check_task - Проверка задания")
        # Обычная проверка задания
        # Проверить задание
        pprint("task.task_check_data")
        pprint(task.task_check_data)

        fixed_success, fixed_failures, fixed_errors = self.run_tests(code, task.task_check_data)
        
        # Generate random test cases
        random_test_cases = self.generate_random_test_cases(task)
        random_success, random_failures, random_errors = self.run_tests(code, random_test_cases)
        
        return fixed_success and random_success, fixed_failures + random_failures, fixed_errors + random_errors
    
    def rewrite_task(self, task: CodewarsTask) -> str:
        logging.info("game_task_gen - rewrite_task - Переписывание задания")
        # Переписать задание

        template = """
        Учитывая следующий контекст задачи Codewars, перепишите его, чтобы сделать его более ясным и увлекательным:

        Контекст: {context}

        Обязательно укажи, в каком языке программирования нужно написать код.
        Обязательно укажи, что нужно написать функцию main() и с какими параметрами.
        К примеру:
        Язык программирования: Python
        Функция: main(a, b), возвращает c.

        Переписанная задача:
        """

        prompt = PromptTemplate(template=template, input_variables=["context"])
        chain = LLMChain(llm=CHAT_MODEL, prompt=prompt)

        rewritten_problem = chain.run(context=task.task_description)
        task.task_description = rewritten_problem

        return task.task_description

    def get_hint(self, code: str, task: CodewarsTask) -> str:
        logging.info("game_task_gen - get_hint - Получение подсказки")
        # Получить подсказку

        prompt = PromptTemplate(
            input_variables=["problem_description", "user_code"],
            template=""" 
Дайте полезную подсказку, не раскрывая полного решения, основываясь на следующем описании проблемы Codewars и черновике кода пользователя:

Описание проблемы:
{problem_description}

Черновик кода пользователя:
{user_code}

Подсказка:
"""
        )

        chain = LLMChain(llm=CHAT_MODEL, prompt=prompt)
        return chain.run(problem_description=task.task_description, user_code=code)

    def run_tests(self, solution_code: str, test_cases: list) -> tuple[bool, list, list]:
        logging.info("game_task_gen - run_tests - Запуск тестов")
        # Запуск всех тестов
        # Код всегда должен содержать функцию function()
        
        # Create a new module to hold the solution code
        module = types.ModuleType('solution')

        pprint("solution_code")
        pprint(solution_code)

        pprint("test_cases")
        pprint(test_cases)
        
        # Execute the solution code in the module's namespace
        try:
            exec(solution_code, module.__dict__)
        except Exception as e:
            return False, [], [(None, f"Error in code execution: {str(e)}")]
        
        # Create a test class dynamically
        class SolutionTest(unittest.TestCase):
            pass
        
        # Add test methods to the test class
        for i, (input_data, expected_output) in enumerate(test_cases):

            def create_test(input_data, expected_output):
                def test(self):
                    # Call the solution function
                    result = module.main(*input_data)
                    
                    # Check if the result matches the expected output
                    self.assertEqual(result, expected_output)
                
                return test
            
            test_method = create_test(input_data, expected_output)
            setattr(SolutionTest, f'test_case_{i}', test_method)
        
        # Run the tests
        test_suite = unittest.TestLoader().loadTestsFromTestCase(SolutionTest)
        test_result = unittest.TextTestRunner(stream=io.StringIO()).run(test_suite)

        pprint("test_result")
        pprint(test_result.wasSuccessful())
        pprint("test_result.failures")
        pprint(test_result.failures)
        pprint("test_result.errors")
        pprint(test_result.errors)
        
        # Return the test results
        return test_result.wasSuccessful(), test_result.failures, test_result.errors

    def generate_random_test_cases(self, task: CodewarsTask) -> list:
        logging.info("game_task_gen - generate_random_test_cases - Генерация случайных тестов")
        # This method should be implemented to generate random test cases based on the task
        # For now, we'll return an empty list
        return []

    @staticmethod
    def load_tasks_from_json(json_file_path: str) -> dict:
        logging.info("game_task_gen - load_tasks_from_json - Загрузка задач из JSON")
        with open(json_file_path, 'r') as file:
            return json.load(file)

    def run_task(self, code: str, task: CodewarsTask) -> bool:
        logging.info("game_task_gen - run_task - Запуск задания")
        # Запуск задания 
        codewars_task = task
        
        # Run the tests
        success, failures, errors = self.check_task(code, codewars_task)
        
        print("Test Results:")
        if success:
            print("All tests passed!")
        else:
            print("Some tests failed:")
            for failure in failures:
                print(f"- {failure[0]}: {failure[1]}")
            for error in errors:
                print(f"- {error[0]}: {error[1]}")
        
        return success

    def explain_solution(self, task: CodewarsTask, solution: str) -> str:
        logging.info("game_task_gen - explain_solution - Объяснение решения")
        # Create a prompt template
        prompt_template = ChatPromptTemplate.from_template(
            """
            Вы - полезный помощник, объясняющий решения программных задач.

            Описание проблемы:
            {problem_description}

            Решение:
            {solution}

            Объясните, как работает это решение, шаг за шагом:
            """
        )

        # Create an LLMChain
        chain = LLMChain(llm=self.chat, prompt=prompt_template)

        # Run the chain
        response = chain.run(problem_description=task.task_description, solution=solution)

        return response