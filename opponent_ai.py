class OpponentAI:
    # 상대 선수를 움직이는 규칙형 AI
    # 키보드 대신 상태 머신 이벤트(move_start, move_stop, jump, kick)를 넣어 줌

    def __init__(self, character):
        # character: AI가 조종할 선수
        self.character = character

    def update(self):
        pass

    def draw(self):
        pass
