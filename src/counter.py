# src/counter.py

from collections import deque
from config.settings import MAX_OCCUPANCY

class OccupancyCounter:
    def __init__(self, window_size=10, max_occupancy=MAX_OCCUPANCY):
        """
        Args:
            window_size (int): number of past frames to average
            max_occupancy (int): threshold for triggering actions
        """
        self.window_size = window_size
        self.max_occupancy = max_occupancy
        self.history = deque(maxlen=window_size)

    def update(self, current_count):
        """
        Add the latest frame's person count
        Args:
            current_count (int): number of people detected in current frame
        """
        self.history.append(current_count)

    def get_average(self):
        """
        Returns:
            float: average number of people over the rolling window
        """
        if not self.history:
            return 0
        return sum(self.history) / len(self.history)

    def is_over_limit(self):
        """
        Returns:
            bool: True if average occupancy exceeds max_occupancy
        """
        return self.get_average() >= self.max_occupancy
