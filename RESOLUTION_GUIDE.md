# 해상도별 템플릿 관리 가이드

## 개요

이 프로젝트는 **다중 해상도 지원**을 위해 해상도별로 템플릿 이미지를 관리합니다.

## 지원 해상도

- **1920x1080** (Full HD) - 기본 해상도
- **2560x1440** (QHD)
- **3840x2160** (4K UHD)

## 디렉토리 구조

```
assets/templates/
├── 1920x1080/          # Full HD 템플릿
│   ├── buttons/
│   ├── icons/
│   └── ui/
├── 2560x1440/          # QHD 템플릿
│   ├── buttons/
│   ├── icons/
│   └── ui/
└── 3840x2160/          # 4K UHD 템플릿
    ├── buttons/
    ├── icons/
    └── ui/
```

## 해상도 설정 방법

### 1. GUI를 통한 설정 (권장)

```bash
python gui_test_runner.py
```

1. 우측 상단의 **"🖥 디스플레이"** 버튼 클릭
2. 사용할 해상도 선택
3. 저장 버튼 클릭
4. 프로그램 재시작

### 2. 수동 설정

`config/display_settings.json` 파일 생성:

```json
{
  "resolution": "1920x1080"
}
```

## 새 해상도 추가하기

### 1. 템플릿 디렉토리 생성

```bash
mkdir -p assets/templates/[해상도]/buttons
mkdir -p assets/templates/[해상도]/icons
mkdir -p assets/templates/[해상도]/ui
```

예: `1920x1080`, `2560x1440`, `3840x2160`

### 2. 템플릿 이미지 캡처

해당 해상도에서 게임을 실행하고 다음 이미지들을 캡처:

**buttons/**
- deploy_button.png
- mission_start_button.png
- phase_end_button.png
- battle_log_button.png
- damage_report_close_button.png
- victory_confirm.png
- rank_reward_confirm_button.png

**icons/**
- start_tile.png
- enemy_tile.png
- empty_tile.png

**ui/**
- formation_screen.png
- stage_map.png
- stage_map_2.png
- battle_ui.png
- victory.png
- damage_report.png
- rank_reward.png

### 3. settings.py에 해상도 등록 (선택)

`config/settings.py`에 새 해상도 추가:

```python
SUPPORTED_RESOLUTIONS = {
    "1920x1080": {"width": 1920, "height": 1080, "name": "Full HD (1920x1080)"},
    "2560x1440": {"width": 2560, "height": 1440, "name": "QHD (2560x1440)"},
    "새해상도": {"width": xxxx, "height": yyyy, "name": "이름"},
}
```

## 템플릿 캡처 가이드

### 중요 사항

1. **고정 해상도**: 게임 해상도를 고정하고 캡처
2. **안정적인 UI**: 애니메이션이 없는 상태에서 캡처
3. **적절한 크기**: 너무 크거나 작지 않게 (변동이 적은 영역)
4. **일관성**: 같은 상태에서 캡처 (밝기, 이펙트 등)

### 캡처 도구

- Windows: `Win + Shift + S` (화면 캡처)
- Python: `pyautogui.screenshot()`
- 외부 툴: ShareX, Greenshot 등

### 신뢰도 조정

특정 템플릿의 인식률이 낮을 경우:

```python
# src/recognition/template_matcher.py
# 또는 개별 테스트 스크립트에서

matcher.find_template(
    template_path,
    confidence=0.5  # 기본값 0.8에서 낮춤
)
```

## 자동 전환 시스템

프로그램 실행 시 `config/display_settings.json`의 해상도 설정을 자동으로 읽어서:

```
assets/templates/{해상도}/buttons/
assets/templates/{해상도}/icons/
assets/templates/{해상도}/ui/
```

경로를 사용합니다.

## 문제 해결

### 템플릿을 찾을 수 없음

1. 해상도가 올바르게 설정되었는지 확인
2. 템플릿 디렉토리가 존재하는지 확인
3. 템플릿 이미지 파일명이 정확한지 확인

### 인식률이 낮음

1. 게임 해상도와 템플릿 해상도 일치 확인
2. 템플릿 이미지 다시 캡처
3. 신뢰도(confidence) 값 조정
4. 템플릿 영역 크기 조정 (더 작거나 크게)

### 해상도 변경이 적용되지 않음

1. 프로그램 완전히 재시작
2. `config/display_settings.json` 파일 확인
3. Python 캐시 삭제: `__pycache__` 폴더 삭제

## 현재 상태

- ✅ **1920x1080**: 템플릿 준비 완료
- ⏳ **2560x1440**: 템플릿 디렉토리만 생성됨 (이미지 추가 필요)
- ⏳ **3840x2160**: 템플릿 디렉토리만 생성됨 (이미지 추가 필요)

## 기여하기

다른 해상도의 템플릿을 기여하려면:

1. 해당 해상도에서 템플릿 캡처
2. `assets/templates/[해상도]/` 디렉토리에 추가
3. 테스트 후 PR 생성
