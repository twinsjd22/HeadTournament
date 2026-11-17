from pico2d import load_image

import game_framework
import game_world

# 이펙트 애니메이션: 4칸을 0.25초 동안 보여 줌
HIT_FRAMES_PER_SECOND = 16.0


class HitEffect:
    image = None

    def __init__(self, x, y, size=128):
        # size: 그릴 크기 (기본 128px, 파워슛처럼 센 터치는 더 크게)
        self.x, self.y = x, y
        self.size = size
        self.frame = 0
        if HitEffect.image == None:
            HitEffect.image = load_image('resource/fx_hit_sheet.png')

    def update(self):
        self.frame += HIT_FRAMES_PER_SECOND * game_framework.frame_time
        # 4칸을 다 보여 주면 world에서 사라짐
        if self.frame >= 4:
            game_world.remove_object(self)

    def draw(self):
        HitEffect.image.clip_draw(int(self.frame) * 128, 0, 128, 128, self.x, self.y, self.size, self.size)
