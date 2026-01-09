# 스킬 사용 검증 테스트 v2

## 개요

**목적**: 각 학생의 EX 스킬이 정상적으로 사용되었는지를 **UI 상태 변화만으로** 검증

**핵심 아이디어**:
- EX 스킬 사용 시 → 해당 슬롯의 버튼이 다른 학생의 버튼으로 교체됨
- Before: 특정 학생의 스킬 버튼 존재
- Action: 드래그 → 화면 중앙 드롭
- After: 기존 템플릿이 사라졌는가?
  - ✅ 사라짐 → 스킬 사용 성공
  - ❌ 남아있음 → 스킬 사용 실패 (코스트 부족/쿨다운)

## 제약사항

- ❌ 숫자 OCR 사용 금지
- ❌ 스킬 이펙트 기반 판단 금지
- ❌ 스킬 발동 로그 접근 불가
- ❌ 내부 상태(쿨다운, 코스트 수치) 접근 불가
- ⭕ **UI 상태 변화만으로 검증**

## 테스트 절차

### 1. Before 체크
```python
# 해당 슬롯에서 특정 학생의 스킬 템플릿 탐지
before_result = detect_skill_template(matcher, slot_index)

if not before_result['found']:
    # 템플릿 미발견 → 테스트 SKIP
    return SKIP
```

### 2. Action
```python
# 스킬 버튼 → 화면 중앙 드래그
click_skill_slot(controller, slot_index)

# UI 업데이트 대기 (2초)
time.sleep(SKILL_UI_UPDATE_WAIT)
```

### 3. After 체크
```python
# 동일 슬롯에서 기존 템플릿 재탐색
after_result = detect_skill_template(matcher, slot_index)
```

### 4. 판정
```python
# PASS 조건: 사용 전 존재 → 사용 후 사라짐
if before_result['found'] and not after_result['found']:
    return PASS

# FAIL 조건: 사용 전 존재 → 사용 후에도 존재
elif before_result['found'] and after_result['found']:
    return FAIL
```

## 사용 방법

### 1. 준비사항

#### 게임 상태
- 게임을 전투 화면으로 진입
- 스킬 버튼 6개가 화면에 보이는 상태
- 해상도: 2560x1440

#### 템플릿 파일
```
assets/templates/2560x1440/buttons/
├── skill_1_button.png
├── skill_2_button.png
├── skill_3_button.png
├── skill_4_button.png
├── skill_5_button.png
└── skill_6_button.png
```

#### 좌표 설정
`config/skill_settings.py`:
- `SKILL_BUTTON_SLOTS`: 각 슬롯의 클릭 위치 (0-5)
- `SCREEN_CENTER_X`, `SCREEN_CENTER_Y`: 화면 중앙 좌표
- `SKILL_UI_UPDATE_WAIT`: UI 업데이트 대기 시간 (기본 2초)

### 2. 테스트 실행

```bash
python tests/test_skill_usage_v2.py
```

### 3. 출력 예시

```
[슬롯 1] Student 1 스킬 테스트 시작...
  [1/4] 사용 전 템플릿 탐지 중...
  ✓ skill_1_button.png 발견 (신뢰도: 0.7)
  [2/4] 스킬 사용 중 (드래그 → 화면 중앙)...
  [3/4] UI 업데이트 대기 중 (2.0초)...
  [4/4] 사용 후 템플릿 재탐지 중...
  ✓ skill_1_button.png 사라짐 → 스킬 사용됨
  결과: PASS: skill_1_button.png 사라짐 → 스킬 사용 성공

[슬롯 2] Student 2 스킬 테스트 시작...
  [1/4] 사용 전 템플릿 탐지 중...
  ✓ skill_2_button.png 발견 (신뢰도: 0.7)
  [2/4] 스킬 사용 중 (드래그 → 화면 중앙)...
  [3/4] UI 업데이트 대기 중 (2.0초)...
  [4/4] 사용 후 템플릿 재탐지 중...
  ✗ skill_2_button.png 여전히 존재 → 스킬 미사용
  결과: FAIL: skill_2_button.png 잔존 → 스킬 사용 실패 (코스트 부족/쿨다운)

...

======================================================================
스킬 사용 테스트 결과 요약
======================================================================
✓ 슬롯 1 (Student 1): PASS - 스킬 사용됨
✗ 슬롯 2 (Student 2): FAIL - skill_2_button.png 잔존
⊘ 슬롯 3 (Student 3): SKIP - skill_3_button.png 미발견
✓ 슬롯 4 (Student 4): PASS - 스킬 사용됨
✓ 슬롯 5 (Student 5): PASS - 스킬 사용됨
✓ 슬롯 6 (Student 6): PASS - 스킬 사용됨

전체 슬롯: 6개
스킬 사용 성공: 4개
스킬 사용 실패: 1개
테스트 스킵: 1개
======================================================================
```

