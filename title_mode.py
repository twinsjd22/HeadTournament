# 메인 화면: 게임 시작과 종료 메뉴

from pico2d import *

import game_framework
import loading_mode
import ranking_mode
import select_mode
import tournament

# 메뉴 글자 (위에서부터 이 순서로 버튼을 놓음)
MENUS = ('게임 시작', '랭킹', '종료')

# 첫 번째 버튼 위치와 버튼 사이 간격 (로고는 배경 그림에 들어 있음)
BUTTON_X, BUTTON_Y = 640, 270
BUTTON_GAP = 84
# 버튼 글자 크기
FONT_SIZE = 32

# 지금 고르고 있는 메뉴 번호 (MENUS 안의 위치)
selected = 0
background = None
button_normal = None
button_selected = None
font = None


def draw_center(text, x, y):
    # font.draw는 x가 글자의 왼쪽 끝이므로, 글자 폭을 어림해서 가운데에 오게 함
    # (한글은 글자 크기만큼, 띄어쓰기는 그 절반 정도 폭)
    width = sum(FONT_SIZE if ord(c) > 127 else FONT_SIZE * 0.5 for c in text)
    font.draw(x - width / 2, y, text, (255, 255, 255))


def init():
    global selected, background, button_normal, button_selected, font

    # 화면에 들어올 때마다 "게임 시작"부터
    selected = 0
    background = load_image('resource/title_screen.png')
    button_normal = load_image('resource/btn_normal.png')
    button_selected = load_image('resource/btn_selected.png')
    font = load_font('resource/BlackHanSans-Regular.ttf', FONT_SIZE)


def finish():
    global background, button_normal, button_selected, font

    # 메인 화면에서만 쓰는 이미지와 글꼴을 놓아 줌
    background = None
    button_normal = button_selected = None
    font = None


def update():
    pass


def draw():
    clear_canvas()
    background.draw(640, 360)
    # 버튼을 위에서부터 놓고, 고른 버튼만 주황색
    for i, menu in enumerate(MENUS):
        y = BUTTON_Y - i * BUTTON_GAP
        if i == selected:
            button_selected.draw(BUTTON_X, y)
        else:
            button_normal.draw(BUTTON_X, y)
        draw_center(menu, BUTTON_X, y)
    update_canvas()


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
                    # 새 토너먼트를 32강부터 시작
                    tournament.start()
                    # 로딩 화면에서 선택 화면 리소스를 미리 불러온 뒤 캐릭터 선택으로
                    loading_mode.next_mode = select_mode
                    loading_mode.tasks = select_mode.preload_tasks()
                    game_framework.change_mode(loading_mode)
                elif MENUS[selected] == '랭킹':
                    game_framework.change_mode(ranking_mode)
                else:
                    game_framework.quit()


def pause():
    pass


def resume():
    pass
