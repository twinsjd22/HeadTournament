import play_mode

# 공과 가로 거리가 이보다 멀면 공 쪽으로 움직이기 시작
FOLLOW_START_DISTANCE = 30
# 공과 가로 거리가 이보다 가까우면 멈춤 (시작 거리보다 짧게 두어 멈췄다 움직였다 떨리지 않게 함)
FOLLOW_STOP_DISTANCE = 10


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

    def draw(self):
        pass
