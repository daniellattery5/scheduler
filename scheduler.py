class Task:
    def __init__(self, title):
        self.title = title
        self.done = False

    def mark_done(self):
        self.done = True

    def __str__(self):
        # Show [X] if done, otherwise [ ]
        if self.done:
            box = "[X]"
        else:
            box = "[ ]"
        return f"{box} {self.title}"

    def __bool__(self):
        # True if done, False if not done
        return self.done


class TaskManager:
    def __init__(self):
        # list to store Task objects
        self.tasks = []

    def add_task(self, title):
        self.tasks.append(Task(title))

    def list_tasks(self):
        if len(self.tasks) == 0:
            print("No tasks yet.")
            return

        print(f"Tasks (total = {len(self.tasks)}):")
        for i, task in enumerate(self.tasks, start=1):
            print(f"{i} - {task}")

    def filter_tasks(self, f):
        # remove tasks where f(task) returns True
        new_list = []
        for t in self.tasks:
            if not f(t):
                new_list.append(t)
        self.tasks = new_list

    def mark_task_done(self, index):
        # index starts at 1 when the user selects a task
        if index < 1 or index > len(self.tasks):
            print("Invalid task number.")
            return

        task = self.tasks[index - 1]
        task.mark_done()
        print("Task marked as done!")


def main():
    manager = TaskManager()

    while True:
        print("\n--- Task Manager ---")
        print("1. Add task")
        print("2. List tasks")
        print("3. Mark task as done")
        print("4. Clear completed tasks")
        print("5. Quit")

        choice = input("Enter option: ")

        # try to convert to int but don’t crash the program
        try:
            option = int(choice)
        except ValueError:
            print("Please enter a number from the menu.")
            continue

        if option == 1:
            title = input("Enter task name: ")
            manager.add_task(title)
            print("Task added!")

        elif option == 2:
            manager.list_tasks()

        elif option == 3:
            if len(manager.tasks) == 0:
                print("No tasks to mark.")
                continue

            num = input("Enter task number to mark done: ")
            try:
                idx = int(num)
                manager.mark_task_done(idx)
            except ValueError:
                print("Invalid number.")

        elif option == 4:
            # clear all tasks where t.done == True
            manager.filter_tasks(lambda t: t.done)
            print("Completed tasks cleared!")

        elif option == 5:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please pick from 1–5.")


# Standard Python entry point
if __name__ == "__main__":
    main()


# -------------------------------------------------------------------------------------------
# TESTING
# These comments show how I tested the program manually.
# ------------------------------------------------------------------------------------------
# > 1. Add task
# > Enter task name:
# Do Laundry
# > Task added!

# > 2. List tasks
# Tasks (total = 1):
# 1 - [ ] Do laundry

# > 3. Mark task as done
# > Enter task number:
# 1
# Task marked as done!

# > 2. List tasks
# Tasks (total = 1):
# 1 - [X] Do laundry

# > 4. Clear completed tasks
# Completed tasks cleared!

# > 2. List tasks
# No tasks yet.

# EDGE CASE TESTS:
# - I also entered a letter instead of a number in the menu. It gave a warning but did not crash
# - I also marked a non-existing task number. The result was - "Invalid task number."
# - I also cleared the tasks when none exist. The result was - "Completed tasks cleared!"
# -------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
# Part 2 — ScheduledTask Class and Scheduler
# ------------------------------------------------------------------------------------------------

class ScheduledTask(Task):
    def __init__(self, title, duration, earliest_start=None, latest_finish=None):
        super().__init__(title)
        self.duration = duration  # minutes
        self.earliest_start = earliest_start
        self.latest_finish = latest_finish

    def __str__(self):
        # Override to show timing information
        es = self.earliest_start if self.earliest_start is not None else "None"
        lf = self.latest_finish if self.latest_finish is not None else "None"
        base = super().__str__()
        return f"{base} (duration={self.duration}, earliest={es}, latest={lf})"


# Extend TaskManager with scheduling
class TaskManager(TaskManager):
    # Note: The class will be re-defined only to ADD the new method.

    def build_schedule(self, tasks):
        """
        Greedy scheduler for a single-day window [0, 480)
        Returns: list of (start, end, task)
        """

        schedule = []
        current_time = 0

        # A simple, predictable approach: sort tasks by earliest_start (None = 0).
        def sort_key(t):
            if t.earliest_start is None:
                return 0
            return t.earliest_start

        ordered = sorted(tasks, key=sort_key)

        for t in ordered:
            # Determine actual start time
            if t.earliest_start is None:
                start = current_time
            else:
                start = max(current_time, t.earliest_start)

            end = start + t.duration

            # Check scheduling constraints
            if end > 480:
                # Does not fit in the day
                continue

            if t.latest_finish is not None and end > t.latest_finish:
                # Violates deadline
                continue

            # Add to schedule
            schedule.append((start, end, t))
            current_time = end  # move the clock

        return schedule

# -------------------------------------------------------
# TESTING FOR PART 2 (SCHEDULER)
# -------------------------------------------------------
# Example 1:
# tasks = [
#     ScheduledTask("Study Computer Systems", 120, earliest_start=0),
#     ScheduledTask("Gym", 60, earliest_start=200),
#     ScheduledTask("Cook dinner", 90),
# ]
# manager = TaskManager()
# result = manager.build_schedule(tasks)
# for s, e, t in result:
#     print(f"{t.title}: {s} -> {e}")

# Expected (approx):
# Study Computer Systems: 0 -> 120
# Cook dinner: 120 -> 210
# Gym: 210 -> 270
#
# (Gym might shift depending on earliest_start)
#
# Example 2 — A task that can't fit:
# tasks = [
#     ScheduledTask("Long task", 500),
#     ScheduledTask("Short task", 50),
# ]
# result = manager.build_schedule(tasks)
# Only "Short task" fits into the 480-minute day.
#
# Example 3 — Deadline failure :
# tasks = [
#     ScheduledTask("Task A", 60, latest_finish=50),
# ]
# No output because the task violates its deadline.
# --------------------------------------------------------------------