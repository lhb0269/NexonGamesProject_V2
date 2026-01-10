# 보상 획득 UI 검증 테스트

## 테스트 목적

전투 종료 후 **보상 획득 UI가 정상적으로 표시되고, 보상 아이템이 결과 화면에 매핑되었는지 여부만을 검증**합니다.

### 테스트 범위

✅ **포함**
- Victory 화면 확인
- MISSION COMPLETE 화면 노출 확인
- 보상 아이템 카드 UI 존재 여부 확인 (아이콘 단위)

❌ **제외**
- 실제 인벤토리 반영 여부
- 보상 아이템 수량 검증 (OCR)
- 서버 데이터 무결성 검증

## 테스트 시나리오

```
[1단계] Victory 화면 확인
   ↓
[2단계] Victory 확인 버튼 클릭
   ↓
[3단계] MISSION COMPLETE 화면 확인
   ↓
[4단계] MISSION COMPLETE 확인 버튼 클릭 (+ 5초 대기)
   ↓
[5단계] 보상 아이템 UI 확인
   ├─ 크레딧 아이콘
   └─ 활동 보고서 아이콘
   ↓
[결과] PASS / FAIL 판정
```

## 필요한 템플릿 이미지

### 1. UI 템플릿 (assets/templates/2560x1440/ui/)

| 템플릿 파일명 | 설명 | 상태 |
|--------------|------|------|
| `victory.png` | Victory 화면 | ✅ 존재 |
| `mission_complete.png` | MISSION COMPLETE 화면 또는 보상 획득 타이틀 | ⚠️ **필요** |

### 2. 버튼 템플릿 (assets/templates/2560x1440/buttons/)

| 템플릿 파일명 | 설명 | 상태 |
|--------------|------|------|
| `victory_confirm.png` | Victory 확인 버튼 | ✅ 존재 |
| `reward_confirm.png` | MISSION COMPLETE 확인 버튼 | ⚠️ **필요** |

### 3. 아이콘 템플릿 (assets/templates/2560x1440/icons/)

| 템플릿 파일명 | 설명 | 상태 |
|--------------|------|------|
| `credit_icon.png` | 크레딧 아이콘 | ⚠️ **필요** |
| `activity_report_icon.png` | 활동 보고서 아이콘 | ⚠️ **필요** |

## 템플릿 캡처 가이드

### mission_complete.png
- **위치**: Victory 확인 버튼 클릭 후 나타나는 MISSION COMPLETE 화면
- **캡처 대상**: "MISSION COMPLETE" 텍스트 또는 타이틀 영역
- **권장 크기**: 화면 상단 중앙의 타이틀 영역만 캡처 (전체 화면 X)

### reward_confirm.png
- **위치**: MISSION COMPLETE 화면 하단 확인 버튼
- **캡처 대상**: 확인 버튼 전체 (텍스트 포함)
- **권장 크기**: 버튼 크기만큼 (배경 최소화)

### credit_icon.png
- **위치**: 보상 화면에서 크레딧을 표시하는 아이콘
- **캡처 대상**: 크레딧 아이콘만 (숫자 제외)
- **권장 크기**: 아이콘 크기만큼 (배경 포함 X)

### activity_report_icon.png
- **위치**: 보상 화면에서 활동 보고서를 표시하는 아이콘
- **캡처 대상**: 활동 보고서 아이콘만 (숫자 제외)
- **권장 크기**: 아이콘 크기만큼 (배경 포함 X)

## 실행 방법

### 1. 직접 실행
```bash
python tests/test_reward_ui_verification.py
```

### 2. GUI 테스트 러너에서 실행
```bash
python gui_test_runner.py
```
- TC-007: 보상 획득 UI 검증 선택 후 실행

## 테스트 시작 조건

- 블루 아카이브 게임 실행
- Normal 1-4 전투 승리 후 **Victory 화면**에서 대기
- 게임 창이 화면에 보이도록 배치
- 게임 해상도: **2560x1440** (다른 해상도는 템플릿 재캡처 필요)

## 성공 조건

다음 모든 조건을 만족하면 **PASS**:

