#define CLK 5
#define DT 4
#define SW 3

const int buttonPins[] = {A1, A2, A0, 11, 10, 9, 2, 6, 7, 8};  // ultimi = MEDIA

int counter = 0;
int currentStateCLK;
int lastStateCLK;

void setup() {
  Serial.begin(9600);
  Serial.println("CONSOLEDECK_READY");  // messaggio di avvio: conferma che lo sketch e' in esecuzione

  // Encoder
  pinMode(CLK, INPUT);
  pinMode(DT, INPUT);
  pinMode(SW, INPUT_PULLUP);
  lastStateCLK = digitalRead(CLK);

  // Pulsanti
  for (int i = 0; i < 10; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  // Encoder rotazione
  currentStateCLK = digitalRead(CLK);
  if (currentStateCLK != lastStateCLK) {
    if (digitalRead(DT) != currentStateCLK) {
      counter++;
    } else {
      counter--;
    }
    Serial.print("VOLUME_");
    Serial.println(counter);
  }
  lastStateCLK = currentStateCLK;

  // Pulsante encoder = MUTE
  if (digitalRead(SW) == LOW) {
    Serial.println("MUTE");
    delay(200); // debounce
  }

  // Pulsanti utente
  for (int i = 0; i < 10; i++) {
    if (digitalRead(buttonPins[i]) == LOW) {
      if (i < 9) {
        Serial.print("BUTTON_");
        Serial.println(i + 1);
      } else {
        Serial.println("MEDIA");
      }
      delay(200); // debounce
    }
  }
}
