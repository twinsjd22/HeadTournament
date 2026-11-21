from pico2d import load_image, load_font

import game_framework

# 트로피: 화면 가운데 아래쪽, 원래 그림의 이 배율로 그림
TROPHY_X, TROPHY_Y = 640, 232
TROPHY_SCALE = 0.77
# 트로피 뒤 빛줄기: 화면을 가득 채우는 크기와 1초에 도는 각도(라디안)
RAYS_SIZE = 1500
RAYS_TURN_SPEED = 0.25
# 크게 그리면 빛줄기가 너무 진해서 반투명하게 (0이면 투명, 1이면 원래대로)
RAYS_OPACITY = 0.45
# "우승!" 글자: 위쪽 가운데
LOGO_X, LOGO_Y = 640, 648
LOGO_SCALE = 0.52
# 나타날 때 작게 시작해 커지는 시간(초)
POP_TIME = 0.35
# 아래 안내 글자
HINT_Y = 35
HINT_FONT_SIZE = 22
HINT_TEXT = 'Space 메인으로'


class ChampionBoard:
    # 결승에서 이기면 멈춘 경기장 위에 빛줄기, 트로피, 우승 글자를 보여 줌
    dim = None
    rays = None
    trophy = None
    logo = None
    font = None

    def __init__(self):
        # 나타난 뒤 지난 시간 (커지기, 빛줄기 회전)
        self.time = 0.0
        if ChampionBoard.dim == None:
            ChampionBoard.dim = load_image('resource/result_dim_light.png')
            ChampionBoard.rays = load_image('resource/result_rays.png')
            ChampionBoard.rays.opacify(RAYS_OPACITY)
            ChampionBoard.trophy = load_image('resource/trophy.png')
            ChampionBoard.logo = load_image('resource/result_champion.png')
            ChampionBoard.font = load_font('resource/NanumGothic-Bold.ttf', HINT_FONT_SIZE)

    def update(self):
        self.time += game_framework.frame_time

    def draw(self):
        # 경기장을 살짝 어둡게 덮고, 트로피 뒤에서 빛줄기가 크게 돎
        ChampionBoard.dim.draw(640, 360)
        pop = min(self.time / POP_TIME, 1.0)
        ChampionBoard.rays.composite_draw(self.time * RAYS_TURN_SPEED, '', TROPHY_X, TROPHY_Y,
                                          RAYS_SIZE * pop, RAYS_SIZE * pop)

        # 트로피와 우승 글자 (작게 시작해 커지며 나타남)
        trophy, logo = ChampionBoard.trophy, ChampionBoard.logo
        trophy.draw(TROPHY_X, TROPHY_Y, trophy.w * TROPHY_SCALE * pop, trophy.h * TROPHY_SCALE * pop)
        logo.draw(LOGO_X, LOGO_Y, logo.w * LOGO_SCALE * pop, logo.h * LOGO_SCALE * pop)

        # 아래 안내 (한글은 글자 크기만큼, 나머지는 절반 남짓으로 폭을 어림해 가운데 맞춤)
        width = sum(HINT_FONT_SIZE if ord(c) > 127 else HINT_FONT_SIZE * 0.55 for c in HINT_TEXT)
        ChampionBoard.font.draw(640 - width / 2, HINT_Y, HINT_TEXT, (255, 255, 255))
