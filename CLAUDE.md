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
pip install pyautogui pillow opencv-python
```

### 프로젝트 구조
```
NexonGamesProject_V2/
├── src/
│   ├── automation/     # 자동화 로직
│   │   ├── game_controller.py    # 게임 제어 (마우스/키보드)
│   │   └── stage_runner.py       # 스테이지 전체 흐름 실행
│   ├── recognition/    # 이미지 인식
│   │   └── template_matcher.py   # pyautogui 템플릿 매칭 래퍼
│   ├── verification/   # 검증 로직
│   │   ├── movement_checker.py   # 이동 검증
│   │   ├── battle_checker.py     # 전투 검증
│   │   ├── skill_checker.py      # 스킬 검증
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
│   └── test_tile_movement.py    # 발판 이동 테스트
├── config/
│   └── settings.py     # 전역 설정
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
- **SkillChecker**: 스킬 사용 검증 (사용 안 함)
- **RewardChecker**: 보상 획득 검증 (현재는 damage_report 검증으로 변경)

#### 4. Logging Layer (로깅 계층)
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
   └─ phase_end_button.png 탐색 및 클릭

4. 전투 진입 확인
   └─ battle_ui.png 출현 대기 (3단계에서 확인 안 됐을 경우)

5. 전투 종료 확인
   └─ victory.png 출현 대기 (최대 120초)

6. 통계 버튼 클릭 → 데미지 기록 확인
   ├─ battle_log_button.png 탐색 및 클릭
   └─ damage_report.png 출현 대기
```

### 조건부 분기 로직
- **적 발판 감지 시**: 즉시 전투 진입 → Phase 종료 스킵
- **빈 발판 감지 시**: 학생 이동 → Phase 종료 버튼 클릭 필요

## 현재 구현 상태

### ✅ 완료된 항목
1. **기본 인프라**
   - TemplateMatcher (템플릿 매칭 래퍼)
   - GameController (마우스/키보드 제어)
   - TestLogger (JSON 로깅 + 스크린샷)

2. **검증 모듈**
   - MovementChecker
   - BattleChecker
   - SkillChecker (구현됨, 현재 시나리오에서 미사용)
   - RewardChecker

3. **StageRunner**
   - 전체 플로우 통합 완료
   - 조건부 분기 로직 구현 (적 유무 자동 판단)

4. **테스트 스크립트**
   - test_modules.py: 기본 모듈 동작 테스트
   - test_partial_stage.py: 시작 → 편성 → 출격 → 맵 → 임무 개시 (5/5 통과)
   - test_tile_movement.py: 발판 이동 단독 테스트 (작성 완료)

### 🔄 진행 중
- 발판 이동 테스트 (템플릿 이미지 조정 필요)

### ⏳ 미완료
- 전투 종료 후 단계 (Victory → 통계 → 데미지 기록)
- 전체 플로우 end-to-end 테스트

## 개발 우선순위

### Phase 1 - 핵심 기능 (필수)
1. ✅ 템플릿 매칭 시스템
2. ✅ 발판 이동 (시작 → 편성 → 출격 → 맵 → 임무 개시)
3. 🔄 발판 클릭 (적/빈 발판 자동 판단)
4. ⏳ 전투 진입 감지
5. ⏳ 전투 종료 감지 (Victory)
6. ⏳ 데미지 기록 확인 (통계 버튼)

### Phase 2 - 추가 기능 (선택)
- ❌ 스킬 사용 (현재 시나리오에서 제외)
- ❌ 코스트 소모 확인 (현재 시나리오에서 제외)

### Phase 3 - 기술적 한계 (문서화)
- ⚠️ 실시간 데미지 캡처 (기술적 한계)

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
- deploy_button.png (출격 버튼)
- mission_start_button.png (임무 개시 버튼)
- phase_end_button.png (Phase 종료 버튼)
- battle_log_button.png (통계 버튼) - 미준비

**icons/**
- start_tile.png (시작 발판)
- enemy_tile.png (적 있는 발판) - 조정 필요
- empty_tile.png (빈 발판) - 조정 필요

**ui/**
- formation_screen.png (편성 화면)
- stage_map.png (스테이지 맵)
- battle_ui.png (전투 UI) - 검증 필요
- victory.png (승리 화면) - 미준비
- damage_report.png (데미지 기록 창) - 미준비

### 템플릿 캡처 가이드
- 게임 해상도 고정
- UI 변동이 적은 영역 선택
- 너무 크거나 작지 않게 (적절한 크기)
- 애니메이션 없는 상태에서 캡처

## 알려진 제약사항

1. **화면 인식 기반**: 게임 화면이 가려지거나 최소화되면 작동 불가
2. **해상도 의존**: 템플릿 이미지는 특정 해상도 기준 (재캡처 필요 시)
3. **동적 화면**: 전투 중 화면 움직임으로 인한 템플릿 매칭 실패 가능
4. **이펙트 간섭**: 스킬 이펙트가 UI를 가려 인식 방해
5. **타이밍 변동**: 네트워크 지연 시 대기 시간 부족할 수 있음

## 일정
- **마감일**: 2026년 1월 13일 (월요일)
- **현재 상태**: Phase 1 진행 중 (발판 이동 테스트)
- **다음 단계**: 발판 이동 완료 → 전투 종료 → 데미지 기록
