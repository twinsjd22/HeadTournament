from pico2d import load_image

import game_framework
import sound

# 골 표시 시간(초): 끝나면 선수와 공이 처음 자리로 돌아감
GOAL_EFFECT_TIME = 1.2
# GOAL! 글자: 위치, 원래 그림(700x260)에 곱하는 크기 배율
TEXT_X, TEXT_Y = 640, 450
TEXT_SCALE = 0.6
# 살짝 크게 나타났다가 원래 크기로 줄어드는 시간(초)과 처음 크기 배율
POP_TIME = 0.15
POP_SCALE = 1.3


class GoalEffect:
    # 골이 들어가면 GOAL! 글자를 가볍게 띄우고, 잠시 뒤 처음 자리로 돌아가게 알려 줌
    image = None

    def __init__(self):
        if GoalEffect.image == None:
            GoalEffect.image = load_image('resource/goal.png')
        # 골 표시가 시작된 뒤 지난 시간 (None이면 표시 중이 아님)
        self.time = None

    def start(self):
        self.time = 0.0
        # GOAL! 글자가 뜨는 순간 골 함성 (소리가 글자보다 길어서 처음 자리로 돌아간 뒤에도 조금 이어짐)
        sound.play('goal')

    def is_playing(self):
        return self.time is not None

    def update(self):
        if self.time is None:
            return
        self.time += game_framework.frame_time
        if self.time >= GOAL_EFFECT_TIME:
            self.time = None

    def draw(self):
        if self.time is None:
            return
        scale = TEXT_SCALE * (POP_SCALE - (POP_SCALE - 1) * min(self.time / POP_TIME, 1.0))
        image = GoalEffect.image
        image.draw(TEXT_X, TEXT_Y, image.w * scale, image.h * scale)
