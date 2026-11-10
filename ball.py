import math

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

        if self.y == 80 + 32:
            self.vx *= 0.95
            if abs(self.vx) < 0.5:
                self.vx = 0

        if self.x - 32 < 0:
            self.x = 32
            self.vx = -self.vx * 0.7
        elif self.x + 32 > 1280:
            self.x = 1280 - 32
            self.vx = -self.vx * 0.7

        self.frame = (self.frame + self.vx / 25) % 8

    def get_circle(self):
        return self.x, self.y, 32

    def bounce_from(self, cx, cy, r):
        dx, dy = self.x - cx, self.y - cy
        d = math.sqrt(dx * dx + dy * dy)
        if d == 0:
            dx, dy, d = 0, 1, 1
        nx, ny = dx / d, dy / d

        self.x = cx + nx * (r + 32)
        self.y = cy + ny * (r + 32)

        speed = max(math.sqrt(self.vx * self.vx + self.vy * self.vy) * 0.8, 20)
        self.vx, self.vy = nx * speed, ny * speed

    def kicked(self, face_dir):
        self.vx = face_dir * 30
        self.vy = 25

    def draw(self):
        Ball.image.clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y)
