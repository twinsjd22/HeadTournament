import math
from collections import deque
from types import SimpleNamespace

import py_trees

import common
import debug_view
import game_framework

from ball import GRAVITY_PPS2
from character import JUMP_SPEED_PPS, GRAVITY_PPS2 as CHARACTER_GRAVITY_PPS2
from character import GAUGE_MAX

# 공과 가로 거리가 이보다 멀면 공 쪽으로 움직이기 시작
FOLLOW_START_DISTANCE = 30
# 공과 가로 거리가 이보다 가까우면 멈춤 (시작 거리보다 짧게 두어 멈췄다 움직였다 떨리지 않게 함)
FOLLOW_STOP_DISTANCE = 10

# 헤딩 점프: 공이 가로로 이만큼 가깝고, 머리 위 이 높이 사이에서 내려오고 있으면 점프
JUMP_DISTANCE = 60
JUMP_MIN_HEIGHT = 230
JUMP_MAX_HEIGHT = 400

# 킥: 공이 바라보는 쪽 발 앞 이 거리 사이에 있고 (발이 닿는 거리), 이 높이보다 낮으면 킥
KICK_MIN_DISTANCE = 30
KICK_MAX_DISTANCE = 70
KICK_MAX_HEIGHT = 170

# 공이 이 높이보다 낮으면 공 오른쪽(자기 골대 쪽)에 서서 왼쪽으로 공격함
BALL_LOW_HEIGHT = 170
# 공 오른쪽에 설 때 공과의 가로 거리
BEHIND_DISTANCE = 50
# 공이 오른쪽 앞(자기 골대 쪽)에 이 거리 안으로 낮게 있으면 점프해서 넘어감
JUMP_OVER_DISTANCE = 90
# 높은 공은 공보다 이만큼 오른쪽에 서서, 공이 머리 왼쪽에 맞아 플레이어 쪽으로 튕기게 함
HEADING_OFFSET = 20
# 수비 (골대 지키기): 공이 이 속도보다 빠르게 자기 골대 쪽(오른쪽)으로 오거나,
# 공이 자기 골대에서 이 거리 안인데 AI보다 골대 쪽에 있으면 위험으로 봄
DANGER_BALL_SPEED_PPS = 2.5 * (150.0 / 1.75)
DANGER_DISTANCE = 480
# 지킬 때는 공보다 이만큼 골대 쪽에 서되, 이 x보다 골대 안쪽으로는 들어가지 않음
DEFEND_GAP = 70
DEFEND_MAX_X = 1170
# 필살 슛 (파워형, 감아차기형, 무회전형): AI가 이 가로 위치 사이에서 공이 발 앞에 있을 때만 준비함
# (플레이어 골대가 왼쪽 끝이라 x가 곧 골대까지의 거리, 테스트에서 각 슛이 잘 들어간 범위)
SHOT_SKILL_RANGES = {'power': (0, 900), 'curve': (580, 1030), 'knuckle': (300, 1050)}
# 하드태클 (수비형): 플레이어가 공을 갖고 (공에서 이 거리 안, 공이 낮음) 태클이 닿는 거리 앞에 있을 때
# (태클은 0.6초 동안 약 180px 미끄러지고 다리가 앞으로 75px 뻗음)
PLAYER_ON_BALL_DISTANCE = 100
TACKLE_MIN_REACH = 60
TACKLE_MAX_REACH = 240
# 트릭스터 (개인기형): 공이 발 앞에 있고 플레이어가 이 거리 안에서 앞을 막고 있을 때 (트릭은 1초 동안 약 300px 돌진)
TRICK_BALL_MIN, TRICK_BALL_MAX = 20, 120
TRICK_BLOCK_MIN, TRICK_BLOCK_MAX = 60, 300
# 점프로 슛 막기: 서 있을 때 머리 중심 높이, 머리와 공이 닿는 거리 (머리 반지름 30 + 공 반지름 32)
HEAD_CENTER_Y = 199
HEAD_HIT_DISTANCE = 62
# 철벽 방어 (골키퍼형): 공이 이 속도보다 빠르게 자기 골대 쪽으로 날아오며, 이 거리 안에 이 높이보다 낮게 오면 사용
GUARD_BALL_SPEED_PPS = 3.0 * (150.0 / 1.75)
GUARD_DISTANCE = 140
GUARD_MAX_HEIGHT = 300
# 오버헤드킥 (공중형): 공이 머리 위 뒤쪽(자기 골대 쪽)에서 이 높이 사이로 떨어지면 점프하고,
# 점프 중 공이 차는 발에서 이 거리 안에 들어오면 사용
OVERHEAD_JUMP_DISTANCE = 90
OVERHEAD_MIN_HEIGHT = 300
OVERHEAD_MAX_HEIGHT = 480
OVERHEAD_USE_DISTANCE = 70
# 오버헤드킥을 노릴 때는 공이 떨어질 자리보다 이만큼 왼쪽에 서서, 공이 머리 위 뒤쪽(차는 발 쪽)으로 오게 함
OVERHEAD_STAND_OFFSET = 40
# 거대화 (거인형): 높은 공이 이 거리 안에서 이 높이 사이로 떨어지고 있으면 커져서 공중볼을 따냄
GIANT_DISTANCE = 220
GIANT_MIN_HEIGHT = 230
GIANT_MAX_HEIGHT = 520

