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
HEADING_MIN_SPEED_MPS = 3.0
# 헤딩으로 튕길 때 들어온 속도를 유지하는 비율 (낮을수록 공이 빨리 내려와 킥할 기회가 생김)
HEADING_KEEP_RATE = 0.6
# 헤딩한 선수가 바라보는 쪽으로 공을 더 밀어 주는 속도 (머리 위에서 계속 통통 튀지 않고 앞으로 나감)
HEADING_FORWARD_MPS = 2.5
HEADING_FORWARD_PPS = (HEADING_FORWARD_MPS * PIXEL_PER_METER)
HEADING_MIN_SPEED_PPS = (HEADING_MIN_SPEED_MPS * PIXEL_PER_METER)
# 점프 헤딩 때 공이 머리보다 이만큼 더 빨리 떠나게 함 (다시 맞지 않을 만큼만)
HEADING_LEAVE_MARGIN_MPS = 0.5
HEADING_LEAVE_MARGIN_PPS = (HEADING_LEAVE_MARGIN_MPS * PIXEL_PER_METER)

# 킥 속도 (가로, 세로, 파워 능력치 3 기준)
KICK_SPEED_X_MPS = 6.0
KICK_SPEED_X_PPS = (KICK_SPEED_X_MPS * PIXEL_PER_METER)
KICK_SPEED_Y_MPS = 5.0
KICK_SPEED_Y_PPS = (KICK_SPEED_Y_MPS * PIXEL_PER_METER)

# 빠르게 날아와 선수 몸에 막힌 낮은 공은 위로 튀어 오름
BLOCK_MIN_SPEED_MPS = 2.5
BLOCK_MIN_SPEED_PPS = (BLOCK_MIN_SPEED_MPS * PIXEL_PER_METER)
BLOCK_UP_SPEED_MPS = 10.0
BLOCK_UP_SPEED_PPS = (BLOCK_UP_SPEED_MPS * PIXEL_PER_METER)
BLOCK_MAX_HEIGHT = 170

# 두 선수 머리 사이에서 공이 좌우로 왕복하면(핑퐁) 위로 크게 튀어 빠져나가게 함
PINGPONG_TIME = 0.3        # 이 시간(초) 안에 다른 선수 머리에 맞으면 왕복 1번
PINGPONG_COUNT = 2         # 왕복이 이만큼 되면 위로 튀김
PINGPONG_UP_SPEED_MPS = 10.0
PINGPONG_UP_SPEED_PPS = (PINGPONG_UP_SPEED_MPS * PIXEL_PER_METER)
HEAD_IGNORE_TIME = 0.15    # 위로 튄 직후 이 시간 동안은 머리에 맞지 않음 (빠져나가는 중)
HEAD_STUCK_TIME = 0.05     # 같은 머리에 이 시간 안에 또 맞으면 공이 머리에 붙어 있는 것으로 봄

# 파워슛: 가로 속도만 이만큼 세게 해서 낮고 빠르게 날아감
POWER_SHOT_RATE = 2.0

# 하드태클에 쓸려 나가는 공의 속도 (가로, 세로)
TACKLE_SWEEP_X_MPS = 8.0
TACKLE_SWEEP_X_PPS = (TACKLE_SWEEP_X_MPS * PIXEL_PER_METER)
TACKLE_SWEEP_Y_MPS = 2.0
TACKLE_SWEEP_Y_PPS = (TACKLE_SWEEP_Y_MPS * PIXEL_PER_METER)

# 회전 애니메이션: 공 둘레를 8칸으로 나눈 거리만큼 굴러가면 한 칸
PIXELS_PER_FRAME = (2 * math.pi * 32 / 8)


