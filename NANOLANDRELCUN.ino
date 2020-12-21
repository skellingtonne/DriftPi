/*
* Kyrel Silva, Landon Brown, Duncan Stannard
* ECET 261
*/

#define steer_left_max 640 //max 660
#define steer_right_max 430 //max is 440
#define steer_straight 538 // straigh is 557
#define steer_straight_buffer 14
#define steer_pwm_factor 28 //maybe 25
#define steer_pwm_factor_straight 25 //maybe 23?


#define pin_pwm 6
#define pin_steer_left 7 //in1 -7, 
#define pin_steer_right 8//in2 -8
#define steer_input A1

#define pi_input_left 10
#define pi_input_right 11

#define bat_volt_min 185
#define bat_input A0
#define fuck_off_pi_pin 4

//prototypes
void SteerLeft();
void SteerRight();
void SteerStraight();
void PiInput();
void SteerJitter();

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  pinMode(pin_pwm, OUTPUT);
  pinMode(pin_steer_left, OUTPUT);
  pinMode(pin_steer_right, OUTPUT);
  pinMode(steer_input, INPUT);
  pinMode(pi_input_left, INPUT);
  pinMode(pi_input_right, INPUT);
  pinMode(fuck_off_pi_pin, OUTPUT);
  digitalWrite(fuck_off_pi_pin, LOW);
}


void SteerLeft() //set left pin high, right pin low, set pwm 0-100*steer_pwm_factor and all should be good
{
  //Serial.print("We go left: ");
  while (analogRead(steer_input) < steer_left_max)
  {
    if (analogRead(steer_input) < 350)
    {
      SteerJitter();
    }
    //Serial.println(analogRead(steer_input));
    analogWrite(pin_pwm, 2.55 * steer_pwm_factor);
    digitalWrite(pin_steer_left, HIGH);
    digitalWrite(pin_steer_right, LOW);
  }
  digitalWrite(pin_steer_right, LOW);
  digitalWrite(pin_steer_left, LOW);
  return;

}

void SteerRight() //set right pin high, left pin low, set pwm 0-100*steer_pwm_factor and all should be good
{
  //Serial.print("We go right: ");
  while (analogRead(steer_input) > steer_right_max)
  {
    if (analogRead(steer_input) < 350)
    {
      SteerJitter();
    }
    //Serial.println(analogRead(steer_input));
    analogWrite(pin_pwm, 2.55 * steer_pwm_factor);
    digitalWrite(pin_steer_right, HIGH);
    digitalWrite(pin_steer_left, LOW);
  }
  digitalWrite(pin_steer_right, LOW);
  digitalWrite(pin_steer_left, LOW);
  return;

}


// measure the pot value and then turn motor in proper direction until put value reads steer_straight, then hold motor
void SteerStraight()
{
  int analog_steer = analogRead(steer_input);
  if (analogRead(steer_input) < 350)
  {
    SteerJitter();
  }
  //Serial.print("We go straight: ");
  //Serial.println(analogRead(steer_input));
  else if ((analog_steer >= steer_straight - steer_straight_buffer) && (analog_steer <= steer_straight )) //implement buffer for straight steering
  {
    digitalWrite(pin_steer_right, LOW);
    digitalWrite(pin_steer_left, LOW);
    return;
  }
  else if ((analog_steer <= steer_straight + steer_straight_buffer) && (analog_steer >= steer_straight ))
  {
    digitalWrite(pin_steer_right, LOW);
    digitalWrite(pin_steer_left, LOW);
    return;
  }
  else if (analog_steer > steer_straight)
  {
    while (analogRead(steer_input) > steer_straight ) //if tires are left, steer right
    {
      if (analogRead(steer_input) < 350)
      {
        SteerJitter();
      }
      //Serial.print("correct right");
      //Serial.println(analogRead(analog_steer));
      analogWrite(pin_pwm, 2.55 * steer_pwm_factor_straight);
      digitalWrite(pin_steer_right, HIGH);
      digitalWrite(pin_steer_left, LOW);
    }
  }

  else if (analog_steer < steer_straight)
  {
    while (analogRead(steer_input) < steer_straight) //if tires are right, steer left
    {
      if (analogRead(steer_input) < 350)
      {
        SteerJitter();
      }
      //Serial.print("correct left ");
      //Serial.println(analogRead(steer_input));
      analogWrite(pin_pwm, 2.55 * steer_pwm_factor_straight);
      digitalWrite(pin_steer_left, HIGH);
      digitalWrite(pin_steer_right, LOW);
    }
  }
  digitalWrite(pin_steer_right, LOW);
  digitalWrite(pin_steer_left, LOW);
}

//input received will be active high. input for pin is measured and then proper direction is called, if neither, vehicle returns straight
void PiInput()
{
  if (digitalRead(pi_input_left) == HIGH)
  {
    //Serial.println("PI input left");
    SteerLeft();
    return ;
  }
  else if (digitalRead(pi_input_right) == HIGH)
  {
    //Serial.println("PI input right");
    SteerRight();
    return ;
  }
  else
  {
    //Serial.println("straight ;)");
    SteerStraight();
    return ;
  }
}

//zero spot in the pot used for steering feedback, this jitter code will run if the analog reading is ever less than the max right
void SteerJitter()
{
  analogWrite(pin_pwm, 2.55 * 60);
  digitalWrite(pin_steer_right, HIGH);
  digitalWrite(pin_steer_left, LOW);
  delay(1);
  digitalWrite(pin_steer_right, LOW);
  digitalWrite(pin_steer_left, HIGH);
  analogWrite(pin_pwm, 2.55 * 40);
  return;
}

void loop()
{
  //while(analogRead(A4) > bat_volt_min)
  //{
  //Serial.print("in main loop ");
  //Serial.println(analogRead(steer_input));
  PiInput();
  //}
  //digitalWrite(fuck_off_pi_pin, HIGH);
}
