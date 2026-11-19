from pico2d import load_image, clamp, draw_circle, draw_rectangle, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_SPACE, SDLK_z
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

# 스킬 게이지 최대값 (가득 차면 필살 스킬 사용 가능)
GAUGE_MAX = 100
# 스킬 게이지가 오르는 양
GAUGE_TOUCH = 5
GAUGE_SCORE = 30
GAUGE_CONCEDE = 15
# 공 터치로 게이지가 오른 뒤, 이 시간(초) 동안은 다시 터치해도 오르지 않음
# (두 선수 사이에 공이 끼어 연달아 맞을 때 게이지가 한꺼번에 차지 않게 함)
TOUCH_COOLDOWN = 0.5

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

# 트릭스터: 이 시간(초) 동안 개인기 동작으로 움직임
TRICK_TIME = 1.0
# 트릭스터 애니메이션 (trick 줄 5칸을 1초에 두 번 반복)
TRICK_FRAMES_PER_SECOND = 10.0
# 트릭스터 돌진 속도: 달리기 속도의 이 배율 (1초 동안 상대를 확실히 지나감)
TRICK_SPEED_RATE = 1.5

# 하드태클: 바라보는 방향으로 이 속도로 미끄러져 나가며 점점 느려짐
TACKLE_SPEED_MPS = 7.0
TACKLE_SPEED_PPS = (TACKLE_SPEED_MPS * PIXEL_PER_METER)
# 하드태클 동작 시간(초), tackle 줄 4칸을 넘어가며 보여 주고 마지막 칸에서 미끄러짐
TACKLE_TIME = 0.6
TACKLE_FRAMES_PER_SECOND = 10.0

# 넘어짐: 이 시간(초) 동안 쓰러져 있다가 일어남
FALL_TIME = 1.2
# 넘어짐 애니메이션 (fall 줄 4칸을 넘어가며 보여 주고 마지막 칸에서 누워 있음)
FALL_FRAMES_PER_SECOND = 10.0


