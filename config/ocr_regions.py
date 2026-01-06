"""
OCR 영역(ROI) 좌표 정의

게임 화면에서 텍스트/숫자를 읽을 영역의 좌표를 정의합니다.
좌표 형식: (x1, y1, x2, y2)

주의: 게임 해상도에 따라 좌표 조정 필요
"""

# ========================================
# 전투 화면 - 코스트 UI
# ========================================

# 현재 코스트 표시 영역 (우측 상단)
# 예: "7/10" 형태로 표시
BATTLE_COST_CURRENT_REGION = (1700, 50, 1850, 100)

# 코스트 숫자만 읽기 (현재 코스트)
# 예: "7" 부분만
BATTLE_COST_VALUE_REGION = (1700, 50, 1750, 100)

# 최대 코스트 숫자 읽기
# 예: "10" 부분만
BATTLE_COST_MAX_REGION = (1800, 50, 1850, 100)


# ========================================
# 전투 화면 - 스킬 아이콘 영역
# ========================================

# 스킬 아이콘 1번 학생 (좌측부터)
SKILL_ICON_STUDENT_1 = (100, 800, 180, 880)

# 스킬 아이콘 2번 학생
SKILL_ICON_STUDENT_2 = (200, 800, 280, 880)

# 스킬 아이콘 3번 학생
SKILL_ICON_STUDENT_3 = (300, 800, 380, 880)

# 스킬 아이콘 4번 학생
SKILL_ICON_STUDENT_4 = (400, 800, 480, 880)


# ========================================
# 전투 결과 화면 - 데미지 기록
# ========================================

# 학생 1 이름 영역
DAMAGE_REPORT_NAME_1 = (100, 200, 300, 240)

# 학생 1 데미지 영역
DAMAGE_REPORT_DAMAGE_1 = (400, 200, 550, 240)

# 학생 2 이름 영역
DAMAGE_REPORT_NAME_2 = (100, 260, 300, 300)

# 학생 2 데미지 영역
DAMAGE_REPORT_DAMAGE_2 = (400, 260, 550, 300)

# 학생 3 이름 영역
DAMAGE_REPORT_NAME_3 = (100, 320, 300, 360)

# 학생 3 데미지 영역
DAMAGE_REPORT_DAMAGE_3 = (400, 320, 550, 360)

# 학생 4 이름 영역
DAMAGE_REPORT_NAME_4 = (100, 380, 300, 420)

# 학생 4 데미지 영역
DAMAGE_REPORT_DAMAGE_4 = (400, 380, 550, 420)


# ========================================
# 유틸리티 함수
# ========================================

def get_damage_report_regions(student_count: int = 4):
    """
    데미지 기록 영역 리스트 반환

    Args:
        student_count: 학생 수 (기본 4명)

    Returns:
        [(name_bbox, damage_bbox), ...]
    """
    regions = [
        (DAMAGE_REPORT_NAME_1, DAMAGE_REPORT_DAMAGE_1),
        (DAMAGE_REPORT_NAME_2, DAMAGE_REPORT_DAMAGE_2),
        (DAMAGE_REPORT_NAME_3, DAMAGE_REPORT_DAMAGE_3),
        (DAMAGE_REPORT_NAME_4, DAMAGE_REPORT_DAMAGE_4),
    ]
    return regions[:student_count]


def get_skill_icon_region(student_index: int):
    """
    스킬 아이콘 영역 반환

    Args:
        student_index: 학생 인덱스 (0-3)

    Returns:
        (x1, y1, x2, y2) 또는 None
    """
    regions = [
        SKILL_ICON_STUDENT_1,
        SKILL_ICON_STUDENT_2,
        SKILL_ICON_STUDENT_3,
        SKILL_ICON_STUDENT_4,
    ]

    if 0 <= student_index < len(regions):
        return regions[student_index]
    return None


# ========================================
# 좌표 보정 함수 (해상도 대응)
# ========================================

def scale_region(region: tuple, scale_x: float = 1.0, scale_y: float = 1.0):
    """
    좌표를 해상도에 맞게 스케일 조정

    Args:
        region: (x1, y1, x2, y2)
        scale_x: X축 스케일
        scale_y: Y축 스케일

    Returns:
        스케일 조정된 좌표
    """
    x1, y1, x2, y2 = region
    return (
        int(x1 * scale_x),
        int(y1 * scale_y),
        int(x2 * scale_x),
        int(y2 * scale_y)
    )


# ========================================
# 주의사항
# ========================================

# 위 좌표는 예시 좌표입니다.
# 실제 게임 화면에서 다음 절차로 좌표를 측정해야 합니다:
#
# 1. 게임을 전투 화면으로 진입
# 2. 스크린샷 캡처
# 3. 이미지 편집 도구로 코스트 UI 영역 측정
# 4. 좌표 업데이트
#
# 좌표 측정 도구 추천:
# - Windows: Paint, IrfanView
# - Python: Pillow로 픽셀 좌표 확인
