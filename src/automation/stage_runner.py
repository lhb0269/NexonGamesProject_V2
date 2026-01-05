"""스테이지 자동 실행 및 검증 모듈"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from src.verification.movement_checker import MovementChecker
from src.verification.battle_checker import BattleChecker
from src.verification.skill_checker import SkillChecker
from src.verification.reward_checker import RewardChecker
from src.logger.test_logger import TestLogger
from config.settings import (
    BUTTONS_DIR,
    ICONS_DIR,
    UI_DIR,
    WAIT_SCREEN_TRANSITION,
)

logger = logging.getLogger(__name__)


class StageRunner:
    """스테이지 자동 실행 및 검증 클래스"""

    def __init__(
        self,
        matcher: Optional[TemplateMatcher] = None,
        controller: Optional[GameController] = None,
        test_logger: Optional[TestLogger] = None
    ):
        """
        Args:
            matcher: 템플릿 매칭 객체 (None이면 기본값 생성)
            controller: 게임 컨트롤러 객체 (None이면 기본값 생성)
            test_logger: 테스트 로거 객체 (None이면 기본값 생성)
        """
        self.matcher = matcher or TemplateMatcher()
        self.controller = controller or GameController()
        self.test_logger = test_logger or TestLogger("stage_run")

        # Checker 초기화
        self.movement_checker = MovementChecker(self.matcher, self.controller)
        self.battle_checker = BattleChecker(self.matcher, self.controller)
        self.skill_checker = SkillChecker(self.matcher, self.controller)
        self.reward_checker = RewardChecker(self.matcher, self.controller)

        logger.info("StageRunner 초기화 완료")

    def run_normal_1_4(
        self,
        skill_configs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Normal 1-4 스테이지 자동 실행 및 검증

        전체 플로우:
        1. 시작 발판 클릭 → 편성 화면 이동
        2. 출격 버튼 클릭 → 학생 배치
        2.5. 임무 개시 버튼 클릭
        3. 발판 이동 (적이 없는 발판으로)
        3.5. Phase 종료 버튼 클릭
        4. 적 발판 클릭 → 전투 시작
        5. 스킬 사용
        6. 전투 종료 대기
        7. 보상 수령

        Args:
            skill_configs: 스킬 설정 리스트 (None이면 자동 탐지)

        Returns:
            전체 실행 결과 딕셔너리
        """
        logger.info("="*60)
        logger.info("Normal 1-4 스테이지 실행 시작")
        logger.info("="*60)

        overall_success = True

        # ============================================================
        # 1단계: 시작 발판 클릭 → 편성 화면 이동
        # ============================================================
        logger.info("\n[1단계] 시작 발판 클릭")

        start_tile_result = self._click_start_tile()
        self.test_logger.log_check(
            "발판_이동_시작발판",
            start_tile_result["success"],
            start_tile_result["message"],
            start_tile_result
        )

        if not start_tile_result["success"]:
            overall_success = False
            logger.error("시작 발판 클릭 실패, 중단")
            return self._finalize_results(overall_success)

        # ============================================================
        # 2단계: 편성 화면 확인 → 출격 버튼 클릭
        # ============================================================
        logger.info("\n[2단계] 출격 버튼 클릭")

        deploy_result = self._click_deploy_button()
        self.test_logger.log_check(
            "발판_이동_출격",
            deploy_result["success"],
            deploy_result["message"],
            deploy_result
        )

        if not deploy_result["success"]:
            overall_success = False
            logger.error("출격 버튼 클릭 실패, 중단")
            return self._finalize_results(overall_success)

        # ============================================================
        # 2.5단계: 임무 개시 버튼 클릭
        # ============================================================
        logger.info("\n[2.5단계] 임무 개시 버튼 클릭")

        mission_start_result = self._click_mission_start_button()
        self.test_logger.log_check(
            "임무_개시",
            mission_start_result["success"],
            mission_start_result["message"],
            mission_start_result
        )

        if not mission_start_result["success"]:
            overall_success = False
            logger.error("임무 개시 버튼 클릭 실패, 중단")
            return self._finalize_results(overall_success)

        # ============================================================
        # 3단계: 발판 이동 (적이 없는 발판으로)
        # ============================================================
        logger.info("\n[3단계] 발판 이동")

        move_result = self._move_to_enemy_tile()
        self.test_logger.log_check(
            "발판_이동",
            move_result["success"],
            move_result["message"],
            move_result
        )

        if not move_result["success"]:
            overall_success = False
            logger.warning("발판 이동 실패 (선택 사항, 계속 진행)")
            # 발판 이동 실패해도 계속 진행 (바로 적 발판으로 갈 수도 있음)

        # ============================================================
        # 3.5단계: Phase 종료 버튼 클릭
        # ============================================================
        logger.info("\n[3.5단계] Phase 종료")

        phase_end_result = self._end_phase()
        self.test_logger.log_check(
            "Phase_종료",
            phase_end_result["success"],
            phase_end_result["message"],
            phase_end_result
        )

        if not phase_end_result["success"]:
            overall_success = False
            logger.warning("Phase 종료 실패 (선택 사항, 계속 진행)")

        # ============================================================
        # 4단계: 적 발판 클릭 → 전투 진입
        # ============================================================
        logger.info("\n[4단계] 적 발판 클릭 및 전투 진입")

        battle_entry_result = self._enter_battle()
        self.test_logger.log_check(
            "전투_정상_진입",
            battle_entry_result["success"],
            battle_entry_result["message"],
            battle_entry_result
        )

        if not battle_entry_result["success"]:
            overall_success = False
            logger.error("전투 진입 실패, 중단")
            return self._finalize_results(overall_success)

        # ============================================================
        # 5단계: 스킬 사용
        # ============================================================
        logger.info("\n[5단계] 스킬 사용")

        skill_result = self._use_skills(skill_configs)
        self.test_logger.log_check(
            "스킬_사용",
            skill_result["success"],
            skill_result["message"],
            skill_result
        )

        if not skill_result["success"]:
            overall_success = False
            logger.warning("스킬 사용 실패 (전투는 계속)")

        # ============================================================
        # 6단계: 전투 종료 대기
        # ============================================================
        logger.info("\n[6단계] 전투 종료 대기")

        battle_end_result = self.battle_checker.wait_battle_end(timeout=120)
        self.test_logger.log_check(
            "전투_종료",
            battle_end_result["success"],
            battle_end_result["message"],
            battle_end_result
        )

        if not battle_end_result["success"]:
            overall_success = False
            logger.error("전투 종료 확인 실패")
            return self._finalize_results(overall_success)

        # ============================================================
        # 7단계: 보상 수령
        # ============================================================
        logger.info("\n[7단계] 보상 수령")

        reward_result = self.reward_checker.verify_and_claim(wait_for_reward=15)
        self.test_logger.log_check(
            "보상_정상_획득",
            reward_result["success"],
            reward_result["message"],
            reward_result
        )

        if not reward_result["success"]:
            overall_success = False
            logger.warning("보상 수령 실패")

        # ============================================================
        # 최종 결과
        # ============================================================
        return self._finalize_results(overall_success)

    def _click_start_tile(self) -> Dict[str, Any]:
        """시작 발판 클릭 및 편성 화면 전환 검증"""
        start_tile = ICONS_DIR / "start_tile.png"
        formation_screen = UI_DIR / "formation_screen.png"

        return self.movement_checker.verify_movement(
            tile_template=start_tile,
            expected_screen_template=formation_screen,
            timeout=10
        )

    def _click_deploy_button(self) -> Dict[str, Any]:
        """출격 버튼 클릭 및 학생 배치 확인"""
        deploy_button = BUTTONS_DIR / "deploy_button.png"
        stage_map = UI_DIR / "stage_map.png"

        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "screen_changed": False,
            "message": ""
        }

        # 출격 버튼 찾기
        button_location = self.matcher.find_template(deploy_button)
        if not button_location:
            result["message"] = "출격 버튼을 찾을 수 없습니다"
            return result

        result["button_found"] = True

        # 출격 버튼 클릭
        try:
            clicked = self.controller.click_template(
                button_location,
                wait_after=WAIT_SCREEN_TRANSITION
            )
            if not clicked:
                result["message"] = "출격 버튼 클릭 실패"
                return result

            result["button_clicked"] = True

            # 스테이지 맵 화면 확인
            map_appeared = self.matcher.wait_for_template(stage_map, timeout=10)
            if map_appeared:
                result["screen_changed"] = True
                result["success"] = True
                result["message"] = "출격 성공"
            else:
                result["message"] = "스테이지 맵 화면이 나타나지 않음"

        except Exception as e:
            result["message"] = f"출격 버튼 클릭 중 오류: {e}"

        return result

    def _click_mission_start_button(self) -> Dict[str, Any]:
        """임무 개시 버튼 클릭"""
        mission_start_button = BUTTONS_DIR / "mission_start_button.png"

        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "message": ""
        }

        # 임무 개시 버튼 찾기
        button_location = self.matcher.find_template(mission_start_button)
        if not button_location:
            result["message"] = "임무 개시 버튼을 찾을 수 없습니다"
            return result

        result["button_found"] = True

        # 임무 개시 버튼 클릭
        try:
            clicked = self.controller.click_template(
                button_location,
                wait_after=2.0
            )
            if clicked:
                result["button_clicked"] = True
                result["success"] = True
                result["message"] = "임무 개시 성공"
            else:
                result["message"] = "임무 개시 버튼 클릭 실패"

        except Exception as e:
            result["message"] = f"임무 개시 버튼 클릭 중 오류: {e}"

        return result

    def _move_to_enemy_tile(self) -> Dict[str, Any]:
        """적 발판으로 이동 (적이 없는 발판을 거쳐서)"""
        empty_tile = ICONS_DIR / "empty_tile.png"

        result = {
            "success": False,
            "moved": False,
            "message": ""
        }

        # 적이 없는 발판 클릭 (학생 이동)
        tile_location = self.matcher.find_template(empty_tile)
        if not tile_location:
            result["message"] = "이동 가능한 발판을 찾을 수 없습니다"
            logger.warning(result["message"])
            return result

        logger.info(f"이동 가능한 발판 발견: {tile_location}")

        # 발판 클릭
        try:
            clicked = self.controller.click_template(tile_location, wait_after=1.5)
            if clicked:
                result["moved"] = True
                result["success"] = True
                result["message"] = "발판 이동 성공"
                logger.info(result["message"])
            else:
                result["message"] = "발판 클릭 실패"
                logger.error(result["message"])
        except Exception as e:
            result["message"] = f"발판 클릭 중 오류: {e}"
            logger.error(result["message"])

        return result

    def _end_phase(self) -> Dict[str, Any]:
        """Phase 종료 버튼 클릭"""
        phase_end_button = BUTTONS_DIR / "phase_end_button.png"

        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "message": ""
        }

        # Phase 종료 버튼 찾기
        button_location = self.matcher.find_template(phase_end_button)
        if not button_location:
            result["message"] = "Phase 종료 버튼을 찾을 수 없습니다"
            logger.warning(result["message"])
            return result

        result["button_found"] = True
        logger.info(f"Phase 종료 버튼 발견: {button_location}")

        # Phase 종료 버튼 클릭
        try:
            clicked = self.controller.click_template(button_location, wait_after=2.0)
            if clicked:
                result["button_clicked"] = True
                result["success"] = True
                result["message"] = "Phase 종료 성공"
                logger.info(result["message"])
            else:
                result["message"] = "Phase 종료 버튼 클릭 실패"
                logger.error(result["message"])
        except Exception as e:
            result["message"] = f"Phase 종료 버튼 클릭 중 오류: {e}"
            logger.error(result["message"])

        return result

    def _enter_battle(self) -> Dict[str, Any]:
        """적 발판 클릭 및 전투 진입"""
        enemy_tile = ICONS_DIR / "enemy_tile.png"
        battle_ui = UI_DIR / "battle_ui.png"

        result = {
            "success": False,
            "tile_found": False,
            "tile_clicked": False,
            "battle_started": False,
            "message": ""
        }

        # 적 발판 찾기
        tile_location = self.matcher.find_template(enemy_tile)
        if not tile_location:
            result["message"] = "적 발판을 찾을 수 없습니다"
            logger.error(result["message"])
            return result

        result["tile_found"] = True
        logger.info(f"적 발판 발견: {tile_location}")

        # 적 발판 클릭
        try:
            clicked = self.controller.click_template(tile_location, wait_after=2.0)
            if not clicked:
                result["message"] = "적 발판 클릭 실패"
                logger.error(result["message"])
                return result

            result["tile_clicked"] = True
            logger.info("적 발판 클릭 성공")

        except Exception as e:
            result["message"] = f"적 발판 클릭 중 오류: {e}"
            logger.error(result["message"])
            return result

        # 전투 진입 확인 (전투 UI 출현)
        battle_started = self.matcher.wait_for_template(battle_ui, timeout=15)

        if battle_started:
            result["battle_started"] = True
            result["success"] = True
            result["message"] = "전투 진입 성공"
            logger.info(result["message"])
        else:
            result["message"] = "전투 UI가 나타나지 않음"
            logger.warning(result["message"])

        return result

    def _use_skills(
        self,
        skill_configs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """스킬 사용"""
        # 기본 스킬 설정 (없으면 자동으로 스킬 찾기 시도)
        if skill_configs is None:
            skill_configs = self._auto_detect_skills()

        if not skill_configs:
            return {
                "success": False,
                "message": "스킬 설정이 없습니다"
            }

        return self.skill_checker.verify_multiple_skills(
            skill_configs=skill_configs,
            sequential=True
        )

    def _auto_detect_skills(self) -> List[Dict[str, Any]]:
        """자동으로 사용 가능한 스킬 탐지 (기본 설정)"""
        # 기본 학생 스킬 이미지 경로
        default_skills = [
            {"student_name": "학생1", "skill_icon": ICONS_DIR / "skill_student1.png"},
            {"student_name": "학생2", "skill_icon": ICONS_DIR / "skill_student2.png"},
            {"student_name": "학생3", "skill_icon": ICONS_DIR / "skill_student3.png"},
            {"student_name": "학생4", "skill_icon": ICONS_DIR / "skill_student4.png"},
        ]

        # 실제로 존재하는 스킬만 필터링
        valid_skills = []
        for skill in default_skills:
            if Path(skill["skill_icon"]).exists():
                valid_skills.append(skill)

        return valid_skills

    def _finalize_results(self, overall_success: bool) -> Dict[str, Any]:
        """최종 결과 정리 및 로그 저장"""
        logger.info("\n" + "="*60)
        logger.info("스테이지 실행 완료")
        logger.info("="*60)

        result_file = self.test_logger.finalize()

        return {
            "success": overall_success,
            "result_file": str(result_file),
            "results": self.test_logger.get_results()
        }
