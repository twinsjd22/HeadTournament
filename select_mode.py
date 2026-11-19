# 캐릭터 선택 화면: 아래 슬롯 줄에서 캐릭터를 고르면 가운데 패널에 정보를 보여 주고, 결정하면 경기로 넘어감

from pico2d import *

import game_framework
import loading_mode
import play_mode
import title_mode
from character_data import CHARACTER_TYPES

# 고를 수 있는 유형 키 (슬롯을 왼쪽부터 이 순서로 놓음)
TYPE_KEYS = list(CHARACTER_TYPES.keys())

# 정보 패널 (760x330)의 가운데 위치
PANEL_X, PANEL_Y = 640, 376
PANEL_LEFT, PANEL_TOP = PANEL_X - 380, PANEL_Y + 165
# 아래 슬롯 줄: 가운데 높이, 슬롯 사이 간격
SLOT_Y = 112
SLOT_GAP = 140
# 능력치 막대: 첫 칸의 가운데 (패널 왼쪽 위 기준), 칸 사이 간격, 속도 줄과 파워 줄의 높이
STAT_X = 447
STAT_GAP = 40
SPEED_Y, POWER_Y = 241, 283

# 지금 고르고 있는 슬롯 번호 (TYPE_KEYS 안의 위치)
selected = 0
background = None
panel = None
stat_seg = None
slot_normal = None
slot_selected = None
sheets = None
portraits = None
name_font = None
skill_font = None
desc_font = None


def panel_pos(x, y):
    # 패널 그림의 왼쪽 위 기준 위치(아래로 갈수록 y 증가)를 화면 위치로 바꿈
    return PANEL_LEFT + x, PANEL_TOP - y


def load_screen_images():
    global background, panel, stat_seg, slot_normal, slot_selected

    background = load_image('resource/select_bg.png')
    panel = load_image('resource/info_panel.png')
    stat_seg = load_image('resource/stat_seg.png')
    slot_normal = load_image('resource/slot_normal.png')
    slot_selected = load_image('resource/slot_selected.png')


def load_fonts():
    global name_font, skill_font, desc_font

    name_font = load_font('resource/BlackHanSans-Regular.ttf', 40)
    skill_font = load_font('resource/NanumGothic-Bold.ttf', 22)
    desc_font = load_font('resource/NanumGothic-Bold.ttf', 22)


def load_character(key):
    global sheets, portraits

    # 한 유형의 큰 그림용 선수 시트와 슬롯용 초상화 (TYPE_KEYS 순서대로 불러야 함)
    if sheets is None:
        sheets, portraits = [], []
    sheets.append(load_image(CHARACTER_TYPES[key]['sheet']))
    portraits.append(load_image(CHARACTER_TYPES[key]['portrait']))


def preload_tasks():
    # 로딩 화면에서 미리 할 일 목록: 화면 이미지, 글꼴, 유형마다 시트와 초상화
    tasks = [load_screen_images, load_fonts]
    for key in TYPE_KEYS:
        tasks.append(lambda key=key: load_character(key))
    return tasks


def init():
    global selected

    # 화면에 들어올 때마다 첫 번째 슬롯부터
    selected = 0
    # 로딩 화면을 거치지 않고 들어왔으면 여기서 한꺼번에 불러옴
    if background is None:
        for task in preload_tasks():
            task()


def finish():
    global background, panel, stat_seg, slot_normal, slot_selected, sheets, portraits
    global name_font, skill_font, desc_font

    # 선택 화면에서만 쓰는 이미지와 글꼴을 놓아 줌
    background = panel = stat_seg = None
    slot_normal = slot_selected = None
    sheets = portraits = None
    name_font = skill_font = desc_font = None


def update():
    pass


def draw_panel():
    # 고른 캐릭터의 정보 패널
    data = CHARACTER_TYPES[TYPE_KEYS[selected]]
    panel.draw(PANEL_X, PANEL_Y)

    # 왼쪽에 큰 선수 그림 (시트 맨 윗줄 서 있기의 첫 칸)
    sheets[selected].clip_draw(0, 7 * 256, 256, 256, *panel_pos(150, 178), 290, 290)

    # 이름, 필살기 (주황 띠 가운데), 설명
    name_font.draw(*panel_pos(344, 50), data['name'], (255, 255, 255))
    skill_text = f'필살기  {data["skill"]}'
    # 글자 폭을 어림해서 주황 띠 가운데에 오게 함 (한글은 글자 크기만큼, 띄어쓰기는 절반)
    skill_width = sum(22 if ord(c) > 127 else 11 for c in skill_text)
    skill_font.draw(*panel_pos(470 - skill_width / 2, 131), skill_text, (25, 30, 55))
    desc_font.draw(*panel_pos(344, 181), data['desc'], (200, 205, 220))

    # 능력치만큼 빈 칸 위에 주황 칸을 덮어 그림
    for i in range(data['speed']):
        stat_seg.draw(*panel_pos(STAT_X + i * STAT_GAP, SPEED_Y))
    for i in range(data['power']):
        stat_seg.draw(*panel_pos(STAT_X + i * STAT_GAP, POWER_Y))


def draw_slots():
    # 아래 슬롯 줄: 화면 가운데를 기준으로 유형 수만큼 나란히 놓음
    first_x = 640 - (len(TYPE_KEYS) - 1) * SLOT_GAP / 2
    for i in range(len(TYPE_KEYS)):
        x = first_x + i * SLOT_GAP
        portraits[i].draw(x, SLOT_Y)
        # 고른 슬롯은 주황 빛 테두리, 나머지는 흰 테두리
        if i == selected:
            slot_selected.draw(x, SLOT_Y)
        else:
            slot_normal.draw(x, SLOT_Y)


def draw():
    clear_canvas()
    background.draw(640, 360)
    draw_panel()
    draw_slots()
    update_canvas()


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
