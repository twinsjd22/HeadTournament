# 토너먼트 기록 저장: 토너먼트 한 번이 끝날 때마다 기록 하나를 파일에 남기고 랭킹 순으로 정리함
# (게임을 껐다 켜도 남도록 json 파일로 저장)

import json
import time

import tournament

# 기록 파일 (게임 폴더 안)
RECORD_FILE = 'records.json'
# 랭킹에 남기는 최대 기록 수
MAX_RECORDS = 10


def load():
    # 저장된 기록 목록 (파일이 없거나 깨졌으면 빈 목록)
    try:
        with open(RECORD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def rank_key(record):
    # 랭킹 순서: 많이 이긴 기록(멀리 올라간 기록)이 위, 같으면 득실차가 큰 기록이 위
    return record['wins'], record['goals_for'] - record['goals_against']


def add(name, char_type, wins, goals_for, goals_against):
    # 토너먼트 한 번의 기록을 추가하고, 랭킹 순으로 정렬해 상위 기록만 저장
    # wins: 이긴 경기 수 (0이면 32강 탈락, 라운드 수와 같으면 우승)
    records = load()
    records.append({'name': name, 'char_type': char_type, 'wins': wins,
                    'goals_for': goals_for, 'goals_against': goals_against,
                    'date': time.strftime('%m/%d')})
    # 랭킹 기준이 같으면 먼저 세운 기록이 위 (정렬이 원래 순서를 유지함)
    records.sort(key=rank_key, reverse=True)
    records = records[:MAX_RECORDS]
    with open(RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def result_text(record):
    # 성적 글자: 모두 이겼으면 '우승', 아니면 진 라운드 이름 + '탈락' (예: '8강 탈락')
    if record['wins'] >= len(tournament.ROUNDS):
        return '우승'
    return f'{tournament.ROUNDS[record["wins"]]} 탈락'
