"""템플릿 매칭 모듈 - pyautogui.locateOnScreen 래퍼"""

import time
import pyautogui
from pathlib import Path
from typing import Optional, Tuple
import logging

from config.settings import (
    TEMPLATE_MATCHING_CONFIDENCE,
    TEMPLATE_MATCHING_RETRY,
    TEMPLATE_MATCHING_TIMEOUT,
)

logger = logging.getLogger(__name__)


class TemplateMatcher:
    """화면에서 템플릿 이미지를 찾는 클래스"""

    def __init__(
        self,
        confidence: float = TEMPLATE_MATCHING_CONFIDENCE,
        retry_count: int = TEMPLATE_MATCHING_RETRY,
        timeout: int = TEMPLATE_MATCHING_TIMEOUT,
    ):
        """
        Args:
            confidence: 템플릿 매칭 신뢰도 임계값 (0.0 ~ 1.0)
            retry_count: 매칭 실패 시 재시도 횟수
            timeout: 전체 작업 타임아웃 (초)
        """
        self.confidence = confidence
        self.retry_count = retry_count
        self.timeout = timeout

    def find_template(
        self,
        template_path: Path | str,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        화면에서 템플릿 이미지 찾기

        Args:
            template_path: 템플릿 이미지 경로
            region: 검색할 화면 영역 (left, top, width, height). None이면 전체 화면
            grayscale: 그레이스케일 변환 여부 (성능 향상)

        Returns:
            찾은 위치 (left, top, width, height) 또는 None
        """
        template_path = Path(template_path)

        if not template_path.exists():
            logger.error(f"템플릿 파일이 존재하지 않습니다: {template_path}")
            return None

        start_time = time.time()

        for attempt in range(self.retry_count):
            if time.time() - start_time > self.timeout:
                logger.warning(f"템플릿 검색 타임아웃: {template_path.name}")
                return None

            try:
                location = pyautogui.locateOnScreen(
                    str(template_path),
                    confidence=self.confidence,
                    region=region,
                    grayscale=grayscale
                )

                if location:
                    logger.info(f"템플릿 발견: {template_path.name} at {location}")
                    return location

            except pyautogui.ImageNotFoundException:
                pass
            except Exception as e:
                logger.error(f"템플릿 매칭 중 오류 발생: {e}")

            # 재시도 전 짧은 대기
            if attempt < self.retry_count - 1:
                time.sleep(0.5)

        logger.debug(f"템플릿을 찾지 못함: {template_path.name}")
        return None

    def find_template_center(
        self,
        template_path: Path | str,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> Optional[Tuple[int, int]]:
        """
        템플릿의 중앙 좌표 찾기 (클릭용)

        Args:
            template_path: 템플릿 이미지 경로
            region: 검색할 화면 영역
            grayscale: 그레이스케일 변환 여부

        Returns:
            중앙 좌표 (x, y) 또는 None
        """
        location = self.find_template(template_path, region, grayscale)

        if location:
            center_x = location[0] + location[2] // 2
            center_y = location[1] + location[3] // 2
            return (center_x, center_y)

        return None

    def wait_for_template(
        self,
        template_path: Path | str,
        timeout: Optional[int] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        check_interval: float = 0.5,
        grayscale: bool = True
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        템플릿이 화면에 나타날 때까지 대기

        Args:
            template_path: 템플릿 이미지 경로
            timeout: 대기 시간 (초). None이면 기본값 사용
            region: 검색할 화면 영역
            check_interval: 확인 간격 (초)
            grayscale: 그레이스케일 변환 여부

        Returns:
            찾은 위치 또는 None (타임아웃)
        """
        timeout = timeout or self.timeout
        start_time = time.time()

        logger.info(f"템플릿 대기 중: {Path(template_path).name}")

        while time.time() - start_time < timeout:
            location = self.find_template(template_path, region, grayscale)
            if location:
                return location
            time.sleep(check_interval)

        logger.warning(f"템플릿 대기 타임아웃: {Path(template_path).name}")
        return None

    def wait_for_template_disappear(
        self,
        template_path: Path | str,
        timeout: Optional[int] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        check_interval: float = 0.5,
        grayscale: bool = True
    ) -> bool:
        """
        템플릿이 화면에서 사라질 때까지 대기

        Args:
            template_path: 템플릿 이미지 경로
            timeout: 대기 시간 (초)
            region: 검색할 화면 영역
            check_interval: 확인 간격 (초)
            grayscale: 그레이스케일 변환 여부

        Returns:
            성공적으로 사라졌으면 True, 타임아웃이면 False
        """
        timeout = timeout or self.timeout
        start_time = time.time()

        logger.info(f"템플릿 소멸 대기 중: {Path(template_path).name}")

        while time.time() - start_time < timeout:
            location = self.find_template(template_path, region, grayscale)
            if not location:
                logger.info(f"템플릿 사라짐: {Path(template_path).name}")
                return True
            time.sleep(check_interval)

        logger.warning(f"템플릿 소멸 대기 타임아웃: {Path(template_path).name}")
        return False

    def template_exists(
        self,
        template_path: Path | str,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> bool:
        """
        템플릿이 화면에 존재하는지 빠르게 확인

        Args:
            template_path: 템플릿 이미지 경로
            region: 검색할 화면 영역
            grayscale: 그레이스케일 변환 여부

        Returns:
            존재하면 True, 없으면 False
        """
        location = self.find_template(template_path, region, grayscale)
        return location is not None
