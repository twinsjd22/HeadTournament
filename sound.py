# 사운드: 효과음과 BGM을 처음 쓸 때 한 번만 불러 두고 계속 다시 사용
# 다른 모듈은 sound.play('kick'), sound.play_bgm('match')처럼 이름으로만 부름
from pico2d import load_wav, load_music

# 효과음 이름: (파일, 볼륨 0~128)
SFX_FILES = {
    'kick': ('resource/sfx_kick.wav', 64),
    'header': ('resource/sfx_header.wav', 64),
    'whistle': ('resource/sfx_whistle.wav', 64),
    'goal': ('resource/sfx_goal.wav', 64),
    'skill': ('resource/sfx_skill.wav', 64),
    'select': ('resource/sfx_select.wav', 64),
}
# BGM 이름: (파일, 볼륨 0~128)
BGM_FILES = {
    'title': ('resource/bgm_title.mp3', 40),
    'match': ('resource/bgm_match.mp3', 40),
}

# 불러 둔 효과음과 BGM (이름: 객체)
sfx = {}
bgms = {}
# 지금 나오고 있는 BGM 이름 (같은 BGM을 다시 틀면 처음부터 다시 나오지 않게 함)
current_bgm = None


def play(name):
    # 효과음 한 번 재생
    pass


def play_bgm(name):
    # BGM을 바꿔서 반복 재생
    pass


def stop_bgm():
    # BGM 끄기
    pass
