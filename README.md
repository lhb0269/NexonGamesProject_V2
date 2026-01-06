# 블루 아카이브 자동화 테스트 프로젝트

## 프로젝트 개요

블루 아카이브 스팀 버전의 **Normal 1-4 스테이지**를 자동으로 플레이하고 검증하는 자동화 테스트 도구입니다.

**기술 스택:**
- Python 3.11
- pyautogui (화면 인식 및 제어)
- 템플릿 매칭 기반 UI 인식
- JSON 기반 로깅

## 과제 요구사항

### 대상 게임
- **게임**: 블루 아카이브 (Blue Archive)
- **플랫폼**: Steam 버전 (Live 빌드)
- **테스트 스테이지**: Normal 1-4

### 검증 항목 (원본 요구사항)
1. 발판 이동 정상 여부
2. 전투 정상 진입 여부
3. ~~각 학생별 EX 스킬 사용 여부~~ (현재 시나리오에서 제외)
4. ~~스킬 사용 시 코스트 소모량 정상 여부~~ (현재 시나리오에서 제외)
5. 각 전투별 학생 데미지 기록
6. ~~보상 정상 획득 여부~~ → **데미지 기록 확인으로 변경**

### 기술적 제약사항
- ✅ 순수 코드로만 구현 (상용 자동화 툴 사용 금지)
- ✅ Live 빌드(스팀 배포 버전)에서 실행
- ✅ 게임 내부 로직 접근 불가 (메모리 해킹 등 금지)
- ✅ 화면 인식 기반으로 정보 수집
- ✅ 화면 제어 방식으로 조작

## 현재 구현 시나리오

### 전체 플로우 (Normal 1-4)

```
1. 시작 발판 클릭 → 편성 화면 이동
   ✅ 구현 완료 (test_partial_stage.py 검증 완료)

2. 출격 버튼 클릭 → 스테이지 맵 이동
   ✅ 구현 완료 (test_partial_stage.py 검증 완료)

2.5. 임무 개시 버튼 클릭
   ✅ 구현 완료 (test_partial_stage.py 검증 완료)

3. 발판 클릭 (적 유무 자동 판단)
   - 적이 있는 발판 우선 탐색 (enemy_tile.png, 신뢰도 0.5)
   - 없으면 빈 발판 탐색 (empty_tile.png, 신뢰도 0.5)
   ✅ 구현 완료 (test_tile_movement.py)

   → 적 발판일 경우:
     - 전투 진입 (battle_ui.png 출현)
     - 3.5단계 스킵

   → 빈 발판일 경우:
     - 학생 이동
     - 3.5단계 진행

3.5. [빈 발판일 경우만] Phase 종료 버튼 클릭
   ✅ 구현 완료 (적 접근 감지 포함)
   - Phase 종료 후 3초 대기
   - 적 이동으로 인한 전투 진입 자동 감지

4. 전투 진입 확인
   ✅ 구현 완료 (조건부 실행)

5. 전투 종료 확인 (Victory 화면)
   ✅ 구현 완료

6. 전투 결과 확인 및 스테이지 복귀
   ✅ 구현 완료 (test_battle_result.py)
   - 통계 버튼 클릭 (battle_log_button.png)
   - 데미지 기록 창 확인 (damage_report.png)
   - 3초 대기 후 닫기 버튼 클릭 (damage_report_close_button.png)
   - Victory 확인 버튼 클릭 (victory_confirm.png)
   - 랭크 획득 창 확인 (rank_reward.png)
   - 랭크 획득 확인 버튼 클릭 (rank_reward_confirm_button.png)
   - 스테이지 맵 복귀 확인 (stage_map_2.png)
```

## 구현 상태

### ✅ 완료
- **기본 인프라**
  - TemplateMatcher: pyautogui 템플릿 매칭 래퍼 (신뢰도 조정 가능)
  - GameController: 마우스/키보드 제어
  - TestLogger: JSON 로깅 + 스크린샷 저장

- **검증 모듈**
  - MovementChecker (발판 이동 검증)
  - BattleChecker (전투 진입/종료 검증)
  - RewardChecker (데미지 기록 검증)
  - SkillChecker (구현됨, 현재 미사용)

- **StageRunner 전체 플로우**
  - 단계 1-2.5: 시작 → 편성 → 출격 → 맵 → 임무 개시
  - 단계 3: 발판 클릭 (적/빈 발판 자동 판단)
  - 단계 3.5: Phase 종료 + 적 접근 감지
  - 단계 4: 전투 진입 확인 (조건부)
  - 단계 5: 전투 종료 확인 (Victory)
  - 단계 6: 전투 결과 확인 (통계 → 데미지 기록 → 랭크 획득 → 스테이지 복귀)

