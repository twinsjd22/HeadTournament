from pico2d import load_image, load_font

import game_framework
import tournament

# 승리 / 패배 글자: 위쪽 가운데, 원래 그림의 이 배율로 그림
LOGO_X, LOGO_Y = 640, 590
LOGO_SCALE = 0.55
# 승리 글자 뒤 빛줄기: 크기와 1초에 도는 각도(라디안)
RAYS_SIZE = 700
RAYS_TURN_SPEED = 0.4
# 나타날 때 글자가 작게 시작해 커지는 시간(초)
POP_TIME = 0.25

# 결과 패널 (640x210) 가운데 위치
PANEL_X, PANEL_Y = 640, 350
PANEL_LEFT, PANEL_TOP = PANEL_X - 320, PANEL_Y + 105
# 패널 안 위치 (패널 그림의 왼쪽 위 기준): 위 띠 가운데 높이, 점수 칸 가운데 높이와 왼쪽/오른쪽 점수 가운데, 안내 높이
BAR_Y = 28
SCORE_Y = 110
SCORE_LEFT_X, SCORE_RIGHT_X = 260, 380
HINT_Y = 180

BAR_FONT_SIZE = 24
SCORE_FONT_SIZE = 52
HINT_FONT_SIZE = 20


def text_width(text, size):
    # 글자 폭 어림 (한글은 글자 크기만큼, 숫자와 영어, 띄어쓰기는 절반 남짓)
    return sum(size if ord(c) > 127 else size * 0.55 for c in text)


class ResultBoard:
    # 경기가 끝나면 멈춘 경기장 위에 승리 / 패배와 점수, 다음 안내를 보여 줌
    dim = None
    rays = None
    win_logo = None
    lose_logo = None
    win_panel = None
    lose_panel = None
    bar_font = None
    score_font = None
    hint_font = None

    def __init__(self, won, score_left, score_right):
        # won: 플레이어가 이겼는지, score_left / score_right: 플레이어 / 상대 점수
        self.won = won
        self.score_left, self.score_right = score_left, score_right
        # 나타난 뒤 지난 시간 (글자 커지기, 빛줄기 회전)
        self.time = 0.0
        if ResultBoard.dim == None:
            ResultBoard.dim = load_image('resource/result_dim_light.png')
            ResultBoard.rays = load_image('resource/result_rays.png')
            ResultBoard.win_logo = load_image('resource/result_win.png')
            ResultBoard.lose_logo = load_image('resource/result_lose.png')
            ResultBoard.win_panel = load_image('resource/result_panel_win.png')
            ResultBoard.lose_panel = load_image('resource/result_panel_lose.png')
            ResultBoard.bar_font = load_font('resource/BlackHanSans-Regular.ttf', BAR_FONT_SIZE)
            ResultBoard.score_font = load_font('resource/BlackHanSans-Regular.ttf', SCORE_FONT_SIZE)
            ResultBoard.hint_font = load_font('resource/NanumGothic-Bold.ttf', HINT_FONT_SIZE)

    def hint(self):
        # 아래 안내: 이기면 다음 라운드 (결승이면 메인으로), 지면 처음부터 다시 또는 메인으로
        if not self.won:
            return 'Space 처음부터 다시      ESC 메인으로'
        if tournament.is_final():
            return 'Space 메인으로'
        return 'Space 다음 라운드'

    def update(self):
        self.time += game_framework.frame_time

    def draw_center(self, font, size, x, y, text):
        # 패널 안 위치(왼쪽 위 기준)에 글자를 가운데 맞춰 씀
        font.draw(PANEL_LEFT + x - text_width(text, size) / 2, PANEL_TOP - y, text, (255, 255, 255))

    def draw(self):
        # 경기장을 살짝 어둡게 덮음
        ResultBoard.dim.draw(640, 360)

        # 승리 / 패배 글자 (처음에 작게 시작해 커지며 나타남), 승리면 뒤에서 빛줄기가 돎
        pop = min(self.time / POP_TIME, 1.0)
        if self.won:
            ResultBoard.rays.composite_draw(self.time * RAYS_TURN_SPEED, '', LOGO_X, LOGO_Y, RAYS_SIZE * pop, RAYS_SIZE * pop)
            logo = ResultBoard.win_logo
        else:
            logo = ResultBoard.lose_logo
        logo.draw(LOGO_X, LOGO_Y, logo.w * LOGO_SCALE * pop, logo.h * LOGO_SCALE * pop)

        # 결과 패널: 위 띠에 라운드, 가운데 칸에 점수, 아래에 안내
        panel = ResultBoard.win_panel if self.won else ResultBoard.lose_panel
        panel.draw(PANEL_X, PANEL_Y)
        round_text = f'{tournament.round_name()}  {tournament.round_index + 1} / {len(tournament.ROUNDS)} 경기'
        self.draw_center(ResultBoard.bar_font, BAR_FONT_SIZE, 320, BAR_Y, round_text)
        self.draw_center(ResultBoard.score_font, SCORE_FONT_SIZE, SCORE_LEFT_X, SCORE_Y, str(self.score_left))
        self.draw_center(ResultBoard.score_font, SCORE_FONT_SIZE, SCORE_RIGHT_X, SCORE_Y, str(self.score_right))
        self.draw_center(ResultBoard.hint_font, HINT_FONT_SIZE, 320, HINT_Y, self.hint())
