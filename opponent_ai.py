import math

import play_mode
from ball import GRAVITY_PPS2

# 공과 가로 거리가 이보다 멀면 공 쪽으로 움직이기 시작
FOLLOW_START_DISTANCE = 30
# 공과 가로 거리가 이보다 가까우면 멈춤 (시작 거리보다 짧게 두어 멈췄다 움직였다 떨리지 않게 함)
FOLLOW_STOP_DISTANCE = 10

# 헤딩 점프: 공이 가로로 이만큼 가깝고, 머리 위 이 높이 사이에서 내려오고 있으면 점프
JUMP_DISTANCE = 60
JUMP_MIN_HEIGHT = 230
JUMP_MAX_HEIGHT = 400

# 킥: 공이 바라보는 쪽 발 앞 이 거리 사이에 있고 (발이 닿는 거리), 이 높이보다 낮으면 킥
KICK_MIN_DISTANCE = 30
KICK_MAX_DISTANCE = 70
KICK_MAX_HEIGHT = 170

# 공이 이 높이보다 낮으면 공 오른쪽(자기 골대 쪽)에 서서 왼쪽으로 공격함
BALL_LOW_HEIGHT = 170
# 공 오른쪽에 설 때 공과의 가로 거리
BEHIND_DISTANCE = 50
# 공이 오른쪽 앞(자기 골대 쪽)에 이 거리 안으로 낮게 있으면 점프해서 넘어감
JUMP_OVER_DISTANCE = 90
# 높은 공은 공보다 이만큼 오른쪽에 서서, 공이 머리 왼쪽에 맞아 플레이어 쪽으로 튕기게 함
HEADING_OFFSET = 20
# 서 있는 선수의 머리 높이 (높은 공이 이 높이까지 떨어질 자리를 예측함)
HEAD_HEIGHT = 230


def predict_landing_x(ball):
    # 공이 머리 높이까지 떨어졌을 때의 가로 위치 (벽에 튕기는 것은 무시)
    height = ball.y - HEAD_HEIGHT
    if height <= 0:
        return ball.x
    time = (ball.vy + math.sqrt(ball.vy * ball.vy + 2 * GRAVITY_PPS2 * height)) / GRAVITY_PPS2
    return min(max(ball.x + ball.vx * time, 32), 1280 - 32)


class OpponentAI:
    # 상대 선수를 움직이는 규칙형 AI
    # 키보드 대신 상태 머신 이벤트(move_start, move_stop, jump, kick)를 넣어 줌

    def __init__(self, character):
        # character: AI가 조종할 선수
        self.character = character

    def move(self, dir):
        # 키보드의 방향키 처리와 같은 방식으로 방향을 바꾸고 이벤트를 넣음
        self.character.dir = dir
        if dir == 0:
            self.character.move_stop()
        else:
            self.character.face_dir = dir
            self.character.move_start()

    def update(self):
        ball = play_mode.ball
        dx = ball.x - self.character.x

        # 규칙 1: 공 쪽으로 이동
        # 공이 낮으면 공 오른쪽에 서서 플레이어 골대 쪽으로 밀고,
        # 높으면 공이 떨어질 자리보다 약간 오른쪽에 미리 서서 헤딩이 플레이어 쪽으로 가게 함
        if ball.y < BALL_LOW_HEIGHT:
            target_dx = ball.x + BEHIND_DISTANCE - self.character.x
        else:
            target_dx = predict_landing_x(ball) + HEADING_OFFSET - self.character.x
        if self.character.dir == 0:
            if abs(target_dx) > FOLLOW_START_DISTANCE:
                self.move(1 if target_dx > 0 else -1)
        else:
            if abs(target_dx) < FOLLOW_STOP_DISTANCE:
                self.move(0)
                # 멈추면 플레이어 골대 쪽을 바라봄
                self.character.face_dir = -1
            elif target_dx * self.character.dir < 0:
                # 목표가 반대쪽으로 넘어가면 방향을 바꿈
                self.move(-self.character.dir)

        # 규칙 4: 공이 오른쪽 앞(자기 골대 쪽)에 낮게 있으면 밀지 않도록 점프해서 넘어감
        if self.character.dir == 1 and 0 < dx < JUMP_OVER_DISTANCE and ball.y < BALL_LOW_HEIGHT:
            self.character.jump()

        # 규칙 2: 공이 머리 높이로 가까이 내려오면 점프해서 헤딩
        # (공이 머리 오른쪽에 있으면 자기 골대 쪽으로 튕기므로 점프하지 않음)
        if -JUMP_DISTANCE < dx <= 0 and JUMP_MIN_HEIGHT < ball.y < JUMP_MAX_HEIGHT and ball.vy < 0:
            self.character.jump()

        # 규칙 3: 공이 발 앞에 있으면 킥 (자기 골대 쪽으로 차지 않도록 왼쪽을 볼 때만)
        front = dx * self.character.face_dir
        if self.character.face_dir == -1 and KICK_MIN_DISTANCE < front < KICK_MAX_DISTANCE and ball.y < KICK_MAX_HEIGHT:
            self.character.kick()

    def draw(self):
        pass
