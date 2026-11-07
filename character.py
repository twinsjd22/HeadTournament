from pico2d import load_image


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

    def update(self):
        self.frame = (self.frame + 1) % 4

    def draw(self):
        Character.image.clip_draw(self.frame * 256, 7 * 256, 256, 256, self.x, self.y, 160, 160)
