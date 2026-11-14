from pico2d import load_image, load_font

import play_mode


class ScoreBoard:
    image = None
    font = None

    def __init__(self):
        if ScoreBoard.image == None:
            ScoreBoard.image = load_image('resource/ui_score_panel.png')
        if ScoreBoard.font == None:
            ScoreBoard.font = load_font('resource/NanumGothic-Bold.ttf', 40)

    def update(self):
        pass

    def draw(self):
        # 화면 위쪽 가운데에 점수 패널
        ScoreBoard.image.draw(640, 660)
        # 점수 글자 (폭 약 82px)를 패널 가운데에 오도록 왼쪽 끝을 41px 당김
        ScoreBoard.font.draw(640 - 41, 662, f'{play_mode.match.score_left} : {play_mode.match.score_right}', (255, 255, 255))
