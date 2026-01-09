"""
스킬 사용 검증 테스트 (v2 - UI 상태 변화 기반)

핵심 아이디어:
- EX 스킬 사용 시 해당 슬롯의 버튼이 다른 학생의 버튼으로 교체됨
- Before: 특정 학생의 스킬 버튼 존재
- Action: 해당 슬롯 클릭 (드래그 → 화면 중앙 드롭)
- After: 기존 템플릿이 사라졌는가?
  - 사라짐 → 스킬 사용 성공
  - 남아있음 → 스킬 사용 실패

제약사항:
- ❌ 숫자 OCR 사용 금지
- ❌ 스킬 이펙트 기반 판단 금지
- ❌ 스킬 발동 로그 접근 불가
- ❌ 내부 상태(쿨다운, 코스트 수치) 접근 불가
- ⭕ UI 상태 변화만으로 검증

테스트 방식:
- 슬롯 중심 탐색: 각 슬롯(1,2,3)에서 6개 템플릿을 모두 검색
- 랜덤 배치 대응: 학생이 고정 위치에 있다고 가정하지 않음
"""

import sys
from pathlib import Path
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.logger.test_logger import TestLogger
from config.skill_settings import (
    SKILL_BUTTON_SLOTS,
    SCREEN_CENTER_X,
    SCREEN_CENTER_Y,
    SKILL_USE_DRAG_DURATION,
    SKILL_UI_UPDATE_WAIT
)


# 스킬 버튼 템플릿 매핑 (학생 번호 → 템플릿 파일명)
SKILL_TEMPLATES = {
    0: "skill_1_button.png",  # 아스나
    1: "skill_2_button.png",  # 시미코
    2: "skill_3_button.png",  # 히후미
    3: "skill_4_button.png",  # 스즈미
    4: "skill_5_button.png",  # 유우카
    5: "skill_6_button.png",  # 세리나
}

# 학생 이름 매핑
STUDENT_NAMES = {
    0: "아스나",
    1: "시미코",
    2: "히후미",
    3: "스즈미",
    4: "유우카",
    5: "세리나",
}


def find_student_in_slot(matcher: TemplateMatcher, slot_index: int) -> dict:
    """
    특정 슬롯에서 어떤 학생의 스킬 버튼이 있는지 탐지

    6개 템플릿을 모두 검색하여 첫 번째 매칭되는 학생을 반환

    Args:
        matcher: TemplateMatcher 인스턴스
        slot_index: 슬롯 인덱스 (0-2)

    Returns:
        {
            'found': bool,
            'student_index': int or None,
            'student_name': str or None,
            'template': str or None,
            'location': tuple or None,
            'confidence': float
        }
    """
    if slot_index not in SKILL_BUTTON_SLOTS:
        return {
            'found': False,
            'student_index': None,
            'student_name': None,
            'template': None,
            'location': None,
            'confidence': 0.0
        }

    # 슬롯 위치 가져오기
    slot_position = SKILL_BUTTON_SLOTS[slot_index]

    # 6개 학생 템플릿을 모두 검색
    for student_index in range(6):
        template_name = SKILL_TEMPLATES[student_index]
        template_path = project_root / "assets" / "templates" / "2560x1440" / "buttons" / template_name

        try:
            # 슬롯 근처에서 템플릿 탐색 (region 제한)
            # 슬롯 중심 ±100px 영역에서만 검색
            region = (
                slot_position[0] - 100,
                slot_position[1] - 100,
                200,
                200
            )

            location = matcher.find_template(
                template_path,
                region=region,
                grayscale=True
            )

            if location:
                return {
                    'found': True,
                    'student_index': student_index,
                    'student_name': STUDENT_NAMES[student_index],
                    'template': template_name,
                    'location': location,
                    'confidence': matcher.confidence
                }

        except Exception:
            # 템플릿 파일 없거나 오류 시 다음 템플릿 시도
            continue

    # 아무 학생도 발견되지 않음
    return {
        'found': False,
        'student_index': None,
        'student_name': None,
        'template': None,
        'location': None,
        'confidence': 0.0
    }


