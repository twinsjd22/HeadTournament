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
        pass