# 서 있는 선수의 머리 높이 (높은 공이 이 높이까지 떨어질 자리를 예측함)
HEAD_HEIGHT = 230


def predict_landing_x(ball):
    # 공이 머리 높이까지 떨어졌을 때의 가로 위치 (벽에 튕기는 것은 무시)
    height = ball.y - HEAD_HEIGHT
    if height <= 0:
        return ball.x
    time = (ball.vy + math.sqrt(ball.vy * ball.vy + 2 * GRAVITY_PPS2 * height)) / GRAVITY_PPS2
    return min(max(ball.x + ball.vx * time, 32), 1280 - 32)


class SenseBall(py_trees.behaviour.Behaviour):
    # Action "Sense Ball": 반응 지연만큼 전의 공(AI가 본 공)을 블랙보드 ball 에 기록 (감지)

    def __init__(self, name, ai):
        super().__init__(name)
        # 이 노드가 쓰는 AI (공 기록을 갖고 있음)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.WRITE)

    def update(self):
        self.blackboard.ball = self.ai.seen_ball()
        return py_trees.common.Status.SUCCESS


class SetTargetLocation(py_trees.behaviour.Behaviour):
    # Action "Set Target Location": 감지한 공을 보고 AI가 서야 할 가로 위치를 블랙보드 target 에 기록
    # 공이 낮으면 공 오른쪽에 서서 플레이어 골대 쪽으로 밀고,
    # 높으면 공이 떨어질 자리보다 약간 오른쪽에 미리 서서 헤딩이 플레이어 쪽으로 가게 함

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)
        self.blackboard.register_key(key='target', access=py_trees.common.Access.WRITE)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        if ball.y < BALL_LOW_HEIGHT:
            target_x = ball.x + BEHIND_DISTANCE
        else:
            # 공중형이 오버헤드킥을 노릴 때는 공이 차는 발 쪽(뒤쪽)으로 떨어지게 왼쪽에 섬
            if character.char_type == 'aerial' and character.gauge >= GAUGE_MAX:
                offset = -OVERHEAD_STAND_OFFSET
            else:
                offset = HEADING_OFFSET
            target_x = predict_landing_x(ball) + offset
        self.blackboard.target = target_x
        return py_trees.common.Status.SUCCESS


class MoveTo(py_trees.behaviour.Behaviour):
    # Action "Move To": 블랙보드 target (서야 할 가로 위치) 쪽으로 이동
    # 가는 중이면 RUNNING, 도착해서 멈추면 SUCCESS (출발 거리와 멈춤 거리를 다르게 두어 멈췄다 움직였다 떨리지 않게 함)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='target', access=py_trees.common.Access.READ)

    def update(self):
        character = self.ai.character
        target_dx = self.blackboard.target - character.x
        if character.dir == 0:
            if abs(target_dx) <= FOLLOW_START_DISTANCE:
                # 충분히 가까우면 서 있음
                return py_trees.common.Status.SUCCESS
            self.ai.move(1 if target_dx > 0 else -1)
            return py_trees.common.Status.RUNNING
        if abs(target_dx) < FOLLOW_STOP_DISTANCE:
            # 도착: 멈추고 플레이어 골대 쪽을 바라봄
            self.ai.move(0)
            character.face_dir = -1
            return py_trees.common.Status.SUCCESS
        if target_dx * character.dir < 0:
            # 목표가 반대쪽으로 넘어가면 방향을 바꿈
            self.ai.move(-character.dir)
        return py_trees.common.Status.RUNNING


