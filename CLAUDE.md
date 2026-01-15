# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 필요한 가이드를 제공합니다.

## 저장소 개요

이 저장소는 게임 개발 및 언리얼 엔진 학습 노트를 위한 Obsidian 기반 지식 관리 저장소입니다. 주제별로 구성된 여러 개의 독립적인 Obsidian 볼트를 포함하고 있으며, 주로 한국어로 작성되었습니다.

## 저장소 구조

저장소는 멀티 볼트 아키텍처를 따르며, 각 최상위 디렉토리가 독립적인 Obsidian 볼트입니다:

```
D:\Obsidian\
├── Unreal/          # 언리얼 엔진 기초, 아키텍처, 게임플레이 프레임워크
├── Niagara/         # 나이아가라 VFX 시스템, 이펙트 제작 및 최적화
├── Optimization/    # 성능 최적화, 프로파일링, 메모리 관리
├── Tools/           # 개발 도구, 워크플로우, 스크립팅
├── Private/         # 개인 노트 (gitignore 처리됨)
├── Resource/        # 리소스 파일 및 에셋 (gitignore 처리됨)
└── README.md        # 저장소 소개
```

### 볼트별 구조

각 볼트는 다음을 포함합니다:
- `.obsidian/` 디렉토리 (볼트 설정)
- `Init.md` (볼트 진입점, 현재는 빈 플레이스홀더)
- 주제별로 구성된 마크다운 파일들
- `Resources/` 디렉토리 (이미지, 비디오, PDF 등 모든 첨부 파일)

## Obsidian 볼트 작업하기

### 핵심 개념

- **볼트(Vaults)**: 각 주제 디렉토리는 독립적으로 열 수 있는 별도의 Obsidian 볼트입니다
- **볼트 간 링크**: 볼트들은 서로 간 상호 참조를 지원합니다
- **마크다운 형식**: 모든 노트는 Obsidian 확장 기능(위키링크, 임베드)이 포함된 표준 마크다운입니다
- **에셋 구성**: 모든 첨부 파일(이미지, 비디오, PDF 등)은 볼트 루트의 `Resources/` 디렉토리에 통합 저장됩니다

### Obsidian 플러그인 설정

볼트에서 사용하는 플러그인:
- 코어 플러그인: 파일 탐색기, 검색, 그래프 뷰, 백링크, 템플릿, 일일 노트
- 커뮤니티 플러그인: `obsidian-importer`
- 설정 파일: `core-plugins.json`, `community-plugins.json`, `graph.json`

### Git Ignore 전략

`.gitignore` 설정:
- **무시(Ignore)**: 개인 작업 공간 설정, 캐시, 플러그인 파일, 개인 설정, 단축키, 북마크
- **공유(Share)**: 플러그인 목록 (`core-plugins.json`, `community-plugins.json`), 그래프 뷰 설정 (`graph.json`)
- **완전 제외(Exclude completely)**: `Resource/`, `Private/` 및 기타 gitignore 처리된 디렉토리

**중요**: `.gitignore` 파일은 사용자가 이미 완성시켜 놓았으므로 별도 지시 없이 수정하지 마세요.

## 파일 작업

### 새 노트 생성하기

마크다운 파일을 생성할 때:
- 적절한 볼트 디렉토리에 배치하세요
- 내용에 맞는 설명적인 한국어 파일명을 사용하세요
- 첨부 파일(이미지, 비디오, PDF 등)은 볼트 루트의 `Resources/` 디렉토리에 자동 저장됩니다
- 상호 참조는 Obsidian 위키링크 문법을 사용하세요: `[[노트 이름]]`

### 콘텐츠 구성하기

- 각 볼트는 주제적 초점을 유지해야 합니다 (Unreal, Niagara, Optimization, Tools)
- 볼트 내에서 하위 디렉토리를 사용하여 관련 주제를 구성하세요
- 빈 `Init.md` 파일은 볼트 진입점 역할을 합니다 - 실질적인 내용을 추가할 때 채우세요

### 에셋 작업하기

- 모든 첨부 파일(이미지, GIF, 비디오, PDF 등)은 볼트 루트의 `Resources/` 디렉토리에 저장됩니다
- 임베드된 리소스는 Obsidian의 `![[filename.png]]` 문법을 사용합니다
- 파일명은 설명적인 이름을 사용하세요

**Obsidian 설정**:
각 볼트의 `.obsidian/app.json` 파일에 다음과 같이 설정되어 있습니다:
```json
{
  "attachmentFolderPath": "Resources"
}
```

이 설정으로 어느 폴더에서 작업하든 첨부 파일은 항상 볼트 루트의 `Resources/` 폴더에 저장됩니다.

## 개발 워크플로우

이 저장소는 문서 저장소이므로 빌드 프로세스나 테스트가 없습니다. 일반적인 작업:

### 콘텐츠 추가하기
```bash
# 적절한 볼트에 새 노트 생성
touch Unreal/NewTopic.md

# 첨부 파일은 Obsidian에서 자동으로 Unreal/Resources/에 저장됨
```

### Git 작업
```bash
# 추적 중인 파일 확인 (일부 디렉토리는 gitignore 처리됨)
git status

# 노트 스테이징 및 커밋 (접두사 사용)
git add Unreal/NewTopic.md
git commit -m "[NEW] NewTopic.md"

# 수정 사항 커밋
git add Unreal/ExistingTopic.md
git commit -m "[FIX] ExistingTopic.md"
```

**커밋 메시지 컨벤션**:
- `[NEW]` - 새로운 노트 추가 시
- `[FIX]` - 기존 노트 수정 시
- 접두사 뒤에 파일명 또는 간단한 설명 작성

### Obsidian에서 열기
사용자는 루트 디렉토리가 아닌 각 볼트 디렉토리를 Obsidian에서 개별적으로 열어야 합니다.

## 언어 및 콘텐츠

- **주요 언어**: 한국어
- **콘텐츠 초점**: 게임 개발, 언리얼 엔진 5, VFX, 최적화
- **학습 스타일**: 튜토리얼, 코드 스니펫, 기술적 설명이 포함된 개인 학습 노트
- 콘텐츠를 추가하거나 수정할 때는 특정 기술 용어를 번역하는 경우를 제외하고 한국어를 유지하세요

## 중요 사항

- gitignore 처리된 디렉토리에는 파일을 커밋하지 마세요
- `.obsidian/workspace.json`, `.obsidian/app.json`, `.obsidian/appearance.json` 파일은 수정하지 마세요
- 의미 있는 내용을 추가하지 않는 한 빈 `Init.md` 파일을 유지하세요
- 커밋 메시지는 반드시 `[NEW]` 또는 `[FIX]` 접두사를 사용하세요
