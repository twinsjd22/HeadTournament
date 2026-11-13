from pico2d import load_image, load_font


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
