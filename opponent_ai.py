import play_mode

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
        # 규칙 1: 공의 가로 위치 쪽으로 이동
        dx = play_mode.ball.x - self.character.x
        if self.character.dir == 0:
            if abs(dx) > FOLLOW_START_DISTANCE:
                self.move(1 if dx > 0 else -1)
        else:
            if abs(dx) < FOLLOW_STOP_DISTANCE:
                self.move(0)
            elif dx * self.character.dir < 0:
                # 공이 반대쪽으로 넘어가면 방향을 바꿈
                self.move(-self.character.dir)

        # 규칙 2: 공이 머리 높이로 가까이 내려오면 점프해서 헤딩
        ball = play_mode.ball
        if abs(dx) < JUMP_DISTANCE and JUMP_MIN_HEIGHT < ball.y < JUMP_MAX_HEIGHT and ball.vy < 0:
            self.character.jump()

        # 규칙 3: 공이 발 앞에 있으면 킥 (자기 골대 쪽으로 차지 않도록 왼쪽을 볼 때만)
        front = dx * self.character.face_dir
        if self.character.face_dir == -1 and KICK_MIN_DISTANCE < front < KICK_MAX_DISTANCE and ball.y < KICK_MAX_HEIGHT:
            self.character.kick()

    def draw(self):
        pass
