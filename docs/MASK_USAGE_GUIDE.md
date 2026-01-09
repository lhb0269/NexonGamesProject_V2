# 마스크 기반 템플릿 매칭 가이드

## 개요

마스크 기반 템플릿 매칭은 배경이 변하는 UI 요소를 인식할 때 사용합니다.
예: 캐릭터 마커(중앙이 비어있는 역삼각형)는 배경(맵 타일)이 변해도 테두리 부분만 매칭하여 인식합니다.

## 마스크란?

- **흰색(255) 영역**: 템플릿 매칭에 사용됨 (테두리, 아이콘 등)
- **검은색(0) 영역**: 템플릿 매칭에서 무시됨 (중앙 빈 공간, 배경 등)

## 언제 사용하나요?

### ✅ 마스크 사용이 필요한 경우
- 캐릭터 마커: 중앙이 비어있고 배경(맵)이 변함
- 테두리만 있는 버튼: 내부 텍스트가 변하지만 테두리는 일정함
- 투명도가 있는 아이콘: 배경이 보이는 UI 요소

### ❌ 마스크가 필요 없는 경우
- 배경이 단색인 버튼
- 전체가 채워진 아이콘
- 배경이 변하지 않는 UI

## 사용 방법

### 1단계: 캐릭터 마커 템플릿 캡처

게임 화면에서 캐릭터 마커를 캡처합니다:

```
assets/templates/2560x1440/icons/character_marker.png
```

### 2단계: 마스크 생성

마스크 생성 도구를 실행합니다:

```bash
python tools/create_mask.py
```

#### 마스크 생성 도구 사용법

1. **템플릿 경로 입력**
   ```
   템플릿 이미지 경로를 입력하세요: assets/templates/2560x1440/icons/character_marker.png
   ```

2. **중앙 빈 공간 선택**
   - **다각형 모드** (기본): 마우스로 클릭하여 점 추가
   - **사각형 모드**: `m` 키로 전환 후 드래그

3. **영역 반전**
   - `i` 키를 눌러 선택 영역을 검은색(무시)으로 변경

4. **저장**
   - `s` 키: 중간 저장
   - `q` 키: 최종 저장 및 종료

5. **생성된 파일**
   - `character_marker_mask.png`: 마스크 파일
   - `character_marker_mask_preview.png`: 미리보기

#### 키보드 단축키

| 키 | 기능 |
|---|---|
| 마우스 좌클릭 | 점 추가 (다각형) / 사각형 드래그 |
| `m` | 모드 전환 (다각형 ↔ 사각형) |
| `c` | 선택 초기화 |
| `i` | 선택 영역 반전 (검은색으로) |
| `s` | 마스크 저장 |
| `q` | 종료 및 저장 |
| `ESC` | 취소 및 종료 |

### 3단계: 코드에서 사용

#### 기본 사용법

```python
from src.recognition.template_matcher import TemplateMatcher
from pathlib import Path

matcher = TemplateMatcher(confidence=0.6)

# 템플릿과 마스크 경로
template = Path("assets/templates/2560x1440/icons/character_marker.png")
mask = Path("assets/templates/2560x1440/icons/character_marker_mask.png")

# 마스크 기반 매칭
location = matcher.find_template_with_mask(template, mask)

if location:
    print(f"캐릭터 마커 발견: {location}")
else:
    print("캐릭터 마커를 찾을 수 없음")
```

#### 선택적 마스크 사용 (추천)

마스크가 있으면 사용하고, 없으면 일반 매칭으로 fallback:

```python
# 마스크 파일 존재 확인
use_mask = mask.exists()

# 조건부 매칭
if use_mask:
    location = matcher.find_template_with_mask(template, mask)
else:
    location = matcher.find_template(template)
```

## 예제: 캐릭터 마커 (역삼각형)

### 문제점
- 캐릭터 마커는 중앙이 비어있음 (배경이 보임)
- 이동 전후로 배경(맵 타일)이 달라짐
- 일반 템플릿 매칭 실패 (배경 불일치)

### 해결 방법
1. 역삼각형 **테두리만** 흰색으로 마스크 생성
2. **중앙 빈 공간**은 검은색으로 마스크 생성
3. 마스크 기반 매칭으로 테두리만 비교

### 마스크 생성 팁

#### 역삼각형 마커의 경우
1. **다각형 모드** 사용 권장 (삼각형 형태)
2. 중앙 빈 공간을 클릭하여 다각형 생성
3. `i` 키로 반전하여 테두리만 흰색으로 남김

#### 사각형 버튼의 경우
1. **사각형 모드** 사용 (`m` 키로 전환)
2. 내부를 드래그하여 선택
3. `i` 키로 반전하여 테두리만 흰색으로 남김

## 트러블슈팅

### 마스크 생성 후에도 인식 실패
- **원인**: 마스크가 너무 작거나 큼
- **해결**: 테두리 두께를 조정하여 다시 생성
- **팁**: 픽셀 2-3개 정도 여유 두기

### OpenCV 설치 오류
마스크 기반 매칭은 OpenCV가 필요합니다:

```bash
pip install opencv-python
```

### 신뢰도 조정
마스크 기반 매칭도 신뢰도 임계값을 조정할 수 있습니다:

```python
# 낮은 신뢰도 (더 관대하게)
location = matcher.find_template_with_mask(template, mask, threshold=0.5)

# 높은 신뢰도 (더 엄격하게)
location = matcher.find_template_with_mask(template, mask, threshold=0.8)
```

## 마스크 파일 위치

해상도별로 마스크 파일을 생성해야 합니다:

```
assets/templates/
├── 1920x1080/
│   └── icons/
│       ├── character_marker.png
│       └── character_marker_mask.png
└── 2560x1440/
    └── icons/
        ├── character_marker.png
        └── character_marker_mask.png
```

## 참고사항

- 마스크는 **그레이스케일** 이미지여야 합니다
- 마스크 크기는 템플릿과 **동일**해야 합니다
- OpenCV의 `TM_CCORR_NORMED` 방식 사용
- 마스크 파일명은 `{템플릿명}_mask.png` 규칙 권장

## 실제 적용 예제

[test_tile_movement.py](../tests/test_tile_movement.py)에서 캐릭터 마커 이동 검증에 사용됩니다:

```python
# 마스크 존재 확인
use_mask = character_marker_mask.exists()

# 초기 위치 찾기
if use_mask:
    initial_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
else:
    initial_pos = matcher.find_template(character_marker)

# 이동 후 위치 찾기
if use_mask:
    final_pos = matcher.find_template_with_mask(character_marker, character_marker_mask)
else:
    final_pos = matcher.find_template(character_marker)

# 이동 거리 계산
distance = calculate_distance(initial_pos, final_pos)
print(f"캐릭터 이동 거리: {distance:.2f} 픽셀")
```
