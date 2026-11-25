# 여러 모듈이 함께 쓰는 경기 객체 (경기 화면이 init에서 채움)
# 다른 모듈은 import common 후 common.ball 처럼 씀
# (from common import ball 은 안 됨: import 할 때의 None이 복사되어 바뀐 값을 못 봄)

player = None
opponent = None
ball = None
