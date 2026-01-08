"""템플릿 매칭 기반 코스트 인식 모듈 (OCR 대체)"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import Image

from config.settings import UI_DIR

logger = logging.getLogger(__name__)


class CostRecognizer:
    """
    템플릿 매칭 기반 코스트 숫자 인식 클래스

    게임 UI의 코스트 숫자는 커스텀 폰트와 특수한 시각적 스타일을 가지므로,
    OCR보다 템플릿 분류 방식이 더 안정적이고 정확함.

    특징:
    - 코스트 값: 2~5 (고정 범위)
    - 흰색 숫자 + 짙은 남색 원형 배경 + 흰색 외곽선
    - 템플릿 매칭으로 가장 유사한 숫자 분류
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Args:
            template_dir: 코스트 템플릿 디렉토리 (None이면 기본 경로 사용)
        """
        self.template_dir = template_dir or UI_DIR
        self.templates = self._load_templates()

        if not self.templates:
            logger.warning("코스트 템플릿을 로드하지 못했습니다. 템플릿 파일을 확인하세요.")

    def _load_templates(self) -> Dict[int, np.ndarray]:
        """
        코스트 숫자 템플릿 로드 (2~5)

        Returns:
            {숫자: 전처리된 템플릿 이미지} 딕셔너리
        """
        templates = {}

        for cost_value in range(2, 6):  # 2, 3, 4, 5
            template_path = self.template_dir / f"cost_{cost_value}.png"

            if not template_path.exists():
                logger.warning(f"템플릿 파일 없음: {template_path}")
                continue

            try:
                # PIL로 로드 후 OpenCV 형식으로 변환
                pil_img = Image.open(template_path)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

                # 전처리 (흰색 숫자 추출)
                processed = self._preprocess_cost_image(img)

                templates[cost_value] = processed
                logger.info(f"템플릿 로드 성공: cost_{cost_value}.png")

            except Exception as e:
                logger.error(f"템플릿 로드 실패 ({template_path}): {e}")

        return templates

    def _preprocess_cost_image(self, img: np.ndarray) -> np.ndarray:
        """
        코스트 이미지 전처리 (흰색 숫자만 추출)

        게임 UI 특성:
        - 흰색 숫자 (HSV: V 높음, S 낮음)
        - 파란 원형 배경 제거 필요
        - 흰색 외곽선 포함

        Args:
            img: BGR 이미지

        Returns:
            전처리된 이진 이미지
        """
        # HSV 변환
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 흰색 영역 마스크
        # H(색상): 전 범위, S(채도): 낮음, V(명도): 높음
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])

        mask = cv2.inRange(hsv, lower_white, upper_white)

        # 모폴로지 연산: 노이즈 제거 및 숫자 두께 약간 증가
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask

    def recognize_cost(
        self,
        roi_image: np.ndarray,
        confidence_threshold: float = 0.6
    ) -> Tuple[Optional[int], float]:
        """
        ROI 이미지에서 코스트 값 인식

        Args:
            roi_image: 코스트 영역 이미지 (BGR or RGB)
            confidence_threshold: 최소 신뢰도 (0.0 ~ 1.0)

        Returns:
            (인식된 코스트 값, 신뢰도)
            인식 실패 시 (None, 0.0)
        """
        if not self.templates:
            logger.error("로드된 템플릿이 없습니다")
            return None, 0.0

        # RGB -> BGR 변환 (필요시)
        if len(roi_image.shape) == 3 and roi_image.shape[2] == 3:
            # PIL 이미지는 RGB, OpenCV는 BGR
            if isinstance(roi_image, np.ndarray):
                # 이미 OpenCV BGR이면 그대로, PIL RGB면 변환
                try:
                    roi_bgr = cv2.cvtColor(roi_image, cv2.COLOR_RGB2BGR)
                except:
                    roi_bgr = roi_image
            else:
                roi_bgr = roi_image
        else:
            roi_bgr = roi_image

        # 전처리
        try:
            processed_roi = self._preprocess_cost_image(roi_bgr)
        except Exception as e:
            logger.error(f"ROI 전처리 실패: {e}")
            return None, 0.0

        # 각 템플릿과 매칭
        best_match = None
        best_score = 0.0
        match_results = {}

        for cost_value, template in self.templates.items():
            try:
                # 템플릿 크기 조정 (ROI와 크기가 다를 경우)
                if processed_roi.shape[:2] != template.shape[:2]:
                    template_resized = cv2.resize(
                        template,
                        (processed_roi.shape[1], processed_roi.shape[0]),
                        interpolation=cv2.INTER_AREA
                    )
                else:
                    template_resized = template

                # 템플릿 매칭 (정규화된 상관계수)
                result = cv2.matchTemplate(
                    processed_roi,
                    template_resized,
                    cv2.TM_CCOEFF_NORMED
                )

                score = result.max()
                match_results[cost_value] = score

                if score > best_score:
                    best_score = score
                    best_match = cost_value

            except Exception as e:
                logger.warning(f"템플릿 매칭 실패 (cost_{cost_value}): {e}")

        # 결과 로깅
        logger.debug(f"매칭 결과: {match_results}")

        # 신뢰도 체크
        if best_score < confidence_threshold:
            logger.warning(
                f"코스트 인식 신뢰도 부족: {best_score:.2f} < {confidence_threshold:.2f}"
            )
            return None, best_score

        logger.info(f"코스트 인식 성공: {best_match} (신뢰도: {best_score:.2f})")
        return best_match, best_score

    def recognize_cost_from_screenshot(
        self,
        screenshot: Image.Image,
        region: Tuple[int, int, int, int],
        confidence_threshold: float = 0.6
    ) -> Tuple[Optional[int], float]:
        """
        스크린샷에서 특정 영역의 코스트 인식

        Args:
            screenshot: PIL Image 스크린샷
            region: (left, top, right, bottom) 영역
            confidence_threshold: 최소 신뢰도

        Returns:
            (인식된 코스트 값, 신뢰도)
        """
        # 영역 크롭
        roi = screenshot.crop(region)

        # NumPy 배열로 변환
        roi_array = np.array(roi)

        # 인식
        return self.recognize_cost(roi_array, confidence_threshold)
