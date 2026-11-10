from pico2d import *
import pico2d.pico2d as pico2d_core

import game_world
from background import Background
from ground import Ground
from character import Character
from ball import Ball

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720


def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            player.handle_event(event)


def reset_world():
    global running
    global player
    global ball

    running = True

    background = Background()
    game_world.add_object(background, 0)

    ground = Ground()
    game_world.add_object(ground, 0)

    player = Character()
    game_world.add_object(player, 1)

    ball = Ball()
    game_world.add_object(ball, 1)


def collide_circle(a, b):
    ax, ay, ar = a
    bx, by, br = b
    return (ax - bx) ** 2 + (ay - by) ** 2 < (ar + br) ** 2


def update_world():
    game_world.update()

    if collide_circle(player.get_head(), ball.get_circle()):
        ball.bounce_from(*player.get_head())

    if player.state == 'KICK' and 2 <= player.frame <= 4:
        if collide_circle(player.get_foot(), ball.get_circle()):
            ball.kicked(player.face_dir)


def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()


open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
SDL_SetWindowFullscreen(pico2d_core.window, SDL_WINDOW_FULLSCREEN_DESKTOP)
SDL_RenderSetLogicalSize(pico2d_core.renderer, SCREEN_WIDTH, SCREEN_HEIGHT)
reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.05)

close_canvas()
