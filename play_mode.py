from pico2d import *

import game_framework
import game_world
from background import Background
from ground import Ground
from character import Character
from ball import Ball
from goal import Goal
from hit_effect import HitEffect
from score_board import ScoreBoard
from timer_board import TimerBoard

player = None
ball = None
goal_left = None
goal_right = None
# 점수: 왼쪽 팀(플레이어), 오른쪽 팀(상대)
score_left = 0
score_right = 0
# 경기 남은 시간 (초)
MATCH_TIME = 60.0
time_left = MATCH_TIME


def collide_circle(a, b):
    ax, ay, ar = a
    bx, by, br = b
    return (ax - bx) ** 2 + (ay - by) ** 2 < (ar + br) ** 2


def collide_circle_box(c, bb):
    cx, cy, r = c
    left, bottom, right, top = bb
    # 사각형 위에서 원 중심과 가장 가까운 점까지의 거리가 반지름보다 짧으면 충돌
    px = clamp(left, cx, right)
    py = clamp(bottom, cy, top)
    return (cx - px) ** 2 + (cy - py) ** 2 < r ** 2


def reset_positions():
    # 득점 후 선수와 공을 처음 자리로 되돌림
    player.x, player.y = 320, 160
    player.vy = 0
    ball.x, ball.y = 640, 400
    ball.vx, ball.vy = 0, 0


def init():
    global player
    global ball
    global goal_left
    global goal_right
    global score_left
    global score_right
    global time_left

    score_left, score_right = 0, 0
    time_left = MATCH_TIME

    background = Background()
    game_world.add_object(background, 0)

    ground = Ground()
    game_world.add_object(ground, 0)

    player = Character()
    game_world.add_object(player, 1)

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


def finish():
    pass


def update():
    global score_left
    global score_right
    global time_left

    game_world.update()

    # 남은 시간을 지난 시간만큼 줄임 (0 밑으로는 내려가지 않음)
    time_left = max(time_left - game_framework.frame_time, 0)

    if collide_circle(player.get_head(), ball.get_circle()):
        ball.bounce_from(*player.get_head())
        # 머리와 공이 맞닿은 자리(두 중심의 가운데)에 이펙트
        head_x, head_y, head_r = player.get_head()
        game_world.add_object(HitEffect((head_x + ball.x) / 2, (head_y + ball.y) / 2), 1)

    if player.state == 'KICK' and 2 <= int(player.frame) <= 4 and not player.kick_hit:
        if collide_circle(player.get_foot(), ball.get_circle()):
            ball.kicked(player.face_dir)
            player.kick_hit = True
            # 발과 공이 맞닿은 자리(두 중심의 가운데)에 이펙트
            foot_x, foot_y, foot_r = player.get_foot()
            game_world.add_object(HitEffect((foot_x + ball.x) / 2, (foot_y + ball.y) / 2), 1)

    # 공이 크로스바에 맞으면 튕김
    for goal in (goal_left, goal_right):
        if collide_circle_box(ball.get_circle(), goal.get_bb()):
            ball.bounce_from_box(*goal.get_bb())

    # 공이 골대 안에 들어가면 골 (확인용 출력 후 선수와 공을 처음 자리로)
    for goal in (goal_left, goal_right):
        if goal.is_ball_in(*ball.get_circle()):
            # 왼쪽 골대에 들어가면 오른쪽 팀, 오른쪽 골대에 들어가면 왼쪽 팀 득점
            if goal.side == 'left':
                score_right += 1
            else:
                score_left += 1
            print(f'골! ({goal.side} 골대) {score_left} : {score_right}')
            reset_positions()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)


def pause():
    pass


def resume():
    pass
