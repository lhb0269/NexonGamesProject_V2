# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고하는 가이드를 제공합니다.

## 프로젝트 개요

**블루 아카이브 자동화 테스트 프로젝트** - 블루 아카이브 스팀 버전 Normal 1-4 스테이지 자동 플레이 및 검증 시스템

### 프로젝트 목표
- Live 빌드에서 화면 인식 기반 자동화 구현
- 스테이지 클리어 과정의 주요 항목 검증
- 검증 결과 로그 생성

### 기술 스택
- **언어**: Python 3.x
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
pip install pyautogui
pip install pillow  # 이미지 처리
pip install opencv-python  # pyautogui 의존성
```

### 프로젝트 구조
```
NexonGamesProject_V2/
├── src/
│   ├── automation/     # 자동화 로직
│   │   ├── game_controller.py    # 게임 제어
│   │   └── stage_runner.py       # 스테이지 실행
│   ├── recognition/    # 이미지 인식
│   │   ├── template_matcher.py   # 템플릿 매칭
│   │   └── ui_detector.py        # UI 요소 감지
│   ├── verification/   # 검증 로직
│   │   ├── movement_checker.py   # 이동 검증
│   │   ├── battle_checker.py     # 전투 검증
│   │   └── reward_checker.py     # 보상 검증
│   └── logger/         # 결과 기록
│       └── test_logger.py
├── assets/
│   └── templates/      # UI 템플릿 이미지
│       ├── buttons/    # 버튼 이미지
│       ├── icons/      # 아이콘 이미지
│       └── ui/         # UI 요소
├── logs/               # 테스트 결과 로그
├── tests/              # 단위 테스트
├── config/             # 설정 파일
│   └── settings.py
├── main.py             # 메인 실행 파일
├── requirements.txt
└── README.md
```

## 아키텍처

### 핵심 컴포넌트

#### 1. Recognition Layer (인식 계층)
- **TemplateMatcher**: pyautogui.locateOnScreen() 래퍼
  - UI 요소 위치 탐색
  - 신뢰도 임계값 설정
  - 재시도 로직 포함

- **UIDetector**: 특정 UI 상태 감지
  - 화면 전환 감지
  - 버튼 활성화 상태 확인

#### 2. Automation Layer (자동화 계층)
- **GameController**: 기본 게임 조작
  - 클릭, 드래그, 키 입력
  - 대기 시간 관리
  - 안전 장치 (게임 응답 확인)

- **StageRunner**: 스테이지 실행 흐름
  - 발판 이동
  - 전투 시작
  - 스킬 사용
  - 보상 수령

#### 3. Verification Layer (검증 계층)
- **MovementChecker**: 발판 이동 검증
- **BattleChecker**: 전투 진입/진행 검증
- **SkillChecker**: 스킬 사용 검증
- **RewardChecker**: 보상 획득 검증

#### 4. Logging Layer (로깅 계층)
- **TestLogger**: 검증 결과 기록
  - 타임스탬프
  - 검증 항목별 성공/실패
  - 스크린샷 첨부

### 실행 흐름
```
main.py
  └─> StageRunner.run()
       ├─> GameController.navigate_to_stage()
       ├─> MovementChecker.verify_movement()
       ├─> BattleChecker.verify_battle_entry()
       ├─> GameController.use_skills()
       ├─> SkillChecker.verify_skill_usage()
       ├─> BattleChecker.wait_battle_end()
       └─> RewardChecker.verify_rewards()
```

## 개발 우선순위

### Phase 1 - 핵심 기능 (필수 구현)
1. ✅ 템플릿 매칭 기본 시스템
2. ✅ 발판 이동 감지
3. ✅ 전투 진입 감지
4. ✅ 보상 획득 감지
5. ⚠️ EX 스킬 사용 시도 (간접 확인)

### Phase 2 - 도전 과제 (시간 허용 시)
6. ⚠️ 코스트 소모 확인 (OCR 활용)

### Phase 3 - 기술적 한계 (문서화)
7. ❌ 학생별 데미지 기록 (시도 + 한계 분석)

## 중요 개발 노트

### 템플릿 매칭 최적화
- 신뢰도(confidence) 임계값: 0.8 이상 권장
- 그레이스케일 변환으로 성능 향상 가능
- 전투 중에는 매칭 실패율 높음 → 재시도 로직 필수

### 타이밍 관리
- 화면 전환 대기: 1-2초
- 애니메이션 대기: 0.5-1초
- 전투 로딩: 3-5초
- 스킬 쿨다운 확인: 0.3초 간격

### 에러 처리
- 템플릿을 찾지 못한 경우 재시도 (최대 3회)
- 타임아웃 설정 (각 작업당 최대 30초)
- 예상치 못한 팝업 처리 로직

### 테스트 전략
- 각 검증 항목을 독립적으로 테스트
- 실패 시 스크린샷 자동 저장
- 로그에 타임스탬프 및 상세 정보 기록

## 알려진 제약사항

1. **동적 화면**: 전투 중 화면이 계속 움직여 템플릿 매칭 정확도 하락
2. **이펙트 간섭**: 스킬 이펙트가 UI를 가려 인식 방해
3. **OCR 한계**: 특수 폰트 및 애니메이션으로 인한 정확도 저하
4. **실시간 데이터**: 빠르게 변화하는 데미지 숫자 캡처 불가능

## 일정
- **마감일**: 2026년 1월 13일 (월요일)
- **현재 상태**: 프로젝트 구조 설계 완료
- **다음 단계**: 기본 템플릿 매칭 시스템 구현
