# 템플릿 이미지 준비 가이드

## 개요

이 문서는 전투 진입 다중 조건 검증을 위한 템플릿 이미지 준비 방법을 안내합니다.

## 필요한 템플릿

### 다중 조건 검증용 템플릿 (신규)

전투 진입 시 3가지 UI 요소를 동시 확인하여 정확도를 높입니다.

#### 1. stage_info_ui.png
- **위치**: `assets/templates/2560x1440/ui/stage_info_ui.png`
- **캡처 대상**: 전투 화면 상단의 스테이지 정보 UI
  - 예: "Normal 1-4" 표시 영역
  - 스테이지 이름, 난이도 정보가 포함된 상단 바
- **캡처 시점**: 전투 진입 직후
- **권장 크기**: 가로 200~400px (너무 크지 않게)
- **주의사항**:
  - 스테이지마다 텍스트가 다르므로 "Normal 1-4"에 특화된 영역 캡처
  - 또는 스테이지 번호 제외하고 고정 UI 부분만 캡처

#### 2. pause_button.png
- **위치**: `assets/templates/2560x1440/buttons/pause_button.png`
- **캡처 대상**: 전투 화면 우측 상단의 일시정지 버튼
  - 보통 "||" 모양의 아이콘
  - 또는 톱니바퀴/메뉴 아이콘
- **캡처 시점**: 전투 중 (애니메이션 없는 상태)
- **권장 크기**: 버튼 크기만큼 (50~100px)
- **주의사항**:
  - 버튼 주변 배경 포함하지 않기
  - 호버 상태가 아닌 기본 상태 캡처

#### 3. battle_ui.png (기존)
- **위치**: `assets/templates/2560x1440/ui/battle_ui.png`
- **상태**: ✅ 이미 존재
- **용도**: 기존 전투 UI 전체 또는 특징적인 부분

## 템플릿 캡처 방법

### 1. 게임 실행 및 화면 준비
```
1. 블루 아카이브 실행
2. Normal 1-4 스테이지 진입
3. 전투 시작 (UI가 완전히 로드될 때까지 대기)
```

### 2. 스크린샷 도구 사용
- **Windows 기본**: Win + Shift + S (부분 캡처)
- **추천 도구**:
  - Greenshot (무료)
  - ShareX (무료)
  - Windows Snipping Tool

### 3. 영역 선택 가이드

#### stage_info_ui.png 캡처 예시
```
┌────────────────────────┐
│  Normal 1-4  ⭐⭐⭐    │  ← 이 부분 캡처
└────────────────────────┘
```

캡처 팁:
- 스테이지 이름이 바뀌지 않는 고정 UI 부분 선택
- 배경색이 일정한 영역 포함
- 너무 크게 잡지 말 것 (200~400px 정도)

#### pause_button.png 캡처 예시
```
화면 우측 상단:
                    ┌────┐
                    │ || │  ← 이 버튼만 캡처
                    └────┘
```

캡처 팁:
- 버튼 아이콘만 정확히 선택
- 주변 여백 최소화
- 버튼이 눌리지 않은 기본 상태

### 4. 이미지 저장

1. **파일명 확인**:
   - `stage_info_ui.png`
   - `pause_button.png`

2. **저장 위치**:
   - `assets/templates/2560x1440/ui/stage_info_ui.png`
   - `assets/templates/2560x1440/buttons/pause_button.png`

3. **형식**: PNG (필수)

4. **해상도별 추가**:
   - 1920x1080 사용 시: `assets/templates/1920x1080/` 하위에도 동일하게 준비

## 검증 로직

### 다중 조건 검증 기준

BattleChecker.verify_battle_entry_multi_condition() 메서드는 다음과 같이 동작합니다:

```python
# 3가지 UI 요소 확인
1. battle_ui.png ✓
2. stage_info_ui.png ✓
3. pause_button.png ✓

# 판단 기준
- 3개 중 2개 이상 인식 → 전투 진입 성공 ✅
- 1개 이하만 인식 → 전투 진입 실패 또는 대기 중 ⏳
```

### 장점

1. **신뢰도 향상**: 단일 템플릿보다 오인식 확률 감소
2. **유연성**: 1개 템플릿이 실패해도 다른 2개로 보완
3. **명확성**: 전투 화면 특유의 UI로 정확한 구분

## 템플릿 없을 경우

템플릿 파일이 없어도 코드는 정상 동작합니다:
- 존재하는 템플릿만으로 검증 수행
- 로그에 경고 메시지 출력: `템플릿 파일 없음: ... (건너뜀)`
- 최소 `battle_ui.png`만 있으면 기존 방식으로 작동

## 테스트 방법

### 1. 템플릿 확인
```bash
ls assets/templates/2560x1440/ui/stage_info_ui.png
ls assets/templates/2560x1440/buttons/pause_button.png
```

### 2. Python 테스트 스크립트 (예정)
```python
from src.verification.battle_checker import BattleChecker
from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController

matcher = TemplateMatcher()
controller = GameController()
checker = BattleChecker(matcher, controller)

# 다중 조건 검증 실행
result = checker.verify_battle_entry_multi_condition(
    timeout=15,
    required_matches=2  # 3개 중 2개 이상
)

print(f"성공: {result['success']}")
print(f"매칭 수: {result['match_count']}")
print(f"조건별 결과: {result['conditions_met']}")
```

### 3. 로그 확인
```
[INFO] 전투 진입 다중 조건 검증 시작
[INFO] ✓ battle_ui 인식 성공
[INFO] ✓ stage_info 인식 성공
[INFO] ✓ pause_button 인식 성공
[INFO] 전투 진입 확인 (3/3개 조건 충족)
[INFO] 충족 조건: ['battle_ui', 'stage_info', 'pause_button']
```

## 문제 해결

### Q1: 템플릿 매칭이 안 돼요
**A**:
- 캡처한 해상도가 현재 게임 해상도와 일치하는지 확인
- 템플릿 크기가 너무 크거나 작지 않은지 확인 (100~400px 권장)
- 배경이 포함되지 않았는지 확인

### Q2: 어떤 부분을 캡처해야 할지 모르겠어요
**A**:
- `stage_info_ui`: 화면 상단 중앙의 스테이지 정보 (텍스트 포함된 바)
- `pause_button`: 화면 우측 상단의 일시정지/설정 버튼

### Q3: 신뢰도(confidence)를 조정하고 싶어요
**A**:
- `BattleChecker.verify_battle_entry_multi_condition()` 내부의 `confidence=0.8` 값 수정
- 0.7~0.9 사이 권장 (너무 낮으면 오인식, 너무 높으면 인식 실패)

## 참고

- 다른 템플릿 준비 방법은 [CLAUDE.md](CLAUDE.md) 참고
- 해상도별 템플릿 관리는 [RESOLUTION_GUIDE.md](RESOLUTION_GUIDE.md) 참고
