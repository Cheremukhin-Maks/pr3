from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable):
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(*args, **kwargs)


class SortStrategy(ABC):

    @abstractmethod
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        pass

class SortByPriority(SortStrategy):
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.priority)


class SortByDeadline(SortStrategy):
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.deadline)


class SortByCreationDate(SortStrategy):

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.created_at, reverse=True)

@dataclass
class Task:
    title: str
    priority: int
    deadline: datetime
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class TaskModel(EventEmitter):

    def __init__(self):
        super().__init__()
        self._tasks: list[Task] = []

    def add_task(self, title: str, priority: int, deadline: datetime):
        task = Task(title=title, priority=priority, deadline=deadline)
        self._tasks.append(task)
        self.emit("task_added", task)

    def complete_task(self, index: int):
        if 0 <= index < len(self._tasks):
            task = self._tasks[index]
            task.completed = True
            self.emit("task_completed", task)

    def remove_task(self, index: int):
        if 0 <= index < len(self._tasks):
            task = self._tasks.pop(index)
            self.emit("task_removed", task)

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        if include_completed:
            return self._tasks[:]
        return [task for task in self._tasks if not task.completed]

    def get_statistics(self) -> dict:
        total = len(self._tasks)
        completed = sum(1 for task in self._tasks if task.completed)
        active = total - completed
        return {"total": total, "completed": completed, "active": active}

class TaskView:

    def show_tasks(self, tasks: list[Task], title: str = "Завдання"):
        print(f"\n--- {title} ---")
        if not tasks:
            print("Список завдань порожній.")
            return

        header = f"{'№':<4} | {'Назва':<25} | {'Пріоритет':<10} | {'Дедлайн':<19} | {'Статус':<10}"
        print(header)
        print("-" * len(header))

        for idx, task in enumerate(tasks, 1):
            status = "Виконано" if task.completed else "Активне"
            deadline_str = task.deadline.strftime("%Y-%m-%d %H:%M")
            print(
                f"{idx:<4} | {task.title:<25} | {task.priority:<10} | {deadline_str:<19} | {status:<10}"
            )

    def show_message(self, message: str):
        print(f"[INFO] {message}")

    def show_statistics(self, stats: dict):
        print("\n--- Статистика ---")
        print(f"Всього завдань: {stats.get('total', 0)}")
        print(f"Виконано:      {stats.get('completed', 0)}")
        print(f"Активних:      {stats.get('active', 0)}")

class TaskController:

    def __init__(self, model: TaskModel, view: TaskView):
        self._model = model
        self._view = view
        self._sort_strategy: SortStrategy = SortByPriority()

        self._model.on(
            "task_added",
            lambda task: self._view.show_message(f"Додано завдання: '{task.title}'"),
        )
        self._model.on(
            "task_completed",
            lambda task: self._view.show_message(f"Завдання виконано: '{task.title}'"),
        )
        self._model.on(
            "task_removed",
            lambda task: self._view.show_message(f"Видалено завдання: '{task.title}'"),
        )

    def set_sort_strategy(self, strategy: SortStrategy):
        """Змінити стратегію сортування (Strategy)."""
        self._sort_strategy = strategy

    def add_task(self, title: str, priority: int, deadline: datetime):
        self._model.add_task(title, priority, deadline)

    def complete_task(self, index: int):
        self._model.complete_task(index)

    def show_all(self):
        tasks = self._model.get_tasks()
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks, title="Усі завдання")

    def show_active(self):
        tasks = self._model.get_tasks(include_completed=False)
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks, title="Активні завдання")

    def show_stats(self):
        self._view.show_statistics(self._model.get_statistics())


def main():
    model = TaskModel()
    view = TaskView()
    ctrl = TaskController(model, view)

    now = datetime.now()

    ctrl.add_task("Підготувати звіт", priority=1, deadline=now + timedelta(days=2))
    ctrl.add_task("Купити продукти", priority=4, deadline=now + timedelta(hours=5))
    ctrl.add_task("Пройти курс Python", priority=2, deadline=now + timedelta(days=10))
    ctrl.add_task("Заплатити за комунальні", priority=3, deadline=now + timedelta(days=1))

    ctrl.show_all()

    ctrl.set_sort_strategy(SortByDeadline())
    ctrl.show_all()

    ctrl.complete_task(1)

    ctrl.show_active()

    ctrl.show_stats()


if __name__ == "__main__":
    main()
