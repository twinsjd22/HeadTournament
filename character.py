from pico2d import load_image
from transitions import Machine


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

        # 현재 캐릭터는 IDLE 상태 하나만 갖는다.
        self.machine = Machine(
            model=self,
            states=['IDLE'],
            initial='IDLE',
            auto_transitions=False,
        )

    def handle_event(self, event):
        pass

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 4

    def draw(self):
        if self.state == 'IDLE':
            Character.image.clip_draw(self.frame * 256, 7 * 256, 256, 256, self.x, self.y, 160, 160)
