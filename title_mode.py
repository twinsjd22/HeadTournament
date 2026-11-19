# 메인 화면: 게임 시작과 종료 메뉴

from pico2d import *

import game_framework
import play_mode

# 메뉴 글자 (위에서부터 이 순서로 버튼을 놓음)
MENUS = ('게임 시작', '종료')

# 지금 고르고 있는 메뉴 번호 (MENUS 안의 위치)
selected = 0


def init():
    global selected

    # 화면에 들어올 때마다 "게임 시작"부터
    selected = 0


def finish():
    pass


def update():
    pass


def draw():
    pass


def handle_events():
    global selected

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_UP:
                # 맨 위에서는 더 올라가지 않음
                selected = max(selected - 1, 0)
            elif event.key == SDLK_DOWN:
                selected = min(selected + 1, len(MENUS) - 1)
            elif event.key in (SDLK_SPACE, SDLK_RETURN):
                if MENUS[selected] == '게임 시작':
                    # 지금은 바로 경기로 (로딩, 선택 화면이 생기면 그쪽으로 바꿈)
                    game_framework.change_mode(play_mode)
                else:
                    game_framework.quit()


def pause():
    pass


def resume():
    pass
