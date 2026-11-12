import math

from pico2d import load_image, clamp

import game_framework

# 선수와 같은 크기 기준 (150px = 1.75m)
PIXEL_PER_METER = (150.0 / 1.75)

# 공에 작용하는 중력 (실제 중력)
GRAVITY_MPS2 = 9.8
GRAVITY_PPS2 = (GRAVITY_MPS2 * PIXEL_PER_METER)

# 바닥에 튕길 때 이 속도보다 느리면 더 튀지 않고 멈춤
BOUNCE_STOP_SPEED_MPS = 3.0
BOUNCE_STOP_SPEED_PPS = (BOUNCE_STOP_SPEED_MPS * PIXEL_PER_METER)

# 굴러가는 속도가 이보다 느리면 멈춤
ROLL_STOP_SPEED_MPS = 0.1
ROLL_STOP_SPEED_PPS = (ROLL_STOP_SPEED_MPS * PIXEL_PER_METER)

# 바닥에서 굴러갈 때 1초 동안 남는 속도의 비율 (지금 마찰과 같게)
ROLL_SPEED_KEEP_PER_SECOND = 0.4

# 헤딩으로 튕겨 나가는 최소 속도
HEADING_MIN_SPEED_MPS = 4.0
HEADING_MIN_SPEED_PPS = (HEADING_MIN_SPEED_MPS * PIXEL_PER_METER)

# 킥 속도 (가로, 세로)
KICK_SPEED_X_MPS = 6.0
KICK_SPEED_X_PPS = (KICK_SPEED_X_MPS * PIXEL_PER_METER)
KICK_SPEED_Y_MPS = 5.0
KICK_SPEED_Y_PPS = (KICK_SPEED_Y_MPS * PIXEL_PER_METER)

# 회전 애니메이션: 공 둘레를 8칸으로 나눈 거리만큼 굴러가면 한 칸
PIXELS_PER_FRAME = (2 * math.pi * 32 / 8)


class Ball:
    image = None

    def __init__(self):
        self.x, self.y = 640, 400
        self.frame = 0
        self.vx, self.vy = 0, 0
        if Ball.image == None:
            Ball.image = load_image('resource/ball_sheet.png')

    def update(self):
        self.x += self.vx * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        self.vy -= GRAVITY_PPS2 * game_framework.frame_time

        if self.y - 32 < 80:
            self.y = 80 + 32
            self.vy = -self.vy * 0.7
            if self.vy < BOUNCE_STOP_SPEED_PPS:
                self.vy = 0

        if self.y == 80 + 32:
            self.vx *= ROLL_SPEED_KEEP_PER_SECOND ** game_framework.frame_time
            if abs(self.vx) < ROLL_STOP_SPEED_PPS:
                self.vx = 0

        if self.x - 32 < 0:
            self.x = 32
            self.vx = -self.vx * 0.7
        elif self.x + 32 > 1280:
            self.x = 1280 - 32
            self.vx = -self.vx * 0.7

        self.frame = (self.frame + self.vx * game_framework.frame_time / PIXELS_PER_FRAME) % 8

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

        speed = max(math.sqrt(self.vx * self.vx + self.vy * self.vy) * 0.8, HEADING_MIN_SPEED_PPS)
        self.vx, self.vy = nx * speed, ny * speed

    def bounce_from_box(self, left, bottom, right, top):
        # 사각형 위에서 공 중심과 가장 가까운 점
        px = clamp(left, self.x, right)
        py = clamp(bottom, self.y, top)
        dx, dy = self.x - px, self.y - py
        d = math.sqrt(dx * dx + dy * dy)
        if d == 0:
            dx, dy, d = 0, 1, 1
        nx, ny = dx / d, dy / d

        # 공을 사각형 바깥으로 밀어냄
        self.x = px + nx * 32
        self.y = py + ny * 32

        # 사각형 쪽으로 오던 속도만 반대로 튕김 (벽처럼 0.7배)
        vn = self.vx * nx + self.vy * ny
        if vn < 0:
            self.vx -= (1 + 0.7) * vn * nx
            self.vy -= (1 + 0.7) * vn * ny

    def kicked(self, face_dir):
        self.vx = face_dir * KICK_SPEED_X_PPS
        self.vy = KICK_SPEED_Y_PPS

    def draw(self):
        Ball.image.clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y)
