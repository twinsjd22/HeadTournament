from pico2d import load_image


class Ground:
    image = None

    def __init__(self):
        if Ground.image == None:
            Ground.image = load_image('resource/ground.png')

    def update(self):
        pass

    def draw(self):
        Ground.image.draw(640, 40)
