from pico2d import load_image

import game_framework
import sound

# 3, 2, 1을 하나씩 보여 주는 시간(초)과 "시작!"을 보여 주는 시간(초)
NUMBER_TIME = 0.7
START_TIME = 0.7
# 글자가 크게 나타났다가 원래 크기로 줄어드는 시간(초)과 처음 크기 배율
POP_TIME = 0.15
POP_SCALE = 1.6
# 글자 위치 (화면 가운데보다 조금 위)
TEXT_X, TEXT_Y = 640, 420


class Countdown:
    # 경기 시작과 골 뒤에 3, 2, 1, 시작!을 보여 줌 (3, 2, 1 동안은 경기가 멈춤)
    images = None

    def __init__(self):
        if Countdown.images == None:
            Countdown.images = [load_image(f'resource/count_{name}.png') for name in ('3', '2', '1', 'start')]
        # 카운트다운이 시작된 뒤 지난 시간 (None이면 보여 주지 않음)
        self.time = None

    def start(self):
        self.time = 0.0

    def stop(self):
        # 남은 "시작!" 글자도 바로 지움 (시작하자마자 골이 들어가 GOAL! 글자와 겹치지 않게)
        self.time = None

    def is_counting(self):
        # 3, 2, 1을 세는 중인지 (이때는 경기가 멈춤, "시작!"이 뜨면 경기 시작)
        return self.time is not None and self.time < NUMBER_TIME * 3

    def update(self):
        if self.time is None:
            return
        before = self.time
        self.time += game_framework.frame_time
        # 3, 2, 1이 끝나고 "시작!"이 뜨는 순간 휘슬 (이번 프레임에 그 시간을 넘었을 때 한 번만)
        if before < NUMBER_TIME * 3 <= self.time:
            sound.play('whistle')
        if self.time >= NUMBER_TIME * 3 + START_TIME:
            self.time = None

    def draw(self):
        if self.time is None:
            return
        # 지금 보여 줄 글자 (0, 1, 2는 3, 2, 1, 3은 시작!)와 그 글자가 나타난 뒤 지난 시간
        index = min(int(self.time / NUMBER_TIME), 3)
        shown_time = self.time - index * NUMBER_TIME
        # 크게 튀어나왔다가 원래 크기로 줄어듦
        scale = POP_SCALE - (POP_SCALE - 1) * min(shown_time / POP_TIME, 1.0)
        image = Countdown.images[index]
        image.draw(TEXT_X, TEXT_Y, image.w * scale, image.h * scale)
