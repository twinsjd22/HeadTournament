from pico2d import load_image, load_font


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
        pass