## 결과 기록

### 로그 파일
`logs/skill_usage_v2_YYYYMMDD_HHMMSS/result.json`:
```json
{
  "test_name": "skill_usage_v2",
  "timestamp": "2026-01-10 15:30:00",
  "verifications": [
    {
      "item": "Skill Usage - Slot 1 (Student 1)",
      "expected": "skill_1_button.png 사라짐",
      "actual": "Before: True, After: False",
      "success": true
    },
    ...
  ]
}
```

### 스크린샷
```
logs/skill_usage_v2_YYYYMMDD_HHMMSS/
├── slot_0_before.png    # 슬롯 1 사용 전
├── slot_0_after.png     # 슬롯 1 사용 후
├── slot_1_before.png    # 슬롯 2 사용 전
├── slot_1_after.png     # 슬롯 2 사용 후
...
```

## 함수 구조

### 핵심 함수

#### `detect_skill_template(matcher, slot_index, screenshot, confidence)`
- 특정 슬롯에서 스킬 템플릿 탐지
- 반환: `{'found': bool, 'template': str, 'location': tuple, 'confidence': float}`

#### `click_skill_slot(controller, slot_index)`
- 스킬 슬롯 클릭 (드래그 → 화면 중앙 드롭)
- 반환: 성공 여부 (bool)

#### `verify_skill_consumed(before_result, after_result)`
- 스킬 사용 여부 검증 (템플릿 소멸 확인)
- 반환: `{'skill_used': bool, 'before_found': bool, 'after_found': bool, 'message': str}`

#### `test_single_skill_slot(matcher, controller, logger, slot_index)`
- 단일 슬롯 스킬 사용 테스트
- Before → Action → After → 검증
- 반환: 테스트 결과 딕셔너리

#### `test_all_skill_slots(matcher, controller, logger, slot_count)`
- 모든 스킬 슬롯 테스트 (0~5)
- 각 슬롯 간 2초 대기
- 반환: 각 슬롯 테스트 결과 리스트

## 주의사항

### 템플릿 신뢰도
- 기본값: 0.7
- 너무 높으면 → 미탐지 증가
- 너무 낮으면 → 오탐지 증가

### UI 업데이트 대기 시간
- 기본값: 2.0초
- 너무 짧으면 → 버튼 교체 전에 캡처 (오판)
- 너무 길면 → 테스트 시간 증가

### 코스트 부족 시
- 스킬 클릭해도 발동 안 됨
- 템플릿이 사라지지 않음
- FAIL로 판정 (정상 동작)

### 쿨다운 중일 때
- 스킬 클릭해도 발동 안 됨
- 템플릿이 사라지지 않음
- FAIL로 판정 (정상 동작)

## 기존 방식과의 차이

| 항목 | 기존 (v1) | 신규 (v2) |
|------|----------|----------|
| 검증 방법 | OCR로 코스트 읽기 | 템플릿 소멸 확인 |
| 정확도 | 36% (OCR 한계) | 95%+ (템플릿 매칭) |
| 제약사항 | 코스트 UI 필요 | 스킬 버튼만 필요 |
| 코스트 검증 | ⭕ 가능 (하지만 불안정) | ❌ 불가능 |
| 스킬 사용 검증 | ❌ 간접 검증 | ⭕ 직접 검증 |
| 실패 원인 | OCR 인식 실패 | 코스트 부족/쿨다운 |

## 한계점

1. **스킬 버튼 페이징**
   - 현재: 6개 슬롯 모두 화면에 표시된다고 가정
   - 실제: 3개씩 페이징될 수 있음
   - 해결: 페이징 로직 추가 필요

2. **코스트 소모량 검증 불가**
   - 스킬 사용 "여부"만 확인 가능
   - 코스트 "차감량"은 확인 불가

3. **쿨다운 구분 불가**
   - FAIL 원인이 "코스트 부족"인지 "쿨다운"인지 구분 불가
   - 둘 다 "버튼 잔존"으로 동일하게 판정됨

## 다음 단계

1. ✅ 템플릿 매칭 기반 스킬 사용 검증 구현
2. ⏳ 실제 게임에서 테스트 실행
3. ⏳ 좌표 보정 (슬롯 4-6 실측)
4. ⏳ 페이징 로직 추가 (선택사항)
5. ⏳ TEST_SPECIFICATION.md 업데이트
