# 일시정지 화면: 경기 중 ESC를 누르면 멈춘 경기장 위에 메뉴를 띄움 (계속하기, 다시 시작, 메인 메뉴)

from pico2d import *

import game_framework
import play_mode

# 메뉴 (위에서부터 패널 그림의 버튼 순서와 같음)
MENUS = ('계속하기', '다시 시작', '메인 메뉴')

# 지금 고르고 있는 메뉴 번호 (MENUS 안의 위치)
selected = 0


def init():
    global selected

    # 띄울 때마다 "계속하기"부터
    selected = 0


def finish():
    pass


def update():
    pass


def draw():
    pass


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
            elif event.key == SDLK_UP:
                selected = max(selected - 1, 0)
            elif event.key == SDLK_DOWN:
                selected = min(selected + 1, len(MENUS) - 1)
            elif event.key in (SDLK_RETURN, SDLK_KP_ENTER):
                # Space는 경기 중 킥이라 실수로 누르기 쉬워서 Enter로만 실행
                run_menu()
                return


def pause():
    pass


def resume():
    pass
