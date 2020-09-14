
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);

  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
}

String waitForCommand() {
  while (Serial.available() == 0) {};
  String cmd = Serial.readString() ;
  if (cmd[cmd.length() - 1] == '\n') {
    return cmd.substring(0, cmd.length() - 1);
  }
  return cmd;
}

// the loop function runs over and over again forever
void loop() {
  String cmd = waitForCommand();
  if (cmd.equals("counter_9")) {
    set_counter(9);
  } else if (cmd.equals("counter_8")) {
    set_counter(8);
  } else if (cmd.equals("counter_7")) {
    set_counter(7);
  } else if (cmd.equals("counter_6")) {
    set_counter(6);
  } else if (cmd.equals("counter_5")) {
    set_counter(5);
  } else if (cmd.equals("counter_4")) {
    set_counter(4);
  } else if (cmd.equals("counter_3")) {
    set_counter(3);
  } else if (cmd.equals("counter_2")) {
    set_counter(2);
  } else if (cmd.equals("counter_1")) {
    set_counter(1);
  } else if (cmd.equals("counter_0")) {
    set_counter(0);
  }

}

void set_counter(int n) {

  switch (n) {
    case 9:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
      digitalWrite(8, HIGH);
      digitalWrite(9, HIGH);
      break;
    case 8:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(8, HIGH);
      digitalWrite(9, HIGH);
      break;
    case 7:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
      digitalWrite(8, LOW);
      digitalWrite(9, LOW);
      break;
    case 6:
      digitalWrite(2, HIGH);
      digitalWrite(3, LOW);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(8, HIGH);
      digitalWrite(9, HIGH);
      break;
    case 5:
      digitalWrite(2, HIGH);
      digitalWrite(3, LOW);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(6, LOW);
      digitalWrite(8, HIGH);
      digitalWrite(9, HIGH);
      break;
    case 4:
      digitalWrite(2, LOW);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
      digitalWrite(8, HIGH);
      digitalWrite(9, HIGH);
      break;
    case 3:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(6, LOW);
      digitalWrite(8, HIGH);
      digitalWrite(9, LOW);
      break;
    case 2:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, LOW);
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(8, HIGH);
      digitalWrite(9, LOW);
      break;
    case 1:
      digitalWrite(2, LOW);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, LOW);
      digitalWrite(6, LOW);
      digitalWrite(8, LOW);
      digitalWrite(9, LOW);
      break;
    case 0:
      digitalWrite(2, HIGH);
      digitalWrite(3, HIGH);
      digitalWrite(4, HIGH);
      digitalWrite(5, HIGH);
      digitalWrite(6, HIGH);
      digitalWrite(8, LOW);
      digitalWrite(9, HIGH);
      break;
  }
}
