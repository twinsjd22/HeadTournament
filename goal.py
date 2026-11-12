from pico2d import load_image, draw_rectangle


class Goal:
    image_left = None
    image_right = None

    def __init__(self, side):
        # side: 'left' 또는 'right' (어느 쪽 골대인지)
        self.side = side
        if Goal.image_left == None:
            Goal.image_left = load_image('resource/goal_left.png')
        if Goal.image_right == None:
            Goal.image_right = load_image('resource/goal_right.png')

    def update(self):
        pass

    def get_bb(self):
        # 크로스바(골대 맨 위 가로대) 영역: 왼쪽, 아래, 오른쪽, 위
        if self.side == 'left':
            return 3, 288, 78, 300
        else:
            return 1280 - 78, 288, 1280 - 3, 300

    def is_ball_in(self, x, y, r):
        # 공 전체가 골라인(앞 기둥)을 넘어가고, 크로스바보다 아래에 있으면 골
        if self.side == 'left':
            return x + r < 75 and y < 288
        else:
            return x - r > 1280 - 75 and y < 288

    def draw(self):
        # 이미지 바깥쪽 끝을 화면 끝에, 아래쪽 끝을 바닥 윗면(y=80)에 맞춤
        if self.side == 'left':
            Goal.image_left.draw(170 // 2, 80 + 230 // 2)
        else:
            Goal.image_right.draw(1280 - 170 // 2, 80 + 230 // 2)
        draw_rectangle(*self.get_bb())
