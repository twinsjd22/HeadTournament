# 캐릭터 선택 화면: 아래 슬롯 줄에서 캐릭터를 고르면 가운데 패널에 정보를 보여 주고, 결정하면 경기로 넘어감

from pico2d import *

import game_framework
import loading_mode
import play_mode
import title_mode
from character_data import CHARACTER_TYPES

# 고를 수 있는 유형 키 (슬롯을 왼쪽부터 이 순서로 놓음)
TYPE_KEYS = list(CHARACTER_TYPES.keys())

# 지금 고르고 있는 슬롯 번호 (TYPE_KEYS 안의 위치)
selected = 0


def init():
    global selected

    # 화면에 들어올 때마다 첫 번째 슬롯부터
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
                # 게임을 끄지 않고 메인 화면으로 돌아감
                game_framework.change_mode(title_mode)
            elif event.key == SDLK_LEFT:
                # 왼쪽 끝에서는 더 가지 않음
                selected = max(selected - 1, 0)
            elif event.key == SDLK_RIGHT:
                selected = min(selected + 1, len(TYPE_KEYS) - 1)
            elif event.key == SDLK_SPACE:
                # 로딩 화면에서 경기 리소스를 미리 불러온 뒤 경기로
                # (어떤 유형을 골랐는지는 나중에 play_mode가 selected로 읽음)
                loading_mode.next_mode = play_mode
                loading_mode.tasks = play_mode.preload_tasks()
                game_framework.change_mode(loading_mode)


def pause():
    pass


def resume():
    pass
