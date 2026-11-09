from pico2d import load_image


class Ball:
    image = None

    def __init__(self):
        self.x, self.y = 640, 400
        self.frame = 0
        self.vx, self.vy = 0, 0
        if Ball.image == None:
            Ball.image = load_image('resource/ball_sheet.png')

    def update(self):
        pass

    def draw(self):
        Ball.image.clip_draw(self.frame * 64, 0, 64, 64, self.x, self.y)
