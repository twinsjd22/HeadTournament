from pico2d import load_image, clamp, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

        # 현재 캐릭터는 IDLE, RUN, JUMP 상태를 갖는다.
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'JUMP'],
            transitions=[
                {'trigger': 'move_start', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'move_stop', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'jump', 'source': ['IDLE', 'RUN'], 'dest': 'JUMP'},
                {'trigger': 'land', 'source': 'JUMP', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,
        )

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key == SDLK_RIGHT:
                self.dir += 1
            elif event.key == SDLK_LEFT:
                self.dir -= 1
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key == SDLK_RIGHT:
                self.dir -= 1
            elif event.key == SDLK_LEFT:
                self.dir += 1
        else:
            return

        if self.dir == 0:
            self.move_stop()
        else:
            self.face_dir = self.dir
            self.move_start()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 4
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 6
            self.x += self.dir * 10
            self.x = clamp(50, self.x, 1280 - 50)

    def draw(self):
        flip = '' if self.face_dir == 1 else 'h'
        if self.state == 'IDLE':
            Character.image.clip_composite_draw(self.frame * 256, 7 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'RUN':
            Character.image.clip_composite_draw(self.frame * 256, 6 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