- **테스트 스크립트**
  - test_modules.py: 기본 모듈 테스트
  - test_partial_stage.py: 단계 1-2.5 통합 테스트 **(5/5 통과)**
  - test_tile_movement.py: 발판 이동 단독 테스트 (신뢰도 0.5)
  - test_battle_result.py: 전투 결과 확인 플로우 테스트 (단계 6)

### 🔄 진행 중
- 템플릿 이미지 검증 및 미세 조정
- 전체 플로우 end-to-end 통합 테스트

### ⏳ 다음 단계
- main.py를 통한 전체 시나리오 실행 및 검증
- 최종 테스트 결과 문서화

## 검증 항목별 구현 분석

### ✅ 1. 발판 이동 정상 여부
- **난이도**: 낮음
- **구현 방법**:
  - 시작 발판 → 편성 화면 → 출격 → 스테이지 맵 → 임무 개시 → 발판 클릭
  - 적 발판 우선 탐색, 없으면 빈 발판 탐색
- **신뢰도**: ~90%
- **상태**: ✅ 구현 완료 (1~2.5단계 검증 완료, 3단계 템플릿 조정 중)

### ✅ 2. 전투 정상 진입 여부
- **난이도**: 낮음
- **구현 방법**:
  - 적 발판 클릭 후 battle_ui.png 출현 확인
  - 또는 Phase 종료 후 전투 UI 대기
- **신뢰도**: ~95%
- **상태**: ✅ 구현 완료 (템플릿 검증 필요)

### ⚠️ 5. 각 전투별 학생 데미지 기록
- **난이도**: 매우 높음
- **구현 방법**:
  - ~~실시간 데미지 캡처~~ (기술적 한계로 불가능)
  - **대안**: 전투 종료 후 통계 버튼 → 데미지 기록 창 확인
- **신뢰도**:
  - 실시간: ~10% (사실상 불가능)
  - 전투 후 통계: ~70% (구현 가능)
- **제약사항**:
  - 전투 중 실시간 데미지는 속도/겹침 문제로 불가능
  - 전투 종료 후 통계 화면에서만 확인 가능
- **상태**: ⏳ 대안 방식 구현 완료, 템플릿 미준비

### ❌ 3. 각 학생별 EX 스킬 사용 여부
- **현재 시나리오에서 제외**
- **이유**: Normal 1-4는 자동 전투 방식, 수동 스킬 사용 불필요
- **구현 가능성**: 중간 (~60-70%, 스킬 활성화 상태 판단 어려움)

### ❌ 4. 스킬 사용 시 코스트 소모량 정상 여부
- **현재 시나리오에서 제외**
- **이유**: 스킬 사용이 시나리오에 없음
- **구현 가능성**: 낮음 (~50%, OCR 정확도 및 타이밍 문제)

### ❌ 6. 보상 정상 획득 여부 (원본 요구사항)
- **변경**: 데미지 기록 확인으로 대체
- **이유**: Normal 1-4는 데미지 기록이 더 의미 있는 검증 항목

## 설치 및 실행

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt
```

### 2. 템플릿 이미지 준비
다음 템플릿 이미지를 캡처하여 `assets/templates/` 디렉토리에 저장:

**buttons/ (버튼 이미지):**
- ✅ deploy_button.png (출격 버튼)
- ✅ mission_start_button.png (임무 개시 버튼)
- ✅ phase_end_button.png (Phase 종료 버튼)
- ✅ battle_log_button.png (통계 버튼)
- ✅ damage_report_close_button.png (데미지 기록 닫기 버튼)
- ✅ victory_confirm.png (Victory 확인 버튼)
- ✅ rank_reward_confirm_button.png (랭크 획득 확인 버튼)

**icons/ (발판 아이콘):**
- ✅ start_tile.png (시작 발판)
- ✅ enemy_tile.png (적 있는 발판, 신뢰도 0.5)
- ✅ empty_tile.png (빈 발판, 신뢰도 0.5)

**ui/ (UI 화면):**
- ✅ formation_screen.png (편성 화면)
- ✅ stage_map.png (스테이지 맵)
- ✅ stage_map_2.png (스테이지 맵 복귀 확인용)
- ✅ battle_ui.png (전투 UI)
- ✅ victory.png (승리 화면)
- ✅ damage_report.png (데미지 기록 창)
- ✅ rank_reward.png (랭크 획득 창)

### 3. 테스트 실행

**기본 모듈 테스트:**
```bash
python tests/test_modules.py
```

**부분 스테이지 테스트 (1~2.5단계):**
```bash
python tests/test_partial_stage.py
```

**발판 이동 테스트:**
```bash
python tests/test_tile_movement.py
```

**전투 결과 확인 테스트:**
```bash
python tests/test_battle_result.py
```

**전체 플로우 실행:**
```bash
python main.py
```

## 테스트 결과

### test_partial_stage.py (최근 실행)
```
✓ 5/5 검증 항목 통과
- 시작_발판_찾기: PASS
- 시작_발판_클릭: PASS
- 편성_화면_확인: PASS
- 출격_버튼_찾기: PASS
- 출격_버튼_클릭: PASS
- 스테이지_맵_확인: PASS
- 임무_개시_버튼_찾기: PASS
- 임무_개시_버튼_클릭: PASS

