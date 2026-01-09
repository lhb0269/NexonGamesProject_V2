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


# 스킬 버튼 템플릿 매핑 (슬롯 번호 → 템플릿 파일명)
SKILL_TEMPLATES = {
    0: "skill_1_button.png",
    1: "skill_2_button.png",
    2: "skill_3_button.png",
    3: "skill_4_button.png",
    4: "skill_5_button.png",
    5: "skill_6_button.png",
}

# 학생 이름 매핑 (실제 게임 학생 이름으로 수정 가능)
STUDENT_NAMES = {
    0: "Student 1",
    1: "Student 2",
    2: "Student 3",
    3: "Student 4",
    4: "Student 5",
    5: "Student 6",
}


def detect_skill_template(matcher: TemplateMatcher, slot_index: int,
                          screenshot=None, confidence: float = 0.7) -> dict:
    """
    특정 슬롯에서 스킬 템플릿을 탐지

    Args:
        matcher: TemplateMatcher 인스턴스
        slot_index: 슬롯 인덱스 (0-5)
        screenshot: 스크린샷 (None이면 새로 캡처)
        confidence: 신뢰도 임계값 (기본 0.7)

    Returns:
        {
            'found': bool,              # 템플릿 발견 여부
            'template': str,            # 템플릿 파일명
            'location': tuple or None,  # (x, y, w, h) or None
            'confidence': float or None # 매칭 신뢰도
        }
    """
    if slot_index not in SKILL_TEMPLATES:
        return {
            'found': False,
            'template': None,
            'location': None,
            'confidence': None,
            'error': f"Invalid slot index: {slot_index}"
        }

    template_name = SKILL_TEMPLATES[slot_index]
    template_path = f"2560x1440/buttons/{template_name}"

    try:
        location = matcher.find_template(
            template_path,
            confidence=confidence,
            screenshot=screenshot
        )

        if location:
            return {
                'found': True,
                'template': template_name,
                'location': location,
                'confidence': confidence
            }
        else:
            return {
                'found': False,
                'template': template_name,
                'location': None,
                'confidence': None
            }

    except Exception as e:
        return {
            'found': False,
            'template': template_name,
            'location': None,
            'confidence': None,
            'error': str(e)
        }


def click_skill_slot(controller: GameController, slot_index: int) -> bool:
    """
    스킬 슬롯 클릭 (드래그 → 화면 중앙 드롭)

    Args:
        controller: GameController 인스턴스
        slot_index: 슬롯 인덱스 (0-5)

    Returns:
        성공 여부
    """
    if slot_index not in SKILL_BUTTON_SLOTS:
        print(f"✗ 잘못된 슬롯 인덱스: {slot_index}")
        return False

    try:
        start_pos = SKILL_BUTTON_SLOTS[slot_index]
        end_pos = (SCREEN_CENTER_X, SCREEN_CENTER_Y)

        # 드래그 (슬롯 → 화면 중앙)
        controller.drag(start_pos, end_pos, duration=SKILL_USE_DRAG_DURATION)

        return True

    except Exception as e:
        print(f"✗ 스킬 클릭 실패: {e}")
        return False


def verify_skill_consumed(before_result: dict, after_result: dict) -> dict:
    """
    스킬 사용 여부 검증 (템플릿 소멸 확인)

    Args:
        before_result: detect_skill_template() Before 결과
        after_result: detect_skill_template() After 결과

    Returns:
        {
            'skill_used': bool,     # 스킬 사용됨
            'before_found': bool,   # 사용 전 템플릿 발견
            'after_found': bool,    # 사용 후 템플릿 발견
            'template': str,        # 템플릿 이름
            'message': str          # 판정 메시지
        }
    """
    before_found = before_result.get('found', False)
    after_found = after_result.get('found', False)
    template = before_result.get('template', 'Unknown')

    # PASS 조건: 사용 전 존재 → 사용 후 사라짐
    if before_found and not after_found:
        return {
            'skill_used': True,
            'before_found': True,
            'after_found': False,
            'template': template,
            'message': f"PASS: {template} 사라짐 → 스킬 사용 성공"
        }

    # FAIL 조건: 사용 전 존재 → 사용 후에도 존재
    elif before_found and after_found:
        return {
            'skill_used': False,
            'before_found': True,
            'after_found': True,
            'template': template,
            'message': f"FAIL: {template} 잔존 → 스킬 사용 실패 (코스트 부족/쿨다운)"
        }

    # 스킵: 사용 전부터 템플릿 없음
    elif not before_found:
        return {
            'skill_used': False,
            'before_found': False,
            'after_found': after_found,
            'template': template,
            'message': f"SKIP: {template} 사용 전부터 미발견 (다른 학생 스킬 장착됨)"
        }

    # 예외: 사용 전 없었는데 사용 후 생김 (비정상)
    else:
        return {
            'skill_used': False,
            'before_found': False,
            'after_found': True,
            'template': template,
            'message': f"ERROR: {template} 사용 전 없었는데 사용 후 생김 (비정상)"
        }