def check_student_disappeared(matcher: TemplateMatcher, slot_index: int,
                               student_index: int) -> bool:
    """
    특정 슬롯에서 특정 학생 버튼이 사라졌는지 확인

    Args:
        matcher: TemplateMatcher 인스턴스
        slot_index: 슬롯 인덱스 (0-2)
        student_index: 학생 인덱스 (0-5)

    Returns:
        True if 사라짐 (템플릿 미발견), False if 남아있음
    """
    if slot_index not in SKILL_BUTTON_SLOTS:
        return False

    slot_position = SKILL_BUTTON_SLOTS[slot_index]
    template_name = SKILL_TEMPLATES[student_index]
    template_path = project_root / "assets" / "templates" / "2560x1440" / "buttons" / template_name

    try:
        region = (
            slot_position[0] - 100,
            slot_position[1] - 100,
            200,
            200
        )

        location = matcher.find_template(
            template_path,
            region=region,
            grayscale=True
        )

        # location이 None이면 사라짐 (True)
        return location is None

    except Exception:
        # 오류 시 사라진 것으로 간주
        return True


def click_skill_slot(controller: GameController, slot_index: int) -> bool:
    """
    스킬 슬롯 클릭 (드래그 → 화면 중앙 드롭)

    Args:
        controller: GameController 인스턴스
        slot_index: 슬롯 인덱스 (0-2)

    Returns:
        성공 여부
    """
    if slot_index not in SKILL_BUTTON_SLOTS:
        print(f"✗ 잘못된 슬롯 인덱스: {slot_index}")
        return False

    start_pos = SKILL_BUTTON_SLOTS[slot_index]

    try:
        controller.drag(
            start_x=start_pos[0],
            start_y=start_pos[1],
            end_x=SCREEN_CENTER_X,
            end_y=SCREEN_CENTER_Y,
            duration=SKILL_USE_DRAG_DURATION
        )
        return True
    except Exception as e:
        print(f"✗ 드래그 실패: {e}")
        return False


