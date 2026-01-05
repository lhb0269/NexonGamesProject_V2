"""테스트 결과 로깅 모듈"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict
from PIL import Image

from config.settings import (
    LOGS_DIR,
    LOG_LEVEL,
    SAVE_SCREENSHOTS_ON_ERROR,
    SCREENSHOT_FORMAT,
)


class TestLogger:
    """테스트 결과를 기록하는 로거 클래스"""

    def __init__(self, test_name: str = "blue_archive_test"):
        """
        Args:
            test_name: 테스트 이름 (로그 파일명에 사용)
        """
        self.test_name = test_name
        self.start_time = datetime.now()
        self.test_id = self.start_time.strftime("%Y%m%d_%H%M%S")

        # 로그 디렉토리 생성
        self.log_dir = Path(LOGS_DIR)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 현재 테스트용 하위 디렉토리
        self.current_test_dir = self.log_dir / f"{test_name}_{self.test_id}"
        self.current_test_dir.mkdir(parents=True, exist_ok=True)

        # 스크린샷 디렉토리
        self.screenshot_dir = self.current_test_dir / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 결과 데이터
        self.results: Dict[str, Any] = {
            "test_name": test_name,
            "test_id": self.test_id,
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "checks": {},
            "errors": [],
            "screenshots": []
        }

        # 로거 설정
        self._setup_logger()

    def _setup_logger(self) -> None:
        """로거 설정"""
        # 로그 파일 경로
        log_file = self.current_test_dir / f"{self.test_name}.log"

        # 로거 생성
        self.logger = logging.getLogger(f"{self.test_name}_{self.test_id}")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))

        # 파일 핸들러
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))

        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_check(
        self,
        check_name: str,
        passed: bool,
        message: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        검증 항목 결과 기록

        Args:
            check_name: 검증 항목 이름
            passed: 통과 여부
            message: 추가 메시지
            details: 상세 정보
        """
        timestamp = datetime.now().isoformat()

        check_result = {
            "timestamp": timestamp,
            "passed": passed,
            "message": message,
            "details": details or {}
        }

        self.results["checks"][check_name] = check_result

        # 로그 출력
        status = "✓ PASS" if passed else "✗ FAIL"
        log_msg = f"[{check_name}] {status}"
        if message:
            log_msg += f" - {message}"

        if passed:
            self.logger.info(log_msg)
        else:
            self.logger.error(log_msg)

        if details:
            self.logger.debug(f"상세 정보: {json.dumps(details, ensure_ascii=False)}")

    def log_error(self, error_message: str, exception: Optional[Exception] = None) -> None:
        """
        에러 기록

        Args:
            error_message: 에러 메시지
            exception: 예외 객체
        """
        timestamp = datetime.now().isoformat()

        error_data = {
            "timestamp": timestamp,
            "message": error_message,
            "exception": str(exception) if exception else None,
            "exception_type": type(exception).__name__ if exception else None
        }

        self.results["errors"].append(error_data)
        self.logger.error(error_message, exc_info=exception is not None)

    def save_screenshot(
        self,
        screenshot: Image.Image,
        name: str,
        on_error_only: bool = False
    ) -> Optional[Path]:
        """
        스크린샷 저장

        Args:
            screenshot: PIL Image 객체
            name: 파일명 (확장자 제외)
            on_error_only: 에러 시에만 저장 (설정 확인)

        Returns:
            저장된 파일 경로 또는 None
        """
        if on_error_only and not SAVE_SCREENSHOTS_ON_ERROR:
            return None

        timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
        filename = f"{name}_{timestamp}.{SCREENSHOT_FORMAT}"
        filepath = self.screenshot_dir / filename

        try:
            screenshot.save(filepath)
            self.logger.info(f"스크린샷 저장: {filename}")

            # 결과에 기록
            self.results["screenshots"].append({
                "filename": filename,
                "path": str(filepath),
                "timestamp": datetime.now().isoformat()
            })

            return filepath

        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {e}")
            return None

    def finalize(self) -> Path:
        """
        테스트 종료 및 결과 저장

        Returns:
            저장된 결과 파일 경로
        """
        end_time = datetime.now()
        self.results["end_time"] = end_time.isoformat()
        self.results["duration_seconds"] = (end_time - self.start_time).total_seconds()

        # 통과/실패 통계
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for check in self.results["checks"].values() if check["passed"])
        failed_checks = total_checks - passed_checks

        self.results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "total_errors": len(self.results["errors"]),
            "total_screenshots": len(self.results["screenshots"])
        }

        # JSON 파일로 저장
        result_file = self.current_test_dir / "test_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 최종 로그
        self.logger.info("=" * 60)
        self.logger.info("테스트 완료")
        self.logger.info(f"소요 시간: {self.results['duration_seconds']:.2f}초")
        self.logger.info(f"총 검증 항목: {total_checks}")
        self.logger.info(f"  - 통과: {passed_checks}")
        self.logger.info(f"  - 실패: {failed_checks}")
        self.logger.info(f"총 에러: {len(self.results['errors'])}")
        self.logger.info(f"결과 파일: {result_file}")
        self.logger.info("=" * 60)

        return result_file

    def get_results(self) -> Dict[str, Any]:
        """
        현재까지의 결과 반환

        Returns:
            결과 딕셔너리
        """
        return self.results.copy()
