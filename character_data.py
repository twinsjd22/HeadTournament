# 캐릭터 유형 데이터 (플레이어와 상대 AI가 같이 사용)
# 능력치는 1~5 단계, 기획서 초안 값 (플레이 테스트로 조정)
# 점프 높이는 모든 유형이 같으므로 능력치에 넣지 않음
# 신규 유형은 같은 모양으로 한 줄씩 추가

CHARACTER_TYPES = {
    'defender': {'name': '수비형', 'sheet': 'resource/sheet_defender.png',
                 'speed': 5, 'power': 3, 'skill': '하드태클'},
    'trickster': {'name': '개인기형', 'sheet': 'resource/sheet_trickster.png',
                  'speed': 4, 'power': 2, 'skill': '트릭스터'},
    'power': {'name': '파워형', 'sheet': 'resource/sheet_power.png',
              'speed': 2, 'power': 5, 'skill': '파워슛'},
}
