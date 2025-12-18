import unittest
from index import CipherManager, ShiftCipherText, SubstitutionCipherText, CipherType


class TestCipherManager(unittest.TestCase):
    """
    Набор модульных тестов для класса CipherManager.
    Проверяет основные сценарии добавления, удаления и валидации данных.
    """

    def setUp(self):
        """Выполняется перед КАЖДЫМ тестом. Создает чистый менеджер."""
        self.manager = CipherManager()

    # --- ТЕСТЫ НА УСПЕШНОЕ ВЫПОЛНЕНИЕ (Positive Tests) ---

    def test_add_shift_cipher_success(self):
        """Проверка успешного добавления шифра сдвига."""
        args = ['type=shift', 'owner=TestUser', 'text=Hello', 'shift=3']
        self.manager.add(args)

        # Проверяем, что в контейнере 1 объект
        self.assertEqual(len(self.manager._container), 1)

        # Проверяем тип созданного объекта и его поля
        obj = self.manager._container[0]
        self.assertIsInstance(obj, ShiftCipherText)
        self.assertEqual(obj.name, 'TestUser')
        self.assertEqual(obj.shift_by, 3)

    def test_add_substitution_cipher_success(self):
        """Проверка успешного добавления шифра замены."""
        args = ['type=substitution', 'owner=Alice',
                'text=Secret', 'source=abc', 'target=def']
        self.manager.add(args)

        self.assertEqual(len(self.manager._container), 1)
        obj = self.manager._container[0]
        self.assertIsInstance(obj, SubstitutionCipherText)
        self.assertEqual(obj.source_alpha, 'abc')

    def test_remove_by_condition_success(self):
        """Проверка удаления объектов по условию (shift > 5)."""
        # Добавляем два объекта
        self.manager.add(['type=shift', 'owner=User1',
                         'text=A', 'shift=3'])  # Оставим
        self.manager.add(['type=shift', 'owner=User2',
                         'text=B', 'shift=10'])  # Удалим

        # Выполняем удаление
        self.manager.remove('shift>5')

        # Должен остаться только один
        self.assertEqual(len(self.manager._container), 1)
        self.assertEqual(self.manager._container[0].shift_by, 3)

    def test_remove_by_string_equality(self):
        """Проверка удаления по строковому равенству (owner=Bob)."""
        self.manager.add(['type=shift', 'owner=Bob', 'text=Msg1', 'shift=1'])
        self.manager.add(['type=shift', 'owner=Alice', 'text=Msg2', 'shift=1'])

        self.manager.remove('owner=Bob')

        self.assertEqual(len(self.manager._container), 1)
        self.assertEqual(self.manager._container[0].name, 'Alice')

    # --- ТЕСТЫ НА ИСКЛЮЧИТЕЛЬНЫЕ СИТУАЦИИ (Negative Tests) ---

    def test_add_missing_required_fields(self):
        """Проверка обработки неполных данных (нет text)."""
        # Попытка добавить без поля text
        args = ['type=shift', 'owner=User', 'shift=5']
        self.manager.add(args)

        # Объект не должен быть добавлен (длина контейнера 0)
        self.assertEqual(len(self.manager._container), 0)

    def test_add_invalid_number_format(self):
        """Проверка обработки некоректного числа (shift=abc)."""
        args = ['type=shift', 'owner=User', 'text=Hi', 'shift=not_a_number']
        self.manager.add(args)

        # Объект не должен быть добавлен из-за ValueError
        self.assertEqual(len(self.manager._container), 0)

    def test_add_unknown_cipher_type(self):
        """Проверка обработки неизвестного типа шифра."""
        args = ['type=ufo_cipher', 'owner=Alien', 'text=Beep']
        self.manager.add(args)

        self.assertEqual(len(self.manager._container), 0)

    def test_remove_with_invalid_condition_format(self):
        """Проверка REM с условием без оператора."""
        self.manager.add(['type=shift', 'owner=User', 'text=Hi', 'shift=3'])

        # Передаем некорректную строку условия (нет >, < или =)
        self.manager.remove('shift_is_5')

        # Объект не должен удалиться
        self.assertEqual(len(self.manager._container), 1)


if __name__ == '__main__':
    unittest.main()