class Character:
    # 유형별 시트 이미지 (같은 유형끼리는 한 번만 불러와 공유)
    images = {}

    def __init__(self, char_type, x, face_dir):
        # char_type: 'defender', 'trickster', 'power' 같은 유형 키
        # x, face_dir: 시작 위치와 바라보는 방향 (1은 오른쪽, -1은 왼쪽)
        self.char_type = char_type
        # 속도 능력치로 이 선수의 달리기 속도와 달리기 애니메이션 속도를 정함
        speed_rate = 1 - SPEED_STEP_RATE * (5 - CHARACTER_TYPES[char_type]['speed'])
        self.run_speed_pps = RUN_SPEED_PPS * speed_rate
        self.run_frames_per_second = RUN_FRAMES_PER_SECOND * speed_rate
        # 파워 능력치로 킥 세기 배율을 정함
        self.kick_power_rate = 1 + POWER_STEP_RATE * (CHARACTER_TYPES[char_type]['power'] - 3)
        self.x, self.y = x, 160
        self.frame = 0
        self.dir = 0
        self.face_dir = face_dir
        self.vy = 0
        # 스킬 게이지 (새 경기마다 0에서 시작)
        self.gauge = 0
        # 다음 터치 게이지까지 남은 시간
        self.touch_cooldown = 0.0
        # 파워슛 준비 상태 (필살 스킬을 쓰면 다음 킥이 파워슛)
        self.power_shot = False
        # 이번 킥에서 이미 공을 찼는지 (킥 한 번에 공은 한 번만 맞음)
        self.kick_hit = False
        if char_type not in Character.images:
            Character.images[char_type] = load_image(CHARACTER_TYPES[char_type]['sheet'])
        self.image = Character.images[char_type]

        # 현재 캐릭터는 IDLE, RUN, JUMP, KICK, POWER 상태를 갖는다.
        # POWER: 파워슛 킥 (파워형 필살 스킬을 준비한 뒤 Space)
        # TRICK: 트릭스터 (개인기형 필살 스킬, 약 1초 동안 개인기 동작으로 이동)
        # TACKLE: 하드태클 (수비형 필살 스킬, 앞으로 미끄러지며 대시)
        # FALL: 하드태클에 맞아 넘어짐 (잠시 움직이지 못함, 점프 중에는 맞지 않음)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'JUMP', 'KICK', 'POWER', 'TRICK', 'FALL', 'TACKLE'],
            transitions=[
                {'trigger': 'move_start', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'move_stop', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'jump', 'source': ['IDLE', 'RUN'], 'dest': 'JUMP'},
                {'trigger': 'land', 'source': 'JUMP', 'dest': 'IDLE'},
                {'trigger': 'kick', 'source': ['IDLE', 'RUN'], 'dest': 'KICK'},
                {'trigger': 'power_kick', 'source': ['IDLE', 'RUN'], 'dest': 'POWER'},
                {'trigger': 'trick', 'source': ['IDLE', 'RUN'], 'dest': 'TRICK'},
                {'trigger': 'trick_end', 'source': 'TRICK', 'dest': 'IDLE'},
                {'trigger': 'tackle', 'source': ['IDLE', 'RUN'], 'dest': 'TACKLE'},
                {'trigger': 'tackle_end', 'source': 'TACKLE', 'dest': 'IDLE'},
                {'trigger': 'fall', 'source': ['IDLE', 'RUN', 'KICK', 'POWER'], 'dest': 'FALL'},
                {'trigger': 'get_up', 'source': 'FALL', 'dest': 'IDLE'},
                {'trigger': 'kick_end', 'source': ['KICK', 'POWER'], 'dest': 'IDLE'},
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

    def on_enter_TRICK(self):
        self.frame = 0
        self.trick_time = TRICK_TIME
        # 돌진 방향은 시작할 때 바라보던 쪽으로 고정 (도중에 방향키를 눌러도 돌아서지 않음)
        self.trick_dir = self.face_dir

    def on_enter_TACKLE(self):
        self.frame = 0
        self.tackle_time = TACKLE_TIME
        # 태클 한 번에 공은 한 번만 쓸어 감
        self.kick_hit = False

    def on_enter_FALL(self):
        self.frame = 0
        self.fall_time = FALL_TIME

    def on_enter_POWER(self):
        self.frame = 0
        self.kick_hit = False

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_UP:
            self.jump()
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_z:
            self.use_skill()
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            # 파워슛이 준비되어 있으면 파워슛 킥, 아니면 보통 킥
            if self.power_shot:
                self.power_kick()
            else:
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
        self.touch_cooldown = max(self.touch_cooldown - game_framework.frame_time, 0)

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
        elif self.state in ('KICK', 'POWER'):
            self.frame += KICK_FRAMES_PER_SECOND * game_framework.frame_time
            if self.frame >= 5:
                self.kick_end()
                if self.dir != 0:
                    self.move_start()
        elif self.state == 'TRICK':
            # 방향키와 상관없이 바라보는 쪽으로 달리기보다 빠르게 돌진 (상대를 뚫고 지나감)
            self.frame = (self.frame + TRICK_FRAMES_PER_SECOND * game_framework.frame_time) % 5
            self.face_dir = self.trick_dir
            self.x += self.face_dir * self.run_speed_pps * TRICK_SPEED_RATE * game_framework.frame_time
            self.x = clamp(50, self.x, 1280 - 50)
            self.trick_time -= game_framework.frame_time
            if self.trick_time <= 0:
                self.trick_end()
                # 끝나면 누르고 있던 방향키 쪽으로 다시 달림
                if self.dir != 0:
                    self.face_dir = self.dir
                    self.move_start()
        elif self.state == 'TACKLE':
            # 바라보는 방향으로 미끄러지며, 남은 시간에 비례해 점점 느려짐
            self.frame = min(self.frame + TACKLE_FRAMES_PER_SECOND * game_framework.frame_time, 3)
            speed = TACKLE_SPEED_PPS * self.tackle_time / TACKLE_TIME
            self.x += self.face_dir * speed * game_framework.frame_time
            self.x = clamp(50, self.x, 1280 - 50)
            self.tackle_time -= game_framework.frame_time
            if self.tackle_time <= 0:
                self.tackle_end()
                if self.dir != 0:
                    self.move_start()
        elif self.state == 'FALL':
            # 쓰러지는 4칸을 보여 준 뒤 마지막 칸(누운 모습)에서 멈춰 있음
            self.frame = min(self.frame + FALL_FRAMES_PER_SECOND * game_framework.frame_time, 3)
            self.fall_time -= game_framework.frame_time
            if self.fall_time <= 0:
                self.get_up()
                if self.dir != 0:
                    self.move_start()

    def reset(self, x, face_dir):
        # 득점 후 처음 자리로 돌아감
        # 하던 동작(태클, 넘어짐, 트릭스터, 킥 등)도 끝내고 서 있는 상태에서 다시 시작
        self.x, self.y = x, 160
        self.vy = 0
        self.face_dir = face_dir
        self.frame = 0
        self.machine.set_state('IDLE')
        # 방향키를 누르고 있었다면 바로 달림
        if self.dir != 0:
            self.face_dir = self.dir
            self.move_start()

    def use_skill(self):
        # 게이지가 가득 찼을 때만 필살 스킬 사용, 사용하면 게이지는 0
        if self.gauge < GAUGE_MAX:
            return
        # 태클과 트릭스터는 서 있거나 달릴 때만 나가므로, 그 밖의 상태에서는 게이지를 쓰지 않음
        # (파워슛은 준비만 하는 것이라 언제든 가능)
        if self.char_type != 'power' and self.state not in ('IDLE', 'RUN'):
            return
        self.gauge = 0
        print(f'필살 스킬 사용 : {CHARACTER_TYPES[self.char_type]["skill"]}')
        if self.char_type == 'power':
            self.power_shot = True
        elif self.char_type == 'trickster':
            self.trick()
        elif self.char_type == 'defender':
            self.tackle()

    def touch_ball(self):
        # 공을 건드리면 게이지 증가 (쿨다운 중이면 오르지 않음)
        if self.touch_cooldown == 0:
            self.add_gauge(GAUGE_TOUCH)
            self.touch_cooldown = TOUCH_COOLDOWN

    def add_gauge(self, amount):
        # 게이지를 올리되 최대값을 넘지 않게 함
        self.gauge = min(self.gauge + amount, GAUGE_MAX)

    def get_head(self):
        if self.state == 'RUN':
            return self.x + self.face_dir * 16, self.y + 39, 30
        return self.x + self.face_dir * 2, self.y + 39, 30

    def get_bb(self):
        # 몸통 영역 (머리 원 아래부터 발끝까지): 왼쪽, 아래, 오른쪽, 위
        return self.x - 18, self.y - 80, self.x + 18, self.y + 10

    def get_tackle_bb(self):
        # 하드태클로 뻗은 다리 영역 (바닥 가까이, 바라보는 쪽 앞): 왼쪽, 아래, 오른쪽, 위
        if self.face_dir == 1:
            return self.x - 20, self.y - 80, self.x + 75, self.y - 30
        return self.x - 75, self.y - 80, self.x + 20, self.y - 30

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
        elif self.state == 'TACKLE':
            # 시트 4번 줄(tackle)
            self.image.clip_composite_draw(int(self.frame) * 256, 3 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'FALL':
            # 시트 5번 줄(fall)
            self.image.clip_composite_draw(int(self.frame) * 256, 2 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'TRICK':
            # 시트 6번 줄(trick)
            self.image.clip_composite_draw(int(self.frame) * 256, 1 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        elif self.state == 'POWER':
            # 시트 맨 아래 줄(power)
            self.image.clip_composite_draw(int(self.frame) * 256, 0 * 256, 256, 256, 0, flip, self.x, self.y, 160, 160)
        draw_circle(*self.get_head(), 255, 0, 0)
        draw_rectangle(*self.get_bb())
        if self.state in ('KICK', 'POWER'):
            draw_circle(*self.get_foot(), 255, 0, 0)
        if self.state == 'TACKLE':
            draw_rectangle(*self.get_tackle_bb())
