import sys


class ProgressBar:
    def __init__(self):
        self.max_value = 100
        self.current_value = 0
        self.status = ""
        self.last_length = 0

    def set_max(self, max_val):
        if max_val <= 0:
            raise ValueError("Максимальное значение должно быть положительным")
        self.max_value = max_val

    def set_progress(self, progress):
        self.current_value = max(0, min(progress, self.max_value))
        self._update_display()

    def set_status(self, status):
        self.status = status
        self._update_display()

    def _update_display(self):
        percent = 100.0 * self.current_value / self.max_value
        display_str = f"{self.status}: {percent:.1f}%"
        sys.stdout.write("\r" + " " * self.last_length + "\r")

        sys.stdout.write(display_str)
        sys.stdout.flush()
        self.last_length = len(display_str)

    def finish(self):
        sys.stdout.write("\n")
        sys.stdout.flush()