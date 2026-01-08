"""게이지 면적 기반 코스트 검증 모듈

숫자를 읽지 않고 '상태 변화'를 증명하는 방식
코스트 게이지의 픽셀 면적 변화로 소모 여부를 판단
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class CostGaugeAnalyzer:
    """
    게이지 면적 변화 분석 클래스

    숫자 인식 대신 게이지 영역의 채워진 픽셀 수를 카운트하여
    Before/After 비교로 코스트 소모를 검증

    장점:
    - 많은 픽셀 → 노이즈 평균화
    - 프레임 흔들림 영향 적음
    - OCR/템플릿 매칭 불필요
    - QA 자동화 베스트 프랙티스 (상태 변화 검증)
    """

    def __init__(
        self,
        gauge_color_hsv_range: Optional[Tuple[np.ndarray, np.ndarray]] = None
    ):
        """
        Args:
            gauge_color_hsv_range: 게이지 색상 HSV 범위 (lower, upper)
                                   None이면 기본값 사용 (청록색 게이지)
        """
        # 기본 게이지 색상 범위 (블루 아카이브 코스트 게이지 - 청록색)
        if gauge_color_hsv_range is None:
            # HSV 범위: 청록색 게이지
            # H(색상): 85-100 (청록), S(채도): 100-255, V(명도): 150-255
            self.lower_gauge = np.array([85, 100, 150])
            self.upper_gauge = np.array([100, 255, 255])
        else:
            self.lower_gauge, self.upper_gauge = gauge_color_hsv_range

        logger.info("CostGaugeAnalyzer 초기화 완료")
        logger.debug(f"게이지 HSV 범위: {self.lower_gauge} ~ {self.upper_gauge}")

    def count_gauge_pixels(
        self,
        image: np.ndarray,
        region: Tuple[int, int, int, int]
    ) -> int:
        """
        게이지 영역의 채워진 픽셀 수 카운트

        Args:
            image: BGR 이미지 (OpenCV 형식) 또는 RGB (PIL 형식)
            region: (left, top, right, bottom) 영역

        Returns:
            채워진 픽셀 수
        """
        left, top, right, bottom = region

        # 영역 크롭
        roi = image[top:bottom, left:right]

        if roi.size == 0:
            logger.warning(f"빈 ROI 영역: {region}")
            return 0

        # RGB → BGR 변환 (PIL에서 온 경우)
        # OpenCV는 BGR, PIL은 RGB
        if len(roi.shape) == 3 and roi.shape[2] == 3:
            # 간단한 휴리스틱: 파란색이 강하면 BGR, 빨간색이 강하면 RGB
            # 실제로는 항상 BGR로 통일하는 것이 안전
            try:
                roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
            except:
                roi_bgr = roi
        else:
            roi_bgr = roi

        # HSV 변환
        try:
            hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
        except Exception as e:
            logger.error(f"HSV 변환 실패: {e}")
            return 0

        # 게이지 색상 마스크
        mask = cv2.inRange(hsv, self.lower_gauge, self.upper_gauge)

        # 흰색 픽셀 수 카운트 (255인 픽셀 = 게이지 영역)
        pixel_count = np.count_nonzero(mask)

        logger.debug(f"게이지 픽셀 수: {pixel_count} (영역: {region})")

        return pixel_count

    def verify_gauge_decreased(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray,
        region: Tuple[int, int, int, int],
        min_decrease_threshold: int = 100
    ) -> Dict[str, any]:
        """
        게이지 감소 여부 검증

        Before/After 이미지의 게이지 면적을 비교하여
        코스트가 소모되었는지 확인

        Args:
            before_image: 액션 전 이미지 (BGR)
            after_image: 액션 후 이미지 (BGR)
            region: 게이지 영역 (left, top, right, bottom)
            min_decrease_threshold: 최소 감소 픽셀 수 (기본 100)

        Returns:
            검증 결과 딕셔너리
            {
                "success": bool,           # 코스트 소모 확인됨
                "before_pixels": int,      # Before 픽셀 수
                "after_pixels": int,       # After 픽셀 수
                "decreased_pixels": int,   # 감소한 픽셀 수
                "decreased_ratio": float,  # 감소 비율 (0.0 ~ 1.0)
                "message": str
            }
        """
        result = {
            "success": False,
            "before_pixels": 0,
            "after_pixels": 0,
            "decreased_pixels": 0,
            "decreased_ratio": 0.0,
            "message": ""
        }

        # Before 픽셀 카운트
        try:
            before_pixels = self.count_gauge_pixels(before_image, region)
            result["before_pixels"] = before_pixels
        except Exception as e:
            result["message"] = f"Before 이미지 분석 실패: {e}"
            logger.error(result["message"])
            return result

        # After 픽셀 카운트
        try:
            after_pixels = self.count_gauge_pixels(after_image, region)
            result["after_pixels"] = after_pixels
        except Exception as e:
            result["message"] = f"After 이미지 분석 실패: {e}"
            logger.error(result["message"])
            return result

        # 감소량 계산
        decreased = before_pixels - after_pixels
        result["decreased_pixels"] = decreased

        # 감소 비율 계산
        if before_pixels > 0:
            ratio = decreased / before_pixels
            result["decreased_ratio"] = ratio

        # 검증
        if decreased < min_decrease_threshold:
            result["message"] = (
                f"게이지 감소 부족: {decreased}px < {min_decrease_threshold}px "
                f"(Before: {before_pixels}px, After: {after_pixels}px)"
            )
            logger.warning(result["message"])
            return result

        # 성공
        result["success"] = True
        result["message"] = (
            f"코스트 소모 확인 ✓ "
            f"({decreased}px 감소, {ratio:.1%} 감소)"
        )
        logger.info(result["message"])
        logger.info(f"  Before: {before_pixels}px → After: {after_pixels}px")

        return result

    def verify_gauge_decreased_from_screenshots(
        self,
        before_screenshot: Image.Image,
        after_screenshot: Image.Image,
        region: Tuple[int, int, int, int],
        min_decrease_threshold: int = 100
    ) -> Dict[str, any]:
        """
        PIL 스크린샷으로부터 게이지 감소 검증

        Args:
            before_screenshot: PIL Image (Before)
            after_screenshot: PIL Image (After)
            region: 게이지 영역
            min_decrease_threshold: 최소 감소 픽셀 수

        Returns:
            검증 결과 딕셔너리
        """
        # PIL → NumPy (RGB)
        before_array = np.array(before_screenshot)
        after_array = np.array(after_screenshot)

        # RGB → BGR 변환
        before_bgr = cv2.cvtColor(before_array, cv2.COLOR_RGB2BGR)
        after_bgr = cv2.cvtColor(after_array, cv2.COLOR_RGB2BGR)

        return self.verify_gauge_decreased(
            before_bgr,
            after_bgr,
            region,
            min_decrease_threshold
        )
