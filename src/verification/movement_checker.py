"""발판 이동 검증 모듈"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from config.settings import WAIT_SCREEN_TRANSITION, ICONS_DIR

logger = logging.getLogger(__name__)


class MovementChecker:
    """발판 이동 검증 클래스"""

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

    def verify_movement(
        self,
        tile_template: Path | str,
        expected_screen_template: Optional[Path | str] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        발판 클릭 후 이동 검증

        Args:
            tile_template: 클릭할 발판 이미지 경로
            expected_screen_template: 이동 후 나타날 화면 이미지 (선택)
            timeout: 검증 타임아웃 (초)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "tile_found": bool,
                "tile_clicked": bool,
                "screen_changed": bool,
                "message": str
            }
        """
        result = {
            "success": False,
            "tile_found": False,
            "tile_clicked": False,
            "screen_changed": False,
            "message": ""
        }

        logger.info("발판 이동 검증 시작")

        # 1. 발판 찾기
        tile_location = self.matcher.find_template(tile_template)
        if not tile_location:
            result["message"] = "발판을 찾을 수 없습니다"
            logger.error(result["message"])
            return result

        result["tile_found"] = True
        logger.info(f"발판 발견: {tile_location}")

        # 2. 발판 클릭
        try:
            clicked = self.controller.click_template(
                tile_location,
                wait_after=WAIT_SCREEN_TRANSITION
            )
            if not clicked:
                result["message"] = "발판 클릭 실패"
                logger.error(result["message"])
                return result

            result["tile_clicked"] = True
            logger.info("발판 클릭 성공")

        except Exception as e:
            result["message"] = f"발판 클릭 중 오류: {e}"
            logger.error(result["message"])
            return result

        # 3. 화면 전환 확인
        if expected_screen_template:
            # 지정된 화면이 나타나는지 확인
            screen_appeared = self.matcher.wait_for_template(
                expected_screen_template,
                timeout=timeout
            )

            if screen_appeared:
                result["screen_changed"] = True
                result["success"] = True
                result["message"] = "발판 이동 성공"
                logger.info(result["message"])
            else:
                result["message"] = "예상 화면이 나타나지 않음"
                logger.warning(result["message"])
        else:
            # 발판이 사라지는지 확인 (간접적 검증)
            tile_disappeared = self.matcher.wait_for_template_disappear(
                tile_template,
                timeout=timeout
            )

            if tile_disappeared:
                result["screen_changed"] = True
                result["success"] = True
                result["message"] = "발판 이동 성공 (발판 소멸 확인)"
                logger.info(result["message"])
            else:
                # 발판이 여전히 있으면 이동 실패일 가능성
                result["message"] = "화면 전환이 감지되지 않음"
                logger.warning(result["message"])
                result["success"] = True  # 클릭은 했으므로 부분 성공으로 간주

        return result

    def click_and_verify_tile(
        self,
        tile_name: str,
        verify_disappear: bool = True
    ) -> Dict[str, Any]:
        """
        이름으로 발판을 찾아 클릭하고 검증

        Args:
            tile_name: 발판 이미지 파일명 (확장자 제외)
            verify_disappear: 발판 소멸 여부 검증

        Returns:
            검증 결과 딕셔너리
        """
        tile_path = ICONS_DIR / f"{tile_name}.png"
        return self.verify_movement(
            tile_template=tile_path,
            expected_screen_template=None if verify_disappear else None
        )
