"""
스킬 사용 관련 설정

2560x1440 해상도 기준 (실측 좌표)
"""

# ========================================
# 화면 중앙 좌표 (스킬 타겟 위치)
# ========================================

SCREEN_CENTER_X = 1280
SCREEN_CENTER_Y = 720

# ========================================
# 스킬 버튼 클릭 위치 (슬롯 1, 2, 3)
# ========================================

# 슬롯 1 버튼 중심점
SKILL_BUTTON_SLOT_1 = (1797, 1242)

# 슬롯 2 버튼 중심점
SKILL_BUTTON_SLOT_2 = (2000, 1240)

# 슬롯 3 버튼 중심점
SKILL_BUTTON_SLOT_3 = (2200, 1240)


# ========================================
# 스킬 코스트 OCR 영역 (슬롯 1, 2, 3)
# ========================================

# 슬롯 1 스킬 코스트 영역
SKILL_COST_SLOT_1 = (1768, 1304, 1815, 1350)

# 슬롯 2 스킬 코스트 영역
SKILL_COST_SLOT_2 = (1973, 1304, 2017, 1350)

# 슬롯 3 스킬 코스트 영역
SKILL_COST_SLOT_3 = (2174, 1304, 2225, 1350)


# ========================================
# 대기 시간 설정
# ========================================

# 스킬 버튼 클릭 후 타겟 설정까지 대기
SKILL_CLICK_TO_TARGET_WAIT = 0.5

# 타겟 클릭 후 코스트 업데이트까지 대기
TARGET_CLICK_TO_COST_UPDATE_WAIT = 1.0


# ========================================
# 유틸리티 함수
# ========================================

def get_skill_button_position(slot_index: int) -> tuple:
    """
    슬롯 인덱스로 스킬 버튼 위치 반환

    Args:
        slot_index: 0 (슬롯1), 1 (슬롯2), 2 (슬롯3)

    Returns:
        (x, y) 좌표 또는 None
    """
    positions = [
        SKILL_BUTTON_SLOT_1,
        SKILL_BUTTON_SLOT_2,
        SKILL_BUTTON_SLOT_3,
    ]

    if 0 <= slot_index < len(positions):
        return positions[slot_index]
    return None


def get_skill_cost_region(slot_index: int) -> tuple:
    """
    슬롯 인덱스로 스킬 코스트 OCR 영역 반환

    Args:
        slot_index: 0 (슬롯1), 1 (슬롯2), 2 (슬롯3)

    Returns:
        (x1, y1, x2, y2) 좌표 또는 None
    """
    regions = [
        SKILL_COST_SLOT_1,
        SKILL_COST_SLOT_2,
        SKILL_COST_SLOT_3,
    ]

    if 0 <= slot_index < len(regions):
        return regions[slot_index]
    return None


def get_all_skill_cost_regions() -> list:
    """모든 스킬 코스트 영역 리스트 반환"""
    return [
        SKILL_COST_SLOT_1,
        SKILL_COST_SLOT_2,
        SKILL_COST_SLOT_3,
    ]
