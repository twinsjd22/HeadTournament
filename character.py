from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

        # 현재 캐릭터는 IDLE, RUN 상태를 갖는다.
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN'],
            transitions=[
                {'trigger': 'move_start', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'move_stop', 'source': 'RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,
        )

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.move_start()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.move_stop()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 4
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 6

    def draw(self):
        if self.state == 'IDLE':
            Character.image.clip_draw(self.frame * 256, 7 * 256, 256, 256, self.x, self.y, 160, 160)
        elif self.state == 'RUN':
            Character.image.clip_draw(self.frame * 256, 6 * 256, 256, 256, self.x, self.y, 160, 160)