class IsBallAtFoot(py_trees.behaviour.Behaviour):
    # Condition "Is Ball At Foot": 공이 발 앞(발이 닿는 거리)에 낮게 있고, 플레이어 골대 쪽(왼쪽)을 보고 있는가?
    # (자기 골대 쪽으로 차지 않도록 왼쪽을 볼 때만)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        front = (ball.x - character.x) * character.face_dir
        if character.face_dir == -1 and KICK_MIN_DISTANCE < front < KICK_MAX_DISTANCE and ball.y < KICK_MAX_HEIGHT:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Kick(py_trees.behaviour.Behaviour):
    # Action "Kick": 킥 (파워슛이나 필살 킥이 준비되어 있으면 그 동작으로 참, 키보드의 Space와 같음)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai

    def update(self):
        character = self.ai.character
        if character.power_shot:
            character.power_kick()
        elif character.skill_kick:
            character.skill_kick_start()
        else:
            character.kick()
        return py_trees.common.Status.SUCCESS


class IsGoalInDanger(py_trees.behaviour.Behaviour):
    # Condition "Is Goal In Danger": 자기 골대(오른쪽)가 위험한가?
    # 공이 자기 골대 쪽으로 빠르게 오거나, 골대 가까이에서 공이 AI보다 골대 쪽에 있을 때

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        coming = ball.vx > DANGER_BALL_SPEED_PPS and ball.x < character.x + 40
        behind = 1280 - ball.x < DANGER_DISTANCE and ball.x > character.x
        if coming or behind:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class SetDefendLocation(py_trees.behaviour.Behaviour):
    # Action "Set Defend Location": 공과 자기 골대 사이 (공보다 골대 쪽)를 서야 할 자리로 블랙보드 target 에 기록

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)
        self.blackboard.register_key(key='target', access=py_trees.common.Access.WRITE)

    def update(self):
        ball = self.blackboard.ball
        self.blackboard.target = min(ball.x + DEFEND_GAP, DEFEND_MAX_X)
        return py_trees.common.Status.SUCCESS


class IsShotOverHead(py_trees.behaviour.Behaviour):
    # Condition "Is Shot Over Head": 자기 골대 쪽으로 날아오는 슛이, 서 있으면 머리 위로 넘어가지만
    # 지금 점프하면 머리에 맞는가? (공이 AI 자리에 올 때의 높이와 그때 점프한 머리 높이를 미리 계산)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        dx = character.x - ball.x
        if ball.vx <= DANGER_BALL_SPEED_PPS or dx <= 0:
            return py_trees.common.Status.FAILURE
        # 공이 AI 자리에 오는 시간과 그때의 공 높이
        time = dx / ball.vx
        ball_y = ball.y + ball.vy * time - 0.5 * GRAVITY_PPS2 * time * time
        # 서 있어도 머리에 맞으면 점프할 필요 없음
        if abs(ball_y - HEAD_CENTER_Y) < HEAD_HIT_DISTANCE:
            return py_trees.common.Status.FAILURE
        # 지금 점프하면 그때 머리가 있을 높이 (아직 땅에 있을 때만 계산)
        head_y = HEAD_CENTER_Y + JUMP_SPEED_PPS * time - 0.5 * CHARACTER_GRAVITY_PPS2 * time * time
        if head_y > HEAD_CENTER_Y and abs(ball_y - head_y) < HEAD_HIT_DISTANCE:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsGaugeFull(py_trees.behaviour.Behaviour):
    # Condition "Is Gauge Full": 스킬 게이지가 가득 찼는가?

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai

    def update(self):
        if self.ai.character.gauge >= GAUGE_MAX:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsInShotRange(py_trees.behaviour.Behaviour):
    # Condition "Is In Shot Range": 이 유형의 필살 슛이 잘 들어가는 거리에 있는가?

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.min_x, self.max_x = SHOT_SKILL_RANGES[ai.character.char_type]

    def update(self):
        if self.min_x <= self.ai.character.x <= self.max_x:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsPlayerOnBall(py_trees.behaviour.Behaviour):
    # Condition "Is Player On Ball": 플레이어가 공을 갖고 태클이 닿는 거리 앞에 있는가? (하드태클할 때)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character, player = self.ai.character, common.player
        player_front = (player.x - character.x) * character.face_dir
        has_ball = abs(player.x - ball.x) < PLAYER_ON_BALL_DISTANCE and ball.y < BALL_LOW_HEIGHT
        if character.face_dir == -1 and has_ball and TACKLE_MIN_REACH < player_front < TACKLE_MAX_REACH:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsPlayerBlocking(py_trees.behaviour.Behaviour):
    # Condition "Is Player Blocking": 공이 발 앞에 있고 플레이어가 그 앞을 막고 있는가? (트릭스터로 뚫을 때)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character, player = self.ai.character, common.player
        ball_front = (ball.x - character.x) * character.face_dir
        player_front = (player.x - character.x) * character.face_dir
        if (character.face_dir == -1 and TRICK_BALL_MIN < ball_front < TRICK_BALL_MAX and ball.y < BALL_LOW_HEIGHT
                and TRICK_BLOCK_MIN < player_front < TRICK_BLOCK_MAX):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class SkillCondition(py_trees.behaviour.Behaviour):
    # 필살기 Condition 들의 부모: 블랙보드의 감지한 공을 읽고, 플레이어 골대 쪽(왼쪽)을 볼 때만 검사함
    # (자식 클래스는 check(ball, dx) 만 만들면 됨, dx: AI에서 공까지의 가로 거리)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        if character.face_dir == -1 and self.check(ball, ball.x - character.x):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsShotComing(SkillCondition):
    # Condition "Is Shot Coming" (골키퍼형 철벽 방어): 슛이 자기 골대 쪽으로 빠르게 날아와 가까이 왔는가?

    def check(self, ball, dx):
        return ball.vx > GUARD_BALL_SPEED_PPS and -GUARD_DISTANCE < dx < 0 and ball.y < GUARD_MAX_HEIGHT