def test_single_skill_slot(matcher: TemplateMatcher, controller: GameController,
                            logger: TestLogger, slot_index: int) -> dict:
    """
    단일 슬롯 스킬 사용 테스트

    Args:
        matcher: TemplateMatcher 인스턴스
        controller: GameController 인스턴스
        logger: TestLogger 인스턴스
        slot_index: 슬롯 인덱스 (0-5)

    Returns:
        테스트 결과 딕셔너리
    """
    student_name = STUDENT_NAMES.get(slot_index, f"Unknown Student {slot_index}")
    template_name = SKILL_TEMPLATES.get(slot_index, "Unknown")

    print(f"\n[슬롯 {slot_index + 1}] {student_name} 스킬 테스트 시작...")

    # Before: 스킬 템플릿 탐지
    print("  [1/4] 사용 전 템플릿 탐지 중...")
    before_screenshot = controller.screenshot()
    before_result = detect_skill_template(matcher, slot_index, screenshot=before_screenshot)

    if before_result['found']:
        print(f"  ✓ {template_name} 발견 (신뢰도: {before_result['confidence']})")
    else:
        print(f"  ✗ {template_name} 미발견 → 스킵")
        logger.save_screenshot(before_screenshot, f"slot_{slot_index}_before_skip")
        return {
            'slot_index': slot_index,
            'student_name': student_name,
            'skill_used': False,
            'skipped': True,
            'before_result': before_result,
            'after_result': None,
            'verification': {
                'message': f"SKIP: {template_name} 사용 전부터 미발견"
            }
        }

    logger.save_screenshot(before_screenshot, f"slot_{slot_index}_before")

    # Action: 스킬 사용 (드래그)
    print("  [2/4] 스킬 사용 중 (드래그 → 화면 중앙)...")
    click_success = click_skill_slot(controller, slot_index)

    if not click_success:
        print("  ✗ 스킬 클릭 실패")
        return {
            'slot_index': slot_index,
            'student_name': student_name,
            'skill_used': False,
            'skipped': False,
            'error': 'Click failed',
            'before_result': before_result,
            'after_result': None,
            'verification': None
        }

    # UI 업데이트 대기
    print(f"  [3/4] UI 업데이트 대기 중 ({SKILL_UI_UPDATE_WAIT}초)...")
    time.sleep(SKILL_UI_UPDATE_WAIT)

    # After: 스킬 템플릿 재탐지
    print("  [4/4] 사용 후 템플릿 재탐지 중...")
    after_screenshot = controller.screenshot()
    after_result = detect_skill_template(matcher, slot_index, screenshot=after_screenshot)

    if after_result['found']:
        print(f"  ✗ {template_name} 여전히 존재 → 스킬 미사용")
    else:
        print(f"  ✓ {template_name} 사라짐 → 스킬 사용됨")

    logger.save_screenshot(after_screenshot, f"slot_{slot_index}_after")

    # 검증
    verification = verify_skill_consumed(before_result, after_result)
    print(f"  결과: {verification['message']}")

    # 결과 기록
    result = {
        'slot_index': slot_index,
        'student_name': student_name,
        'template': template_name,
        'skill_used': verification['skill_used'],
        'skipped': False,
        'before_result': before_result,
        'after_result': after_result,
        'verification': verification
    }

    logger.add_verification(
        item=f"Skill Usage - Slot {slot_index + 1} ({student_name})",
        expected=f"{template_name} 사라짐",
        actual=f"Before: {before_result['found']}, After: {after_result['found']}",
        success=verification['skill_used']
    )

    return result


