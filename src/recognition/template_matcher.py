"""템플릿 매칭 모듈 - pyautogui.locateOnScreen 래퍼"""

import time
import pyautogui
from pathlib import Path
from typing import Optional, Tuple
import logging
from PIL import Image
import tempfile
import numpy as np

from config.settings import (
    TEMPLATE_MATCHING_CONFIDENCE,
    TEMPLATE_MATCHING_RETRY,
    TEMPLATE_MATCHING_TIMEOUT,
    CURRENT_RESOLUTION,
)

logger = logging.getLogger(__name__)

# OpenCV 사용 가능 여부 확인
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV를 사용할 수 없습니다. 마스크 기반 템플릿 매칭이 제한됩니다.")


class TemplateMatcher:
    """화면에서 템플릿 이미지를 찾는 클래스"""

    def __init__(
        self,
        confidence: float = TEMPLATE_MATCHING_CONFIDENCE,
        retry_count: int = TEMPLATE_MATCHING_RETRY,
        timeout: int = TEMPLATE_MATCHING_TIMEOUT,
        auto_scale: bool = True,
    ):
        """
        Args:
            confidence: 템플릿 매칭 신뢰도 임계값 (0.0 ~ 1.0)
            retry_count: 매칭 실패 시 재시도 횟수
            timeout: 전체 작업 타임아웃 (초)
            auto_scale: 해상도에 맞게 템플릿 자동 스케일링 여부
        """
        self.confidence = confidence
        self.retry_count = retry_count
        self.timeout = timeout
        self.auto_scale = auto_scale

        # 현재 화면 해상도
        screen_size = pyautogui.size()
        self.screen_resolution = f"{screen_size.width}x{screen_size.height}"

    def _scale_template(self, template_path: Path) -> Optional[str]:
        """
        템플릿을 현재 해상도에 맞게 스케일링

        Args:
            template_path: 원본 템플릿 경로

        Returns:
            스케일링된 템플릿의 임시 파일 경로 또는 None
        """
        if not self.auto_scale:
            return str(template_path)

        # 템플릿 경로에서 해상도 추출 (예: assets/templates/2560x1440/buttons/...)
        path_parts = template_path.parts
        template_resolution = None

        for part in path_parts:
            if 'x' in part and part.replace('x', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '') == '':
                template_resolution = part
                break

        # 해상도가 같으면 스케일링 불필요
        if template_resolution == self.screen_resolution or template_resolution is None:
            return str(template_path)

        # 스케일 비율 계산
        try:
            template_width, template_height = map(int, template_resolution.split('x'))
            screen_width, screen_height = map(int, self.screen_resolution.split('x'))

            scale_x = screen_width / template_width
            scale_y = screen_height / template_height

            # 이미지 로드 및 스케일링
            img = Image.open(template_path)
            new_width = int(img.width * scale_x)
            new_height = int(img.height * scale_y)

            scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            scaled_img.save(temp_file.name, 'PNG')
            temp_file.close()

            logger.debug(f"템플릿 스케일링: {template_resolution} → {self.screen_resolution} (비율: {scale_x:.2f}x)")

            return temp_file.name

        except Exception as e:
            logger.warning(f"템플릿 스케일링 실패: {e}, 원본 사용")
            return str(template_path)

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

        # 템플릿 스케일링
        scaled_template_path = self._scale_template(template_path)
        if scaled_template_path is None:
            return None

        start_time = time.time()
        temp_file_to_cleanup = None if scaled_template_path == str(template_path) else scaled_template_path

        try:
            for attempt in range(self.retry_count):
                if time.time() - start_time > self.timeout:
                    logger.warning(f"템플릿 검색 타임아웃: {template_path.name}")
                    return None

                try:
                    # OpenCV가 설치되어 있으면 confidence 사용
                    try:
                        location = pyautogui.locateOnScreen(
                            scaled_template_path,
                            confidence=self.confidence,
                            region=region,
                            grayscale=grayscale
                        )
                    except TypeError as te:
                        # OpenCV 없을 때 confidence 없이 재시도
                        if "confidence" in str(te):
                            logger.warning("OpenCV가 설치되지 않아 confidence 없이 템플릿 매칭합니다. 'pip install opencv-python' 실행 권장")
                            location = pyautogui.locateOnScreen(
                                scaled_template_path,
                                region=region,
                                grayscale=grayscale
                            )
                        else:
                            raise

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

        finally:
            # 임시 파일 정리
            if temp_file_to_cleanup:
                try:
                    import os
                    os.unlink(temp_file_to_cleanup)
                except:
                    pass

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

    def find_template_with_mask(
        self,
        template_path: Path | str,
        mask_path: Optional[Path | str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        threshold: Optional[float] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        마스크를 사용한 템플릿 매칭 (OpenCV 필요)

        마스크는 흰색(255) 영역만 매칭에 사용되고, 검은색(0) 영역은 무시됩니다.
        중앙이 비어있는 캐릭터 마커처럼 배경이 변하는 템플릿에 유용합니다.

        Args:
            template_path: 템플릿 이미지 경로
            mask_path: 마스크 이미지 경로 (흰색=매칭, 검은색=무시)
                       None이면 템플릿의 알파 채널을 마스크로 사용
            region: 검색할 화면 영역 (left, top, width, height)
            threshold: 매칭 임계값 (0.0 ~ 1.0). None이면 self.confidence 사용

        Returns:
            찾은 위치 (left, top, width, height) 또는 None
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV가 설치되지 않아 마스크 기반 매칭을 사용할 수 없습니다.")
            return None

        template_path = Path(template_path)

        if not template_path.exists():
            logger.error(f"템플릿 파일이 존재하지 않습니다: {template_path}")
            return None

        threshold = threshold or self.confidence

        try:
            # 화면 캡처
            screenshot = pyautogui.screenshot(region=region)
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            # 템플릿 로드 (알파 채널 포함)
            template_with_alpha = cv2.imread(str(template_path), cv2.IMREAD_UNCHANGED)

            if template_with_alpha is None:
                logger.error(f"템플릿 이미지를 로드할 수 없습니다: {template_path}")
                return None

            # 마스크 처리
            mask = None
            if mask_path is not None:
                # 명시적으로 마스크 파일이 제공된 경우
                mask_path = Path(mask_path)
                if not mask_path.exists():
                    logger.error(f"마스크 파일이 존재하지 않습니다: {mask_path}")
                    return None
                mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
                if mask is None:
                    logger.error(f"마스크 이미지를 로드할 수 없습니다: {mask_path}")
                    return None
                logger.debug(f"외부 마스크 파일 사용: {mask_path.name}")
            elif template_with_alpha.shape[2] == 4:
                # 템플릿에 알파 채널이 있는 경우 (투명 PNG)
                # 알파 채널을 마스크로 사용
                mask = template_with_alpha[:, :, 3]
                logger.debug("템플릿의 알파 채널을 마스크로 사용")
            else:
                # 마스크 없음
                logger.warning("마스크가 제공되지 않았고 템플릿에 알파 채널도 없습니다. 일반 매칭으로 진행합니다.")

            # 템플릿을 BGR로 변환 (알파 채널 제거)
            if template_with_alpha.shape[2] == 4:
                template = cv2.cvtColor(template_with_alpha, cv2.COLOR_BGRA2BGR)
            else:
                template = template_with_alpha

            # 템플릿 매칭 (TM_CCORR_NORMED 방식, 마스크 지원)
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCORR_NORMED, mask=mask)

            # 최대값 위치 찾기
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 임계값 확인
            if max_val >= threshold:
                # 템플릿 크기
                h, w = template.shape[:2]

                # region이 지정되어 있으면 절대 좌표로 변환
                if region:
                    left = region[0] + max_loc[0]
                    top = region[1] + max_loc[1]
                else:
                    left = max_loc[0]
                    top = max_loc[1]

                location = (left, top, w, h)
                logger.info(f"마스크 기반 템플릿 발견: {template_path.name} at {location} (신뢰도: {max_val:.3f})")
                return location
            else:
                logger.debug(f"마스크 기반 템플릿 매칭 실패: {template_path.name} (최고 신뢰도: {max_val:.3f} < {threshold:.3f})")
                return None

        except Exception as e:
            logger.error(f"마스크 기반 템플릿 매칭 중 오류 발생: {e}")
            return None
