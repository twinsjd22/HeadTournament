import math

from pico2d import load_image, load_font

import play_mode


class TimerBoard:
    image = None
    font = None

    def __init__(self):
        if TimerBoard.image == None:
            TimerBoard.image = load_image('resource/ui_timer_panel.png')
        if TimerBoard.font == None:
            TimerBoard.font = load_font('resource/NanumGothic-Bold.ttf', 28)

    def update(self):
        pass

    def draw(self):
        # 점수 패널 아래 가운데에 타이머 패널
        TimerBoard.image.draw(640, 584)
        # 남은 시간을 올림해서 분:초로 (60초는 1:00, 0.3초는 0:01)
        seconds = math.ceil(play_mode.time_left)
        # 시간 글자 (폭 약 59px)를 패널 가운데에 오도록 왼쪽 끝을 30px 당김
        TimerBoard.font.draw(640 - 30, 584, f'{seconds // 60}:{seconds % 60:02d}', (255, 255, 255))