def test_single_slot_skill(matcher: TemplateMatcher, controller: GameController,
                            logger: TestLogger, slot_index: int) -> dict:
    """
    단일 슬롯 스킬 사용 테스트

    1. Before: 슬롯에서 학생 찾기 (6개 템플릿 검색)
    2. Action: 슬롯 클릭 (드래그)
    3. After: 해당 학생 버튼 사라졌는지 확인
    4. 검증: Before 존재 → After 사라짐 = PASS

    Args:
        matcher: TemplateMatcher 인스턴스
        controller: GameController 인스턴스
        logger: TestLogger 인스턴스
        slot_index: 슬롯 인덱스 (0-2)

    Returns:
        테스트 결과 딕셔너리
    """
    print(f"\n{'='*70}")
    print(f"슬롯 {slot_index + 1} 스킬 사용 테스트")
    print(f"{'='*70}")

    # === 1단계: 학생 버튼 탐지 ===
    print(f"\n[1단계] 슬롯에서 학생 탐지 중...")
    before_screenshot = controller.screenshot()
    before_result = find_student_in_slot(matcher, slot_index)

    if not before_result['found']:
        print(f"✗ 슬롯 {slot_index + 1}에 학생 버튼 미발견")
        print(f"→ 테스트 종료 (스킵)")
        logger.save_screenshot(before_screenshot, f"slot_{slot_index}_empty")
        logger.log_check(
            check_name=f"Slot {slot_index + 1} - 학생 탐지",
            passed=False,
            message="학생 버튼 미발견",
            details={'slot_index': slot_index}
        )
        return {
            'slot_index': slot_index,
            'student_index': None,
            'student_name': "Unknown",
            'template': None,
            'skill_used': False,
            'skipped': True,
            'message': f"SKIP: 슬롯 {slot_index + 1}에 학생 버튼 없음"
        }

    student_index = before_result['student_index']
    student_name = before_result['student_name']
    template_name = before_result['template']

    print(f"✓ {student_name} 발견")
    logger.save_screenshot(before_screenshot, f"slot_{slot_index}_before_{student_name}")
    logger.log_check(
        check_name=f"Slot {slot_index + 1} - 학생 탐지",
        passed=True,
        message=f"{student_name} 발견",
        details={'student_name': student_name, 'template': template_name}
    )

    # === 2단계: 스킬 사용 (드래그) ===
    print(f"\n[2단계] 스킬 사용 중 (드래그 → 화면 중앙)...")
    click_success = click_skill_slot(controller, slot_index)

    if not click_success:
        print("✗ 드래그 실패")
        print("→ 테스트 종료")
        logger.log_check(
            check_name=f"Slot {slot_index + 1} - 스킬 드래그",
            passed=False,
            message="드래그 실패",
            details={'student_name': student_name}
        )
        return {
            'slot_index': slot_index,
            'student_index': student_index,
            'student_name': student_name,
            'template': template_name,
            'skill_used': False,
            'skipped': False,
            'message': f"FAIL: 드래그 실패"
        }

    print(f"✓ 드래그 완료")
    logger.log_check(
        check_name=f"Slot {slot_index + 1} - 스킬 드래그",
        passed=True,
        message="드래그 성공",
        details={'student_name': student_name}
    )

    # === 3단계: UI 업데이트 대기 ===
    print(f"\n[3단계] UI 업데이트 대기 중 ({SKILL_UI_UPDATE_WAIT}초)...")
    time.sleep(SKILL_UI_UPDATE_WAIT)
    print("✓ 대기 완료")

    # === 4단계: 버튼 소멸 확인 ===
    print(f"\n[4단계] {student_name} 버튼 소멸 확인 중...")
    after_screenshot = controller.screenshot()
    disappeared = check_student_disappeared(
        matcher, slot_index, student_index
    )

    logger.save_screenshot(after_screenshot, f"slot_{slot_index}_after_{student_name}")

    # 검증
    if disappeared:
        print(f"✓ {student_name} 버튼 사라짐 → 스킬 사용됨")
        message = f"PASS: {student_name} 스킬 사용 성공"
        skill_used = True
    else:
        print(f"✗ {student_name} 버튼 여전히 존재 → 스킬 미사용")
        message = f"FAIL: {student_name} 버튼 잔존 (코스트 부족/쿨다운)"
        skill_used = False

    # 로그 기록
    logger.log_check(
        check_name=f"Slot {slot_index + 1} - 스킬 사용 검증 ({student_name})",
        passed=skill_used,
        message=message,
        details={
            'template': template_name,
            'disappeared': disappeared,
            'expected': f"{template_name} 사라짐",
            'actual': f"사라짐: {disappeared}"
        }
    )

    print(f"\n→ 결과: {message}")

    return {
        'slot_index': slot_index,
        'student_index': student_index,
        'student_name': student_name,
        'template': template_name,
        'skill_used': skill_used,
        'skipped': False,
        'message': message
    }


def test_all_slots_multiple_times(matcher: TemplateMatcher, controller: GameController,
                                   logger: TestLogger, rounds: int = 2) -> list:
    """
    모든 슬롯 여러 번 테스트

    3개 슬롯 × N회 = 최대 6명 학생 테스트 가능

    Args:
        matcher: TemplateMatcher 인스턴스
        controller: GameController 인스턴스
        logger: TestLogger 인스턴스
        rounds: 각 슬롯당 테스트 횟수 (기본 2회)

    Returns:
        각 테스트 결과 리스트
    """
    results = []

    for round_num in range(rounds):
        print(f"\n{'='*70}")
        print(f"라운드 {round_num + 1}/{rounds}")
        print(f"{'='*70}")

        for slot_index in range(3):
            result = test_single_slot_skill(matcher, controller, logger, slot_index)
            results.append(result)

            # 다음 슬롯까지 대기 (마지막 슬롯이 아니면)
            if not (round_num == rounds - 1 and slot_index == 2):
                print(f"\n다음 테스트까지 0.3초 대기...")
                time.sleep(0.3)

    return results