class IsHighBallNear(SkillCondition):
    # Condition "Is High Ball Near" (거인형 거대화): 높은 공이 가까이 떨어지고 있는가?

    def check(self, ball, dx):
        return abs(dx) < GIANT_DISTANCE and GIANT_MIN_HEIGHT < ball.y < GIANT_MAX_HEIGHT and ball.vy < 0


class IsBallBehindHead(SkillCondition):
    # Condition "Is Ball Behind Head" (공중형): 서 있는데 공이 머리 위 뒤쪽(자기 골대 쪽)으로 떨어지는가? (오버헤드킥 점프)

    def check(self, ball, dx):
        return (self.ai.character.state != 'JUMP' and 0 < dx < OVERHEAD_JUMP_DISTANCE
                and OVERHEAD_MIN_HEIGHT < ball.y < OVERHEAD_MAX_HEIGHT and ball.vy < 0)


class IsBallAtOverheadFoot(SkillCondition):
    # Condition "Is Ball At Overhead Foot" (공중형): 점프 중 공이 오버헤드킥으로 차는 발 가까이 왔는가?

    def check(self, ball, dx):
        character = self.ai.character
        if character.state != 'JUMP':
            return False
        foot_x, foot_y, foot_r = character.get_overhead_foot()
        return math.hypot(ball.x - foot_x, ball.y - foot_y) < OVERHEAD_USE_DISTANCE


class UseSkill(py_trees.behaviour.Behaviour):
    # Action "Use Skill": 필살 스킬 사용 (슛 계열은 다음 킥을 필살 슛으로 준비, Kick 가지가 이어서 참)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai

    def update(self):
        self.ai.character.use_skill()
        return py_trees.common.Status.SUCCESS


class IsBallFallingToHead(py_trees.behaviour.Behaviour):
    # Condition "Is Ball Falling To Head": 공이 머리 높이로 가까이 내려오는가? (점프 헤딩할 때)
    # (공이 머리 오른쪽에 있으면 자기 골대 쪽으로 튕기므로 왼쪽 앞에 있을 때만)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        dx = ball.x - self.ai.character.x
        if -JUMP_DISTANCE < dx <= 0 and JUMP_MIN_HEIGHT < ball.y < JUMP_MAX_HEIGHT and ball.vy < 0:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class IsBallLowBehind(py_trees.behaviour.Behaviour):
    # Condition "Is Ball Low Behind": 자기 골대 쪽(오른쪽)으로 달리는데 공이 그 앞에 낮게 있는가?
    # (그대로 달리면 공을 자기 골대 쪽으로 밀게 되므로 점프해서 넘어갈 때)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai
        self.blackboard = self.attach_blackboard_client(name=name)
        self.blackboard.register_key(key='ball', access=py_trees.common.Access.READ)

    def update(self):
        ball = self.blackboard.ball
        character = self.ai.character
        dx = ball.x - character.x
        if character.dir == 1 and 0 < dx < JUMP_OVER_DISTANCE and ball.y < BALL_LOW_HEIGHT:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Jump(py_trees.behaviour.Behaviour):
    # Action "Jump": 점프 (헤딩할 때와 공을 넘어갈 때 같은 동작, 노드는 쓰는 곳마다 따로 만듦)

    def __init__(self, name, ai):
        super().__init__(name)
        self.ai = ai

    def update(self):
        self.ai.character.jump()
        return py_trees.common.Status.SUCCESS


