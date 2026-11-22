import random
import sys

from pico2d import *

import game_framework
import select_mode
import game_world
import loading_mode
import name_mode
import records
import title_mode
import tournament
from background import Background
from ground import Ground
from character import Character, GAUGE_SCORE, GAUGE_CONCEDE, TRICK_SPEED_RATE
from ball import Ball
from goal import Goal
from hit_effect import HitEffect
from score_board import ScoreBoard
from timer_board import TimerBoard
from match import Match
from opponent_ai import OpponentAI
from gauge_board import GaugeBoard
from round_board import RoundBoard
from result_board import ResultBoard
from champion_board import ChampionBoard
from character_data import CHARACTER_TYPES

# 두 선수 중심 사이의 최소 거리 (머리 사이로 공이 빠져나갈 틈이 생기는 거리)
MIN_PLAYER_DISTANCE = 140
# 두 선수의 높이 차이가 이보다 작으면 같은 높이로 보고 밀어냄 (한쪽이 높이 떠 있을 때는 밀지 않음)
PLAYER_OVERLAP_HEIGHT = 90
# 파워슛 헤딩 이펙트 크기 (보통 128px)
POWER_EFFECT_SIZE = 256
# 밀어내는 최대 속도 (한 번에 확 밀려 순간이동처럼 보이지 않게 함)
PLAYER_PUSH_SPEED_PPS = 400
# 트릭스터가 공을 몰고 갈 때 선수 중심에서 공 중심까지의 가로 거리 (몸 반폭 18 + 공 반지름 32 + 여유)
DRIBBLE_DISTANCE = 54

player = None
opponent = None
ball = None
goal_left = None
goal_right = None
# 플레이어가 상대보다 왼쪽에 있으면 1, 오른쪽에 있으면 -1 (밀어낼 방향)
player_side = 1
match = None
# P 키로 게임을 잠시 멈췄는지 (데모와 확인용)
paused = False
# 경기가 끝나면 보여 주는 결과 또는 우승 장면 (끝나기 전에는 None)
result_board = None


def preload_tasks():
    # 로딩 화면에서 미리 할 일 목록: 객체를 한 번씩 만들어 보면 각 클래스가 공유 이미지와 글꼴을 불러 둠
    # (경기 화면에 들어올 때는 이미 불러 둔 것을 그대로 씀)
    tasks = [Background, Ground, lambda: Goal('left'), Ball, lambda: HitEffect(0, 0),
             ScoreBoard, TimerBoard, RoundBoard, lambda: GaugeBoard(None, 'left'),
             lambda: ResultBoard(True, 0, 0), ChampionBoard]
    # 선수 시트는 유형마다 한 장씩
    for key in CHARACTER_TYPES:
        tasks.append(lambda key=key: Character(key, 0, 1))
    return tasks


def collide_circle(a, b):
    ax, ay, ar = a
    bx, by, br = b
    return (ax - bx) ** 2 + (ay - by) ** 2 < (ar + br) ** 2


def collide_box(a, b):
    # 사각형끼리 충돌 (강의의 바운딩 박스 충돌 검사)
    left_a, bottom_a, right_a, top_a = a
    left_b, bottom_b, right_b, top_b = b
    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False
    return True


def collide_circle_box(c, bb):
    cx, cy, r = c
    left, bottom, right, top = bb
    # 사각형 위에서 원 중심과 가장 가까운 점까지의 거리가 반지름보다 짧으면 충돌
    px = clamp(left, cx, right)
    py = clamp(bottom, cy, top)
    return (cx - px) ** 2 + (cy - py) ** 2 < r ** 2


def ball_players():
    # 공과 부딪힐 수 있는 선수들
    # 한 선수가 트릭스터나 하드태클 중이면 공은 그 선수에게만 반응함 (상대는 공과 부딪히지 않음)
    if player.state in ('TRICK', 'TACKLE'):
        return (player,)
    if opponent.state in ('TRICK', 'TACKLE'):
        return (opponent,)
    # 넘어져 누워 있는 선수는 공과 부딪히지 않음
    return tuple(c for c in (player, opponent) if c.state != 'FALL')


def reset_positions():
    global player_side

    # 득점 후 선수와 공을 처음 자리로 되돌림 (선수는 하던 동작도 끝냄)
    # 플레이어가 다시 왼쪽에 서므로 어느 쪽인지도 처음 값으로
    player_side = 1
    player.reset(320, 1)
    opponent.reset(960, -1)
    ball.x, ball.y = 640, 400
    ball.vx, ball.vy = 0, 0


