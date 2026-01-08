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

    def verify_battle_entry_multi_condition(
        self,
        timeout: int = 15,
        required_matches: int = 2
    ) -> Dict[str, Any]:
        """
        다중 조건으로 전투 진입 검증 (개선된 방식)

        전투 화면 특유의 UI 요소 3가지를 확인:
        1. battle_ui.png - 전투 UI 전체
        2. stage_info_ui.png - 상단 스테이지 정보 UI
        3. pause_button.png - 일시정지 버튼

        3개 중 required_matches개 이상 인식되면 전투 진입으로 판단
        (기본값: 2개 이상)

        Args:
            timeout: 최대 대기 시간 (초)
            required_matches: 필요한 최소 매칭 개수 (기본 2)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,
                "battle_started": bool,
                "conditions_met": Dict[str, bool],  # 각 조건별 결과
                "match_count": int,  # 매칭된 조건 개수
                "message": str
            }
        """
        result = {
            "success": False,
            "battle_started": False,
            "conditions_met": {},
            "match_count": 0,
            "message": ""
        }

        logger.info("전투 진입 다중 조건 검증 시작")

        # 전투 UI 요소 템플릿 정의
        battle_elements = {
            "battle_ui": UI_DIR / "battle_ui.png",
            "stage_info": UI_DIR / "stage_info_ui.png",
            "pause_button": BUTTONS_DIR / "pause_button.png"
        }

        # 시작 시간
        start_time = time.time()
        check_interval = 0.5  # 0.5초마다 확인

        while time.time() - start_time < timeout:
            conditions_met = {}
            match_count = 0

            # 각 UI 요소 확인
            for element_name, template_path in battle_elements.items():
                try:
                    # 템플릿 파일 존재 확인
                    if not Path(template_path).exists():
                        logger.warning(f"템플릿 파일 없음: {template_path} (건너뜀)")
                        conditions_met[element_name] = None  # 파일 없음
                        continue

                    # 템플릿 매칭 시도
                    exists = self.matcher.template_exists(template_path)
                    conditions_met[element_name] = exists

                    if exists:
                        match_count += 1
                        logger.info(f"✓ {element_name} 인식 성공")
                    else:
                        logger.debug(f"✗ {element_name} 인식 실패")

                except Exception as e:
                    logger.warning(f"{element_name} 확인 중 오류: {e}")
                    conditions_met[element_name] = False

            # 결과 업데이트
            result["conditions_met"] = conditions_met
            result["match_count"] = match_count

            # 충분한 조건 충족 시 성공
            if match_count >= required_matches:
                result["battle_started"] = True
                result["success"] = True
                result["message"] = f"전투 진입 확인 ({match_count}/{len(battle_elements)}개 조건 충족)"
                logger.info(result["message"])
                logger.info(f"충족 조건: {[k for k, v in conditions_met.items() if v is True]}")
                return result

            # 재시도 대기
            time.sleep(check_interval)

        # 타임아웃
        result["message"] = f"전투 진입 확인 실패 (타임아웃: {match_count}/{required_matches}개 조건만 충족)"
        logger.warning(result["message"])
        logger.warning(f"충족 조건: {[k for k, v in conditions_met.items() if v is True]}")
        logger.warning(f"미충족 조건: {[k for k, v in conditions_met.items() if v is False]}")

        return result
