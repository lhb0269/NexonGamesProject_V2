"""스킬 사용 검증 모듈"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.recognition.template_matcher import TemplateMatcher
from src.automation.game_controller import GameController
from config.settings import (
    SKILL_CHECK_INTERVAL,
    MAX_SKILL_WAIT_TIME,
    ICONS_DIR
)

logger = logging.getLogger(__name__)


class SkillChecker:
    """스킬 사용 검증 클래스"""

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
