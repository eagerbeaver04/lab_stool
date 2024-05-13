import math
import os
import json
from typing import Union
import task


class InvalidValueError(Exception):
    """
    Исключение, возникающее при неустойчивом положении табуретки.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str = 'Центр тяжести в неустойчивом положении табуретка упала'):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f'{self.message}'


class InvalidValueAngle(Exception):
    """
    Исключение, возникающее при превышении максимального уровня наклона табуретки.

    Attributes:
        value (float): Значение угла, приведшее к ошибке.
        message (str): Сообщение об ошибке.
    """

    def __init__(self, value: float, message: str = "Превышен максимальный уровень наклона, бруски упали"):
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Значение {self.value} - {self.message}"


class Result:
    """
    Класс для хранения и сохранения результата моделирования в формате JSON.

    Attributes:
        result (Union[str, int]): Результат моделирования.
        name (str): Имя пользователя.
    """

    def __init__(self, result: Union[str, float], name: str):
        self.result = result
        self.name = name

    def _res_to_dict(self) -> dict:
        """
        Преобразует результат моделирования в словарь.

        Returns:
            dict: Словарь с результатом моделирования.
        """
        return {self.name: self.result}

    def res_to_json(self) -> None:
        """
        Сохраняет результат моделирования в формате JSON.
        """
        data_dict = self._res_to_dict()
        file_path = 'grades.json'

        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump({}, file)

        with open('result.json', 'r', encoding='UTF-8') as file:
            json_data = json.load(file)
        json_data.update(data_dict)
        with open('result.json', 'w', encoding='UTF-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)


class Chair:
    """
    Класс для моделирования движения табуретки.

    Attributes:
        length_wood (float): Длина брусков.
        length_leg (float): Длина ножек табуретки.
        length_chair (float): Длина сидушки табуретки.
        wood_weight (float): Вес брусков.
        time (float): Время моделирования.
        pause (float): Пауза между движениями.
        time_step (float): Время шага.
        wood_mu (float): Коэффициент трения брусков о табуретку.
        pos_1 (float): Позиция передних ног табуретки.
        pos_2 (float): Позиция задних ног табуретки.
        pos_chair_1 (float): Позиция переднего края табуретки.
        pos_chair_2 (float): Позиция заднего края табуретки.
    """

    def __init__(self, length_wood: float, length_leg: float, length_chair: float, wood_weight: float, time: float,
                 pause: float, time_step: float, wood_mu: float):
        self.length_wood = length_wood
        self.length_leg = length_leg
        self.length_chair = length_chair
        self.wood_weight = wood_weight
        self.wood_mu = wood_mu
        self.alpha_max = math.atan(wood_mu)
        self.time = time
        self.pause = pause
        self.time_step = time_step
        self.pos_1 = length_chair
        self.pos_2 = 0
        self.pos_chair_1 = self.pos_1
        self.pos_chair_2 = self.pos_2

    def _check_position(self) -> None:
        """
        Проверяет, находится ли табуретка в устойчивом положении.

        Raises:
            InvalidValueError: Если табуретка в неустойчивом положении.
        """
        if self.pos_chair_1 - (self.pos_chair_1 - self.pos_chair_2) / 2 > self.pos_1 or self.pos_chair_1 - (
                self.pos_chair_1 - self.pos_chair_2) / 2 < self.pos_2:
            raise InvalidValueError

    def move(self, way_1: float, way_2: float) -> float:
        """
        Моделирует движение табуретки.

        Args:
            way_1 (float): Расстояние, на которое табуретка смещаются передние ноги табуретки.
            way_2 (float): Расстояние, на которое табуретка смещаются задние ноги табуретки.

        Returns:
            float: Общее пройденное расстояние.
        """
        total_way = 0
        timer = 0
        while timer < self.time:
            self.pos_1 += way_1
            alpha_1 = math.asin((self.length_leg - math.tan(
                math.acos(abs(self.pos_chair_1 - self.pos_1) / self.length_leg)) * way_1) / self.length_chair)
            if alpha_1 > self.alpha_max:
                raise InvalidValueAngle(alpha_1)
            total_way += way_1
            self.pos_chair_1 += way_1
            timer += self.time_step + self.pause
            self.pos_chair_2 += way_1
            alpha_2 = math.asin((self.length_leg - math.tan(
                math.acos(abs(self.pos_chair_2 - self.pos_2) / self.length_leg)) * way_2) / self.length_chair)

            if alpha_2 > self.alpha_max:
                raise InvalidValueAngle(alpha_2)
            self.pos_2 += way_2
            timer += self.time_step + self.pause
            self._check_position()
        return total_way


if __name__ == '__main__':
    chair = Chair(40, 60, 80, 2, 1000, 2, 2, 0.1)
    if type(task.student) is str and type(task.front_legs_distance) in (float, int) and type(task.back_legs_distance) in (int, float):
        name = task.student
        way_1, way_2 = task.front_legs_distance, task.back_legs_distance
        try:
            res = chair.move(way_1, way_2)
            if res >= 3733.022748825491:
                answer = 5
            elif res > 0.99 * 3733.022748825491:
                answer = 4
            else:
                answer = 3
            result = Result(answer, name)
            result.res_to_json()
        except Exception as e:
            result = Result(str(e), name)
            result.res_to_json()
    else:
        print('Неверные входные данные')
