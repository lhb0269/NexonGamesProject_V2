"""스테이지 자동 실행 및 검증 모듈"""

import logging
from typing import Optional, Dict, Any

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

    def run_normal_1_4(self) -> Dict[str, Any]:
        """
        Normal 1-4 스테이지 자동 실행 및 검증

        전체 플로우:
        1. 시작 발판 클릭 → 편성 화면 이동
        2. 출격 버튼 클릭 → 스테이지 맵
        2.5. 임무 개시 버튼 클릭
        3. 발판 클릭 (이동 가능한 발판 - 적 유무 상관없이)
           - 적이 있는 발판 → 바로 전투 진입 (3.5 스킵)
           - 적이 없는 발판 → 학생 이동
        3.5. [적이 없었을 경우만] Phase 종료 버튼 클릭
        4. 전투 진입 확인
        5. 전투 종료 확인 (Victory)
        6. 통계 버튼 클릭 → 데미지 기록 창 확인

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
        # 3단계: 발판 클릭 (이동 가능한 발판)
        # ============================================================
        logger.info("\n[3단계] 발판 클릭")

        tile_result = self._click_movable_tile()
        self.test_logger.log_check(
            "발판_클릭",
            tile_result["success"],
            tile_result["message"],
            tile_result
        )

        if not tile_result["success"]:
            overall_success = False
            logger.error("발판 클릭 실패, 중단")
            return self._finalize_results(overall_success)

        has_enemy = tile_result.get("has_enemy", False)
        battle_started = tile_result.get("battle_started", False)

        # ============================================================
        # 3.5단계: Phase 종료 (적이 없었을 경우만)
        # ============================================================
        if not has_enemy and not battle_started:
            logger.info("\n[3.5단계] Phase 종료 (적이 없는 발판이었음)")

            phase_end_result = self._end_phase()
            self.test_logger.log_check(
                "Phase_종료",
                phase_end_result["success"],
                phase_end_result["message"],
                phase_end_result
            )

            if not phase_end_result["success"]:
                overall_success = False
                logger.warning("Phase 종료 실패")
        else:
            logger.info("\n[3.5단계 스킵] 적이 있는 발판이었음, 전투 진입됨")

        # ============================================================
        # 4단계: 전투 진입 확인
        # ============================================================
        logger.info("\n[4단계] 전투 진입 확인")

        if not battle_started:
            # 아직 전투가 시작되지 않았다면 전투 UI 대기
            battle_entry_result = self._verify_battle_entry()
            self.test_logger.log_check(
                "전투_정상_진입",
                battle_entry_result["success"],
                battle_entry_result["message"],
                battle_entry_result
            )

            if not battle_entry_result["success"]:
                overall_success = False
                logger.error("전투 진입 확인 실패, 중단")
                return self._finalize_results(overall_success)
        else:
            logger.info("전투 이미 진입됨 (3단계에서 확인)")
            self.test_logger.log_check(
                "전투_정상_진입",
                True,
                "전투 진입 확인 (3단계에서 적 발판 클릭)",
                {"battle_started": True}
            )

        # ============================================================
        # 5단계: 전투 종료 확인 (Victory)
        # ============================================================
        logger.info("\n[5단계] 전투 종료 확인")

        battle_end_result = self._wait_for_victory(timeout=120)
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
        # 6단계: 통계 버튼 클릭 → 데미지 기록 확인
        # ============================================================
        logger.info("\n[6단계] 통계 버튼 클릭 및 데미지 기록 확인")

        damage_result = self._verify_damage_report()
        self.test_logger.log_check(
            "데미지_기록_확인",
            damage_result["success"],
            damage_result["message"],
            damage_result
        )

        if not damage_result["success"]:
            overall_success = False
            logger.warning("데미지 기록 확인 실패")

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

    def _click_movable_tile(self) -> Dict[str, Any]:
        """이동 가능한 발판 클릭 (적 유무 상관없이)"""
        empty_tile = ICONS_DIR / "empty_tile.png"
        enemy_tile = ICONS_DIR / "enemy_tile.png"
        battle_ui = UI_DIR / "battle_ui.png"

        result = {
            "success": False,
            "tile_clicked": False,
            "has_enemy": False,
            "battle_started": False,
            "message": ""
        }

        # 1. 먼저 적이 있는 발판 찾기
        enemy_location = self.matcher.find_template(enemy_tile)

        if enemy_location:
            logger.info(f"적이 있는 발판 발견: {enemy_location}")
            result["has_enemy"] = True
            tile_to_click = enemy_location
        else:
            # 2. 적이 없으면 빈 발판 찾기
            empty_location = self.matcher.find_template(empty_tile)
            if not empty_location:
                result["message"] = "이동 가능한 발판을 찾을 수 없습니다"
                logger.error(result["message"])
                return result

            logger.info(f"적이 없는 발판 발견: {empty_location}")
            result["has_enemy"] = False
            tile_to_click = empty_location

        # 3. 발판 클릭
        try:
            clicked = self.controller.click_template(tile_to_click, wait_after=2.0)
            if not clicked:
                result["message"] = "발판 클릭 실패"
                logger.error(result["message"])
                return result

            result["tile_clicked"] = True
            logger.info("발판 클릭 성공")

            # 4. 적이 있었다면 전투 진입 확인
            if result["has_enemy"]:
                battle_started = self.matcher.wait_for_template(battle_ui, timeout=10)
                if battle_started:
                    result["battle_started"] = True
                    result["success"] = True
                    result["message"] = "적 발판 클릭 → 전투 진입 성공"
                    logger.info(result["message"])
                else:
                    result["message"] = "적 발판 클릭했으나 전투 UI 미출현"
                    logger.warning(result["message"])
            else:
                result["success"] = True
                result["message"] = "빈 발판 클릭 → 학생 이동 성공"
                logger.info(result["message"])

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

    def _verify_battle_entry(self) -> Dict[str, Any]:
        """전투 진입 확인 (전투 UI 대기)"""
        battle_ui = UI_DIR / "battle_ui.png"

        result = {
            "success": False,
            "battle_ui_found": False,
            "message": ""
        }

        logger.info("전투 UI 출현 대기 중...")

        # 전투 UI 대기
        battle_ui_appeared = self.matcher.wait_for_template(battle_ui, timeout=15)

        if battle_ui_appeared:
            result["battle_ui_found"] = True
            result["success"] = True
            result["message"] = "전투 진입 확인"
            logger.info(result["message"])
        else:
            result["message"] = "전투 UI가 15초 내에 나타나지 않음"
            logger.error(result["message"])

        return result

    def _wait_for_victory(self, timeout: int = 120) -> Dict[str, Any]:
        """전투 종료 대기 (Victory 화면 확인)"""
        victory_screen = UI_DIR / "victory.png"

        result = {
            "success": False,
            "victory_found": False,
            "duration": 0.0,
            "message": ""
        }

        logger.info(f"전투 종료 대기 중 (최대 {timeout}초)...")
        import time
        start_time = time.time()

        # Victory 화면 대기
        victory_appeared = self.matcher.wait_for_template(
            victory_screen,
            timeout=timeout,
            check_interval=2.0
        )

        result["duration"] = time.time() - start_time

        if victory_appeared:
            result["victory_found"] = True
            result["success"] = True
            result["message"] = f"전투 승리 확인 (소요시간: {result['duration']:.1f}초)"
            logger.info(result["message"])
        else:
            result["message"] = f"Victory 화면이 {timeout}초 내에 나타나지 않음"
            logger.error(result["message"])

        return result

    def _verify_damage_report(self) -> Dict[str, Any]:
        """통계 버튼 클릭 및 데미지 기록 확인"""
        battle_log_button = BUTTONS_DIR / "battle_log_button.png"
        damage_report = UI_DIR / "damage_report.png"

        result = {
            "success": False,
            "button_found": False,
            "button_clicked": False,
            "report_found": False,
            "message": ""
        }

        # 1. 통계 버튼 찾기
        button_location = self.matcher.find_template(battle_log_button)
        if not button_location:
            result["message"] = "통계 버튼을 찾을 수 없습니다"
            logger.warning(result["message"])
            return result

        result["button_found"] = True
        logger.info(f"통계 버튼 발견: {button_location}")

        # 2. 통계 버튼 클릭
        try:
            clicked = self.controller.click_template(button_location, wait_after=2.0)
            if not clicked:
                result["message"] = "통계 버튼 클릭 실패"
                logger.error(result["message"])
                return result

            result["button_clicked"] = True
            logger.info("통계 버튼 클릭 성공")

        except Exception as e:
            result["message"] = f"통계 버튼 클릭 중 오류: {e}"
            logger.error(result["message"])
            return result

        # 3. 데미지 기록 창 확인
        report_appeared = self.matcher.wait_for_template(damage_report, timeout=10)

        if report_appeared:
            result["report_found"] = True
            result["success"] = True
            result["message"] = "데미지 기록 창 출현 확인"
            logger.info(result["message"])
        else:
            result["message"] = "데미지 기록 창이 나타나지 않음"
            logger.warning(result["message"])

        return result

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
