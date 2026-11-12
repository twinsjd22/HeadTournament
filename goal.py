from pico2d import load_image


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

    def draw(self):
        # 이미지 바깥쪽 끝을 화면 끝에, 아래쪽 끝을 바닥 윗면(y=80)에 맞춤
        if self.side == 'left':
            Goal.image_left.draw(170 // 2, 80 + 230 // 2)
        else:
            Goal.image_right.draw(1280 - 170 // 2, 80 + 230 // 2)
