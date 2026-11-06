from pico2d import load_image


class Background:
    image = None

    def __init__(self):
        if Background.image == None:
            Background.image = load_image('resource/background.png')

    def update(self):
        pass

    def draw(self):
        Background.image.draw(640, 360)
