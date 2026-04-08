import random
from .data.dataset import DATASETS

class EmailTaskLoader:
    def __init__(self, level: str = "easy"):
        """
        Initializes the Task Loader.
        Level configures the difficulty: easy, medium, hard.
        """
        if level not in DATASETS:
            raise ValueError(f"Invalid task level: {level}")
        self.level = level
        # Shallow copy to avoid mutating the original dataset
        self.emails = DATASETS[level][:]
        self.current_index = 0

    def next_email(self):
        if self.current_index < len(self.emails):
            email = self.emails[self.current_index]
            self.current_index += 1
            return email
        return None

    def reset(self):
        self.current_index = 0
        # Optional: could shuffle here if we want non-deterministic runs

    def remaining(self) -> int:
        return len(self.emails) - self.current_index

    def total(self) -> int:
        return len(self.emails)
