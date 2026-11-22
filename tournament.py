# 토너먼트 진행: 32강부터 결승까지 5경기, 지금 몇 강인지 기억함
# (경기 화면이 바뀌어도 값이 남도록 game_world처럼 모듈 변수로 둠)

# 라운드 이름 (앞에서부터 차례로 진행)
ROUNDS = ('32강', '16강', '8강', '4강', '결승')

# 라운드별 상대 능력치 배율 (달리기 속도, 킥 세기): 32강은 약하게, 결승은 강하게
OPPONENT_STAT_RATES = (0.8, 0.9, 1.0, 1.1, 1.2)

# 라운드별 상대 AI의 반응 지연(초): 32강은 공을 늦게 보고 판단하고, 결승은 바로 반응함
AI_REACTION_DELAYS = (0.3, 0.2, 0.1, 0.05, 0.0)

# 지금 라운드 번호 (ROUNDS 안의 위치)
round_index = 0
# 이번 토너먼트에서 넣은 골과 먹은 골의 합 (기록 저장의 득실차에 씀)
goals_for = 0
goals_against = 0


def start():
    # 새 토너먼트를 32강부터 시작 (득점과 실점 합도 처음부터)
    global round_index, goals_for, goals_against
    round_index = 0
    goals_for = 0
    goals_against = 0


def add_match_score(scored, conceded):
    # 끝난 경기의 점수를 이번 토너먼트 합에 더함
    global goals_for, goals_against
    goals_for += scored
    goals_against += conceded


def round_name():
    # 지금 라운드 이름 (예: '8강')
    return ROUNDS[round_index]


def opponent_stat_rate():
    # 지금 라운드 상대의 능력치 배율
    return OPPONENT_STAT_RATES[round_index]


def ai_reaction_delay():
    # 지금 라운드 상대 AI의 반응 지연
    return AI_REACTION_DELAYS[round_index]


def is_final():
    # 지금 경기가 결승인지 (이기면 우승)
    return round_index == len(ROUNDS) - 1


def next_round():
    # 이긴 뒤 다음 라운드로 (결승 다음은 없음)
    global round_index
    if not is_final():
        round_index += 1
