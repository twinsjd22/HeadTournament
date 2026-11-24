# 캐릭터 유형 데이터 (플레이어와 상대 AI가 같이 사용)
# 능력치는 1~5 단계, 기획서 초안 값 (플레이 테스트로 조정)
# 점프 높이는 모든 유형이 같으므로 능력치에 넣지 않음
# 신규 유형은 같은 모양으로 한 줄씩 추가
# portrait, desc: 선택 화면의 슬롯 초상화와 필살기 설명 한 줄

CHARACTER_TYPES = {
    'defender': {'name': '수비형', 'sheet': 'resource/sheet_defender.png',
                 'portrait': 'resource/portrait_defender.png',
                 'speed': 5, 'power': 3, 'skill': '하드태클',
                 'desc': '공을 빼앗고 상대를 넘어뜨린다'},
    'trickster': {'name': '개인기형', 'sheet': 'resource/sheet_trickster.png',
                  'portrait': 'resource/portrait_trickster.png',
                  'speed': 4, 'power': 2, 'skill': '트릭스터',
                  'desc': '부딪혀도 공을 뺏기지 않는다'},
    'power': {'name': '파워형', 'sheet': 'resource/sheet_power.png',
              'portrait': 'resource/portrait_power.png',
              'speed': 2, 'power': 5, 'skill': '파워슛',
              'desc': '공을 아주 강하게 찬다'},
    'keeper': {'name': '골키퍼형', 'sheet': 'resource/sheet_keeper.png',
               'portrait': 'resource/portrait_keeper.png',
               'speed': 3, 'power': 3, 'skill': '철벽 방어',
               'desc': '잠시 동안 몸에 닿는 공을 모두 막아 낸다'},
    'aerial': {'name': '공중형', 'sheet': 'resource/sheet_aerial.png',
               'portrait': 'resource/portrait_aerial.png',
               'speed': 3, 'power': 4, 'skill': '오버헤드킥',
               'desc': '높이 뛰어올라 공중에서 공을 내리꽂는다'},
    'giant': {'name': '거인형', 'sheet': 'resource/sheet_giant.png',
              'portrait': 'resource/portrait_giant.png',
              'speed': 2, 'power': 4, 'skill': '거대화',
              'desc': '잠시 동안 몸이 커져 공중볼을 따낸다'},
}
