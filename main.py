#!/usr/bin/python3
from RPi.GPIO import *
from time import *
import numpy as np
from vosk import Model, KaldiRecognizer
import pyaudio
import math


def move_to_start():
    ...


def make_dot():
    set_angle(120)
    set_angle(80)


def set_angle(angle):
    duty = angle/18+2
    output(servo_pin, True)
    servo_pwm.ChangeDutyCycle(duty)
    sleep(0.3)
    output(servo_pin, False)
    servo_pwm.ChangeDutyCycle(0)

    
def move_roller_dist(d, direction=True, r=6.35, R=7, D=312.7):
    n_steps = 2222/math.pi/r*(((d**2)/((R-r)**2))/(D**2)+d**2)**(1/2)
    move_roller_steps(n_steps, direction)

        
def move_tube_dist(d, direction=True, r=6.35):
    n_steps = 2000*d/math.pi/r
    move_tube_steps(n_steps, direction)


def move_roller_steps(n, direction=True):
    output(roller_dir_pin, direction)
    roller_pwm.ChangeDutyCycle(50)
    sleep(n/motor_frequency)
    roller_pwm.ChangeDutyCycle(0)


def move_tube_steps(n, direction=True):
    output(tube_dir_pin, direction)
    tube_pwm.ChangeDutyCycle(50)
    sleep(n/motor_frequency)
    tube_pwm.ChangeDutyCycle(0)


def set_speed_roller(freq):
    roller_pwm.ChangeFrequence(freq)


def set_speed_tube(freq):
    tube_pwm.ChangeFrequence(freq)


def set_speed_servo(freq):
    servo_pwm.ChangeFrequence(freq)


d = {
    ' ': np.array([[0, 0], [0, 0], [0, 0]]),
    '-': np.array([[0, 0], [0, 0], [1, 1]]),
    'а': np.array([[1, 0], [0, 0], [0, 0]]), 
    'б': np.array([[1, 0], [1, 0], [0, 0]]), 
    'в': np.array([[0, 1], [1, 1], [0, 1]]), 
    'г': np.array([[1, 1], [1, 1], [0, 0]]),
    'д': np.array([[1, 1], [0, 1], [0, 0]]),
    'е': np.array([[1, 0], [0, 1], [0, 0]]),
    'ё': np.array([[1, 0], [0, 0], [0, 1]]),
    'ж': np.array([[0, 1], [1, 1], [0, 0]]),
    'з': np.array([[1, 0], [0, 1], [1, 1]]),
    'и': np.array([[0, 1], [1, 0], [0, 0]]),
    'й': np.array([[1, 1], [1, 0], [1, 1]]),
    'к': np.array([[1, 0], [0, 0], [1, 0]]),
    'л': np.array([[1, 0], [1, 0], [1, 0]]),
    'м': np.array([[1, 1], [0, 0], [1, 0]]),
    'н': np.array([[1, 1], [0, 1], [1, 0]]),
    'о': np.array([[1, 0], [0, 1], [1, 0]]),
    'п': np.array([[1, 1], [1, 0], [1, 0]]),
    'р': np.array([[1, 0], [1, 1], [1, 0]]),
    'с': np.array([[0, 1], [1, 0], [1, 0]]),
    'т': np.array([[0, 1], [1, 1], [1, 0]]),
    'у': np.array([[1, 0], [0, 0], [1, 1]]),
    'ф': np.array([[1, 1], [1, 0], [0, 0]]),
    'х': np.array([[1, 0], [1, 1], [0, 0]]),
    'ц': np.array([[1, 1], [0, 0], [0, 0]]),
    'ч': np.array([[1, 1], [1, 1], [1, 0]]),
    'ш': np.array([[1, 0], [0, 1], [0, 1]]),
    'щ': np.array([[1, 1], [0, 0], [1, 1]]),
    'ъ': np.array([[1, 0], [1, 1], [1, 1]]),
    'ы': np.array([[0, 1], [1, 0], [1, 1]]),
    'ь': np.array([[0, 1], [1, 1], [1, 1]]),
    'э': np.array([[0, 1], [1, 0], [0, 1]]),
    'ю': np.array([[1, 0], [1, 1], [0, 1]]),
    'я': np.array([[1, 1], [1, 0], [0, 1]]),
}
max_chars = 32
horizontal_letter_dist = 2.5
horizontal_word_dist = 3.5
vertical_letter_dist = 2.5
vertical_word_dist = 5.0


