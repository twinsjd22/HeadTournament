# 닉네임 입력 화면: 토너먼트 기록이 랭킹에 들면 영어와 숫자로 최대 10글자 닉네임을 받아 저장함

import ctypes

from pico2d import *
from sdl2.sdlttf import TTF_SizeUTF8

import game_framework
import game_world
import play_mode
import records
import select_mode
import tournament

# 닉네임 최대 글자 수, 아무것도 안 쓰고 저장할 때의 이름
MAX_NAME_LENGTH = 10
DEFAULT_NAME = 'PLAYER'

# 닉네임 패널 (560x300) 가운데 위치, 패널 안 입력 칸 (패널 그림의 왼쪽 위 기준: 왼쪽 x, 가운데 높이)
PANEL_X, PANEL_Y = 640, 380
PANEL_LEFT, PANEL_TOP = PANEL_X - 280, PANEL_Y + 150
INPUT_LEFT, INPUT_Y = 60, 160
# 입력 칸 왼쪽 안쪽 여백, 글자 크기, 커서와 글자 사이 간격, 커서가 켜졌다 꺼지는 간격(초)
INPUT_PADDING = 24
FONT_SIZE = 36
CARET_GAP = 4
CARET_BLINK_TIME = 0.5
# 패널 아래에 덧붙이는 건너뛰기 안내 (패널 그림에는 Enter, Backspace 안내만 있음)
SKIP_TEXT = 'ESC 등록하지 않고 넘어가기'
SKIP_Y = PANEL_Y - 150 - 28
SKIP_FONT_SIZE = 22

# 기록할 이긴 경기 수 (0이면 32강 탈락, 라운드 수와 같으면 우승), 이 화면으로 오기 전에 정해 줌
wins = 0
# 입력이 끝난 뒤 할 일 (처음부터 다시 또는 메인 화면으로), 이 화면으로 오기 전에 정해 줌
# 저장했을 때와 건너뛰었을 때 모두 부름
after_input = None
# 지금까지 입력한 닉네임, 커서 깜빡임에 쓰는 지난 시간
name = ''
time = 0.0
panel = None
caret = None
font = None
skip_font = None


def init():
    global name, time, panel, caret, font, skip_font

    name = ''
    time = 0.0
    panel = load_image('resource/name_panel.png')
    caret = load_image('resource/name_caret.png')
    font = load_font('resource/BlackHanSans-Regular.ttf', FONT_SIZE)
    skip_font = load_font('resource/NanumGothic-Bold.ttf', SKIP_FONT_SIZE)


def finish():
    global panel, caret, font, skip_font

    # 닉네임 화면에서만 쓰는 이미지와 글꼴을 놓아 줌
    panel = caret = font = skip_font = None


def update():
    global time

    time += game_framework.frame_time
    # 뒤에 깔린 결과 화면 (빛줄기, 꽃가루)은 계속 움직임
    if play_mode.result_board is not None:
        play_mode.result_board.update()


def text_width(text_font, text):
    # 글꼴로 그렸을 때의 실제 글자 폭 (px)
    if not text:
        return 0
    w, h = ctypes.c_int(), ctypes.c_int()
    TTF_SizeUTF8(text_font.font, text.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
    return w.value


def draw():
    clear_canvas()
    # 뒤에는 멈춘 경기장과 결과 화면을 그대로 그리고, 그 위에 닉네임 패널
    game_world.render()
    panel.draw(PANEL_X, PANEL_Y)

    # 입력 칸 왼쪽부터 닉네임, 그 바로 뒤에 깜빡이는 커서
    x = PANEL_LEFT + INPUT_LEFT + INPUT_PADDING
    y = PANEL_TOP - INPUT_Y
    if name:
        font.draw(x, y, name, (255, 255, 255))
    if int(time / CARET_BLINK_TIME) % 2 == 0:
        caret.draw(x + text_width(font, name) + CARET_GAP, y)

    # 패널 바로 아래 가운데에 건너뛰기 안내
    skip_font.draw(PANEL_X - text_width(skip_font, SKIP_TEXT) / 2, SKIP_Y, SKIP_TEXT, (255, 255, 255))
    update_canvas()


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
    after_input()


def handle_events():
    global name

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                save()
                # 화면이 바뀌었으므로 남은 입력은 처리하지 않음
                return
            elif event.key == SDLK_ESCAPE:
                # 기록을 남기지 않고 넘어감
                after_input()
                return
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
