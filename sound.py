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
    # 효과음 한 번 재생 (처음이면 불러 두고 볼륨을 맞춤)
    if name not in sfx:
        path, volume = SFX_FILES[name]
        sfx[name] = load_wav(path)
        sfx[name].set_volume(volume)
    sfx[name].play()


def play_bgm(name):
    # BGM을 바꿔서 반복 재생 (이미 나오고 있는 BGM이면 그대로 둠)
    global current_bgm

    if current_bgm == name:
        return
    if name not in bgms:
        path, volume = BGM_FILES[name]
        bgms[name] = load_music(path)
        bgms[name].set_volume(volume)
    bgms[name].repeat_play()
    current_bgm = name


def stop_bgm():
    # BGM 끄기 (끈 뒤 같은 BGM을 다시 틀 수 있게 이름도 지움)
    global current_bgm

    if current_bgm is not None:
        bgms[current_bgm].stop()
        current_bgm = None


def pause_bgm():
    # BGM을 멈춘 자리에서 잠깐 세움 (resume_bgm으로 그 자리부터 이어서 나옴)
    if current_bgm is not None:
        bgms[current_bgm].pause()
