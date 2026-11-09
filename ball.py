from pico2d import load_image


class Ball:
    image = None

    def __init__(self):
        self.x, self.y = 640, 400
        self.frame = 0
        if Ball.image == None:
            Ball.image = load_image('resource/ball_sheet.png')

    def update(self):
        pass

    def draw(self):
        pass