def init():
    global player
    global opponent
    global ball
    global goal_left
    global goal_right
    global match
    global paused
    global result_board

    # 멈춤 상태로 끝난 경기가 있어도 새 경기는 진행 상태로 시작
    paused = False
    result_board = None

    background = Background()
    game_world.add_object(background, 0)

    ground = Ground()
    game_world.add_object(ground, 0)

    # 플레이어는 선택 화면에서 고른 유형
    player_type = select_mode.TYPE_KEYS[select_mode.selected]
    player = Character(player_type, 320, 1)
    game_world.add_object(player, 1)

    # 상대 선수: 고르지 않은 유형 중 하나, 오른쪽에서 왼쪽을 바라봄
    opponent_type = random.choice([key for key in select_mode.TYPE_KEYS if key != player_type])
    # 상대는 라운드가 오를수록 빨라지고 킥이 세짐
    opponent = Character(opponent_type, 960, -1, tournament.opponent_stat_rate())
    game_world.add_object(opponent, 1)

    # 상대 선수는 AI가 조종 (그림이 없으므로 레이어는 상관없음)
    # 라운드가 낮을수록 AI가 공의 움직임에 늦게 반응함
    opponent_ai = OpponentAI(opponent, tournament.ai_reaction_delay())
    game_world.add_object(opponent_ai, 1)

    ball = Ball()
    game_world.add_object(ball, 1)

    # 골대는 공보다 나중에 그려서, 공이 골대 안으로 들어가는 것처럼 보이게 함
    goal_left = Goal('left')
    game_world.add_object(goal_left, 1)

    goal_right = Goal('right')
    game_world.add_object(goal_right, 1)

    score_board = ScoreBoard()
    game_world.add_object(score_board, 2)

    timer_board = TimerBoard()
    game_world.add_object(timer_board, 2)

    # 왼쪽 위에 토너먼트 라운드
    round_board = RoundBoard()
    game_world.add_object(round_board, 2)

    # 스킬 게이지: 플레이어는 왼쪽 아래, 상대는 오른쪽 아래
    player_gauge = GaugeBoard(player, 'left')
    game_world.add_object(player_gauge, 2)

    opponent_gauge = GaugeBoard(opponent, 'right')
    game_world.add_object(opponent_gauge, 2)

    # 경기 한 판 (그림이 없어서 어느 레이어든 상관없지만, 경기 진행은 UI와 함께 둠)
    match = Match()
    game_world.add_object(match, 2)


def finish():
    # 경기 화면을 떠날 때 world를 비워서, 다시 들어와도 객체가 겹쳐 쌓이지 않게 함
    game_world.clear()