class OpponentAI:
    # 상대 선수를 움직이는 행동 트리 AI (py_trees)
    # 매 프레임 트리를 tick 해서 감지 → 할 일 하나를 고르고, 키보드 대신 상태 머신 이벤트(move_start, jump, kick 등)를 넣어 줌

    def __init__(self, character, reaction_delay=0.0):
        # character: AI가 조종할 선수
        # reaction_delay: 이 시간(초)만큼 전의 공을 보고 판단함 (클수록 늦게 반응하는 약한 AI)
        self.character = character
        self.reaction_delay = reaction_delay
        # 지난 공 모습 기록 (시각, 위치와 속도), 지난 시간
        self.ball_history = deque()
        self.elapsed = 0.0
        # 블랙보드 (노드들이 함께 보는 공용 메모장)는 노드들이 직접 연결해 씀
        # ball : 반응 지연만큼 전의 공 (Sense Ball 이 씀), target : 서야 할 가로 위치 (Set ... Location 이 씀)
        self.build_behavior_tree()

    def build_behavior_tree(self):
        # 공을 감지한 뒤, 할 일을 하나 고름 (Selector: 왼쪽일수록 우선, 처음 SUCCESS나 RUNNING에서 멈춤)
        # memory=False : 매 tick 감지부터, 그리고 우선순위가 높은 킥부터 다시 검사함
        kick = py_trees.composites.Sequence('Kick', memory=False, children=[
            IsBallAtFoot('Is Ball At Foot', self),
            Kick('Kick', self),
        ])
        # 필살 슛 (슛 계열 유형만): 게이지가 차고, 공이 발 앞에 있고, 슛이 잘 들어가는 거리면 준비
        # (트리는 AI가 조종하는 유형에 맞게 만듦)
        branches = []
        if self.character.char_type in SHOT_SKILL_RANGES:
            branches.append(py_trees.composites.Sequence('Shot Skill', memory=False, children=[
                IsGaugeFull('Is Gauge Full', self),
                IsBallAtFoot('Is Ball At Foot For Skill', self),
                IsInShotRange('Is In Shot Range', self),
                UseSkill('Use Shot Skill', self),
            ]))
        elif self.character.char_type == 'defender':
            # 하드태클: 플레이어가 공을 몰고 가까이 오면 공을 빼앗고 넘어뜨림
            branches.append(py_trees.composites.Sequence('Tackle Skill', memory=False, children=[
                IsGaugeFull('Is Gauge Full', self),
                IsPlayerOnBall('Is Player On Ball', self),
                UseSkill('Use Tackle', self),
            ]))
        elif self.character.char_type == 'keeper':
            # 철벽 방어: 슛이 가까이 날아오면 받아침
            branches.append(py_trees.composites.Sequence('Guard Skill', memory=False, children=[
                IsGaugeFull('Is Gauge Full', self),
                IsShotComing('Is Shot Coming', self),
                UseSkill('Use Guard', self),
            ]))
        elif self.character.char_type == 'giant':
            # 거대화: 높은 공이 가까이 떨어지면 커져서 공중볼을 따냄
            branches.append(py_trees.composites.Sequence('Giant Skill', memory=False, children=[
                IsGaugeFull('Is Gauge Full', self),
                IsHighBallNear('Is High Ball Near', self),
                UseSkill('Use Giant', self),
            ]))
        elif self.character.char_type == 'aerial':
            # 오버헤드킥: 점프 중 공이 차는 발에 오면 차고, 서 있을 때 공이 머리 위 뒤쪽으로 떨어지면 먼저 점프
            branches.append(py_trees.composites.Selector('Overhead Skill', memory=False, children=[
                py_trees.composites.Sequence('Overhead Kick', memory=False, children=[
                    IsGaugeFull('Is Gauge Full', self),
                    IsBallAtOverheadFoot('Is Ball At Overhead Foot', self),
                    UseSkill('Use Overhead', self),
                ]),
                py_trees.composites.Sequence('Jump For Overhead', memory=False, children=[
                    IsGaugeFull('Is Gauge Full Before Jump', self),
                    IsBallBehindHead('Is Ball Behind Head', self),
                    Jump('Jump To Overhead', self),
                ]),
            ]))
        elif self.character.char_type == 'trickster':
            # 트릭스터: 공을 가졌는데 플레이어가 앞을 막으면 드리블로 뚫고 지나감
            branches.append(py_trees.composites.Sequence('Trick Skill', memory=False, children=[
                IsGaugeFull('Is Gauge Full', self),
                IsPlayerBlocking('Is Player Blocking', self),
                UseSkill('Use Trick', self),
            ]))
        # 수비: 머리 위로 넘어가는 슛을 점프해서 머리로 막음
        block = py_trees.composites.Sequence('Block Shot', memory=False, children=[
            IsShotOverHead('Is Shot Over Head', self),
            Jump('Jump To Block', self),
        ])
        header = py_trees.composites.Sequence('Header', memory=False, children=[
            IsBallFallingToHead('Is Ball Falling To Head', self),
            Jump('Jump To Head', self),
        ])
        jump_over = py_trees.composites.Sequence('Jump Over', memory=False, children=[
            IsBallLowBehind('Is Ball Low Behind', self),
            Jump('Jump Over Ball', self),
        ])
        # 수비: 골대가 위험하면 공과 골대 사이로 돌아가 섬 (보통 위치 잡기보다 먼저)
        defend = py_trees.composites.Sequence('Defend', memory=False, children=[
            IsGoalInDanger('Is Goal In Danger', self),
            SetDefendLocation('Set Defend Location', self),
            MoveTo('Move To Defend', self),
        ])
        position = py_trees.composites.Sequence('Position', memory=False, children=[
            SetTargetLocation('Set Target Location', self),
            MoveTo('Move To', self),
        ])
        # 킥과 헤딩은 공을 걷어 내는 수비도 되므로 가장 먼저, 넘어가기는 골대 쪽으로 달려갈 때 필요해서 수비보다 먼저
        think_and_act = py_trees.composites.Selector('Think and Act', memory=False,
                                                     children=branches + [kick, block, header, jump_over, defend, position])
        root = py_trees.composites.Sequence('Opponent AI', memory=False, children=[
            SenseBall('Sense Ball', self),
            think_and_act,
        ])
        self.bt = py_trees.trees.BehaviourTree(root)
        # 콘솔에 마지막으로 출력한 트리 상태
        self.bt_snapshot = ''

    def seen_ball(self):
        # 반응 지연만큼 전의 공 모습 (지금 공을 기록하고, 지연보다 오래된 기록은 버림)
        ball = common.ball
        self.elapsed += game_framework.frame_time
        self.ball_history.append((self.elapsed, SimpleNamespace(x=ball.x, y=ball.y, vx=ball.vx, vy=ball.vy)))
        while len(self.ball_history) > 1 and self.ball_history[1][0] <= self.elapsed - self.reaction_delay:
            self.ball_history.popleft()
        return self.ball_history[0][1]

    def move(self, dir):
        # 키보드의 방향키 처리와 같은 방식으로 방향을 바꾸고 이벤트를 넣음
        self.character.dir = dir
        if dir == 0:
            self.character.move_stop()
        else:
            self.character.face_dir = dir
            self.character.move_start()

    def update(self):
        # 행동 트리를 한 번 실행 (감지 → 필살기, 킥, 슛 막기, 헤딩, 넘어가기, 수비, 위치 잡기 중 하나)
        self.bt.tick()
        # 확인용: F1 표시를 켰을 때만 트리 상태가 바뀌면 콘솔에 출력 (✓ SUCCESS, ✕ FAILURE, * RUNNING)
        if debug_view.show_bounding:
            snapshot = py_trees.display.unicode_tree(self.bt.root, show_status=True)
            if snapshot != self.bt_snapshot:
                print(snapshot)
                self.bt_snapshot = snapshot

    def draw(self):
        pass
