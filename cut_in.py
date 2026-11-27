import ctypes

from pico2d import load_image, load_font
from sdl2.sdlttf import TTF_SizeUTF8

import game_framework
import sound
from character_data import CHARACTER_TYPES

# 컷인 전체 시간(초), 띠가 들어오는 시간과 나가는 시간(초)
CUT_IN_TIME = 0.7
SLIDE_TIME = 0.15
# 띠(1280x200)의 높이, 띠 안 초상화 칸 가운데 x와 초상화 크기, 기술 이름 가운데 x (띠 왼쪽 끝 기준)
BAND_Y = 380
PORTRAIT_X = 135
PORTRAIT_SIZE = 170
NAME_X = 790
NAME_FONT_SIZE = 64


class CutIn:
    # 필살기를 쓰면 화면이 어두워지고, 띠를 타고 초상화와 기술 이름이 지나감 (그동안 경기는 멈춤)
    dim = None
    band = None
    font = None
    portraits = {}

    def __init__(self):
        if CutIn.dim == None:
            CutIn.dim = load_image('resource/result_dim_light.png')
            CutIn.band = load_image('resource/cutin_band.png')
            CutIn.font = load_font('resource/BlackHanSans-Regular.ttf', NAME_FONT_SIZE)
            # 유형마다 초상화 (경기 도중에 불러와 멈칫하지 않게 미리 모두 불러 둠)
            CutIn.portraits = {key: load_image(data['portrait']) for key, data in CHARACTER_TYPES.items()}
        # 컷인이 시작된 뒤 지난 시간 (None이면 보여 주지 않음), 보여 줄 선수, 들어오는 쪽 (1은 왼쪽, -1은 오른쪽)
        self.time = None
        self.character = None
        self.side = 1

    def start(self, character, side):
        # side: 플레이어는 1 (왼쪽에서 들어옴), 상대는 -1 (오른쪽에서 들어오고 띠를 뒤집어 초상화 칸이 오른쪽)
        self.time = 0.0
        self.character = character
        self.side = side
        # 컷인이 들어오는 순간 필살기 소리 (8종 모두 컷인을 거치므로 여기 한 곳에서 냄)
        sound.play('skill')

    def is_playing(self):
        return self.time is not None

    def update(self):
        if self.time is None:
            return
        self.time += game_framework.frame_time
        if self.time >= CUT_IN_TIME:
            self.time = None

    def draw(self):
        if self.time is None:
            return
        # 띠가 화면 밖에서 미끄러져 들어와 멈췄다가 반대쪽으로 빠져나감
        side = self.side
        if self.time < SLIDE_TIME:
            offset = -(1 - self.time / SLIDE_TIME) * 1280
        elif self.time > CUT_IN_TIME - SLIDE_TIME:
            offset = (self.time - (CUT_IN_TIME - SLIDE_TIME)) / SLIDE_TIME * 1280
        else:
            offset = 0
        band_x = 640 + offset * side

        CutIn.dim.draw(640, 360)
        flip = '' if side == 1 else 'h'
        CutIn.band.composite_draw(0, flip, band_x, BAND_Y)

        # 띠 왼쪽 끝 기준 위치를 화면 위치로 바꿔 초상화와 기술 이름을 그림 (뒤집힌 띠는 좌우 반대로)
        band_left = band_x - 640
        portrait_x = band_left + (PORTRAIT_X if side == 1 else 1280 - PORTRAIT_X)
        name_x = band_left + (NAME_X if side == 1 else 1280 - NAME_X)
        CutIn.portraits[self.character.char_type].draw(portrait_x, BAND_Y, PORTRAIT_SIZE, PORTRAIT_SIZE)
        name = CHARACTER_TYPES[self.character.char_type]['skill']
        w, h = ctypes.c_int(), ctypes.c_int()
        TTF_SizeUTF8(CutIn.font.font, name.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
        CutIn.font.draw(name_x - w.value / 2, BAND_Y, name, (255, 255, 255))