def update():
    global player_side

    # 멈춤 중이면 더 이상 진행하지 않음 (화면은 멈춘 채로 그려짐)
    if paused:
        return
    # 경기가 끝나면 경기장은 멈추고 결과만 움직임
    if match.over:
        if result_board is None:
            show_result()
        result_board.update()
        return

    game_world.update()

    # 두 선수가 너무 붙으면 서로 반씩 밀어냄 (공이 둘 사이에 끼어 갇히지 않게 함)
    # 트릭스터 중이거나 누가 넘어져 있으면 밀어내지 않음 (통과해 제치거나 넘어간 선수를 지나감)
    gap = opponent.x - player.x
    no_push = any(c.state in ('TRICK', 'FALL', 'TACKLE') for c in (player, opponent))
    # 실제로 가까이 붙어 있을 때만 밀어냄 (멀리 떨어져 있으면 순서와 관계없이 밀지 않음)
    if not no_push and abs(gap) < MIN_PLAYER_DISTANCE and abs(player.y - opponent.y) < PLAYER_OVERLAP_HEIGHT and gap * player_side < MIN_PLAYER_DISTANCE:
        # 원래 있던 쪽으로 밀고, 한 프레임에 밀어내는 거리는 최대 속도만큼으로 제한
        push = min((MIN_PLAYER_DISTANCE - gap * player_side) / 2, PLAYER_PUSH_SPEED_PPS * game_framework.frame_time)
        player.x = clamp(50, player.x - player_side * push, 1280 - 50)
        opponent.x = clamp(50, opponent.x + player_side * push, 1280 - 50)
    else:
        # 충분히 떨어져 있거나 한쪽이 높이 떠 있거나 트릭스터 중이면, 지금 위치로 어느 쪽인지 새로 정함
        player_side = 1 if gap >= 0 else -1

    # 하드태클의 다리가 상대 몸에 닿으면 상대가 넘어짐 (점프 중이나 트릭스터 중에는 넘어지지 않음)
    for character, other in ((player, opponent), (opponent, player)):
        if character.state == 'TACKLE' and collide_box(character.get_tackle_bb(), other.get_bb()):
            other.fall()

    # 트릭스터가 끝났으면 몰고 가던 공을 돌진하던 쪽으로 살짝 밀어 놓음
    for character in (player, opponent):
        if character.dribble and character.state != 'TRICK':
            ball.released(character.trick_dir)
            character.dribble = False

    # 두 선수 모두 헤딩과 킥으로 공을 칠 수 있음 (트릭스터 중이면 그 선수만)
    for character in ball_players():
        # 하드태클 중에는 뻗은 다리로만 공을 쓸어 감 (서 있는 자세의 머리, 발 충돌은 없음)
        if character.state == 'TACKLE':
            if not character.kick_hit and collide_circle_box(ball.get_circle(), character.get_tackle_bb()):
                ball.swept(character.face_dir)
                character.kick_hit = True
                game_world.add_object(HitEffect(ball.x, ball.y), 1)
                character.touch_ball()
            continue

        # 철벽 방어 중에는 보호막 범위 안의 공을 바깥으로 튕겨 냄 (머리, 킥, 몸 충돌 대신)
        if character.state == 'GUARD':
            if collide_circle(character.get_guard_circle(), ball.get_circle()):
                ball.repelled(*character.get_guard_circle())
                # 이펙트와 게이지는 한 번 쓸 때 한 번만
                if not character.kick_hit:
                    character.kick_hit = True
                    game_world.add_object(HitEffect(ball.x, ball.y), 1)
                    character.touch_ball()
            continue

        # 트릭스터 중 낮은 공이 몸이나 발에 닿으면 발 앞에 붙여 몰고 감 (머리, 킥 충돌은 없음)
        if character.state == 'TRICK':
            if not character.dribble and (collide_circle_box(ball.get_circle(), character.get_bb()) or collide_circle(character.get_foot(), ball.get_circle())):
                character.dribble = True
                character.touch_ball()
            if character.dribble:
                trick_vx = character.face_dir * character.run_speed_pps * TRICK_SPEED_RATE
                ball.dribbled(character.x + character.face_dir * DRIBBLE_DISTANCE, trick_vx)
                continue

        # 오버헤드킥 중에는 몸이 뒤집혀 머리 대신 위로 올라간 발로 공을 참 (뛰어오를 때 한 번만)
        if character.state == 'OVERHEAD':
            if int(character.frame) == 3 and not character.kick_hit:
                if collide_circle(character.get_overhead_foot(), ball.get_circle()):
                    ball.overhead_kicked(character.face_dir, character.kick_power_rate)
                    character.kick_hit = True
                    foot_x, foot_y, foot_r = character.get_overhead_foot()
                    game_world.add_object(HitEffect((foot_x + ball.x) / 2, (foot_y + ball.y) / 2, POWER_EFFECT_SIZE), 1)
                    character.touch_ball()
            continue

        if ball.head_ignore == 0 and collide_circle(character.get_head(), ball.get_circle()):
            # 점프 중이면 머리가 움직이는 속도를 같이 넘김
            head_vy = character.vy if character.state == 'JUMP' else 0
            ball.bounce_from(*character.get_head(), head_vy, character)
            # 파워슛이 준비되어 있으면 헤딩도 세게, 이펙트도 크게 (한 번 쓰면 해제)
            effect_size = 128
            if character.power_shot:
                ball.power_header()
                character.power_shot = False
                effect_size = POWER_EFFECT_SIZE
            # 머리와 공이 맞닿은 자리(두 중심의 가운데)에 이펙트
            head_x, head_y, head_r = character.get_head()
            game_world.add_object(HitEffect((head_x + ball.x) / 2, (head_y + ball.y) / 2, effect_size), 1)
            # 공을 건드리면 스킬 게이지 증가
            character.touch_ball()

        # 보통 킥과 파워슛 킥 모두 발을 뻗은 칸(2~4)에서 공을 참
        if character.state in ('KICK', 'POWER') and 2 <= int(character.frame) <= 4 and not character.kick_hit:
            if collide_circle(character.get_foot(), ball.get_circle()):
                ball.kicked(character.face_dir, character.kick_power_rate, character.power_shot)
                # 파워슛은 한 번 차면 해제
                character.power_shot = False
                character.kick_hit = True
                # 발과 공이 맞닿은 자리(두 중심의 가운데)에 이펙트
                foot_x, foot_y, foot_r = character.get_foot()
                game_world.add_object(HitEffect((foot_x + ball.x) / 2, (foot_y + ball.y) / 2), 1)
                # 공을 건드리면 스킬 게이지 증가
                character.touch_ball()

    # 공이 선수 몸에 맞으면 튕김 (몸을 통과해 뒤로 빠지지 않음, 트릭스터 중이면 그 선수만)
    for character in ball_players():
        if character.state not in ('TACKLE', 'GUARD') and collide_circle_box(ball.get_circle(), character.get_bb()):
            ball.bounce_from_box(*character.get_bb())
            ball.blocked()

    # 공이 크로스바에 맞으면 튕김
    for goal in (goal_left, goal_right):
        if collide_circle_box(ball.get_circle(), goal.get_bb()):
            ball.bounce_from_box(*goal.get_bb())

    # 공이 골대 안에 들어가면 골 (확인용 출력 후 선수와 공을 처음 자리로)
    for goal in (goal_left, goal_right):
        if goal.is_ball_in(*ball.get_circle()):
            match.goal(goal.side)
            # 넣은 팀은 +30, 먹힌 팀은 +15 (왼쪽 골대에 들어가면 오른쪽 팀인 상대가 넣은 것)
            if goal.side == 'left':
                opponent.add_gauge(GAUGE_SCORE)
                player.add_gauge(GAUGE_CONCEDE)
            else:
                player.add_gauge(GAUGE_SCORE)
                opponent.add_gauge(GAUGE_CONCEDE)
            print(f'골! ({goal.side} 골대) {match.score_left} : {match.score_right}')
            reset_positions()