roller_dir_pin = 26
roller_step_pin = 20
tube_dir_pin = 19
tube_step_pin = 16
servo_pin = 17
buz_pin = 3
motor_frequency = 2000
servo_frequency = 50
buz_frequency = 440
forward_dir = False

setmode(BCM)

setup(tube_step_pin, OUT)
setup(tube_dir_pin, OUT)
setup(roller_step_pin, OUT)
setup(roller_dir_pin, OUT)
setup(servo_pin, OUT)
setup(buz_pin, OUT)

roller_pwm = PWM(roller_step_pin, motor_frequency)
tube_pwm = PWM(tube_step_pin, motor_frequency)
servo_pwm = PWM(servo_pin, servo_frequency)
buz_pwm = PWM(buz_pin, buz_frequency)

model = Model('./vosk-model-small-ru-0.22')
recognizer = KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

roller_pwm.start(0)
tube_pwm.start(0)
servo_pwm.start(0)
buz_pwm.start(0)
stream.start_stream()


started = False
start_word = 'начало'
end_word = 'конец'
clean_word = 'очистить'
sentences = []
while True:
    data = stream.read(4096)
    if recognizer.AcceptWaveform(data):
        text = recognizer.Result()
        text = text[14:-3]
        print(f"Text: |{text}|")
        if clean_word == text:
            sentences = []
            print('Sentences reset')
            continue
        start_i = text.find(start_word)
        if start_i >= 0 and not started:
            sentences = []
            started = True
            text = text[start_i+len(start_word):]
            buz_pwm.ChangeDutyCycle(50)
            sleep(0.5)
            buz_pwm.ChangeDutyCycle(0)
        stop_i = text.find(end_word)
        if stop_i >= 0 and started:
            buz_pwm.ChangeDutyCycle(50)
            sleep(0.5)
            buz_pwm.ChangeDutyCycle(0)
            sleep(0.5)
            buz_pwm.ChangeDutyCycle(50)
            sleep(0.5)
            buz_pwm.ChangeDutyCycle(0)
            text = text[:stop_i]
            sentences.append(text)
            move_to_start()
            queue = []
            print('Converting to points started')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) == 0:
                    continue
                print(f'|{sentence}|')
                points = np.concatenate([d[c] for c in sentence], axis=-1).reshape(-1, len(sentence), 2)
                points = [points[:, i:i+max_chars, :] for i in range(0, len(sentence), max_chars)]
                queue += points
            print('Printing Started')
            dist = 0
            for phrase in queue:
                for row in phrase:
                    for letter in row:
                        for dot in letter:
                            if dot == 1:
                                make_dot()
                                print('dot')
                            dist += horizontal_letter_dist
                            move_roller_dist(horizontal_letter_dist, direction=forward_dir)
                        dist += horizontal_word_dist - horizontal_letter_dist
                        move_roller_dist(horizontal_word_dist - horizontal_letter_dist, direction=forward_dir)
                        print('letter')
                    move_tube_dist(vertical_letter_dist, direction=forward_dir)
                    print('To start,',dist)
                    move_roller_dist(dist, direction=(not forward_dir))
                    dist = 0
                    print('row')
                move_tube_dist(vertical_word_dist - vertical_letter_dist, direction=forward_dir)
                print('phrase')
            print('Printing Ended')
            started = False
                      
        if started:
            sentences.append(text)
        print('Start_idx: {0}, Stop_idx: {1}, Started: {2}'.format(start_i, stop_i, started))

set_angle(80)
roller_pwm.stop()
tube_pwm.stop()
servo_pwm.stop()
buz_pwm.stop()
