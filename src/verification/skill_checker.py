"""스킬 사용 검증 모듈 (OCR 통합)"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.ocr import OCRReader
from config.settings import (
    SKILL_CHECK_INTERVAL,
    MAX_SKILL_WAIT_TIME,
    ICONS_DIR
)
from config.ocr_regions import (
    BATTLE_COST_VALUE_REGION,
    BATTLE_COST_MAX_REGION
)
from config.skill_settings import (
    get_skill_button_position,
    get_skill_cost_region,
    SCREEN_CENTER_X,
    SCREEN_CENTER_Y,
    TARGET_CLICK_TO_COST_UPDATE_WAIT
)

logger = logging.getLogger(__name__)


class SkillChecker:
    """스킬 사용 검증 클래스 (OCR 통합)"""

    def __init__(
        self,
        matcher: TemplateMatcher,
        controller: GameController,
        enable_ocr: bool = False
    ):
        """
        Args:
            matcher: 템플릿 매칭 객체
            controller: 게임 컨트롤러 객체
            enable_ocr: OCR 코스트 검증 활성화 여부
        """
        self.matcher = matcher
        self.controller = controller
        self.enable_ocr = enable_ocr

        # OCR 리더 초기화 (enable_ocr=True일 때만)
        self.ocr_reader = None
        if self.enable_ocr:
            try:
                self.ocr_reader = OCRReader()
                logger.info("OCR 코스트 검증 활성화됨")
            except Exception as e:
                logger.warning(f"OCR 초기화 실패: {e}. 코스트 검증 비활성화됨")
                self.enable_ocr = False

    def verify_skill_usage(
        self,
        skill_icon_template: Path | str,
        student_name: str = "Unknown",
        wait_for_ready: bool = True,
        max_wait: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        스킬 아이콘 클릭 및 사용 검증

        Args:
            skill_icon_template: 스킬 아이콘 이미지
            student_name: 학생(캐릭터) 이름 (로깅용)
            wait_for_ready: 스킬이 준비될 때까지 대기
            max_wait: 최대 대기 시간 (초)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "skill_found": bool,
                "skill_clicked": bool,
                "student_name": str,
                "wait_time": float,
                "message": str
            }
        """
        result = {
            "success": False,
            "skill_found": False,
            "skill_clicked": False,
            "student_name": student_name,
            "wait_time": 0.0,
            "message": ""
        }

        logger.info(f"[{student_name}] 스킬 사용 검증 시작")
        start_time = time.time()
        max_wait = max_wait or MAX_SKILL_WAIT_TIME

        # 스킬 준비 대기
        if wait_for_ready:
            logger.info(f"[{student_name}] 스킬 준비 대기 중...")
            skill_location = self.matcher.wait_for_template(
                skill_icon_template,
                timeout=int(max_wait),
                check_interval=SKILL_CHECK_INTERVAL
            )
        else:
            skill_location = self.matcher.find_template(skill_icon_template)

        result["wait_time"] = time.time() - start_time

        # 스킬 아이콘 못 찾음
        if not skill_location:
            result["message"] = f"[{student_name}] 스킬 아이콘을 찾을 수 없습니다"
            logger.warning(result["message"])
            return result

        result["skill_found"] = True
        logger.info(f"[{student_name}] 스킬 아이콘 발견: {skill_location}")

        # 스킬 클릭
        try:
            clicked = self.controller.click_template(
                skill_location,
                wait_after=0.5  # 스킬 사용 후 짧은 대기
            )

            if clicked:
                result["skill_clicked"] = True
                result["success"] = True
                result["message"] = f"[{student_name}] 스킬 사용 성공"
                logger.info(result["message"])
            else:
                result["message"] = f"[{student_name}] 스킬 클릭 실패"
                logger.error(result["message"])

        except Exception as e:
            result["message"] = f"[{student_name}] 스킬 클릭 중 오류: {e}"
            logger.error(result["message"])

        return result

    def verify_multiple_skills(
        self,
        skill_configs: List[Dict[str, Any]],
        sequential: bool = True
    ) -> Dict[str, Any]:
        """
        여러 학생의 스킬 사용 검증

        Args:
            skill_configs: 스킬 설정 리스트
                [
                    {
                        "student_name": str,
                        "skill_icon": Path | str,
                        "wait_for_ready": bool (optional)
                    },
                    ...
                ]
            sequential: 순차 실행 여부 (True면 하나씩, False면 모두 찾아서 클릭)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "total_skills": int,
                "successful_skills": int,
                "failed_skills": int,
                "results": List[Dict],
                "message": str
            }
        """
        result = {
            "success": False,
            "total_skills": len(skill_configs),
            "successful_skills": 0,
            "failed_skills": 0,
            "results": [],
            "message": ""
        }

        logger.info(f"여러 스킬 사용 검증 시작 (총 {len(skill_configs)}개)")

        for config in skill_configs:
            student_name = config.get("student_name", "Unknown")
            skill_icon = config.get("skill_icon")
            wait_for_ready = config.get("wait_for_ready", True)

            if not skill_icon:
                logger.warning(f"[{student_name}] 스킬 아이콘 경로 없음, 건너뜀")
                continue

            # 개별 스킬 검증
            skill_result = self.verify_skill_usage(
                skill_icon_template=skill_icon,
                student_name=student_name,
                wait_for_ready=wait_for_ready
            )

            result["results"].append(skill_result)

            if skill_result["success"]:
                result["successful_skills"] += 1
            else:
                result["failed_skills"] += 1

            # 순차 실행이면 다음 스킬까지 대기
            if sequential:
                time.sleep(SKILL_CHECK_INTERVAL)

        # 전체 성공 여부
        result["success"] = result["failed_skills"] == 0
        result["message"] = (
            f"스킬 사용 완료: "
            f"성공 {result['successful_skills']}/{result['total_skills']}"
        )

        logger.info(result["message"])
        return result

    def is_skill_ready(
        self,
        skill_icon_template: Path | str
    ) -> bool:
        """
        스킬이 사용 가능한지 확인 (간단 체크)

        Args:
            skill_icon_template: 스킬 아이콘 이미지

        Returns:
            사용 가능하면 True
        """
        return self.matcher.template_exists(skill_icon_template)

    # ========================================
    # OCR 기반 코스트 검증
    # ========================================

    def read_current_cost(
        self,
        screenshot: Optional[Image.Image] = None
    ) -> Optional[int]:
        """
        현재 코스트 값 읽기 (OCR)

        Args:
            screenshot: 화면 이미지 (None이면 자동 캡처)

        Returns:
            코스트 값 또는 None (읽기 실패 시)
        """
        if not self.enable_ocr or not self.ocr_reader:
            logger.warning("OCR이 비활성화되어 있습니다")
            return None

        try:
            # 화면 캡처
            if screenshot is None:
                screenshot = self.controller.screenshot()

            # 코스트 영역 추출 및 OCR
            cost = self.ocr_reader.read_cost_value(
                screenshot,
                bbox=BATTLE_COST_VALUE_REGION
            )

            if cost is not None:
                logger.info(f"현재 코스트: {cost}")
            else:
                logger.warning("코스트 읽기 실패")

            return cost

        except Exception as e:
            logger.error(f"코스트 읽기 중 오류: {e}")
            return None

    def verify_cost_consumption(
        self,
        skill_cost: int,
        before_screenshot: Optional[Image.Image] = None,
        after_screenshot: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        """
        스킬 사용 전후 코스트 소모 검증

        Args:
            skill_cost: 예상 스킬 코스트
            before_screenshot: 스킬 사용 전 화면
            after_screenshot: 스킬 사용 후 화면

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "cost_before": Optional[int],
                "cost_after": Optional[int],
                "consumed": Optional[int],
                "expected_cost": int,
                "match": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "cost_before": None,
            "cost_after": None,
            "consumed": None,
            "expected_cost": skill_cost,
            "match": False,
            "message": ""
        }

        if not self.enable_ocr or not self.ocr_reader:
            result["message"] = "OCR이 비활성화되어 있습니다"
            return result

        try:
            # 사용 전 코스트 읽기
            if before_screenshot is None:
                before_screenshot = self.controller.screenshot()

            cost_before = self.read_current_cost(before_screenshot)
            result["cost_before"] = cost_before

            if cost_before is None:
                result["message"] = "사용 전 코스트 읽기 실패"
                return result

            # 코스트 부족 체크
            if cost_before < skill_cost:
                result["message"] = (
                    f"코스트 부족: 현재 {cost_before}, 필요 {skill_cost}"
                )
                return result

            # 스킬 사용 후 화면 캡처 필요
            if after_screenshot is None:
                logger.warning("사용 후 화면 없음. 수동으로 캡처 필요")
                result["message"] = "사용 후 화면 필요"
                return result

            # 사용 후 코스트 읽기
            cost_after = self.read_current_cost(after_screenshot)
            result["cost_after"] = cost_after

            if cost_after is None:
                result["message"] = "사용 후 코스트 읽기 실패"
                return result

            # 소모량 계산
            consumed = cost_before - cost_after
            result["consumed"] = consumed

            # 검증
            result["match"] = (consumed == skill_cost)
            result["success"] = result["match"]

            if result["match"]:
                result["message"] = (
                    f"코스트 소모 확인: {cost_before} → {cost_after} "
                    f"(소모: {consumed})"
                )
                logger.info(result["message"])
            else:
                result["message"] = (
                    f"코스트 불일치: 예상 {skill_cost}, 실제 {consumed}"
                )
                logger.warning(result["message"])

        except Exception as e:
            result["message"] = f"코스트 검증 중 오류: {e}"
            logger.error(result["message"])

        return result

    def verify_skill_with_cost(
        self,
        skill_icon_template: Path | str,
        skill_cost: int,
        student_name: str = "Unknown",
        wait_for_ready: bool = True,
        max_wait: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        스킬 사용 + 코스트 소모 통합 검증

        Args:
            skill_icon_template: 스킬 아이콘 이미지
            skill_cost: 예상 스킬 코스트
            student_name: 학생 이름
            wait_for_ready: 스킬 준비 대기 여부
            max_wait: 최대 대기 시간

        Returns:
            검증 결과 딕셔너리
        """
        result = {
            "success": False,
            "skill_used": False,
            "cost_verified": False,
            "student_name": student_name,
            "skill_cost": skill_cost,
            "message": ""
        }

        # 1. 스킬 사용 전 코스트 확인
        cost_check = None
        before_screen = None

        if self.enable_ocr:
            before_screen = self.controller.screenshot()
            current_cost = self.read_current_cost(before_screen)

            if current_cost is not None and current_cost < skill_cost:
                result["message"] = (
                    f"[{student_name}] 코스트 부족: "
                    f"현재 {current_cost}, 필요 {skill_cost}"
                )
                logger.warning(result["message"])
                return result

        # 2. 스킬 사용
        skill_result = self.verify_skill_usage(
            skill_icon_template=skill_icon_template,
            student_name=student_name,
            wait_for_ready=wait_for_ready,
            max_wait=max_wait
        )

        result["skill_used"] = skill_result["success"]

        if not skill_result["success"]:
            result["message"] = skill_result["message"]
            return result

        # 3. 스킬 사용 후 코스트 검증
        if self.enable_ocr:
            time.sleep(0.5)  # 코스트 UI 업데이트 대기
            after_screen = self.controller.screenshot()

            cost_check = self.verify_cost_consumption(
                skill_cost=skill_cost,
                before_screenshot=before_screen,
                after_screenshot=after_screen
            )

            result["cost_verified"] = cost_check["success"]
            result["cost_details"] = cost_check

            if not cost_check["success"]:
                result["message"] = (
                    f"[{student_name}] 스킬 사용됨, "
                    f"하지만 코스트 검증 실패: {cost_check['message']}"
                )
                logger.warning(result["message"])
                return result

        # 4. 전체 성공
        result["success"] = True
        if self.enable_ocr:
            result["message"] = (
                f"[{student_name}] 스킬 사용 및 코스트 소모 확인 완료"
            )
        else:
            result["message"] = (
                f"[{student_name}] 스킬 사용 완료 (코스트 검증 비활성화)"
            )

        logger.info(result["message"])
        return result

    # ========================================
    # 스킬 버튼 직접 클릭 방식 (OCR 코스트 읽기)
    # ========================================

    def read_skill_cost_from_button(
        self,
        slot_index: int,
        screenshot: Optional[Image.Image] = None
    ) -> Optional[int]:
        """
        스킬 버튼 하단의 코스트 값 읽기 (OCR)

        Args:
            slot_index: 스킬 슬롯 인덱스 (0=슬롯1, 1=슬롯2, 2=슬롯3)
            screenshot: 화면 이미지 (None이면 자동 캡처)

        Returns:
            코스트 값 또는 None (읽기 실패 시)
        """
        if not self.enable_ocr or not self.ocr_reader:
            logger.warning("OCR이 비활성화되어 있습니다")
            return None

        # 슬롯 인덱스 검증
        cost_region = get_skill_cost_region(slot_index)
        if cost_region is None:
            logger.error(f"잘못된 슬롯 인덱스: {slot_index}")
            return None

        try:
            # 화면 캡처
            if screenshot is None:
                screenshot = self.controller.screenshot()

            # 스킬 코스트 영역 OCR
            skill_cost = self.ocr_reader.read_cost_value(
                screenshot,
                bbox=cost_region
            )

            if skill_cost is not None:
                logger.info(f"슬롯 {slot_index + 1} 스킬 코스트: {skill_cost}")
            else:
                logger.warning(f"슬롯 {slot_index + 1} 스킬 코스트 읽기 실패")

            return skill_cost

        except Exception as e:
            logger.error(f"슬롯 {slot_index + 1} 스킬 코스트 읽기 중 오류: {e}")
            return None

    def use_skill_and_verify(
        self,
        slot_index: int,
        student_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        스킬 버튼 드래그 → 화면 중앙 타겟 → 코스트 소모 검증

        전체 플로우:
        1. 스킬 버튼의 코스트 읽기 (OCR)
        2. 현재 코스트 읽기 (사용 전)
        3. 현재 코스트 >= 스킬 코스트 체크
        4. 스킬 버튼에서 화면 중앙으로 드래그 (0.5초 duration)
        5. 1.0초 대기 (코스트 UI 업데이트)
        6. 현재 코스트 읽기 (사용 후)
        7. 코스트 차감 검증: (사용 전 - 사용 후) == 스킬 코스트

        Args:
            slot_index: 스킬 슬롯 인덱스 (0=슬롯1, 1=슬롯2, 2=슬롯3)
            student_name: 학생 이름 (로깅용)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "student_name": str,
                "slot_index": int,
                "skill_cost": Optional[int],
                "cost_before": Optional[int],
                "cost_after": Optional[int],
                "consumed": Optional[int],
                "sufficient_cost": bool,
                "cost_matched": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "student_name": student_name,
            "slot_index": slot_index,
            "skill_cost": None,
            "cost_before": None,
            "cost_after": None,
            "consumed": None,
            "sufficient_cost": False,
            "cost_matched": False,
            "message": ""
        }

        logger.info(f"[{student_name}] 슬롯 {slot_index + 1} 스킬 사용 시작")

        # OCR 필수 체크
        if not self.enable_ocr or not self.ocr_reader:
            result["message"] = "OCR이 비활성화되어 있습니다"
            logger.error(result["message"])
            return result

        # 슬롯 위치 가져오기
        button_position = get_skill_button_position(slot_index)
        if button_position is None:
            result["message"] = f"잘못된 슬롯 인덱스: {slot_index}"
            logger.error(result["message"])
            return result

        try:
            # 1. 스킬 버튼 코스트 읽기
            screenshot = self.controller.screenshot()
            skill_cost = self.read_skill_cost_from_button(slot_index, screenshot)

            if skill_cost is None:
                result["message"] = f"[{student_name}] 슬롯 {slot_index + 1} 스킬 코스트 읽기 실패"
                logger.error(result["message"])
                return result

            result["skill_cost"] = skill_cost
            logger.info(f"[{student_name}] 스킬 요구 코스트: {skill_cost}")

            # 2. 현재 코스트 읽기 (사용 전)
            cost_before = self.read_current_cost(screenshot)

            if cost_before is None:
                result["message"] = f"[{student_name}] 사용 전 코스트 읽기 실패"
                logger.error(result["message"])
                return result

            result["cost_before"] = cost_before
            logger.info(f"[{student_name}] 사용 전 코스트: {cost_before}")

            # 3. 코스트 부족 체크
            if cost_before < skill_cost:
                result["message"] = (
                    f"[{student_name}] 코스트 부족: "
                    f"현재 {cost_before}, 필요 {skill_cost}"
                )
                logger.warning(result["message"])
                return result

            result["sufficient_cost"] = True

            # 4. 스킬 버튼에서 화면 중앙으로 드래그 (스킬 타겟 설정)
            logger.info(f"[{student_name}] 스킬 드래그: {button_position} → ({SCREEN_CENTER_X}, {SCREEN_CENTER_Y})")
            self.controller.drag(
                start_x=button_position[0],
                start_y=button_position[1],
                end_x=SCREEN_CENTER_X,
                end_y=SCREEN_CENTER_Y,
                duration=0.5  # 0.5초 동안 드래그
            )
            time.sleep(TARGET_CLICK_TO_COST_UPDATE_WAIT)

            # 6. 사용 후 코스트 읽기
            screenshot_after = self.controller.screenshot()
            cost_after = self.read_current_cost(screenshot_after)

            if cost_after is None:
                result["message"] = f"[{student_name}] 사용 후 코스트 읽기 실패"
                logger.warning(result["message"])
                # 코스트 읽기 실패해도 스킬 사용은 했을 수 있음
                return result

            result["cost_after"] = cost_after
            logger.info(f"[{student_name}] 사용 후 코스트: {cost_after}")

            # 7. 코스트 소모 검증
            consumed = cost_before - cost_after
            result["consumed"] = consumed

            if consumed == skill_cost:
                result["cost_matched"] = True
                result["success"] = True
                result["message"] = (
                    f"[{student_name}] 스킬 사용 성공: "
                    f"{cost_before} → {cost_after} (소모: {consumed})"
                )
                logger.info(result["message"])
            else:
                result["message"] = (
                    f"[{student_name}] 코스트 불일치: "
                    f"예상 {skill_cost}, 실제 소모 {consumed}"
                )
                logger.warning(result["message"])

        except Exception as e:
            result["message"] = f"[{student_name}] 스킬 사용 중 오류: {e}"
            logger.error(result["message"])
            import traceback
            traceback.print_exc()

        return result
