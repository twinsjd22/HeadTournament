from pico2d import *

import game_framework
import game_world
from background import Background
from ground import Ground
from character import Character, GAUGE_SCORE, GAUGE_CONCEDE
from ball import Ball
from goal import Goal
from hit_effect import HitEffect
from score_board import ScoreBoard
from timer_board import TimerBoard
from match import Match
from opponent_ai import OpponentAI
from gauge_board import GaugeBoard

# 두 선수 중심 사이의 최소 거리 (머리 사이로 공이 빠져나갈 틈이 생기는 거리)
MIN_PLAYER_DISTANCE = 140
# 두 선수의 높이 차이가 이보다 작으면 같은 높이로 보고 밀어냄 (한쪽이 높이 떠 있을 때는 밀지 않음)
PLAYER_OVERLAP_HEIGHT = 90
# 파워슛 헤딩 이펙트 크기 (보통 128px)
POWER_EFFECT_SIZE = 256
# 밀어내는 최대 속도 (한 번에 확 밀려 순간이동처럼 보이지 않게 함)
PLAYER_PUSH_SPEED_PPS = 400

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

    background = Background()
    game_world.add_object(background, 0)

    ground = Ground()
    game_world.add_object(ground, 0)

    player = Character('defender', 320, 1)
    game_world.add_object(player, 1)

    # 상대 선수: 오른쪽에서 왼쪽을 바라봄 (움직임은 나중에 AI로)
    opponent = Character('trickster', 960, -1)
    game_world.add_object(opponent, 1)

    # 상대 선수는 AI가 조종 (그림이 없으므로 레이어는 상관없음)
    opponent_ai = OpponentAI(opponent)
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

    # 멈춤 중이거나 경기가 끝나면 더 이상 진행하지 않음 (화면은 멈춘 채로 그려짐)
    if paused or match.over:
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
        if character.state != 'TACKLE' and collide_circle_box(ball.get_circle(), character.get_bb()):
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


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def handle_events():
    global paused

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
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
