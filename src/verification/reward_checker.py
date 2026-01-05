"""보상 획득 검증 모듈"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from config.settings import WAIT_SCREEN_TRANSITION, UI_DIR

logger = logging.getLogger(__name__)


class RewardChecker:
    """보상 획득 검증 클래스"""

    def __init__(
        self,
        matcher: TemplateMatcher,
        controller: GameController
    ):
        """
        Args:
            matcher: 템플릿 매칭 객체
            controller: 게임 컨트롤러 객체
        """
        self.matcher = matcher
        self.controller = controller

    def verify_reward_screen(
        self,
        reward_screen_template: Optional[Path | str] = None,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """
        보상 화면 출현 검증

        Args:
            reward_screen_template: 보상 화면 이미지
            timeout: 최대 대기 시간 (초)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "reward_screen_found": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "reward_screen_found": False,
            "message": ""
        }

        logger.info("보상 화면 검증 시작")

        # 기본 템플릿 경로
        if reward_screen_template is None:
            reward_screen_template = UI_DIR / "reward_screen.png"

        # 보상 화면 대기
        reward_appeared = self.matcher.wait_for_template(
            reward_screen_template,
            timeout=timeout
        )

        if reward_appeared:
            result["reward_screen_found"] = True
            result["success"] = True
            result["message"] = "보상 화면 출현 확인"
            logger.info(result["message"])
        else:
            result["message"] = f"보상 화면이 {timeout}초 내에 나타나지 않음"
            logger.warning(result["message"])

        return result

    def claim_rewards(
        self,
        claim_button_template: Optional[Path | str] = None,
        reward_screen_template: Optional[Path | str] = None,
        verify_after_claim: bool = True
    ) -> Dict[str, Any]:
        """
        보상 수령 버튼 클릭 및 검증

        Args:
            claim_button_template: 보상 수령 버튼 이미지
            reward_screen_template: 보상 화면 이미지 (사라지는지 확인)
            verify_after_claim: 수령 후 화면 전환 검증

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "button_found": bool,
                "button_clicked": bool,
                "reward_claimed": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "reward_claimed": False,
            "message": ""
        }

        logger.info("보상 수령 시작")

        # 기본 템플릿 경로
        if claim_button_template is None:
            claim_button_template = UI_DIR / "claim_button.png"
        if reward_screen_template is None:
            reward_screen_template = UI_DIR / "reward_screen.png"

        # 1. 보상 수령 버튼 찾기
        button_location = self.matcher.find_template(claim_button_template)
        if not button_location:
            result["message"] = "보상 수령 버튼을 찾을 수 없습니다"
            logger.error(result["message"])
            return result

        result["button_found"] = True
        logger.info(f"보상 수령 버튼 발견: {button_location}")

        # 2. 보상 수령 버튼 클릭
        try:
            clicked = self.controller.click_template(
                button_location,
                wait_after=WAIT_SCREEN_TRANSITION
            )

            if not clicked:
                result["message"] = "보상 수령 버튼 클릭 실패"
                logger.error(result["message"])
                return result

            result["button_clicked"] = True
            logger.info("보상 수령 버튼 클릭 성공")

        except Exception as e:
            result["message"] = f"보상 수령 버튼 클릭 중 오류: {e}"
            logger.error(result["message"])
            return result

        # 3. 보상 수령 후 화면 전환 확인
        if verify_after_claim:
            # 보상 화면이 사라지는지 확인
            reward_screen_disappeared = self.matcher.wait_for_template_disappear(
                reward_screen_template,
                timeout=10
            )

            if reward_screen_disappeared:
                result["reward_claimed"] = True
                result["success"] = True
                result["message"] = "보상 수령 완료 (화면 전환 확인)"
                logger.info(result["message"])
            else:
                result["message"] = "보상 수령 후 화면 전환이 감지되지 않음"
                logger.warning(result["message"])
                result["success"] = True  # 클릭은 했으므로 부분 성공
        else:
            result["reward_claimed"] = True
            result["success"] = True
            result["message"] = "보상 수령 버튼 클릭 완료"
            logger.info(result["message"])

        return result

    def verify_and_claim(
        self,
        reward_screen_template: Optional[Path | str] = None,
        claim_button_template: Optional[Path | str] = None,
        wait_for_reward: int = 15
    ) -> Dict[str, Any]:
        """
        보상 화면 대기 → 확인 → 수령 (일괄 처리)

        Args:
            reward_screen_template: 보상 화면 이미지
            claim_button_template: 보상 수령 버튼 이미지
            wait_for_reward: 보상 화면 대기 시간 (초)

        Returns:
            검증 결과 딕셔너리
        """
        logger.info("보상 검증 및 수령 시작")

        # 1. 보상 화면 확인
        verify_result = self.verify_reward_screen(
            reward_screen_template=reward_screen_template,
            timeout=wait_for_reward
        )

        if not verify_result["success"]:
            return {
                **verify_result,
                "button_found": False,
                "button_clicked": False,
                "reward_claimed": False
            }

        # 2. 보상 수령
        claim_result = self.claim_rewards(
            claim_button_template=claim_button_template,
            reward_screen_template=reward_screen_template,
            verify_after_claim=True
        )

        return claim_result

    def is_reward_screen_visible(
        self,
        reward_screen_template: Optional[Path | str] = None
    ) -> bool:
        """
        현재 보상 화면이 보이는지 확인

        Args:
            reward_screen_template: 보상 화면 이미지

        Returns:
            보상 화면이 보이면 True
        """
        if reward_screen_template is None:
            reward_screen_template = UI_DIR / "reward_screen.png"

        return self.matcher.template_exists(reward_screen_template)
