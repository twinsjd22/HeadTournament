import math
import random

from pico2d import load_image

import game_framework

# 꽃가루 시트: 32x32 한 칸씩 8종 (빨강, 노랑, 초록, 파랑, 보라, 주황, 흰색, 하늘색)
CONFETTI_KINDS = 8
CONFETTI_CELL = 32
# 떨어지는 속도(px/s), 좌우로 살랑이는 폭(px)과 1초에 흔들리는 횟수, 1초에 도는 각도(라디안), 그리는 크기(px)
FALL_SPEED_RANGE = (90, 170)
SWAY_WIDTH_RANGE = (10, 35)
SWAY_PER_SECOND_RANGE = (0.5, 1.5)
TURN_SPEED_RANGE = (-6.0, 6.0)
SIZE_RANGE = (16, 26)


class Confetti:
    # 우승 화면에서 위에서 떨어지며 빙글빙글 도는 꽃가루 한 조각
    image = None

    def __init__(self, x, y):
        if Confetti.image == None:
            Confetti.image = load_image('resource/confetti_sheet.png')
        # 시작 위치, 시트에서 고른 칸, 떨어지는 속도, 흔들림, 회전, 크기를 조각마다 무작위로
        self.base_x, self.y = x, y
        self.kind = random.randrange(CONFETTI_KINDS)
        self.fall_speed = random.uniform(*FALL_SPEED_RANGE)
        self.sway_width = random.uniform(*SWAY_WIDTH_RANGE)
        self.sway_speed = random.uniform(*SWAY_PER_SECOND_RANGE) * 2 * math.pi
        self.turn_speed = random.uniform(*TURN_SPEED_RANGE)
        self.size = random.uniform(*SIZE_RANGE)
        self.time = random.uniform(0, 10)

    def update(self):
        self.time += game_framework.frame_time
        self.y -= self.fall_speed * game_framework.frame_time

    def is_gone(self):
        # 화면 아래로 다 떨어졌는지
        return self.y < -self.size

    def draw(self):
        x = self.base_x + math.sin(self.time * self.sway_speed) * self.sway_width
        Confetti.image.clip_composite_draw(self.kind * CONFETTI_CELL, 0, CONFETTI_CELL, CONFETTI_CELL,
                                           self.time * self.turn_speed, '', x, self.y, self.size, self.size)
