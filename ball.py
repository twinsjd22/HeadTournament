import math
import random

from pico2d import load_image, clamp

import game_framework

# 선수와 같은 크기 기준 (150px = 1.75m)
PIXEL_PER_METER = (150.0 / 1.75)

# 공에 작용하는 중력 (실제 중력)
GRAVITY_MPS2 = 9.8
GRAVITY_PPS2 = (GRAVITY_MPS2 * PIXEL_PER_METER)

# 바닥에 튕길 때 남는 속도의 비율 (낮을수록 공이 금방 땅에 깔려 킥하기 좋음)
GROUND_BOUNCE_RATE = 0.5

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
KICK_SPEED_X_MPS = 7.0
KICK_SPEED_X_PPS = (KICK_SPEED_X_MPS * PIXEL_PER_METER)
KICK_SPEED_Y_MPS = 4.0
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
TACKLE_SWEEP_X_MPS = 4.0
TACKLE_SWEEP_X_PPS = (TACKLE_SWEEP_X_MPS * PIXEL_PER_METER)
TACKLE_SWEEP_Y_MPS = 2.0
TACKLE_SWEEP_Y_PPS = (TACKLE_SWEEP_Y_MPS * PIXEL_PER_METER)

# 트릭스터가 끝날 때 몰고 가던 공을 앞으로 밀어 놓는 속도 (140px 정도 굴러감)
TRICK_RELEASE_SPEED_MPS = 1.5
TRICK_RELEASE_SPEED_PPS = (TRICK_RELEASE_SPEED_MPS * PIXEL_PER_METER)

# 철벽 방어 보호막에 맞은 공이 튕겨 나가는 최소 속도
GUARD_REPEL_SPEED_MPS = 10.0
GUARD_REPEL_SPEED_PPS = (GUARD_REPEL_SPEED_MPS * PIXEL_PER_METER)

# 오버헤드킥으로 내리꽂는 속도 (가로, 아래로, 파워 능력치 3 기준)
OVERHEAD_SPEED_X_MPS = 9.0
OVERHEAD_SPEED_X_PPS = (OVERHEAD_SPEED_X_MPS * PIXEL_PER_METER)
OVERHEAD_SPEED_DOWN_MPS = 6.0
OVERHEAD_SPEED_DOWN_PPS = (OVERHEAD_SPEED_DOWN_MPS * PIXEL_PER_METER)

# 드라이브슛: 이 높이까지 높이 떴다가, 꼭대기부터는 중력을 이 배율로 받아 골대 바로 앞으로 뚝 떨어짐
# (찰 때 상대 골대까지 거리를 보고 가로 속도를 정해서 어디서 차도 같은 모양으로 떨어짐)
DRIVE_TOP_Y = 480
DRIVE_DIP_RATE = 3.0
# 노리는 점: 화면 끝에서 이만큼 안쪽(골대 입구 바로 앞), 이 높이 (크로스바 아래로 지나가 골망으로 들어감)
DRIVE_TARGET_GAP = 110
DRIVE_TARGET_Y = 200
# 가로 속도의 범위 (너무 가까우면 느린 로브, 너무 멀면 빠른 슛이 되지 않게 제한)
DRIVE_MIN_SPEED_X_PPS = (3.0 * PIXEL_PER_METER)
DRIVE_MAX_SPEED_X_PPS = (11.0 * PIXEL_PER_METER)

# 무회전슛: 중력 없이 정해진 길로 빠르게 날아감 (회전 없이 흔들리는 공처럼 예측하기 어려운 궤적)
# (1) 낮게 거의 일직선 → (2) 도중에 갑자기 위로 솟음 → (3) 다시 내려와 골대 입구 앞으로
KNUCKLE_SPEED_X_MPS = 11.0
KNUCKLE_SPEED_X_PPS = (KNUCKLE_SPEED_X_MPS * PIXEL_PER_METER)
# 낮게 날아가는 높이와 솟아오르는 높이
KNUCKLE_LOW_Y = 170
KNUCKLE_HIGH_Y = 330
# 솟아오르기 시작하는 곳 (골대까지 거리 중 이 비율 사이에서 매번 다르게), 솟아오르는 데 쓰는 거리의 비율
KNUCKLE_RISE_AT_RANGE = (0.30, 0.45)
KNUCKLE_RISE_LENGTH = 0.18
# 날아가는 동안의 작은 떨림: 1초에 떨리는 횟수와 크기(px), 무회전슛이 이어지는 최대 시간(초)
KNUCKLE_WOBBLE_PER_SECOND = 5.0
KNUCKLE_WOBBLE_SIZE = 6
KNUCKLE_TIME = 2.5
# 공 회전 애니메이션 배율: 드라이브슛은 앞으로 빠르게 감겨 돌고 (탑스핀), 무회전슛은 돌지 않음
DRIVE_SPIN_RATE = 2.5

