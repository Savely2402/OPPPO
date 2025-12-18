
from typing import List, Literal, Dict


class CipherText:
    def __init__(self, sourcestr: str, name: str):
        self.sourcestr: str = sourcestr
        self.name: str = name

    def info(self) -> str:
        return f"Владелец: {self.name}, Текст: {self.sourcestr}"


class ShiftCipherText(CipherText):
    def __init__(self, sourcestr: str, name: str, shift_by: int):
        super().__init__(sourcestr, name)
        self.shift_by: int = shift_by

    def info(self) -> str:
        return f"[Сдвиг] {super().info()}, Сдвиг: {self.shift_by}"


class SubstitutionCipherText(CipherText):

    def __init__(self, sourcestr: str, name: str, source_alpha: str, target_alpha: str):
        super().__init__(sourcestr, name)
        self.source_alpha: str = source_alpha
        self.target_alpha: str = target_alpha

    def info(self) -> str:
        return f"[Замена] {super().info()}, Алфавиты: {self.source_alpha}->{self.target_alpha}"


Commands = Literal['ADD', 'REM', 'PRINT']
CipherMethod = Literal['shift', 'substitution']

COMMAND_LIST: List[Commands] = ['ADD', 'REM', 'PRINT']


results: List[CipherText] = []


def parse_line_to_dict(args: List[str]) -> Dict[str, str]:
    data = {}
    for item in args:
        if '=' in item:
            key, value = item.split('=', 1)
            data[key] = value
    return data


def execute_add_command(args: List[str]):
    params = parse_line_to_dict(args)

    try:
        c_type = params.get('type')
        owner = params.get('owner')
        text = params.get('text')

        if not (c_type and owner and text):
            print(f"Ошибка: Неполные данные в строке: {args}")
            return

        if c_type == 'substitution':
            src = params.get('source')
            tgt = params.get('target')
            if src and tgt:
                obj = SubstitutionCipherText(text, owner, src, tgt)
                results.append(obj)
            else:
                print("Ошибка: Не указаны алфавиты (source/target)")

        elif c_type == 'shift':
            shift_val = params.get('shift')
            if shift_val:
                obj = ShiftCipherText(text, owner, int(shift_val))
                results.append(obj)
            else:
                print("Ошибка: Не указан сдвиг (shift)")

        else:
            print(f"Неизвестный тип: {c_type}")

    except ValueError:
        print("Ошибка: Некорректное число")


def execute_rem_command(condition_str: str):
    global results

    operator = None
    if '>' in condition_str:
        operator = '>'
    elif '<' in condition_str:
        operator = '<'
    elif '=' in condition_str:
        operator = '='

    if not operator:
        print(
            f"Ошибка REM: Не найден оператор сравнения (>, <, =) в '{condition_str}'")
        return

    key, val_str = condition_str.split(operator)

    key_mapping = {
        'owner': 'name',
        'text': 'sourcestr',
        'shift': 'shift_by'
    }

    attr_name = key_mapping.get(key, key)

    new_results = []
    removed_count = 0

    for obj in results:
        if not hasattr(obj, attr_name):
            new_results.append(obj)
            continue

        obj_val = getattr(obj, attr_name)

        try:
            target_val = type(obj_val)(val_str)
        except ValueError:
            new_results.append(obj)
            continue

        should_remove = False
        if operator == '=':
            should_remove = obj_val == target_val
        elif operator == '>':
            if isinstance(obj_val, (int, float)):
                should_remove = obj_val > target_val
        elif operator == '<':
            if isinstance(obj_val, (int, float)):
                should_remove = obj_val < target_val

        if should_remove:
            removed_count += 1
        else:
            new_results.append(obj)

    results = new_results
    print(f"Удалено объектов: {removed_count}")


def execute_print_command(objects: List[CipherText]):
    for obj in objects:
        print(obj.info())


with open('test.txt', 'r', encoding='utf-8') as f:
    for line in f:
        objData = line.split(' ')

        command = objData[0].strip()

        if command == 'ADD':
            execute_add_command(objData)
        elif command == 'PRINT':
            execute_print_command(results)
        elif command == 'REM':
            if len(objData) > 1:
                condition = objData[1]
                execute_rem_command(condition)
            else:
                print("Ошибка: Пустое условие для REM")
