from pico2d import *
import pico2d.pico2d as pico2d_core

import game_framework
import play_mode

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
SDL_SetWindowFullscreen(pico2d_core.window, SDL_WINDOW_FULLSCREEN_DESKTOP)
SDL_RenderSetLogicalSize(pico2d_core.renderer, SCREEN_WIDTH, SCREEN_HEIGHT)
game_framework.run(play_mode)
close_canvas()
