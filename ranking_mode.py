# 랭킹 화면: 저장된 토너먼트 기록 상위 10개를 표로 보여 줌 (메인 메뉴에서 들어오고 ESC로 돌아감)

import ctypes

from pico2d import *
from sdl2.sdlttf import TTF_SizeUTF8

import game_framework
import records
from character_data import CHARACTER_TYPES

# 랭킹 글자 (위쪽 가운데, 원래 그림의 이 배율)
TITLE_X, TITLE_Y = 640, 630
TITLE_SCALE = 0.55
# 표 패널 (1000x520) 가운데 위치
PANEL_X, PANEL_Y = 640, 300
PANEL_LEFT, PANEL_TOP = PANEL_X - 500, PANEL_Y + 260
# 표 줄: 첫 줄 가운데 높이와 줄 간격 (패널 그림의 왼쪽 위 기준, 아래로 갈수록 커짐)
FIRST_ROW_Y = 82
ROW_GAP = 44
# 칸마다 글자 가운데 x (패널 그림의 세로 칸선 130, 330, 490, 630, 770 사이)
RANK_X, NAME_X, CHARACTER_X, RESULT_X, GOALS_X, DATE_X = 75, 230, 410, 560, 700, 875
# 글자 크기와 색 (득실은 +면 초록, -면 빨강)
FONT_SIZE = 22
WHITE = (255, 255, 255)
PLUS_COLOR = (110, 225, 120)
MINUS_COLOR = (245, 105, 105)
# 아래 안내
HINT_TEXT = 'ESC 메인으로'
HINT_Y = 20
EMPTY_TEXT = '아직 기록이 없습니다'

background = None
dim = None
title = None
panel = None
row_highlight = None
medals = None
font = None
# 화면에 보여 줄 기록 목록 (들어올 때 파일에서 읽음)
ranking = []


def init():
    global background, dim, title, panel, row_highlight, medals, font, ranking

    background = load_image('resource/background.png')
    dim = load_image('resource/result_dim_light.png')
    title = load_image('resource/rank_title.png')
    panel = load_image('resource/rank_panel.png')
    row_highlight = load_image('resource/rank_row_hl.png')
    medals = [load_image(f'resource/medal_{color}.png') for color in ('gold', 'silver', 'bronze')]
    font = load_font('resource/NanumGothic-Bold.ttf', FONT_SIZE)
    ranking = records.load()


def finish():
    global background, dim, title, panel, row_highlight, medals, font

    # 랭킹 화면에서만 쓰는 이미지와 글꼴을 놓아 줌
    background = dim = title = panel = row_highlight = medals = font = None


def update():
    pass


def text_width(text):
    # 글꼴로 그렸을 때의 실제 글자 폭 (px)
    w, h = ctypes.c_int(), ctypes.c_int()
    TTF_SizeUTF8(font.font, text.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
    return w.value


def draw_center(x, y, text, color=WHITE):
    # 패널 그림 안 위치(왼쪽 위 기준)에 글자를 가운데 맞춰 씀
    font.draw(PANEL_LEFT + x - text_width(text) / 2, PANEL_TOP - y, text, color)


def draw_row(index, record):
    # 표의 한 줄: 순위 (1~3위는 메달), 이름, 캐릭터, 성적, 득실, 날짜
    y = FIRST_ROW_Y + index * ROW_GAP
    # 이번에 게임을 켜고 방금 저장한 기록이면 줄 전체를 강조
    if index == records.last_index:
        row_highlight.draw(PANEL_X, PANEL_TOP - y)
    if index < len(medals):
        medals[index].draw(PANEL_LEFT + RANK_X, PANEL_TOP - y, 36, 36)
    else:
        draw_center(RANK_X, y, str(index + 1))
    draw_center(NAME_X, y, record['name'])
    character = CHARACTER_TYPES.get(record['char_type'])
    draw_center(CHARACTER_X, y, character['name'] if character else '-')
    draw_center(RESULT_X, y, records.result_text(record))
    goals = record['goals_for'] - record['goals_against']
    goals_color = PLUS_COLOR if goals > 0 else MINUS_COLOR if goals < 0 else WHITE
    draw_center(GOALS_X, y, f'{goals:+d}' if goals != 0 else '0', goals_color)
    draw_center(DATE_X, y, record['date'])


def draw():
    clear_canvas()
    # 경기장 배경을 살짝 어둡게 깔고, 위에 랭킹 글자, 가운데 표
    background.draw(640, 360)
    dim.draw(640, 360)
    title.draw(TITLE_X, TITLE_Y, title.w * TITLE_SCALE, title.h * TITLE_SCALE)
    panel.draw(PANEL_X, PANEL_Y)
    for index, record in enumerate(ranking):
        draw_row(index, record)
    if not ranking:
        draw_center(500, FIRST_ROW_Y + ROW_GAP * 4.5, EMPTY_TEXT)
    font.draw(640 - text_width(HINT_TEXT) / 2, HINT_Y, HINT_TEXT, WHITE)
    update_canvas()


def handle_events():
    pass


def pause():
    pass


def resume():
    pass