class Ball:
    image = None

    def __init__(self):
        self.x, self.y = 640, 400
        self.frame = 0
        self.vx, self.vy = 0, 0
        # 마지막으로 헤딩한 선수, 그 뒤로 지난 시간, 머리 사이 왕복 횟수
        self.last_header = None
        self.time_since_head = 0.0
        self.pingpong = 0
        # 남은 머리 충돌 무시 시간
        self.head_ignore = 0.0
        if Ball.image == None:
            Ball.image = load_image('resource/ball_sheet.png')

    def update(self):
        self.time_since_head += game_framework.frame_time
        self.head_ignore = max(self.head_ignore - game_framework.frame_time, 0)
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

    def bounce_from(self, cx, cy, r, head_vy, header):
        # head_vy: 머리가 위아래로 움직이는 속도 (점프 중이 아니면 0)
        # header: 헤딩한 선수 (머리 사이 왕복 판정용)

        # 같은 선수 머리에 아주 짧은 시간 안에 또 맞았으면, 공이 머리에 붙어 같이 움직이는 것
        stuck_on_head = self.last_header is header and self.time_since_head < HEAD_STUCK_TIME

        # 방금 다른 선수 머리에 맞았던 공이면 왕복 횟수 증가, 아니면 처음부터
        if self.last_header is not None and self.last_header is not header and self.time_since_head < PINGPONG_TIME:
            self.pingpong += 1
        else:
            self.pingpong = 0
        self.last_header = header
        self.time_since_head = 0.0

        dx, dy = self.x - cx, self.y - cy
        d = math.sqrt(dx * dx + dy * dy)
        if d == 0:
            dx, dy, d = 0, 1, 1
        nx, ny = dx / d, dy / d

        self.x = cx + nx * (r + 32)
        self.y = cy + ny * (r + 32)

        speed = max(math.sqrt(self.vx * self.vx + self.vy * self.vy) * HEADING_KEEP_RATE, HEADING_MIN_SPEED_PPS)
        # 머리가 공 쪽으로 올라가며 받으면, 공이 머리보다 조금 더 빨리 떠나게 함
        # (머리가 공을 다시 따라잡지 않아 한 번만 맞음)
        head_speed_to_ball = head_vy * ny
        if head_speed_to_ball > 0:
            speed = max(speed, head_speed_to_ball + HEADING_LEAVE_MARGIN_PPS)
        self.vx, self.vy = nx * speed, ny * speed
        # 바라보는 쪽으로 공을 밀어 줌 (헤딩은 앞으로 보내는 동작)
        self.vx += header.face_dir * HEADING_FORWARD_PPS

        # 올라가는 머리에 공이 붙어 있으면 공이 머리보다 빨리 위로 떠나게 함
        # (벽과 머리 사이에 낀 공이 머리와 같이 올라가며 계속 맞지 않게 함, 보통 헤딩에는 영향 없음)
        if stuck_on_head and head_vy > 0 and ny > 0:
            self.vy = max(self.vy, head_vy + HEADING_LEAVE_MARGIN_PPS)

        # 머리 사이에서 왕복이 계속되면 위로 크게 튀어 빠져나감
        if self.pingpong >= PINGPONG_COUNT:
            self.vx = 0
            self.vy = PINGPONG_UP_SPEED_PPS
            self.head_ignore = HEAD_IGNORE_TIME
            self.pingpong = 0

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

    def blocked(self):
        # 빠른 낮은 공이 몸에 막히면 위로 튀어 오름 (가까이서 서로 차며 갇히지 않게 함)
        if abs(self.vx) > BLOCK_MIN_SPEED_PPS and self.y < BLOCK_MAX_HEIGHT:
            self.vy = max(self.vy, BLOCK_UP_SPEED_PPS)

    def swept(self, face_dir):
        # 하드태클에 쓸려 진행 방향으로 낮고 빠르게 굴러감
        self.vx = face_dir * TACKLE_SWEEP_X_PPS
        self.vy = TACKLE_SWEEP_Y_PPS

    def power_header(self):
        # 파워슛 헤딩: 튕겨 나가는 가로 속도를 파워슛 배율만큼 올림
        self.vx *= POWER_SHOT_RATE

    def kicked(self, face_dir, power_rate, power_shot):
        # power_rate: 찬 선수의 킥 세기 배율 (파워 3이 1.0배)
        # power_shot: 파워슛이면 가로 속도를 크게 올림
        self.vx = face_dir * KICK_SPEED_X_PPS * power_rate
        self.vy = KICK_SPEED_Y_PPS * power_rate
        if power_shot:
            self.vx *= POWER_SHOT_RATE

    def draw(self):
        Ball.image.clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y)