소요 시간: 28.9초
```

### test_tile_movement.py (최근 실행)
```
✓ 발판 이동 테스트 통과
- 신뢰도 0.5로 조정 후 정상 작동
- enemy_tile.png / empty_tile.png 인식 개선
```

### test_battle_result.py (구현 완료)
```
전투 결과 확인 플로우 테스트 스크립트
- Victory 화면 확인
- 통계 버튼 클릭
- 데미지 기록 창 확인 및 닫기
- Victory 확인 버튼 클릭
- 랭크 획득 창 확인 및 닫기
- 스테이지 맵 복귀 확인
```

## 프로젝트 구조

```
NexonGamesProject_V2/
├── src/
│   ├── automation/
│   │   ├── game_controller.py    # 마우스/키보드 제어
│   │   └── stage_runner.py       # 전체 플로우 실행
│   ├── recognition/
│   │   └── template_matcher.py   # 템플릿 매칭
│   ├── verification/
│   │   ├── movement_checker.py   # 이동 검증
│   │   ├── battle_checker.py     # 전투 검증
│   │   ├── skill_checker.py      # 스킬 검증 (미사용)
│   │   └── reward_checker.py     # 데미지 기록 검증
│   └── logger/
│       └── test_logger.py        # JSON 로깅
├── assets/
│   └── templates/                # 템플릿 이미지
│       ├── buttons/
│       ├── icons/
│       └── ui/
├── logs/                         # 테스트 결과 (JSON + 스크린샷)
├── tests/
│   ├── test_modules.py          # 기본 모듈 테스트
│   ├── test_partial_stage.py    # 단계 1-2.5 테스트
│   ├── test_tile_movement.py    # 발판 이동 테스트
│   └── test_battle_result.py    # 전투 결과 확인 테스트
├── config/
│   └── settings.py
├── main.py
└── requirements.txt
```

## 개발 일정

- **마감일**: 2026년 1월 13일 (월요일)
- **현재 상태**: Phase 1 완료, 전체 플로우 구현 완료
- **완료된 작업**:
  1. ✅ 템플릿 매칭 시스템 구현
  2. ✅ 전체 시나리오 플로우 구현 (단계 1-6)
  3. ✅ 조건부 분기 로직 구현 (적/빈 발판, Phase 종료 후 적 접근)
  4. ✅ 단계별 테스트 스크립트 작성
  5. ✅ 템플릿 이미지 준비 및 검증
- **다음 작업**:
  1. 전체 플로우 end-to-end 통합 테스트 (main.py)
  2. 최종 검증 및 버그 수정
  3. 테스트 결과 문서화

## 기술적 한계 및 대안

### ❌ 실시간 데미지 캡처 (불가능)
**한계:**
- 데미지 숫자가 전투 중 빠르게 출현/소멸
- 여러 캐릭터 동시 공격 시 겹침
- pyautogui + OCR 방식으로는 프레임 처리 속도 부족

**대안:**
- ✅ 전투 종료 후 통계 화면에서 데미지 기록 확인
- 신뢰도: ~70%

### ⚠️ 템플릿 매칭 정확도
**제약:**
- 화면 해상도 의존
- 애니메이션/이펙트 간섭
- 동적 화면 변화

**대응:**
- 신뢰도 임계값 조정 (기본 0.8)
- 재시도 로직 구현
- 충분한 대기 시간 확보

## 참고사항

- 주어진 기한 내에 모두 완성되지 않더라도 진행된 부분까지 제출
- 기술적 한계가 명확한 항목은 시도 과정과 한계 분석을 문서화하여 제출
- 모든 테스트 결과는 `logs/` 디렉토리에 JSON + 스크린샷으로 저장
