from pico2d import load_image, clamp, draw_circle, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_SPACE
from transitions import Machine


class Character:
    image = None

    def __init__(self):
        self.x, self.y = 320, 160
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.vy = 0
        if Character.image == None:
            Character.image = load_image('resource/sheet_defender.png')

        # 현재 캐릭터는 IDLE, RUN, JUMP, KICK 상태를 갖는다.
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'JUMP', 'KICK'],
            transitions=[
                {'trigger': 'move_start', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'move_stop', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'jump', 'source': ['IDLE', 'RUN'], 'dest': 'JUMP'},
                {'trigger': 'land', 'source': 'JUMP', 'dest': 'IDLE'},
                {'trigger': 'kick', 'source': ['IDLE', 'RUN'], 'dest': 'KICK'},
                {'trigger': 'kick_end', 'source': 'KICK', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,
        )

    def on_enter_IDLE(self):
        self.frame = 0

    def on_enter_JUMP(self):
        self.frame = 0
        self.vy = 40

    def on_enter_KICK(self):
        self.frame = 0

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_UP:
            self.jump()
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.kick()
            return

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
        elif self.state == 'JUMP':
            self.x += self.dir * 10
            self.x = clamp(50, self.x, 1280 - 50)
            self.y += self.vy
            self.vy -= 5
            if self.vy > 20:
                self.frame = 1
            elif self.vy > 5:
                self.frame = 2
            elif self.vy > -10:
                self.frame = 3
            else:
                self.frame = 4
            if self.y <= 160:
                self.y = 160
                self.land()
                if self.dir != 0:
                    self.move_start()
        elif self.state == 'KICK':
            self.frame += 1
            if self.frame == 5:
                self.kick_end()
                if self.dir != 0:
                    self.move_start()

    def get_head(self):
        if self.state == 'RUN':
            return self.x + self.face_dir * 16, self.y + 39, 30
        return self.x + self.face_dir * 2, self.y + 39, 30

    def draw(self):
        flip = '' if self.face_dir == 1 else 'h'
        if self.state == 'IDLE':
            Character.image.clip_composite_draw(self.frame * 256, 7 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'RUN':
            Character.image.clip_composite_draw(self.frame * 256, 6 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'JUMP':
            Character.image.clip_composite_draw(self.frame * 256, 5 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'KICK':
            Character.image.clip_composite_draw(self.frame * 256, 4 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        draw_circle(*self.get_head(), 255, 0, 0)
