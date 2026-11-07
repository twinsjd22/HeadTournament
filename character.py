from pico2d import load_image


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

    def update(self):
        pass

    def draw(self):
        pass
