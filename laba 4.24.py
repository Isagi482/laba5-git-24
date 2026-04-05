import os
import csv
from typing import List, Iterator, Generator


class Record:
    """Базовый класс для всех записей"""
    
    def __init__(self, record_id: int):
        self._id = record_id
    
    @property
    def id(self):
        return self._id
    
    def __repr__(self):
        return f"Record(id={self._id})"



class Call(Record):
    """
    Класс, описывающий один входящий звонок в call-центр.
    Наследуется от Record.
    """
    
    # Статический метод для валидации телефона
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Проверяет, что телефон состоит только из цифр и имеет длину 11"""
        return phone.isdigit() and len(phone) == 11
    
    # Статический метод для валидации причины обращения
    @staticmethod
    def validate_reason(reason: str) -> bool:
        """Проверяет, что причина обращения не пустая"""
        return bool(reason and reason.strip())
    
    def __init__(self, call_id: int, phone: str, reason: str, solved: bool):
        super().__init__(call_id)  # вызов конструктора родителя
        self._phone = phone
        self._reason = reason
        self._solved = solved

    
    def __setattr__(self, name, value):
        """
        Перегрузка __setattr__ для контроля присваивания свойств.
        Вызывается при любой попытке установить атрибут.
        """
        if name == '_phone':
            if not self.validate_phone(value):
                raise ValueError(f"Некорректный номер телефона: {value}. Должно быть 11 цифр.")
        elif name == '_reason':
            if not self.validate_reason(value):
                raise ValueError(f"Некорректная причина обращения: {value}")
        elif name == '_solved':
            if not isinstance(value, bool):
                raise ValueError(f"Поле solved должно быть bool, получено {type(value)}")
        
        # Вызываем родительский __setattr__ для реального присваивания
        super().__setattr__(name, value)
    
    @property
    def phone(self):
        return self._phone
    
    @property
    def reason(self):
        return self._reason
    
    @property
    def solved(self):
        return self._solved

    
    def __repr__(self):
        """Удобный вывод объекта"""
        solved_str = "Решена" if self._solved else "Не решена"
        return f"Call(№{self._id}, тел:{self._phone}, причина:'{self._reason}', {solved_str})"
    
    def __eq__(self, other):
        """Сравнение звонков по номеру"""
        if isinstance(other, Call):
            return self._id == other._id
        return False
    

class CallCenter:
    """
    Класс для работы с коллекцией звонков.
    Реализует итератор, доступ по индексу, генераторы.
    """
    
    def __init__(self, calls: List[Call] = None):
        self._calls = calls if calls else []

    
    def __getitem__(self, index: int) -> Call:
        """Позволяет обращаться по индексу: call_center[0]"""
        return self._calls[index]
    
    def __len__(self) -> int:
        return len(self._calls)

    
    def __iter__(self) -> Iterator[Call]:
        """Позволяет перебирать звонки в цикле for"""
        return iter(self._calls)
    
    def filter_by_solved(self, solved: bool = True) -> Generator[Call, None, None]:
        """
        Генератор, возвращающий звонки с заданным статусом решения.
        """
        for call in self._calls:
            if call.solved == solved:
                yield call
    
    def filter_by_reason(self, keyword: str) -> Generator[Call, None, None]:
        """
        Генератор, возвращающий звонки, где причина обращения содержит ключевое слово.
        """
        for call in self._calls:
            if keyword.lower() in call.reason.lower():
                yield call
    
    def add_call(self, call: Call):
        """Добавляет звонок в коллекцию"""
        self._calls.append(call)
    
    def sort_by_id(self) -> List[Call]:
        """Сортирует по номеру звонка"""
        return sorted(self._calls, key=lambda c: c.id)
    
    def sort_by_reason(self) -> List[Call]:
        """Сортирует по причине обращения"""
        return sorted(self._calls, key=lambda c: c.reason)

    
    @staticmethod
    def read_from_csv(filename: str):
        """Статический метод: читает CSV файл и возвращает список звонков"""
        calls = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    call = Call(
                        call_id=int(row['№']),
                        phone=row['телефон'],
                        reason=row['причина_обращения'],
                        solved=row['проблема_решена'].lower() in ['да', 'true', '1']
                    )
                    calls.append(call)
        except FileNotFoundError:
            print(f"Файл {filename} не найден!")
        except Exception as e:
            print(f"Ошибка при чтении: {e}")
        return CallCenter(calls)
    
    @staticmethod
    def save_to_csv(filename: str, call_center):
        """Статический метод: сохраняет звонки в CSV файл"""
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['№', 'телефон', 'причина_обращения', 'проблема_решена'])
            for call in call_center:
                solved_str = 'Да' if call.solved else 'Нет'
                writer.writerow([call.id, call.phone, call.reason, solved_str])
        print(f"Данные сохранены в {filename}")
    
    def __repr__(self):
        return f"CallCenter({len(self._calls)} звонков)"


def count_files_in_directory(directory_path: str) -> int:
    """Считает количество файлов в указанной директории"""
    if not os.path.exists(directory_path):
        print(f"Папка {directory_path} не найдена!")
        return 0
    
    count = 0
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            count += 1
    return count


def main():
    print("=" * 60)
    print("Лабораторная работа №4. Классы.")
    print("Вариант 24: История входящих звонков call-центра")
    print("=" * 60)
    
    # Пути к файлам
    DATA_FILE = r"C:\Users\Kholm\OneDrive\Desktop\laba rpp\data.cvm.txt"
    DIRECTORY = r"C:\Users\Kholm\OneDrive\Desktop\laba rpp"

    file_count = count_files_in_directory(DIRECTORY)
    print(f"\nКоличество файлов в папке '{DIRECTORY}': {file_count}")

    call_center = CallCenter.read_from_csv(DATA_FILE)
    
    if len(call_center) == 0:
        print(f"\nНет данных. Создайте файл {DATA_FILE} с заголовками:")
        print("№,телефон,причина_обращения,проблема_решена")
        return
    
    print(f"\nЗагружено звонков: {len(call_center)}")

    print("\n=== Демонстрация __repr__ ===")
    print(call_center)
    print(call_center[0])  # __getitem__

    print("\n=== Итератор (перебор всех звонков) ===")
    for call in call_center:
        print(f"  {call}")

    print("\n=== Сортировка по причине обращения ===")
    sorted_by_reason = call_center.sort_by_reason()
    for call in sorted_by_reason:
        print(f"  {call}")
    
    print("\n=== Сортировка по номеру звонка ===")
    sorted_by_id = call_center.sort_by_id()
    for call in sorted_by_id:
        print(f"  {call}")

    print("\n=== Генератор: только решённые проблемы ===")
    for call in call_center.filter_by_solved(solved=True):
        print(f"  {call}")
    
    print("\n=== Генератор: поиск по ключевому слову 'интернет' ===")
    for call in call_center.filter_by_reason("интернет"):
        print(f"  {call}")
 
    print("\n=== Демонстрация валидации через __setattr__ ===")
    try:
        invalid_call = Call(99, "123", "Тест", True)  # неверный телефон
    except ValueError as e:
        print(f"  Ошибка при создании: {e}")
    
    try:
        invalid_call = Call(99, "89231234567", "", True)  # пустая причина
    except ValueError as e:
        print(f"  Ошибка при создании: {e}")

    add_choice = input("\nХотите добавить новый звонок? (Да/Нет): ").strip().lower()
    if add_choice in ['да', 'yes', '1']:
        try:
            new_id = max([call.id for call in call_center]) + 1 if len(call_center) > 0 else 1
            phone = input("Введите телефон (11 цифр): ")
            reason = input("Введите причину обращения: ")
            solved = input("Проблема решена? (Да/Нет): ").strip().lower() in ['да', 'yes', '1']
            
            new_call = Call(new_id, phone, reason, solved)
            call_center.add_call(new_call)
            print(f"Добавлен: {new_call}")
            
            # Сохранение
            save_choice = input("\nСохранить изменения в файл? (Да/Нет): ").strip().lower()
            if save_choice in ['да', 'yes', '1']:
                CallCenter.save_to_csv(DATA_FILE, call_center)
                
        except ValueError as e:
            print(f"Ошибка: {e}")
    
    print("\nПрограмма завершена.")


# Запуск
if __name__ == "__main__":
    main()
