# 일시정지 화면: 경기 중 ESC를 누르면 멈춘 경기장 위에 메뉴를 띄움 (계속하기, 다시 시작, 메인 메뉴)

from pico2d import *

import game_framework
import game_world
import play_mode
import sound

# 메뉴 (위에서부터 패널 그림의 버튼 순서와 같음)
MENUS = ('계속하기', '다시 시작', '메인 메뉴')

# 일시정지 글자 (위쪽 가운데, 원래 그림의 이 배율)
TITLE_X, TITLE_Y = 640, 600
TITLE_SCALE = 0.55
# 메뉴 패널 (480x340) 가운데 위치, 패널 안 첫 버튼 가운데 높이와 버튼 간격 (패널 그림의 왼쪽 위 기준)
PANEL_X, PANEL_Y = 640, 320
PANEL_TOP = PANEL_Y + 170
FIRST_BUTTON_Y = 62
BUTTON_GAP = 86

# 지금 고르고 있는 메뉴 번호 (MENUS 안의 위치)
selected = 0
dim = None
title = None
panel = None
cursor = None


def init():
    global selected, dim, title, panel, cursor

    # 띄울 때마다 "계속하기"부터
    selected = 0
    dim = load_image('resource/result_dim_light.png')
    title = load_image('resource/pause_title.png')
    panel = load_image('resource/pause_panel.png')
    cursor = load_image('resource/pause_cursor.png')


def finish():
    global dim, title, panel, cursor

    # 일시정지 화면에서만 쓰는 이미지를 놓아 줌
    dim = title = panel = cursor = None


def update():
    pass


def draw():
    clear_canvas()
    # 뒤에는 멈춘 경기장(배경, 선수, 공, 골대)만 그리고 점수판 같은 UI 레이어는 빼서 일시정지 글자와 겹치지 않게 함
    for layer in game_world.world[:2]:
        for o in layer:
            o.draw()
    # 어둡게 덮은 뒤 일시정지 글자와 메뉴 패널
    dim.draw(640, 360)
    title.draw(TITLE_X, TITLE_Y, title.w * TITLE_SCALE, title.h * TITLE_SCALE)
    panel.draw(PANEL_X, PANEL_Y)
    # 고른 버튼 위에 주황 테두리
    cursor.draw(PANEL_X, PANEL_TOP - (FIRST_BUTTON_Y + selected * BUTTON_GAP))
    update_canvas()


def run_menu():
    # 고른 메뉴 실행: 일시정지 화면을 내린 뒤 (pop) 경기로 돌아가거나 다른 화면으로
    menu = MENUS[selected]
    game_framework.pop_mode()
    if menu == '다시 시작':
        # 토너먼트를 같은 캐릭터로 32강부터 다시 (그만둔 토너먼트라 기록하지 않음)
        play_mode.restart_tournament()
    elif menu == '메인 메뉴':
        play_mode.go_to_title()


def handle_events():
    global selected

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # 바로 경기로 돌아감
                game_framework.pop_mode()
                return
            elif event.key in (SDLK_UP, SDLK_DOWN):
                # 맨 위, 맨 아래에서는 더 움직이지 않음 (실제로 메뉴가 바뀔 때만 소리)
                before = selected
                if event.key == SDLK_UP:
                    selected = max(selected - 1, 0)
                else:
                    selected = min(selected + 1, len(MENUS) - 1)
                if selected != before:
                    sound.play('select')
            elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                # Space는 경기 중 킥이라 실수로 누르기 쉬워서 Enter로만 실행 (고르면 결정 소리)
                sound.play('select')
                run_menu()
                return


def pause():
    pass


def resume():
    pass
