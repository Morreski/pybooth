import logging


class LoggerDisplay:
    def show_ready_state(self):
        pass

    def show_capture_state(self):
        pass

    def show_capture_counter(self, n: int):
        logging.info(f"{n} pictures remaining")
