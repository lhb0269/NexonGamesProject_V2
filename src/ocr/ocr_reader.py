"""
OCR (Optical Character Recognition) 통합 클래스

Tesseract OCR을 사용하여 게임 화면에서 텍스트와 숫자를 읽습니다.

설치 요구사항:
    pip install pytesseract opencv-python numpy Pillow

    Tesseract 실행 파일 설치:
    - Windows: https://github.com/UB-Mannheim/tesseract/wiki
    - 한글 언어팩(kor.traineddata) 포함 설치 필요
"""

import re
import time
from typing import Optional, List, Tuple, Dict
from PIL import Image
import numpy as np
import cv2

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRReader:
    """통합 OCR 클래스 - 텍스트/숫자 읽기, 이미지 전처리 포함"""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Args:
            tesseract_cmd: Tesseract 실행 파일 경로 (선택)
                          예: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError(
                "pytesseract가 설치되지 않았습니다. "
                "설치: pip install pytesseract"
            )

        # Tesseract 경로 설정 (Windows 기본 경로 자동 인식)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            # Windows 기본 설치 경로
            import os
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path

    # ========================================
    # 이미지 전처리
    # ========================================

    def preprocess_image(
        self,
        image: Image.Image,
        grayscale: bool = True,
        threshold: bool = True,
        denoise: bool = False,
        scale_factor: float = 2.0
    ) -> Image.Image:
        """
        OCR 정확도 향상을 위한 이미지 전처리

        Args:
            image: 원본 이미지
            grayscale: 그레이스케일 변환 여부
            threshold: 이진화 여부
            denoise: 노이즈 제거 여부
            scale_factor: 이미지 확대 배율 (OCR 정확도 향상)

        Returns:
            전처리된 이미지
        """
        # PIL → numpy
        img_array = np.array(image)

        # 1. 이미지 확대 (작은 글자 인식 개선)
        if scale_factor != 1.0:
            new_width = int(img_array.shape[1] * scale_factor)
            new_height = int(img_array.shape[0] * scale_factor)
            img_array = cv2.resize(
                img_array,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )

        # 2. 그레이스케일 변환
        if grayscale and len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # 3. 노이즈 제거
        if denoise:
            img_array = cv2.fastNlMeansDenoising(img_array, h=10)

        # 4. 이진화 (흑백 대비 강화)
        if threshold:
            _, img_array = cv2.threshold(
                img_array,
                0,
                255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

        # numpy → PIL
        return Image.fromarray(img_array)

    # ========================================
    # 텍스트 읽기
    # ========================================

    def read_text(
        self,
        image: Image.Image,
        lang: str = 'kor+eng',
        preprocess: bool = True,
        config: str = '--psm 6'
    ) -> str:
        """
        이미지에서 텍스트 읽기 (한글 + 영어)

        Args:
            image: 입력 이미지
            lang: 언어 설정 ('kor', 'eng', 'kor+eng')
            preprocess: 전처리 수행 여부
            config: Tesseract 설정
                   --psm 6: 단일 텍스트 블록 (기본, 한글 인식률 최고)
                   --psm 7: 단일 텍스트 라인

        Returns:
            추출된 텍스트 (공백 제거됨)
        """
        if preprocess:
            image = self.preprocess_image(image)

        try:
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            return self._clean_text(text)
        except Exception as e:
            print(f"텍스트 읽기 실패: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """텍스트 정리 (공백, 특수문자 제거)"""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # 연속 공백 제거
        return text

    def read_student_name(
        self,
        image: Image.Image,
        bbox: Optional[Tuple[int, int, int, int]] = None,
        normalize: bool = True
    ) -> str:
        """
        학생 이름 읽기

        Args:
            image: 입력 이미지
            bbox: 이름 영역 좌표 (x1, y1, x2, y2)
            normalize: 이름 정규화 여부 (괄호 제거 등)

        Returns:
            학생 이름
        """
        if bbox:
            image = image.crop(bbox)

        name = self.read_text(image, lang='kor+eng')

        if normalize:
            name = self._normalize_student_name(name)

        return name

    def _normalize_student_name(self, name: str) -> str:
        """학생 이름 정규화 (괄호 제거)"""
        name = name.strip()
        # 괄호 제거 (예: "아루 (수영복)" -> "아루")
        name = re.sub(r'\([^)]*\)', '', name).strip()
        return name

    def batch_read_student_names(
        self,
        image: Image.Image,
        bboxes: List[Tuple[int, int, int, int]]
    ) -> List[str]:
        """
        여러 학생 이름 일괄 읽기

        Args:
            image: 입력 이미지
            bboxes: 이름 영역 좌표 리스트

        Returns:
            학생 이름 리스트
        """
        names = []
        for bbox in bboxes:
            name = self.read_student_name(image, bbox)
            names.append(name)
        return names

    # ========================================
    # 숫자 읽기
    # ========================================

    def read_integer(
        self,
        image: Image.Image,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        retries: int = 3,
        preprocess: bool = True
    ) -> Optional[int]:
        """
        이미지에서 정수 읽기 (재시도 로직 포함)

        Args:
            image: 입력 이미지
            min_value: 최소값 (검증용)
            max_value: 최대값 (검증용)
            retries: 재시도 횟수
            preprocess: 전처리 수행 여부

        Returns:
            추출된 정수 또는 None (실패 시)
        """
        for attempt in range(retries):
            if preprocess:
                processed = self.preprocess_image(image)
            else:
                processed = image

            try:
                # Tesseract 설정: 숫자만 인식
                config = '--psm 7 -c tessedit_char_whitelist=0123456789'
                text = pytesseract.image_to_string(processed, config=config)

                # 숫자 추출
                numbers = re.findall(r'\d+', text)
                if not numbers:
                    continue

                value = int(numbers[0])

                # 범위 검증
                if min_value is not None and value < min_value:
                    continue
                if max_value is not None and value > max_value:
                    continue

                return value

            except (ValueError, IndexError):
                continue

            # 재시도 간 대기
            if attempt < retries - 1:
                time.sleep(0.1)

        return None

    def read_cost_value(
        self,
        image: Image.Image,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[int]:
        """
        코스트 값 읽기 (0-10 범위)

        Args:
            image: 입력 이미지
            bbox: 코스트 영역 좌표 (x1, y1, x2, y2)

        Returns:
            코스트 값 또는 None
        """
        if bbox:
            image = image.crop(bbox)

        return self.read_integer(image, min_value=0, max_value=10)

    def read_damage_value(
        self,
        image: Image.Image,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[int]:
        """
        데미지 값 읽기 (0-999999 범위)

        Args:
            image: 입력 이미지
            bbox: 데미지 영역 좌표 (x1, y1, x2, y2)

        Returns:
            데미지 값 또는 None
        """
        if bbox:
            image = image.crop(bbox)

        return self.read_integer(image, min_value=0, max_value=999999)

    def compare_cost_values(
        self,
        before_image: Image.Image,
        after_image: Image.Image,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        코스트 소모량 비교 (스킬 사용 전후)

        Args:
            before_image: 스킬 사용 전 화면
            after_image: 스킬 사용 후 화면
            bbox: 코스트 영역 좌표

        Returns:
            (사용 전 코스트, 사용 후 코스트, 소모량)
        """
        before = self.read_cost_value(before_image, bbox)
        after = self.read_cost_value(after_image, bbox)

        if before is not None and after is not None:
            consumed = before - after
            return (before, after, consumed)

        return (before, after, None)

    def batch_read_damages(
        self,
        image: Image.Image,
        bboxes: List[Tuple[int, int, int, int]]
    ) -> List[Optional[int]]:
        """
        여러 데미지 값 일괄 읽기

        Args:
            image: 입력 이미지
            bboxes: 데미지 영역 좌표 리스트

        Returns:
            데미지 값 리스트
        """
        damages = []
        for bbox in bboxes:
            damage = self.read_damage_value(image, bbox)
            damages.append(damage)
        return damages

    # ========================================
    # 고급 기능 (ROI 기반 읽기)
    # ========================================

    def extract_from_region(
        self,
        image: Image.Image,
        bbox: Tuple[int, int, int, int],
        read_type: str = 'text',
        **kwargs
    ) -> any:
        """
        특정 영역에서 텍스트/숫자 추출

        Args:
            image: 전체 화면 이미지
            bbox: 추출 영역 (x1, y1, x2, y2)
            read_type: 'text', 'integer', 'cost', 'damage'
            **kwargs: read_text() 또는 read_integer()의 추가 인자

        Returns:
            추출된 값
        """
        cropped = image.crop(bbox)

        if read_type == 'text':
            return self.read_text(cropped, **kwargs)
        elif read_type == 'integer':
            return self.read_integer(cropped, **kwargs)
        elif read_type == 'cost':
            return self.read_cost_value(cropped)
        elif read_type == 'damage':
            return self.read_damage_value(cropped)
        else:
            raise ValueError(f"Unknown read_type: {read_type}")

    def extract_student_data(
        self,
        image: Image.Image,
        name_bbox: Tuple[int, int, int, int],
        damage_bbox: Tuple[int, int, int, int]
    ) -> Dict[str, any]:
        """
        학생 데이터 추출 (이름 + 데미지)

        Args:
            image: 전체 화면 이미지
            name_bbox: 이름 영역 좌표
            damage_bbox: 데미지 영역 좌표

        Returns:
            {'name': str, 'damage': Optional[int]}
        """
        name = self.read_student_name(image, name_bbox)
        damage = self.read_damage_value(image, damage_bbox)

        return {
            'name': name,
            'damage': damage
        }
