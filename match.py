# 경기 시간 (초)
MATCH_TIME = 60.0


class Match:
    # 한 경기의 점수, 남은 시간, 종료 여부를 관리

    def __init__(self):
        # 점수: 왼쪽 팀(플레이어), 오른쪽 팀(상대)
        self.score_left = 0
        self.score_right = 0
        # 남은 시간 (초)
        self.time_left = MATCH_TIME
        # 경기가 끝났는지
        self.over = False

    def update(self):
        pass

    def draw(self):
        pass