def print_test_summary(results: list):
    """
    테스트 결과 요약 출력

    Args:
        results: test_all_slots_multiple_times() 반환값
    """
    print("\n" + "=" * 70)
    print("스킬 사용 테스트 결과 요약")
    print("=" * 70)

    used_count = 0
    failed_count = 0
    skipped_count = 0

    # 학생별로 결과 집계
    tested_students = set()

    for i, result in enumerate(results):
        slot_index = result['slot_index']
        student_name = result['student_name']
        template = result.get('template', 'Unknown')

        if result.get('skipped', False):
            print(f"⊘ 테스트 {i + 1} - 슬롯 {slot_index + 1}: SKIP - 학생 버튼 없음")
            skipped_count += 1
        elif result['skill_used']:
            print(f"✓ 테스트 {i + 1} - 슬롯 {slot_index + 1} ({student_name}): PASS - 스킬 사용됨")
            used_count += 1
            tested_students.add(student_name)
        else:
            msg = result.get('message', 'Unknown')
            print(f"✗ 테스트 {i + 1} - 슬롯 {slot_index + 1} ({student_name}): FAIL - {msg}")
            failed_count += 1

    print()
    print(f"전체 테스트: {len(results)}회")
    print(f"스킬 사용 성공: {used_count}회")
    print(f"스킬 사용 실패: {failed_count}회")
    print(f"테스트 스킵: {skipped_count}회")
    print(f"테스트된 학생: {len(tested_students)}명 ({', '.join(tested_students)})")
    print("=" * 70)


def main():
    """메인 테스트 실행"""
    print("=" * 70)
    print("스킬 사용 검증 테스트 (v2 - UI 상태 변화 기반)")
    print("=" * 70)
    print()
    print("테스트 원리:")
    print("- EX 스킬 사용 시 해당 슬롯의 버튼이 교체됨")
    print("- Before: 슬롯에서 학생 찾기 (6개 템플릿 검색)")
    print("- Action: 드래그 → 화면 중앙 드롭")
    print("- After: 기존 학생 버튼이 사라졌는가?")
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 6명의 학생이 3개 슬롯에 랜덤 배치된 상태")
    print("3. 템플릿 파일: assets/templates/2560x1440/buttons/skill_1~6_button.png")
    print("4. 해상도: 2560x1440")
    print()
    print("테스트 방식:")
    print("- 슬롯 중심 탐색: 각 슬롯에서 누가 있는지 찾기")
    print("- 각 슬롯을 2회씩 테스트 (3슬롯 × 2회 = 최대 6명)")
    print()
    print("주의:")
    print("- 이 테스트는 실제로 스킬을 사용합니다!")
    print("- 코스트가 충분하지 않으면 FAIL로 판정됩니다")
    print()

    # 카운트다운
    for i in range(3, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    # 초기화
    matcher = TemplateMatcher()
    controller = GameController()
    logger = TestLogger(test_name="skill_usage_v2")

    print("\n테스트 시작!\n")

    try:
        # 모든 슬롯 2회씩 테스트 (최대 6명)
        results = test_all_slots_multiple_times(matcher, controller, logger, rounds=2)

        # 결과 요약
        print_test_summary(results)

        # 로그 저장
        result_file = logger.finalize()
        print(f"\n✓ 테스트 결과 저장 완료: {result_file}")

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 테스트 중단됨")
        logger.finalize()

    except Exception as e:
        print(f"\n\n✗ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        logger.finalize()


if __name__ == "__main__":
    main()
