# 로딩 화면: 다음 화면에 쓸 리소스를 미리 불러오며 로딩 바를 채운 뒤 다음 화면으로 넘어감

from pico2d import *

import game_framework

# 로딩 화면을 보여 주는 최소 시간(초): 실제 로딩이 금방 끝나도 바가 차오르는 것이 보이게 함
LOADING_TIME = 1.5
# 로딩 바 틀의 가운데 위치와 채움 이미지 크기 (틀 안쪽에 8px 여백)
BAR_X, BAR_Y = 640, 222
FILL_WIDTH, FILL_HEIGHT = 784, 40
# "게임 준비 중..." 글자 높이와 크기
TEXT_Y = 137
FONT_SIZE = 28

# 로딩이 끝나면 넘어갈 모드 (로딩 화면으로 바꾸기 전에 정해 줌)
next_mode = None
# 로딩 화면에 들어온 뒤 지난 시간, 0~1로 나타낸 진행률
elapsed = 0.0
progress = 0.0
background = None
bar_frame = None
bar_fill = None
ball = None
font = None


def init():
    global elapsed, progress, background, bar_frame, bar_fill, ball, font

    elapsed = 0.0
    progress = 0.0
    background = load_image('resource/loading_screen.png')
    bar_frame = load_image('resource/loading_bar_frame.png')
    bar_fill = load_image('resource/loading_bar_fill.png')
    ball = load_image('resource/ball.png')
    font = load_font('resource/NanumGothic-Bold.ttf', FONT_SIZE)


def finish():
    global background, bar_frame, bar_fill, ball, font

    # 로딩 화면에서만 쓰는 이미지와 글꼴을 놓아 줌
    background = bar_frame = bar_fill = ball = None
    font = None


def update():
    global elapsed, progress

    # 지금은 시간에 따라 바를 채움 (리소스 불러오기는 다음 단계에서)
    elapsed += game_framework.frame_time
    progress = min(elapsed / LOADING_TIME, 1.0)
    if progress >= 1.0:
        game_framework.change_mode(next_mode)


def draw():
    clear_canvas()
    background.draw(640, 360)
    bar_frame.draw(BAR_X, BAR_Y)

    # 진행률만큼 채움 이미지를 왼쪽부터 잘라서 그림
    fill_left = BAR_X - FILL_WIDTH // 2
    width = int(FILL_WIDTH * progress)
    if width > 0:
        bar_fill.clip_draw(0, 0, width, FILL_HEIGHT, fill_left + width / 2, BAR_Y)
    # 채워진 끝에 공을 그림
    ball.draw(fill_left + width, BAR_Y)

    # 글자 폭을 어림해서 가운데에 오게 함 (한글은 글자 크기만큼, 나머지는 절반 정도)
    text = f'게임 준비 중... {int(progress * 100)}%'
    text_width = sum(FONT_SIZE if ord(c) > 127 else FONT_SIZE * 0.5 for c in text)
    font.draw(640 - text_width / 2, TEXT_Y, text, (255, 255, 255))
    update_canvas()


def handle_events():
    # 로딩 중에는 종료만 받음
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()


def pause():
    pass


def resume():
    pass