# 파워슛 잔상: 세게 찬 공 뒤에 남기는 반투명한 공의 수, 잔상끼리의 시간 간격(초), 잔상을 남기는 최대 시간(초)
TRAIL_COUNT = 6
TRAIL_INTERVAL = 0.025
TRAIL_TIME = 0.8
# 공이 이 속도보다 느려지면 잔상을 멈춤, 가장 가까운 잔상의 불투명도 (멀어질수록 옅어짐)
TRAIL_STOP_SPEED_PPS = (4.0 * PIXEL_PER_METER)
TRAIL_OPACITY = 0.45

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
        # 드라이브슛, 무회전슛으로 날아가는 중인지 (다른 데 맞거나 바닥에 닿으면 끝)
        self.drive = False
        self.knuckle = False
        # 무회전슛: 찬 뒤 지난 시간, 찬 곳 (x, 높이), 노리는 골대 입구 x, 솟아오르기 시작하는 비율
        self.knuckle_time = 0.0
        self.knuckle_start_x, self.knuckle_start_y = 0.0, 0.0
        self.knuckle_target_x = 0.0
        self.knuckle_rise_at = 0.0
        # 파워슛 잔상: 남은 잔상 시간, 지난 위치들 (최근 것이 앞), 다음 위치를 남길 때까지 남은 시간
        self.trail_time = 0.0
        self.trail = []
        self.trail_wait = 0.0
        if Ball.image == None:
            Ball.image = load_image('resource/ball_sheet.png')

    def update(self):
        self.time_since_head += game_framework.frame_time
        self.head_ignore = max(self.head_ignore - game_framework.frame_time, 0)
        self.x += self.vx * game_framework.frame_time
        self.y += self.vy * game_framework.frame_time
        # 드라이브슛은 꼭대기를 지나 내려올 때 중력을 더 세게 받아 뚝 떨어지고, 무회전슛은 중력 없이 정해진 길로 날아감
        gravity_rate = 1.0
        if self.drive and self.vy < 0:
            gravity_rate = DRIVE_DIP_RATE
        elif self.knuckle:
            gravity_rate = 0.0
        self.vy -= GRAVITY_PPS2 * gravity_rate * game_framework.frame_time
        if self.knuckle:
            self.update_knuckle()

        if self.y - 32 < 80:
            self.y = 80 + 32
            self.stop_special_flight()
            self.vy = -self.vy * GROUND_BOUNCE_RATE
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

        # 굴러가는 만큼 돌고, 드라이브슛은 더 빨리 감겨 돌며, 무회전슛은 돌지 않음
        spin_rate = 0.0 if self.knuckle else DRIVE_SPIN_RATE if self.drive else 1.0
        self.frame = (self.frame + self.vx * spin_rate * game_framework.frame_time / PIXELS_PER_FRAME) % 8
        self.update_trail()

    def start_trail(self):
        # 파워슛, 파워 헤딩, 오버헤드킥으로 세게 찼을 때 잔상을 남기기 시작
        self.trail_time = TRAIL_TIME
        self.trail = []
        self.trail_wait = 0.0

    def clear_trail(self):
        # 남은 잔상을 모두 지움 (공을 처음 자리로 옮길 때 잔상이 끌려오지 않게)
        self.trail_time = 0.0
        self.trail = []

    def update_trail(self):
        # 잔상 시간 동안 일정 간격으로 지난 위치를 남기고, 시간이 끝나거나 공이 느려지면 잔상을 하나씩 지움
        self.trail_time = max(self.trail_time - game_framework.frame_time, 0)
        if self.trail_time > 0 and math.hypot(self.vx, self.vy) < TRAIL_STOP_SPEED_PPS:
            self.trail_time = 0
        self.trail_wait -= game_framework.frame_time
        if self.trail_wait > 0:
            return
        self.trail_wait = TRAIL_INTERVAL
        if self.trail_time > 0:
            self.trail.insert(0, (self.x, self.y, int(self.frame)))
            del self.trail[TRAIL_COUNT:]
        elif self.trail:
            self.trail.pop()

    def get_circle(self):
        return self.x, self.y, 32

    def bounce_from(self, cx, cy, r, head_vy, header):
        # head_vy: 머리가 위아래로 움직이는 속도 (점프 중이 아니면 0)
        # header: 헤딩한 선수 (머리 사이 왕복 판정용)
        self.stop_special_flight()

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
        self.stop_special_flight()
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
        self.stop_special_flight()
        self.vx = face_dir * TACKLE_SWEEP_X_PPS
        self.vy = TACKLE_SWEEP_Y_PPS

    def dribbled(self, x, vx):
        # 트릭스터 발 앞에 붙어 바닥으로 같이 굴러감
        # x: 붙을 가로 위치, vx: 선수가 움직이는 속도 (공 회전 애니메이션용)
        self.stop_special_flight()
        self.x = clamp(32, x, 1280 - 32)
        self.y = 80 + 32
        self.vx, self.vy = vx, 0

    def released(self, face_dir):
        # 트릭스터가 끝나면 몰고 가던 공을 앞으로 살짝 밀어 놓음 (바로 슛이 되지 않음)
        self.vx = face_dir * TRICK_RELEASE_SPEED_PPS
        self.vy = 0

    def repelled(self, cx, cy, r):
        # 철벽 방어 보호막(원)에 맞으면 원 바깥쪽으로 세게 튕겨 나감
        self.stop_special_flight()
        dx, dy = self.x - cx, self.y - cy
        d = math.sqrt(dx * dx + dy * dy)
        if d == 0:
            dx, dy, d = 0, 1, 1
        nx, ny = dx / d, dy / d
        # 공을 보호막 바깥으로 밀어냄
        self.x = cx + nx * (r + 32)
        self.y = cy + ny * (r + 32)
        # 들어온 속도가 빨라도 느려도 최소 속도 이상으로 바깥쪽을 향해 튕김
        speed = max(math.sqrt(self.vx * self.vx + self.vy * self.vy), GUARD_REPEL_SPEED_PPS)
        self.vx, self.vy = nx * speed, ny * speed

    def overhead_kicked(self, face_dir, power_rate):
        # 오버헤드킥: 바라보는 쪽 아래 대각선으로 세게 내리꽂음 (power_rate: 찬 선수의 킥 세기 배율)
        self.stop_special_flight()
        self.vx = face_dir * OVERHEAD_SPEED_X_PPS * power_rate
        self.vy = -OVERHEAD_SPEED_DOWN_PPS * power_rate
        self.start_trail()

    def stop_special_flight(self):
        # 드라이브슛, 무회전슛을 끝내고 보통 공으로 (다른 데 맞거나 바닥에 닿았을 때)
        self.drive = False
        self.knuckle = False

    def knuckle_height(self, progress):
        # 무회전슛 길에서 골대까지 간 비율(0~1)에 맞는 높이 (점과 점 사이를 부드럽게 이음)
        rise_at = self.knuckle_rise_at
        points = ((0.0, self.knuckle_start_y), (rise_at, KNUCKLE_LOW_Y),
                  (rise_at + KNUCKLE_RISE_LENGTH, KNUCKLE_HIGH_Y), (1.0, DRIVE_TARGET_Y))
        for (p0, y0), (p1, y1) in zip(points, points[1:]):
            if progress <= p1:
                t = (progress - p0) / (p1 - p0)
                t = t * t * (3 - 2 * t)
                return y0 + (y1 - y0) * t
        return DRIVE_TARGET_Y

    def update_knuckle(self):
        # 무회전슛: 골대까지 간 비율로 정해진 높이에 공을 두고, 작게 떨리게 함 (위아래 속도도 맞춰 둠)
        self.knuckle_time += game_framework.frame_time
        progress = (self.x - self.knuckle_start_x) / (self.knuckle_target_x - self.knuckle_start_x)
        if self.knuckle_time > KNUCKLE_TIME or progress >= 1.0:
            # 골대 입구 앞에 닿으면 무회전슛을 끝내고 그대로 내려가며 골망으로 들어감
            self.knuckle = False
            return
        wobble = KNUCKLE_WOBBLE_SIZE * math.sin(2 * math.pi * KNUCKLE_WOBBLE_PER_SECOND * self.knuckle_time)
        new_y = self.knuckle_height(max(progress, 0.0)) + wobble
        if game_framework.frame_time > 0:
            self.vy = (new_y - self.y) / game_framework.frame_time
        self.y = new_y

    def knuckle_kicked(self, face_dir, power_rate):
        # 무회전슛: 빠르게 차고, 솟아오를 곳을 매번 조금씩 다르게 정함 (power_rate: 찬 선수의 킥 세기 배율)
        self.stop_special_flight()
        self.vx = face_dir * KNUCKLE_SPEED_X_PPS * power_rate
        self.vy = 0
        self.knuckle = True
        self.knuckle_time = 0.0
        self.knuckle_start_x, self.knuckle_start_y = self.x, self.y
        self.knuckle_target_x = 1280 - DRIVE_TARGET_GAP if face_dir == 1 else DRIVE_TARGET_GAP
        # 골대에 너무 가까이서 차면 바로 골대 입구로 감 (나누기가 0이 되지 않게)
        if abs(self.knuckle_target_x - self.x) < 1:
            self.knuckle_target_x = self.x + face_dir
        self.knuckle_rise_at = random.uniform(*KNUCKLE_RISE_AT_RANGE)
        self.start_trail()

    def drive_kicked(self, face_dir):
        # 드라이브슛: 꼭대기(DRIVE_TOP_Y)까지 떠올랐다가 상대 골대 입구 높이에 떨어지도록 속도를 정함
        target_x = 1280 - DRIVE_TARGET_GAP if face_dir == 1 else DRIVE_TARGET_GAP
        top_y = max(DRIVE_TOP_Y, self.y + 60)
        # 꼭대기까지 올라가는 위 속도와 시간 (보통 중력), 꼭대기에서 골대 입구 높이까지 떨어지는 시간 (센 중력)
        up_speed = math.sqrt(2 * GRAVITY_PPS2 * (top_y - self.y))
        up_time = up_speed / GRAVITY_PPS2
        down_time = math.sqrt(2 * (top_y - DRIVE_TARGET_Y) / (GRAVITY_PPS2 * DRIVE_DIP_RATE))
        # 그 시간 동안 골대까지 가도록 가로 속도를 정함
        speed_x = abs(target_x - self.x) / (up_time + down_time)
        speed_x = clamp(DRIVE_MIN_SPEED_X_PPS, speed_x, DRIVE_MAX_SPEED_X_PPS)
        self.vx = face_dir * speed_x
        self.vy = up_speed
        self.drive = True
        self.start_trail()

    def power_header(self):
        # 파워슛 헤딩: 튕겨 나가는 가로 속도를 파워슛 배율만큼 올림
        self.vx *= POWER_SHOT_RATE
        self.start_trail()

    def kicked(self, face_dir, power_rate, power_shot):
        # power_rate: 찬 선수의 킥 세기 배율 (파워 3이 1.0배)
        # power_shot: 파워슛이면 가로 속도를 크게 올림
        self.stop_special_flight()
        self.vx = face_dir * KICK_SPEED_X_PPS * power_rate
        self.vy = KICK_SPEED_Y_PPS * power_rate
        if power_shot:
            self.vx *= POWER_SHOT_RATE
            self.start_trail()

    def draw(self):
        # 잔상은 오래된 것부터 옅게 그리고, 그 위에 진짜 공 (같은 공 그림의 불투명도만 잠깐 바꿔 그림)
        for i in range(len(self.trail) - 1, -1, -1):
            x, y, frame = self.trail[i]
            Ball.image.opacify(TRAIL_OPACITY * (1 - i / TRAIL_COUNT))
            Ball.image.clip_draw(frame * 64, 0, 64, 64, x, y)
        Ball.image.opacify(1.0)
        Ball.image.clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y)
