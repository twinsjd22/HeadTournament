# 토너먼트 진행: 32강부터 결승까지 5경기, 지금 몇 강인지 기억함
# (경기 화면이 바뀌어도 값이 남도록 game_world처럼 모듈 변수로 둠)

# 라운드 이름 (앞에서부터 차례로 진행)
ROUNDS = ('32강', '16강', '8강', '4강', '결승')

# 지금 라운드 번호 (ROUNDS 안의 위치)
round_index = 0


def start():
    # 새 토너먼트를 32강부터 시작
    global round_index
    round_index = 0


def round_name():
    # 지금 라운드 이름 (예: '8강')
    return ROUNDS[round_index]


def is_final():
    # 지금 경기가 결승인지 (이기면 우승)
    return round_index == len(ROUNDS) - 1


def next_round():
    # 이긴 뒤 다음 라운드로 (결승 다음은 없음)
    global round_index
    if not is_final():
        round_index += 1
