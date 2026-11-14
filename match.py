import game_framework

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
        # 남은 시간을 지난 시간만큼 줄임 (0 밑으로는 내려가지 않음)
        self.time_left = max(self.time_left - game_framework.frame_time, 0)

        # 시간이 끝났을 때 점수가 다르면 경기 종료 (같으면 골든골로 계속)
        if self.time_left == 0 and self.score_left != self.score_right:
            self.over = True
            if self.score_left > self.score_right:
                print(f'경기 종료 : 승리 {self.score_left} : {self.score_right}')
            else:
                print(f'경기 종료 : 패배 {self.score_left} : {self.score_right}')

    def goal(self, side):
        # 왼쪽 골대에 들어가면 오른쪽 팀, 오른쪽 골대에 들어가면 왼쪽 팀 득점
        if side == 'left':
            self.score_right += 1
        else:
            self.score_left += 1

    def draw(self):
        pass
