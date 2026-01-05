"""게임 제어 모듈 - 마우스/키보드 입력"""

import time
import pyautogui
from typing import Optional, Tuple
import logging

from config.settings import (
    WAIT_SCREEN_TRANSITION,
    WAIT_ANIMATION,
)

logger = logging.getLogger(__name__)

# pyautogui 안전 설정
pyautogui.PAUSE = 0.1  # 각 작업 후 기본 대기 시간
pyautogui.FAILSAFE = True  # 마우스를 화면 좌측 상단 코너로 이동하면 중단


class GameController:
    """게임 제어를 위한 마우스/키보드 입력 클래스"""

    def __init__(self):
        """게임 컨트롤러 초기화"""
        logger.info("GameController 초기화")

    def click(
        self,
        x: int,
        y: int,
        clicks: int = 1,
        interval: float = 0.0,
        button: str = 'left',
        duration: float = 0.0
    ) -> None:
        """
        지정된 좌표 클릭

        Args:
            x: X 좌표
            y: Y 좌표
            clicks: 클릭 횟수
            interval: 클릭 간격 (초)
            button: 'left', 'right', 'middle'
            duration: 마우스 이동 시간 (초)
        """
        try:
            pyautogui.click(
                x=x,
                y=y,
                clicks=clicks,
                interval=interval,
                button=button,
                duration=duration
            )
            logger.info(f"클릭: ({x}, {y}), button={button}, clicks={clicks}")
        except Exception as e:
            logger.error(f"클릭 중 오류 발생: {e}")
            raise

    def click_template(
        self,
        location: Optional[Tuple[int, int, int, int]],
        offset_x: int = 0,
        offset_y: int = 0,
        clicks: int = 1,
        wait_after: Optional[float] = None
    ) -> bool:
        """
        템플릿 위치 클릭 (중앙점 기준)

        Args:
            location: 템플릿 위치 (left, top, width, height)
            offset_x: X 오프셋
            offset_y: Y 오프셋
            clicks: 클릭 횟수
            wait_after: 클릭 후 대기 시간 (초)

        Returns:
            성공 여부
        """
        if not location:
            logger.warning("클릭할 템플릿 위치가 None입니다")
            return False

        center_x = location[0] + location[2] // 2 + offset_x
        center_y = location[1] + location[3] // 2 + offset_y

        self.click(center_x, center_y, clicks=clicks)

        if wait_after:
            time.sleep(wait_after)

        return True

    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: str = 'left'
    ) -> None:
        """
        드래그 동작

        Args:
            start_x: 시작 X 좌표
            start_y: 시작 Y 좌표
            end_x: 끝 X 좌표
            end_y: 끝 Y 좌표
            duration: 드래그 시간 (초)
            button: 마우스 버튼
        """
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(
                end_x - start_x,
                end_y - start_y,
                duration=duration,
                button=button
            )
            logger.info(f"드래그: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        except Exception as e:
            logger.error(f"드래그 중 오류 발생: {e}")
            raise

    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> None:
        """
        키보드 키 입력

        Args:
            key: 키 이름 (예: 'enter', 'space', 'esc')
            presses: 입력 횟수
            interval: 입력 간격 (초)
        """
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"키 입력: {key}, presses={presses}")
        except Exception as e:
            logger.error(f"키 입력 중 오류 발생: {e}")
            raise

    def press_keys(self, keys: list[str], interval: float = 0.1) -> None:
        """
        여러 키 순차적으로 입력

        Args:
            keys: 키 이름 리스트
            interval: 키 입력 간격 (초)
        """
        for key in keys:
            self.press_key(key)
            if interval > 0:
                time.sleep(interval)

    def hotkey(self, *keys: str) -> None:
        """
        단축키 입력 (여러 키 동시 입력)

        Args:
            *keys: 키 이름들 (예: 'ctrl', 'c')
        """
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"단축키 입력: {'+'.join(keys)}")
        except Exception as e:
            logger.error(f"단축키 입력 중 오류 발생: {e}")
            raise

    def type_text(self, text: str, interval: float = 0.0) -> None:
        """
        텍스트 입력

        Args:
            text: 입력할 텍스트
            interval: 문자 간격 (초)
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"텍스트 입력: {text}")
        except Exception as e:
            logger.error(f"텍스트 입력 중 오류 발생: {e}")
            raise

    def wait(self, seconds: float) -> None:
        """
        대기

        Args:
            seconds: 대기 시간 (초)
        """
        logger.debug(f"대기 중: {seconds}초")
        time.sleep(seconds)

    def wait_screen_transition(self) -> None:
        """화면 전환 대기"""
        logger.debug("화면 전환 대기")
        time.sleep(WAIT_SCREEN_TRANSITION)

    def wait_animation(self) -> None:
        """애니메이션 대기"""
        logger.debug("애니메이션 대기")
        time.sleep(WAIT_ANIMATION)

    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> any:
        """
        화면 캡처

        Args:
            region: 캡처할 영역 (left, top, width, height). None이면 전체 화면

        Returns:
            PIL Image 객체
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            logger.debug(f"화면 캡처 완료: region={region}")
            return screenshot
        except Exception as e:
            logger.error(f"화면 캡처 중 오류 발생: {e}")
            raise

    def get_screen_size(self) -> Tuple[int, int]:
        """
        화면 크기 가져오기

        Returns:
            (width, height)
        """
        size = pyautogui.size()
        return (size.width, size.height)

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        현재 마우스 위치 가져오기

        Returns:
            (x, y)
        """
        position = pyautogui.position()
        return (position.x, position.y)