def test_all_skill_slots(matcher: TemplateMatcher, controller: GameController,
                         logger: TestLogger, slot_count: int = 6) -> list:
    """
    모든 스킬 슬롯 테스트 (0~5 또는 지정된 개수)

    Args:
        matcher: TemplateMatcher 인스턴스
        controller: GameController 인스턴스
        logger: TestLogger 인스턀스
        slot_count: 테스트할 슬롯 개수 (기본 6개)

    Returns:
        각 슬롯 테스트 결과 리스트
    """
    results = []

    for slot_index in range(slot_count):
        result = test_single_skill_slot(matcher, controller, logger, slot_index)
        results.append(result)

        # 다음 슬롯까지 대기 (마지막 슬롯 제외)
        if slot_index < slot_count - 1:
            print(f"\n다음 슬롯까지 2초 대기...")
            time.sleep(2)

    return results


def print_test_summary(results: list):
    """
    테스트 결과 요약 출력

    Args:
        results: test_all_skill_slots() 반환값
    """
    print("\n" + "=" * 70)
    print("스킬 사용 테스트 결과 요약")
    print("=" * 70)

    used_count = 0
    failed_count = 0
    skipped_count = 0

    for result in results:
        slot_index = result['slot_index']
        student_name = result['student_name']
        template = result.get('template', 'Unknown')

        if result.get('skipped', False):
            print(f"⊘ 슬롯 {slot_index + 1} ({student_name}): SKIP - {template} 미발견")
            skipped_count += 1
        elif result['skill_used']:
            print(f"✓ 슬롯 {slot_index + 1} ({student_name}): PASS - 스킬 사용됨")
            used_count += 1
        else:
            msg = result.get('verification', {}).get('message', 'Unknown')
            print(f"✗ 슬롯 {slot_index + 1} ({student_name}): FAIL - {msg}")
            failed_count += 1

    print()
    print(f"전체 슬롯: {len(results)}개")
    print(f"스킬 사용 성공: {used_count}개")
    print(f"스킬 사용 실패: {failed_count}개")
    print(f"테스트 스킵: {skipped_count}개")
    print("=" * 70)


def main():
    """메인 테스트 실행"""
    print("=" * 70)
    print("스킬 사용 검증 테스트 (v2 - UI 상태 변화 기반)")
    print("=" * 70)
    print()
    print("테스트 원리:")
    print("- EX 스킬 사용 시 해당 슬롯의 버튼이 교체됨")
    print("- Before: 특정 학생의 스킬 버튼 존재")
    print("- Action: 드래그 → 화면 중앙 드롭")
    print("- After: 기존 템플릿이 사라졌는가?")
    print()
    print("준비사항:")
    print("1. 게임을 전투 화면으로 진입")
    print("2. 스킬 버튼 6개가 화면에 보이는 상태")
    print("3. 템플릿 파일: assets/templates/2560x1440/buttons/skill_1~6_button.png")
    print("4. 해상도: 2560x1440")
    print()
    print("주의:")
    print("- 이 테스트는 실제로 스킬을 사용합니다!")
    print("- 코스트가 충분하지 않으면 FAIL로 판정됩니다")
    print()

    user_input = input("계속 진행하시겠습니까? (y/n): ").strip().lower()
    if user_input != 'y':
        print("테스트 중단")
        return

    # 카운트다운
    for i in range(5, 0, -1):
        print(f"테스트 시작까지: {i}초...")
        time.sleep(1)

    # 초기화
    matcher = TemplateMatcher()
    controller = GameController()
    logger = TestLogger(test_name="skill_usage_v2")

    print("\n테스트 시작!\n")

    try:
        # 모든 슬롯 테스트 (6개)
        results = test_all_skill_slots(matcher, controller, logger, slot_count=6)

        # 결과 요약
        print_test_summary(results)

        # 로그 저장
        logger.finalize()
        print(f"\n로그 저장 완료: {logger.log_dir}")

    except KeyboardInterrupt:
        print("\n\n테스트 중단됨 (Ctrl+C)")
        logger.finalize()
    except Exception as e:
        print(f"\n\n✗ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        logger.finalize()


if __name__ == "__main__":
    main()
