from pico2d import load_image


class HitEffect:
    image = None

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.frame = 0
        if HitEffect.image == None:
            HitEffect.image = load_image('resource/fx_hit_sheet.png')

    def update(self):
        pass

    def draw(self):
        pass
