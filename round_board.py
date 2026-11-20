from pico2d import load_image, load_font

import tournament

# 라운드 패널 위치 (왼쪽 위, 화면 끝에서 20px 안쪽, 점수 패널과 같은 높이)
ROUND_X, ROUND_Y = 20 + 160 // 2, 660
FONT_SIZE = 28


class RoundBoard:
    # 경기 화면 왼쪽 위에 지금 토너먼트 라운드(32강, 결승 등)를 보여 줌
    image = None
    font = None

    def __init__(self):
        if RoundBoard.image == None:
            RoundBoard.image = load_image('resource/ui_round_panel.png')
        if RoundBoard.font == None:
            RoundBoard.font = load_font('resource/NanumGothic-Bold.ttf', FONT_SIZE)

    def update(self):
        pass

    def draw(self):
        RoundBoard.image.draw(ROUND_X, ROUND_Y)
        # 글자 폭을 어림해서 패널 가운데에 오게 함 (한글은 글자 크기만큼, 숫자는 절반 남짓)
        text = tournament.round_name()
        width = sum(FONT_SIZE if ord(c) > 127 else FONT_SIZE * 0.55 for c in text)
        RoundBoard.font.draw(ROUND_X - width / 2, ROUND_Y, text, (255, 255, 255))
