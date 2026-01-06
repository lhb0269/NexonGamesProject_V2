# CLAUDE.md

이 파일은 Claude Code가 이 저장소의 코드 작업 시 참고하는 가이드를 제공합니다.

## 프로젝트 개요

**블루 아카이브 자동화 테스트 프로젝트** - 블루 아카이브 스팀 버전 Normal 1-4 스테이지 자동 플레이 및 검증 시스템

### 프로젝트 목표
- Live 빌드에서 화면 인식 기반 자동화 구현
- 스테이지 클리어 과정의 주요 항목 검증
- 검증 결과 로그 생성

### 기술 스택
- **언어**: Python 3.11
- **자동화 도구**: pyautogui
- **인식 방법**: 템플릿 매칭 (locateOnScreen)
- **제어 방법**: 화면 클릭/키보드 입력

### 제약사항
- 게임 내부 로직 접근 불가
- 메모리 조작 금지
- 순수 화면 인식/제어만 사용

## 개발 환경 설정

### 필수 요구사항
```bash
pip install pyautogui pillow opencv-python pytesseract numpy
```

**추가 요구사항:**
- Tesseract OCR 설치 (Windows: https://github.com/UB-Mannheim/tesseract/wiki)
  - 기본 설치 경로: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - 한국어 언어팩 포함 (kor, eng)

### 프로젝트 구조
```
NexonGamesProject_V2/
├── src/
│   ├── automation/     # 자동화 로직
│   │   ├── game_controller.py    # 게임 제어 (마우스/키보드)
│   │   └── stage_runner.py       # 스테이지 전체 흐름 실행
│   ├── recognition/    # 이미지 인식
│   │   └── template_matcher.py   # pyautogui 템플릿 매칭 래퍼
│   ├── ocr/            # OCR 텍스트 인식
│   │   └── ocr_reader.py         # Tesseract OCR 래퍼 (통합 클래스)
│   ├── verification/   # 검증 로직
│   │   ├── movement_checker.py   # 이동 검증
│   │   ├── battle_checker.py     # 전투 검증
│   │   ├── skill_checker.py      # 스킬 검증 (OCR 통합)
│   │   └── reward_checker.py     # 보상 검증
│   └── logger/         # 결과 기록
│       └── test_logger.py        # JSON 기반 로깅
├── assets/
│   └── templates/      # UI 템플릿 이미지
│       ├── buttons/    # 버튼 이미지 (deploy, mission_start, phase_end 등)
│       ├── icons/      # 아이콘 이미지 (start_tile, enemy_tile, empty_tile 등)
│       └── ui/         # UI 요소 (formation_screen, stage_map, battle_ui, victory 등)
├── logs/               # 테스트 결과 로그 (JSON + 스크린샷)
├── tests/              # 테스트 스크립트
│   ├── test_modules.py          # 기본 모듈 테스트
│   ├── test_partial_stage.py    # 부분 단계별 테스트
│   ├── test_tile_movement.py    # 발판 이동 테스트
│   ├── test_skill_cost_ocr.py   # 코스트 OCR 테스트
│   ├── test_skill_usage.py      # 스킬 사용 시스템 테스트
│   └── test_ocr_simple.py       # OCR 모듈 기본 테스트
├── tools/              # 보조 도구
│   ├── capture_battle_screen.py # 전투 화면 캡처 도구
│   └── find_cost_region.py      # 코스트 영역 좌표 측정 도구
├── config/
│   ├── settings.py              # 전역 설정
│   ├── ocr_regions.py           # OCR 영역 좌표 정의
│   └── skill_settings.py        # 스킬 사용 설정 (좌표, 타이밍)
├── main.py
├── requirements.txt
└── README.md
```

## 아키텍처

### 핵심 컴포넌트

#### 1. Recognition Layer (인식 계층)
**TemplateMatcher** ([src/recognition/template_matcher.py](src/recognition/template_matcher.py))
- pyautogui.locateOnScreen() 래퍼
- 템플릿 탐색 및 대기 기능
- 템플릿 소멸 감지 기능
- 신뢰도 임계값: 0.8 (기본값)

#### 2. Automation Layer (자동화 계층)
**GameController** ([src/automation/game_controller.py](src/automation/game_controller.py))
- 마우스 클릭, 드래그
- 키보드 입력
- 화면 캡처
- 대기 함수

**StageRunner** ([src/automation/stage_runner.py](src/automation/stage_runner.py))
- 전체 스테이지 플로우 오케스트레이션
- 각 Checker 모듈 통합 실행
- 단계별 결과 로깅

#### 3. Verification Layer (검증 계층)
- **MovementChecker**: 발판 이동 검증
- **BattleChecker**: 전투 진입/종료 검증
- **SkillChecker**: 스킬 사용 검증 (OCR 기반 코스트 검증 포함)
- **RewardChecker**: 보상 획득 검증 (현재는 damage_report 검증으로 변경)

#### 4. OCR Layer (OCR 계층)
**OCRReader** ([src/ocr/ocr_reader.py](src/ocr/ocr_reader.py))
- Tesseract OCR 엔진 통합
- 다중 PSM 모드 지원 (7, 8, 6, 13)
- 이미지 전처리 (그레이스케일, 임계값, 노이즈 제거, 스케일링)
- 숫자/텍스트 읽기 전용 메서드
- 코스트 값 읽기 (`read_cost_value`)
- 배치 처리 지원

#### 5. Logging Layer (로깅 계층)
**TestLogger** ([src/logger/test_logger.py](src/logger/test_logger.py))
- 타임스탬프 기반 로그 디렉토리 생성
- 검증 항목별 성공/실패 기록 (JSON)
- 스크린샷 자동 저장

## 실행 시나리오 (Normal 1-4)

### 전체 플로우
```
1. 시작 발판 클릭 → 편성 화면 이동
   ├─ start_tile.png 탐색
   └─ formation_screen.png 출현 대기

2. 출격 버튼 클릭 → 스테이지 맵 이동
   ├─ deploy_button.png 탐색 및 클릭
   └─ stage_map.png 출현 대기

2.5. 임무 개시 버튼 클릭
   └─ mission_start_button.png 탐색 및 클릭

3. 발판 클릭 (적 우선 탐색)
   ├─ enemy_tile.png 탐색 (우선)
   ├─ enemy_tile 없으면 empty_tile.png 탐색
   └─ 발판 클릭

   → 적 발판이었을 경우:
     └─ battle_ui.png 출현 대기 (전투 진입)

   → 빈 발판이었을 경우:
     └─ 3.5단계로

3.5. [빈 발판일 경우만] Phase 종료
   ├─ phase_end_button.png 탐색 및 클릭
   ├─ 3초 대기 (적 이동 시간)
   └─ 적 접근 시 전투 진입 감지

4. 전투 진입 확인
   └─ battle_ui.png 출현 대기 (3/3.5단계에서 확인 안 됐을 경우)

5. 전투 종료 확인
   └─ victory.png 출현 대기 (최대 120초)

6. 전투 결과 확인 및 스테이지 복귀
   ├─ battle_log_button.png 탐색 및 클릭 (통계 버튼)
   ├─ damage_report.png 출현 대기 (데미지 기록 창)
   ├─ 3초 대기 (데미지 확인)
   ├─ damage_report_close_button.png 클릭 (닫기)
   ├─ victory_confirm.png 클릭 (Victory 화면 확인 버튼)
   ├─ rank_reward.png 출현 대기 (랭크 획득 창)
   ├─ rank_reward_confirm_button.png 클릭 (확인)
   └─ stage_map.png 복귀 확인
```

### 조건부 분기 로직
- **적 발판 감지 시**: 즉시 전투 진입 → Phase 종료 스킵
- **빈 발판 감지 시**: 학생 이동 → Phase 종료 버튼 클릭 필요
- **Phase 종료 후 적 접근**: 3초 대기 후 스테이지 맵 소멸 확인 → 전투 진입

## 현재 구현 상태

### ✅ 완료된 항목
1. **기본 인프라**
   - TemplateMatcher (템플릿 매칭 래퍼)
   - GameController (마우스/키보드 제어)
   - TestLogger (JSON 로깅 + 스크린샷)

2. **OCR 시스템 (Phase 2)**
   - OCRReader (Tesseract 통합, 다중 PSM 모드)
   - 이미지 전처리 파이프라인
   - 코스트 값 읽기 (현재 코스트, 스킬 코스트)
   - 좌표 캘리브레이션 도구 (capture, find_cost_region)

3. **검증 모듈**
   - MovementChecker (발판 이동 검증)
   - BattleChecker (전투 진입/종료 검증)
   - SkillChecker (스킬 사용 + OCR 코스트 검증)
   - RewardChecker (보상 획득 검증)

4. **StageRunner 전체 플로우**
   - 단계 1-2.5: 시작 → 편성 → 출격 → 맵 → 임무 개시
   - 단계 3: 발판 클릭 (적/빈 발판 자동 판단)
   - 단계 3.5: Phase 종료 + 적 접근 감지
   - 단계 4: 전투 진입 확인
   - 단계 5: 전투 종료 확인 (Victory)
   - 단계 6: 전투 결과 확인 (통계 → 데미지 기록 → 랭크 획득 → 스테이지 복귀)

5. **테스트 스크립트**
   - test_modules.py: 기본 모듈 동작 테스트
   - test_partial_stage.py: 단계 1-2.5 테스트 (5/5 통과)
   - test_tile_movement.py: 발판 이동 단독 테스트 (신뢰도 0.5 조정)
   - test_battle_result.py: 전투 결과 확인 플로우 테스트 (단계 6)
   - test_ocr_simple.py: OCR 모듈 기본 테스트
   - test_skill_cost_ocr.py: 코스트 OCR 읽기 테스트
   - test_skill_usage.py: 스킬 사용 시스템 통합 테스트

### 🔄 진행 중
- 템플릿 이미지 준비 및 검증
- 전체 플로우 end-to-end 테스트

### ⏳ 미완료
- 전체 플로우 통합 테스트 (main.py 실행)

## 개발 우선순위

### Phase 1 - 핵심 기능 (필수)
1. ✅ 템플릿 매칭 시스템
2. ✅ 발판 이동 (시작 → 편성 → 출격 → 맵 → 임무 개시)
3. ✅ 발판 클릭 (적/빈 발판 자동 판단)
4. ✅ 전투 진입 감지 (Phase 종료 후 적 접근 포함)
5. ✅ 전투 종료 감지 (Victory)
6. ✅ 전투 결과 확인 (통계 → 데미지 기록 → 랭크 획득 → 스테이지 복귀)

### Phase 2 - 스킬 사용 시스템 (완료)
- ✅ OCR 기반 코스트 읽기
  - 현재 코스트 인식 (우측 상단 UI)
  - 스킬 버튼 코스트 인식 (버튼 하단)
- ✅ 스킬 사용 플로우
  - 스킬 버튼 → 화면 중앙 드래그
  - 코스트 소모 검증
  - 코스트 부족 시 스킬 미발동 감지
- ✅ 좌표 캘리브레이션 도구
  - 화면 캡처 도구 (capture_battle_screen.py)
  - 영역 선택 도구 (find_cost_region.py)

### Phase 3 - 기술적 한계 (문서화)
- ⚠️ 실시간 데미지 캡처 (기술적 한계)
- ⚠️ 스킬 쿨다운/대기시간 추적 (현재 미구현)

## 스킬 사용 시스템 (Phase 2)

### 개요
전투 중 스킬 사용을 자동화하고, OCR로 코스트를 검증하는 시스템입니다.

### 시스템 구성

#### 1. 좌표 설정 ([config/skill_settings.py](config/skill_settings.py))
```python
# 2560x1440 해상도 기준

# 스킬 버튼 클릭 위치 (3개 슬롯)
SKILL_BUTTON_SLOT_1 = (1797, 1242)
SKILL_BUTTON_SLOT_2 = (2000, 1240)
SKILL_BUTTON_SLOT_3 = (2200, 1240)

# 스킬 코스트 OCR 영역 (버튼 하단)
SKILL_COST_SLOT_1 = (1768, 1304, 1815, 1350)
SKILL_COST_SLOT_2 = (1973, 1304, 2017, 1350)
SKILL_COST_SLOT_3 = (2174, 1304, 2225, 1350)

# 화면 중앙 (스킬 타겟 위치)
SCREEN_CENTER_X = 1280
SCREEN_CENTER_Y = 720

# 타이밍
TARGET_CLICK_TO_COST_UPDATE_WAIT = 1.0  # 드래그 후 대기
```

#### 2. OCR 영역 설정 ([config/ocr_regions.py](config/ocr_regions.py))
```python
# 현재 코스트 표시 영역 (우측 상단)
BATTLE_COST_VALUE_REGION = (1550, 1300, 1645, 1400)
```

#### 3. 스킬 사용 플로우 ([src/verification/skill_checker.py](src/verification/skill_checker.py))
```python
def use_skill_and_verify(slot_index: int, student_name: str) -> Dict:
    """
    1. 스킬 버튼 코스트 읽기 (OCR)
    2. 현재 코스트 읽기 (사용 전)
    3. 코스트 충분 여부 체크 (부족하면 중단)
    4. 스킬 버튼 → 화면 중앙 드래그 (0.5초)
    5. 1.0초 대기 (코스트 UI 업데이트)
    6. 현재 코스트 읽기 (사용 후)
    7. 코스트 차감 검증: (전 - 후) == 스킬 코스트
    """
```

### 스킬 사용 방식
- **기존 방식 (X)**: 클릭 → 대기 → 클릭
- **현재 방식 (O)**: 스킬 버튼에서 화면 중앙으로 드래그
  - `controller.drag(start, end, duration=0.5)`
  - 게임의 실제 스킬 사용 방식과 동일

### OCR 인식 최적화
- **다중 PSM 모드**: 7, 8, 6, 13 순차 시도
- **전처리 파이프라인**:
  1. 그레이스케일 변환
  2. 임계값 처리 (THRESH_BINARY)
  3. 노이즈 제거 (medianBlur)
  4. 2배 스케일 업 (인식률 향상)
- **숫자 전용 화이트리스트**: `0123456789`

### 좌표 캘리브레이션 도구

#### 화면 캡처 도구
```bash
python tools/capture_battle_screen.py
```
- 5초 카운트다운 후 전투 화면 스크린샷 저장
- 저장 위치: `logs/ocr_calibration/battle_screen_YYYYMMDD_HHMMSS.png`

#### 영역 선택 도구
```bash
python tools/find_cost_region.py
```
- GUI로 코스트 영역 드래그 선택
- 자동으로 좌표 계산 및 출력
- 미리보기 이미지 저장: `cost_region_preview.png`

### 테스트 스크립트

#### 1. OCR 기본 테스트
```bash
python tests/test_ocr_simple.py
```
- OCR 모듈 import 확인
- 의존성 패키지 확인
- 클래스 구조 검증

#### 2. 코스트 OCR 테스트
```bash
python tests/test_skill_cost_ocr.py
```
- OCR 초기화
- 현재 코스트 읽기
- 코스트 검증 로직 시뮬레이션

#### 3. 스킬 사용 시스템 테스트
```bash
python tests/test_skill_usage.py
```
- 스킬 버튼 코스트 읽기 (3개 슬롯)
- 단일 스킬 사용 및 검증
- 다중 스킬 사용 (3개 연속)
- 코스트 부족 시나리오

### 제약사항 및 고려사항

#### 해상도 의존성
- **기준 해상도**: 2560x1440
- 다른 해상도 사용 시 좌표 재측정 필요
- 캘리브레이션 도구로 좌표 재설정 가능

#### OCR 정확도
- **환경**: Tesseract 필수 설치
- **언어팩**: eng (영어) 필수
- **인식률**: 전처리 및 다중 PSM 모드로 최적화

#### 게임 상태
- 전투 화면에서만 동작
- 스킬 애니메이션 중 UI 가려짐 가능
- 네트워크 지연 시 대기 시간 부족 가능

#### 미구현 기능
- 스킬 쿨다운 추적 (현재 버튼 상태 확인 안 함)
- 스킬 대기 시간 (즉시 사용 가능 여부만 확인)
- 스킬 버튼 페이징 (6개 학생 중 3개씩 표시됨)

### 외부 참조

#### Tesseract OCR
- **공식 위키**: https://github.com/UB-Mannheim/tesseract/wiki
- **Windows 설치**: UB Mannheim 빌드 사용
- **기본 경로**: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **자동 인식**: `ocr_reader.py`에서 경로 자동 탐지

#### PSM (Page Segmentation Mode)
- **PSM 7**: 단일 라인 텍스트
- **PSM 8**: 단일 단어
- **PSM 6**: 단일 블록 텍스트
- **PSM 13**: Raw line (전처리 없음)
- 참고: https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html

## 중요 개발 노트

### 템플릿 매칭 최적화
- **신뢰도**: 0.8 (기본값, config/settings.py에서 조정 가능)
- **재시도 로직**: TemplateMatcher에 내장
- **템플릿 이미지**: assets/templates/ 하위에 카테고리별 분류

### 타이밍 관리
- 화면 전환 대기: 2초 (WAIT_SCREEN_TRANSITION)
- 전투 로딩 대기: 10-15초
- 전투 종료 대기: 최대 120초
- 템플릿 탐색 간격: 0.5초 (기본)

### 테스트 전략
- **단계별 테스트**: 각 단계를 독립적으로 테스트
- **템플릿 준비 확인**: 테스트 시작 전 필수 템플릿 존재 확인
- **카운트다운**: 사용자가 게임 화면 준비할 시간 제공 (10초)
- **스크린샷**: 각 단계마다 자동 저장
- **로그**: JSON 형식으로 검증 결과 기록

### 에러 처리
- 템플릿 미발견 시 명확한 에러 메시지
- 실패 시 현재 화면 스크린샷 저장
- 각 단계 실패 시 즉시 중단 (안전성)

## 템플릿 이미지 관리

### 필수 템플릿 목록
**buttons/**
- ✅ deploy_button.png (출격 버튼)
- ✅ mission_start_button.png (임무 개시 버튼)
- ✅ phase_end_button.png (Phase 종료 버튼)
- ✅ battle_log_button.png (통계 버튼)
- ✅ damage_report_close_button.png (데미지 기록 닫기 버튼)
- ✅ victory_confirm.png (Victory 확인 버튼)
- ✅ rank_reward_confirm_button.png (랭크 획득 확인 버튼)

**icons/**
- ✅ start_tile.png (시작 발판)
- ✅ enemy_tile.png (적 있는 발판, 신뢰도 0.5)
- ✅ empty_tile.png (빈 발판, 신뢰도 0.5)

**ui/**
- ✅ formation_screen.png (편성 화면)
- ✅ stage_map.png (스테이지 맵)
- ✅ stage_map_2.png (스테이지 맵 복귀 확인용)
- ✅ battle_ui.png (전투 UI)
- ✅ victory.png (승리 화면)
- ✅ damage_report.png (데미지 기록 창)
- ✅ rank_reward.png (랭크 획득 창)

### 템플릿 캡처 가이드
- 게임 해상도 고정
- UI 변동이 적은 영역 선택
- 너무 크거나 작지 않게 (적절한 크기)
- 애니메이션 없는 상태에서 캡처

## 알려진 제약사항

### 일반 제약사항
1. **화면 인식 기반**: 게임 화면이 가려지거나 최소화되면 작동 불가
2. **해상도 의존**: 템플릿 이미지 및 OCR 좌표는 2560x1440 기준 (재설정 필요 시)
3. **동적 화면**: 전투 중 화면 움직임으로 인한 템플릿 매칭 실패 가능
4. **이펙트 간섭**: 스킬 이펙트가 UI를 가려 인식 방해
5. **타이밍 변동**: 네트워크 지연 시 대기 시간 부족할 수 있음

### OCR 관련 제약사항
6. **Tesseract 의존**: 외부 프로그램 설치 필수
7. **언어팩**: 영어(eng) 언어팩 필수 설치
8. **OCR 정확도**: 스킬 애니메이션/이펙트 중 인식률 저하 가능
9. **좌표 고정**: 해상도 변경 시 OCR 영역 재설정 필요
10. **UI 변동**: 게임 업데이트로 UI 위치 변경 시 좌표 재측정 필요

### 스킬 시스템 제약사항
11. **스킬 쿨다운 미추적**: 버튼 상태 확인 없음 (즉시 사용 가능 가정)
12. **스킬 대기시간 미구현**: 스킬 사용 후 대기 시간 고려 안 함
13. **버튼 페이징 미지원**: 6개 학생 중 3개씩 표시되는 페이징 로직 없음

## 일정
- **마감일**: 2026년 1월 13일 (월요일)
- **현재 상태**: Phase 1 완료, Phase 2 완료 (스킬 사용 시스템)
- **다음 단계**: 전체 플로우 통합 테스트 및 최종 검증

## 개발 히스토리

### Phase 2: 스킬 사용 시스템 (2026-01-07)
**브랜치**: `feature/skill-usage-system`

**구현 내용**:
- Tesseract OCR 통합 (다중 PSM 모드)
- 스킬 버튼 코스트 읽기 (3개 슬롯)
- 현재 코스트 읽기 (우측 상단 UI)
- 스킬 사용 플로우 (드래그 방식)
- 코스트 소모 검증
- 좌표 캘리브레이션 도구 2종

**주요 변경사항**:
- 클릭 → 클릭 방식에서 드래그 방식으로 변경
- 버튼 클릭 후 대기 시간: 0.5초 → 1.0초 → 2.0초 → 드래그로 대체
- 드래그 duration: 0.5초
- 코스트 업데이트 대기: 1.0초

**커밋**:
1. `b695fef` - feat: 스킬 사용 시스템 구현 (OCR 기반 코스트 검증)
2. `83d4fe1` - fix: GameController.click()에 wait_after 파라미터 제거
3. `a66e044` - config: 스킬 버튼 클릭 후 대기 시간 증가 (0.5초 → 1.0초)
4. `8966c2c` - config: 스킬 버튼 클릭 후 대기 시간 증가 (1초 → 2초)
5. `1c4f969` - refactor: 스킬 사용 방식을 클릭→클릭에서 드래그로 변경

**테스트 결과**:
- OCR 초기화: ✓
- 코스트 읽기: ✓
- 스킬 버튼 코스트 읽기: ✓
- 스킬 사용 플로우: 테스트 진행 중
