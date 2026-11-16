from pico2d import load_image

from character import GAUGE_MAX

# 게이지 틀의 중심 위치 (화면 아래 바닥 띠 위, 화면 끝에서 20px 안쪽)
GAUGE_Y = 40
GAUGE_LEFT_X = 20 + 300 // 2
GAUGE_RIGHT_X = 1280 - 20 - 300 // 2


class GaugeBoard:
    # 선수 한 명의 스킬 게이지를 화면 아래 바닥 위에 그림
    frame_image = None
    fill_image = None

    def __init__(self, character, side):
        # character: 게이지를 보여 줄 선수
        # side: 'left' 또는 'right' (화면 어느 쪽에 그릴지)
        self.character = character
        self.side = side
        if GaugeBoard.frame_image == None:
            GaugeBoard.frame_image = load_image('resource/ui_gauge_frame.png')
        if GaugeBoard.fill_image == None:
            GaugeBoard.fill_image = load_image('resource/ui_gauge_fill.png')

    def update(self):
        pass

    def draw(self):
        x = GAUGE_LEFT_X if self.side == 'left' else GAUGE_RIGHT_X
        GaugeBoard.frame_image.draw(x, GAUGE_Y)

        # 게이지 값만큼 채움 이미지를 잘라서 그림 (채움 이미지 폭 292px)
        width = int(292 * self.character.gauge / GAUGE_MAX)
        if width <= 0:
            return
        if self.side == 'left':
            # 왼쪽 게이지는 왼쪽 끝부터 오른쪽으로 참
            GaugeBoard.fill_image.clip_draw(0, 0, width, 22, x - 292 // 2 + width / 2, GAUGE_Y)
        else:
            # 오른쪽 게이지는 오른쪽 끝부터 왼쪽으로 참 (좌우 대칭)
            GaugeBoard.fill_image.clip_draw(292 - width, 0, width, 22, x + 292 // 2 - width / 2, GAUGE_Y)
