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
        self.x += self.vx
        self.y += self.vy
        self.vy -= 3

        if self.y - 32 < 80:
            self.y = 80 + 32
            self.vy = -self.vy * 0.7
            if self.vy < 15:
                self.vy = 0

    def draw(self):
        Ball.image.clip_draw(self.frame * 64, 0, 64, 64, self.x, self.y)
