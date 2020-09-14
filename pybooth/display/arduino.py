import serial


TTY = "/dev/ttyACM0"


class ArduinoDisplay:
    def __init__(self, tty: str):
        self.arduino = None
        self.connect_arduino(tty)

    def connect_arduino(self, tty):
        self.arduino = serial.Serial(tty)

    def show_ready_state(self):
        pass

    def show_capture_state(self):
        pass

    def show_capture_counter(self, n: int):
        self.arduino.write(f"counter_{n}".encode("ascii"))

    def __del__(self):
        if self.arduino is not None:
            self.arduino.close()
