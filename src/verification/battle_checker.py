"""전투 진입 및 진행 검증 모듈"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from config.settings import (
    WAIT_BATTLE_LOADING,
    WAIT_SCREEN_TRANSITION,
    BUTTONS_DIR,
    UI_DIR
)

logger = logging.getLogger(__name__)


class BattleChecker:
    """전투 진입 및 진행 검증 클래스"""

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

    def verify_battle_entry(
        self,
        start_button_template: Optional[Path | str] = None,
        battle_ui_template: Optional[Path | str] = None,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """
        전투 시작 버튼 클릭 후 전투 진입 검증

        Args:
            start_button_template: 전투 시작 버튼 이미지
            battle_ui_template: 전투 UI 이미지 (EX스킬 아이콘 등)
            timeout: 전투 로딩 대기 시간 (초)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "button_found": bool,
                "button_clicked": bool,
                "battle_started": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "battle_started": False,
            "message": ""
        }

        logger.info("전투 진입 검증 시작")

        # 기본 템플릿 경로 설정
        if start_button_template is None:
            start_button_template = BUTTONS_DIR / "battle_start.png"
        if battle_ui_template is None:
            battle_ui_template = UI_DIR / "battle_ui.png"

        # 1. 전투 시작 버튼 찾기
        button_location = self.matcher.find_template(start_button_template)
        if not button_location:
            result["message"] = "전투 시작 버튼을 찾을 수 없습니다"
            logger.error(result["message"])
            return result

        result["button_found"] = True
        logger.info(f"전투 시작 버튼 발견: {button_location}")

        # 2. 전투 시작 버튼 클릭
        try:
            clicked = self.controller.click_template(
                button_location,
                wait_after=WAIT_BATTLE_LOADING
            )
            if not clicked:
                result["message"] = "전투 시작 버튼 클릭 실패"
                logger.error(result["message"])
                return result

            result["button_clicked"] = True
            logger.info("전투 시작 버튼 클릭 성공")

        except Exception as e:
            result["message"] = f"전투 시작 버튼 클릭 중 오류: {e}"
            logger.error(result["message"])
            return result

        # 3. 전투 UI 출현 확인
        battle_ui_appeared = self.matcher.wait_for_template(
            battle_ui_template,
            timeout=timeout
        )

        if battle_ui_appeared:
            result["battle_started"] = True
            result["success"] = True
            result["message"] = "전투 진입 성공"
            logger.info(result["message"])
        else:
            result["message"] = "전투 UI가 나타나지 않음 (로딩 시간 초과)"
            logger.warning(result["message"])

        return result

    def wait_battle_end(
        self,
        victory_template: Optional[Path | str] = None,
        defeat_template: Optional[Path | str] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        전투 종료 대기 및 결과 확인

        Args:
            victory_template: 승리 화면 이미지
            defeat_template: 패배 화면 이미지
            timeout: 최대 대기 시간 (초)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "battle_ended": bool,
                "result": str ("victory" | "defeat" | "timeout"),
                "duration": float,
                "message": str
            }
        """
        result = {
            "success": False,
            "battle_ended": False,
            "result": "timeout",
            "duration": 0.0,
            "message": ""
        }

        logger.info("전투 종료 대기 시작")
        start_time = time.time()

        # 기본 템플릿 경로 설정
        if victory_template is None:
            victory_template = UI_DIR / "victory.png"
        if defeat_template is None:
            defeat_template = UI_DIR / "defeat.png"

        # 전투 종료 대기
        check_interval = 2.0  # 2초마다 확인
        elapsed = 0

        while elapsed < timeout:
            # 승리 화면 확인
            if self.matcher.template_exists(victory_template):
                result["battle_ended"] = True
                result["success"] = True
                result["result"] = "victory"
                result["duration"] = time.time() - start_time
                result["message"] = "전투 승리"
                logger.info(f"{result['message']} (소요시간: {result['duration']:.1f}초)")
                return result

            # 패배 화면 확인
            if self.matcher.template_exists(defeat_template):
                result["battle_ended"] = True
                result["success"] = True
                result["result"] = "defeat"
                result["duration"] = time.time() - start_time
                result["message"] = "전투 패배"
                logger.warning(f"{result['message']} (소요시간: {result['duration']:.1f}초)")
                return result

            time.sleep(check_interval)
            elapsed = time.time() - start_time
            logger.debug(f"전투 진행 중... ({elapsed:.0f}/{timeout}초)")

        # 타임아웃
        result["duration"] = timeout
        result["message"] = "전투 종료 확인 타임아웃"
        logger.error(result["message"])
        return result

    def is_in_battle(
        self,
        battle_ui_template: Optional[Path | str] = None
    ) -> bool:
        """
        현재 전투 중인지 확인

        Args:
            battle_ui_template: 전투 UI 이미지

        Returns:
            전투 중이면 True
        """
        if battle_ui_template is None:
            battle_ui_template = UI_DIR / "battle_ui.png"

        return self.matcher.template_exists(battle_ui_template)