def show_result():
    # 점수판, 타이머 같은 UI를 모두 치우고, 그 자리에 결과를 띄움 (경기장은 그대로)
    global result_board
    won = match.score_left > match.score_right
    # 이번 경기 점수를 토너먼트 합에 더함 (경기가 끝날 때 한 번만 불림)
    tournament.add_match_score(match.score_left, match.score_right)
    # 결승에서 이기면 우승 장면, 아니면 승리 / 패배 결과
    if won and tournament.is_final():
        result_board = ChampionBoard()
    else:
        result_board = ResultBoard(won, match.score_left, match.score_right)
    game_world.clear_layer(2)
    game_world.add_object(result_board, 2)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def start_next_match():
    # 로딩 화면을 거쳐 경기 화면을 새로 시작 (상대는 다시 무작위, 다음 모드는 이 경기 화면 모듈 자신)
    loading_mode.next_mode = sys.modules[__name__]
    loading_mode.tasks = preload_tasks()
    game_framework.change_mode(loading_mode)


def restart_tournament():
    # 같은 캐릭터로 32강부터 다시
    tournament.start()
    start_next_match()


def go_to_title():
    game_framework.change_mode(title_mode)


def end_tournament(next_action):
    # 토너먼트가 끝났을 때 (지거나 우승): 기록이 랭킹에 들면 닉네임 패널을 띄우고, 입력이 끝나면 next_action
    won = match.score_left > match.score_right
    # 이긴 경기 수: 진 경기는 빼고, 우승이면 결승까지 모두
    wins = tournament.round_index + (1 if won else 0)
    if not records.is_ranked(wins, tournament.goals_for, tournament.goals_against):
        next_action()
        return

    def after_input():
        # 닉네임 패널을 내리고 고른 다음 화면으로
        game_framework.pop_mode()
        next_action()

    name_mode.wins = wins
    name_mode.after_input = after_input
    # 닉네임 패널에 가려지지 않게 결과 패널과 안내는 숨기고, 경기 화면 위에 닉네임 패널을 올림
    result_board.show_panel = False
    game_framework.push_mode(name_mode)


def next_after_match(key):
    # 경기가 끝난 뒤 Space / ESC
    # 이기면 Space로 다음 라운드, ESC로 메인 (토너먼트를 그만두면 기록하지 않음)
    # 지거나 우승하면 토너먼트가 끝나 기록을 남김: 지고 Space면 32강부터 다시, 그 밖에는 메인
    won = match.score_left > match.score_right
    if won and not tournament.is_final():
        if key == SDLK_SPACE:
            tournament.next_round()
            start_next_match()
        else:
            go_to_title()
        return
    if not won and key == SDLK_SPACE:
        end_tournament(restart_tournament)
    else:
        end_tournament(go_to_title)


def handle_events():
    global paused

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif match.over:
            # 경기가 끝나면 선수는 움직이지 않고, Space로 다음 경기, ESC로 메인 화면
            if event.type == SDL_KEYDOWN and event.key in (SDLK_SPACE, SDLK_ESCAPE):
                next_after_match(event.key)
                # 화면이 바뀌었으므로 남은 입력은 처리하지 않음
                return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            # P 키를 누를 때마다 멈춤과 다시 진행이 바뀜
            paused = not paused
        else:
            player.handle_event(event)


def pause():
    pass


def resume():
    pass
