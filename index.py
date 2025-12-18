"""
Модуль для управления коллекцией шифрованных текстов.
Поддерживает команды ADD, REM, PRINT из внешнего файла.
"""

from typing import List, Literal, Dict, Any
from enum import Enum
import operator


class CipherType(str, Enum):
    """Типы поддерживаемых шифров."""

    SHIFT = "shift"
    SUBSTITUTION = "substitution"


class CommandType(str, Enum):
    """Поддерживаемые команды."""

    ADD = "ADD"
    REM = "REM"
    PRINT = "PRINT"


FIELD_MAPPING = {"owner": "name", "text": "source_str", "shift": "shift_by"}


class CipherText:
    """Базовый класс для шифрованного текста."""

    def __init__(self, source_str: str, name: str):
        self.source_str: str = source_str
        self.name: str = name

    def info(self) -> str:
        """Возвращает строковое описание объекта."""
        return f"Владелец: {self.name}, Текст: {self.source_str}"


class ShiftCipherText(CipherText):
    """Шифр сдвига (Шифр Цезаря)."""

    def __init__(self, source_str: str, name: str, shift_by: int):
        super().__init__(source_str, name)
        self.shift_by: int = shift_by

    def info(self) -> str:
        return f"[Сдвиг] {super().info()}, Сдвиг: {self.shift_by}"


class SubstitutionCipherText(CipherText):
    """Шифр замены."""

    def __init__(
        self, source_str: str, name: str, source_alpha: str, target_alpha: str
    ):
        super().__init__(source_str, name)
        self.source_alpha: str = source_alpha
        self.target_alpha: str = target_alpha

    def info(self) -> str:
        return f"[Замена] {super().info()}, Алфавиты: {self.source_alpha}->{self.target_alpha}"


class CipherManager:
    """Класс для управления списком шифрованных текстов."""

    def __init__(self):
        self._container: List[CipherText] = []

    def add(self, args: List[str]) -> None:
        """Обрабатывает аргументы команды ADD и добавляет объект в контейнер."""
        params = self._parse_args(args)
        c_type = params.get("type")

        try:
            if c_type == CipherType.SUBSTITUTION:
                self._container.append(
                    SubstitutionCipherText(
                        source_str=params["text"],
                        name=params["owner"],
                        source_alpha=params["source"],
                        target_alpha=params["target"],
                    )
                )
            elif c_type == CipherType.SHIFT:
                self._container.append(
                    ShiftCipherText(
                        source_str=params["text"],
                        name=params["owner"],
                        shift_by=int(params["shift"]),
                    )
                )
            else:
                print(f"Ошибка: Неизвестный или отсутствующий тип шифра: {c_type}")

        except KeyError as error:
            print(f"Ошибка добавления: отсутствует обязательное поле {error}")
        except ValueError:
            print("Ошибка: параметр 'shift' должен быть числом")

    def remove(self, condition_str: str) -> None:
        """
        Удаляет объекты, соответствующие условию.
        Поддерживает операторы >, <, =.
        """
        ops = {">": operator.gt, "<": operator.lt, "=": operator.eq}

        found_op = next((op for op in ops if op in condition_str), None)
        if not found_op:
            print(f"Ошибка REM: Не найден оператор сравнения в '{condition_str}'")
            return

        key_raw, val_str = condition_str.split(found_op, 1)

        attr_name = FIELD_MAPPING.get(key_raw, key_raw)

        initial_len = len(self._container)

        self._container = [
            obj
            for obj in self._container
            if not self._should_remove(obj, attr_name, found_op, val_str, ops)
        ]

        print(f"Удалено объектов: {initial_len - len(self._container)}")

    def print_all(self) -> None:
        """Выводит информацию обо всех объектах в консоль."""
        print("\n--- Содержимое контейнера ---")
        if not self._container:
            print("Контейнер пуст.")
        for i, obj in enumerate(self._container, 1):
            print(f"{i}. {obj.info()}")

    def _parse_args(self, args: List[str]) -> Dict[str, str]:
        """Превращает список ['key=val', ...] в словарь."""
        data = {}
        for item in args:
            if "=" in item:
                key, value = item.split("=", 1)
                data[key] = value
        return data

    def _should_remove(
        self,
        obj: CipherText,
        attr_name: str,
        op_symbol: str,
        val_str: str,
        ops: Dict[str, Any],
    ) -> bool:
        """Проверяет, нужно ли удалять конкретный объект по условию."""
        if not hasattr(obj, attr_name):
            return False

        obj_val = getattr(obj, attr_name)

        try:
            target_val = type(obj_val)(val_str)
            return ops[op_symbol](obj_val, target_val)
        except ValueError:
            return False


Commands = Literal["ADD", "REM", "PRINT"]
CipherMethod = Literal["shift", "substitution"]

COMMAND_LIST: List[Commands] = ["ADD", "REM", "PRINT"]


results: List[CipherText] = []


def main():
    """Главная функция запуска обработки файла."""
    filename = "test.txt"
    manager = CipherManager()

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue

                command = parts[0]
                args = parts[1:]

                if command == CommandType.ADD:
                    manager.add(args)
                elif command == CommandType.PRINT:
                    manager.print_all()
                elif command == CommandType.REM:
                    if args:
                        manager.remove(args[0])
                    else:
                        print("Ошибка REM: пропущено условие")
                else:
                    # Игнорируем или логируем неизвестные команды
                    pass

    except FileNotFoundError:
        print(f"Файл {filename} не найден.")


if __name__ == "__main__":
    main()
