from pico2d import *

import game_framework
import game_world
from background import Background
from ground import Ground
from character import Character
from ball import Ball

player = None
ball = None


def collide_circle(a, b):
    ax, ay, ar = a
    bx, by, br = b
    return (ax - bx) ** 2 + (ay - by) ** 2 < (ar + br) ** 2


def init():
    global player
    global ball

    background = Background()
    game_world.add_object(background, 0)

    ground = Ground()
    game_world.add_object(ground, 0)

    player = Character()
    game_world.add_object(player, 1)

    ball = Ball()
    game_world.add_object(ball, 1)


def finish():
    pass


def update():
    pass


def draw():
    pass


def handle_events():
    pass


def pause():
    pass


def resume():
    pass
