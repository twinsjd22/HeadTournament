# 닉네임 입력 화면: 토너먼트 기록이 랭킹에 들면 영어와 숫자로 최대 10글자 닉네임을 받아 저장함

from pico2d import *

import game_framework
import records
import select_mode
import tournament

# 닉네임 최대 글자 수, 아무것도 안 쓰고 저장할 때의 이름
MAX_NAME_LENGTH = 10
DEFAULT_NAME = 'PLAYER'

# 기록할 이긴 경기 수 (0이면 32강 탈락, 라운드 수와 같으면 우승), 이 화면으로 오기 전에 정해 줌
wins = 0
# 저장한 뒤 할 일 (처음부터 다시 또는 메인 화면으로), 이 화면으로 오기 전에 정해 줌
after_save = None
# 지금까지 입력한 닉네임
name = ''


def init():
    global name

    name = ''


def finish():
    pass


def update():
    pass


def draw():
    pass


def key_to_char(key):
    # 영어 키는 대문자로, 숫자 키는 그대로 (그 밖의 키는 None)
    if SDLK_a <= key <= SDLK_z:
        return chr(key).upper()
    if SDLK_0 <= key <= SDLK_9:
        return chr(key)
    return None


def save():
    # 닉네임과 이번 토너먼트 기록을 저장하고, 정해 둔 다음 할 일로
    character_type = select_mode.TYPE_KEYS[select_mode.selected]
    records.add(name or DEFAULT_NAME, character_type, wins, tournament.goals_for, tournament.goals_against)
    after_save()


def handle_events():
    global name

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                save()
            elif event.key == SDLK_BACKSPACE:
                # 마지막 한 글자를 지움
                name = name[:-1]
            else:
                char = key_to_char(event.key)
                if char is not None and len(name) < MAX_NAME_LENGTH:
                    name += char


def pause():
    pass


def resume():
    pass
