from pico2d import load_image, clamp, draw_circle, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_SPACE
from transitions import Machine

import game_framework
from character_data import CHARACTER_TYPES

# 선수 그림 높이 150px = 키 1.75m
PIXEL_PER_METER = (150.0 / 1.75)

# 달리기 속도 (속도 능력치 5 기준)
RUN_SPEED_KMPH = 8.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)
# 속도 능력치가 5에서 1단계 낮아질 때마다 줄어드는 비율 (4는 0.9배, 2는 0.7배)
SPEED_STEP_RATE = 0.1

# 파워 능력치가 3에서 1단계 달라질 때마다 킥 세기가 바뀌는 비율 (5는 1.3배, 2는 0.85배)
POWER_STEP_RATE = 0.15

# 점프 속도와 중력 (경쾌한 점프를 위해 실제 중력의 2배)
JUMP_SPEED_MPS = 9.0
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER)
GRAVITY_MPS2 = 9.8 * 2
GRAVITY_PPS2 = (GRAVITY_MPS2 * PIXEL_PER_METER)

# 애니메이션 속도 (1초에 넘기는 그림 칸 수, 지금 속도와 같게)
IDLE_FRAMES_PER_SECOND = 17.0

# 달리기 애니메이션: 보폭 하나에 run 줄 6칸
STRIDE_LENGTH_M = 0.8
RUN_FRAMES_PER_STRIDE = 6
RUN_FRAMES_PER_SECOND = RUN_SPEED_MPS / STRIDE_LENGTH_M * RUN_FRAMES_PER_STRIDE

# 킥 애니메이션 (지금 속도와 같게)
KICK_FRAMES_PER_SECOND = 17.0


class Character:
    # 유형별 시트 이미지 (같은 유형끼리는 한 번만 불러와 공유)
    images = {}

    def __init__(self, char_type):
        # char_type: 'defender', 'trickster', 'power' 같은 유형 키
        self.char_type = char_type
        # 속도 능력치로 이 선수의 달리기 속도와 달리기 애니메이션 속도를 정함
        speed_rate = 1 - SPEED_STEP_RATE * (5 - CHARACTER_TYPES[char_type]['speed'])
        self.run_speed_pps = RUN_SPEED_PPS * speed_rate
        self.run_frames_per_second = RUN_FRAMES_PER_SECOND * speed_rate
        # 파워 능력치로 킥 세기 배율을 정함
        self.kick_power_rate = 1 + POWER_STEP_RATE * (CHARACTER_TYPES[char_type]['power'] - 3)
        self.x, self.y = 320, 160
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.vy = 0
        # 이번 킥에서 이미 공을 찼는지 (킥 한 번에 공은 한 번만 맞음)
        self.kick_hit = False
        if char_type not in Character.images:
            Character.images[char_type] = load_image(CHARACTER_TYPES[char_type]['sheet'])
        self.image = Character.images[char_type]

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
        self.vy = JUMP_SPEED_PPS

    def on_enter_KICK(self):
        self.frame = 0
        self.kick_hit = False

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
            self.frame = (self.frame + IDLE_FRAMES_PER_SECOND * game_framework.frame_time) % 4
        elif self.state == 'RUN':
            self.frame = (self.frame + self.run_frames_per_second * game_framework.frame_time) % 6
            self.x += self.dir * self.run_speed_pps * game_framework.frame_time
            self.x = clamp(50, self.x, 1280 - 50)
        elif self.state == 'JUMP':
            self.x += self.dir * self.run_speed_pps * game_framework.frame_time
            self.x = clamp(50, self.x, 1280 - 50)
            self.y += self.vy * game_framework.frame_time
            self.vy -= GRAVITY_PPS2 * game_framework.frame_time
            if self.vy > JUMP_SPEED_PPS * 0.5:
                self.frame = 1
            elif self.vy > JUMP_SPEED_PPS * 0.125:
                self.frame = 2
            elif self.vy > -JUMP_SPEED_PPS * 0.25:
                self.frame = 3
            else:
                self.frame = 4
            if self.y <= 160:
                self.y = 160
                self.land()
                if self.dir != 0:
                    self.move_start()
        elif self.state == 'KICK':
            self.frame += KICK_FRAMES_PER_SECOND * game_framework.frame_time
            if self.frame >= 5:
                self.kick_end()
                if self.dir != 0:
                    self.move_start()

    def get_head(self):
        if self.state == 'RUN':
            return self.x + self.face_dir * 16, self.y + 39, 30
        return self.x + self.face_dir * 2, self.y + 39, 30

    def get_foot(self):
        return self.x + self.face_dir * 37, self.y - 22, 20

    def draw(self):
        flip = '' if self.face_dir == 1 else 'h'
        if self.state == 'IDLE':
            self.image.clip_composite_draw(int(self.frame) * 256, 7 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'RUN':
            self.image.clip_composite_draw(int(self.frame) * 256, 6 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'JUMP':
            self.image.clip_composite_draw(int(self.frame) * 256, 5 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'KICK':
            self.image.clip_composite_draw(int(self.frame) * 256, 4 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        draw_circle(*self.get_head(), 255, 0, 0)
        if self.state == 'KICK':
            draw_circle(*self.get_foot(), 255, 0, 0)