1. ✅ Victory 화면이 정상적으로 표시됨
2. ✅ Victory 확인 버튼 클릭 성공
3. ✅ MISSION COMPLETE 화면이 정상적으로 표시됨
4. ✅ MISSION COMPLETE 확인 버튼 클릭 성공
5. ✅ 최소 1개 이상의 보상 아이템 아이콘이 화면에 표시됨

## 실패 조건

다음 중 하나라도 해당하면 **FAIL**:

1. ❌ Victory 화면을 찾을 수 없음
2. ❌ Victory 확인 버튼을 찾거나 클릭할 수 없음
3. ❌ MISSION COMPLETE 화면이 10초 내에 나타나지 않음
4. ❌ MISSION COMPLETE 확인 버튼을 찾거나 클릭할 수 없음
5. ❌ 보상 아이템 아이콘을 하나도 찾을 수 없음

## 구현 제약사항

- **Live 빌드 환경**: 게임 내부 로직 접근 불가
- **화면 인식 기반**: 템플릿 매칭만 사용
- **메모리 접근 금지**: 내부 상태 조회 불가
- **OCR 사용 금지**: 아이콘 UI 존재 여부만 확인 (수량 검증 안 함)

## 로그 및 스크린샷

### 로그 파일 위치
```
logs/reward_ui_verification_YYYYMMDD_HHMMSS/
├── test_result.json          # 테스트 결과 JSON
├── victory_screen_found.png  # Victory 화면 스크린샷
├── mission_complete_found.png # MISSION COMPLETE 화면 스크린샷
└── reward_items_verification.png # 보상 아이템 검증 스크린샷
```

### 결과 JSON 구조
```json
{
  "test_name": "reward_ui_verification",
  "timestamp": "2026-01-10T02:30:00",
  "checks": [
    {
      "name": "Victory_화면_확인",
      "passed": true,
      "message": "Victory 화면 발견",
      "details": {...}
    },
    {
      "name": "보상_아이템_크레딧",
      "passed": true,
      "message": "크레딧 아이콘 발견",
      "details": {...}
    }
  ],
  "screenshots": [...]
}
```

## 예상 실행 시간

- 정상 케이스: **약 20-25초**
  - Victory 화면 확인: 1초
  - Victory 버튼 클릭 및 대기: 4초
  - MISSION COMPLETE 대기: 최대 10초
  - MISSION COMPLETE 버튼 클릭 및 대기: 6초
  - 보상 아이템 확인: 2초

## 주의사항

1. **템플릿 정확도**: 게임 UI 업데이트 시 템플릿 재캡처 필요
2. **화면 가림 금지**: 테스트 중 게임 화면이 가려지면 안 됨
3. **네트워크 지연**: 보상 화면 로딩이 느리면 타임아웃 발생 가능
4. **해상도 고정**: 2560x1440 이외의 해상도는 별도 템플릿 필요

## 문제 해결

### Q: MISSION COMPLETE 화면이 타임아웃됩니다
A:
- `mission_complete.png` 템플릿이 정확한지 확인
- 네트워크 상태 확인 (서버 응답 지연 가능)
- 타임아웃 시간 조정: `matcher.wait_for_template(template, timeout=20)`

### Q: 보상 아이템 아이콘을 찾을 수 없습니다
A:
- `credit_icon.png`, `activity_report_icon.png` 템플릿 재캡처
- 아이콘만 캡처했는지 확인 (배경 포함 시 매칭 실패 가능)
- 신뢰도 조정: `matcher = TemplateMatcher(confidence=0.6)`

### Q: Victory 화면은 찾았지만 버튼 클릭이 안 됩니다
A:
- `victory_confirm.png` 템플릿 확인
- 게임 화면이 활성화되어 있는지 확인
- 마우스 클릭 위치 로그 확인

## 관련 파일

- **테스트 스크립트**: [tests/test_reward_ui_verification.py](test_reward_ui_verification.py)
- **템플릿 디렉토리**: `assets/templates/2560x1440/`
- **설정 파일**: `config/settings.py`
- **로거**: `src/logger/test_logger.py`

## 업데이트 이력

- **2026-01-10**: 초기 버전 작성
  - Victory → MISSION COMPLETE → 보상 아이템 UI 검증 구현
  - 템플릿 매칭 기반 검증
  - OCR 미사용 (아이콘 UI만 확인)
