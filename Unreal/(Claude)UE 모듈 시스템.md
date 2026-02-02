# Unreal Engine 모듈 시스템 가이드

## 목차
1. [모듈이란?](#모듈이란)
2. [모듈 파일 구조](#모듈-파일-구조)
3. [빌드 파일의 역할](#빌드-파일의-역할)
4. [모듈 의존성 관리](#모듈-의존성-관리)
5. [순환 의존성 문제와 해결](#순환-의존성-문제와-해결)

---

## 모듈이란?

**모듈(Module)**은 Unreal Engine에서 코드의 논리적 단위입니다. 각 모듈은:
- 독립적으로 컴파일 가능
- 자체 의존성 관리
- 다른 모듈에서 참조 가능

### 현재 프로젝트의 모듈 구조
```
Source/
├── MYP/                    # 메인 게임 모듈
│   ├── MYP.Build.cs       # 모듈 정의 파일
│   ├── MYP.cpp            # 모듈 구현
│   ├── MYP.h              # 모듈 헤더
│   ├── Public/            # Public 헤더 파일
│   └── Private/           # Private 구현 파일
├── MYP.Target.cs          # 게임 빌드 타겟
└── MYPEditor.Target.cs    # 에디터 빌드 타겟
```

**MYP 모듈의 특징**:
- **타입**: Runtime 모듈 (게임 실행 시 로드)
- **역할**: 프로젝트의 메인 게임 로직 담당
- **식별**: `MYP.Build.cs` 파일로 정의

---

## 모듈 파일 구조

### 1. 게임 모듈 위치
```
Source/
├── MYP/                   # 메인 게임 모듈
│   ├── MYP.Build.cs      # 모듈 빌드 설정
│   ├── Public/           # Public 헤더
│   └── Private/          # Private 구현
```

### 2. 추가 모듈 생성 시
```
Source/
├── MYP/                   # 기존 메인 모듈
├── AAA/                   # 새로운 모듈
│   ├── AAA.Build.cs
│   ├── Public/
│   └── Private/
└── BBB/                   # 또 다른 모듈
    ├── BBB.Build.cs
    ├── Public/
    └── Private/
```

### 3. 엔진 모듈 (읽기 전용)
- `[UE5_ROOT]/Engine/Source/Runtime/` - 런타임 모듈 (Core, CoreUObject, Engine 등)
- `[UE5_ROOT]/Engine/Source/Editor/` - 에디터 모듈
- `[UE5_ROOT]/Engine/Plugins/` - 엔진 플러그인

### 4. 프로젝트 플러그인
```
Plugins/
└── MyCustomPlugin/
    └── Source/
        └── MyCustomPlugin/
            ├── MyCustomPlugin.Build.cs
            ├── Public/
            └── Private/
```

---

## 빌드 파일의 역할

### 계층 구조

| 파일 | 범위 | 역할 |
|------|------|------|
| **MYP.Target.cs** | 프로젝트 전체 | 프로젝트에 포함할 모듈 결정 |
| **MYPEditor.Target.cs** | 에디터 전체 | 에디터에서 사용할 모듈 결정 |
| **MYP.Build.cs** | MYP 모듈만 | MYP 모듈의 의존성/설정 |
| **AAA.Build.cs** | AAA 모듈만 | AAA 모듈의 의존성/설정 |

### 1. Target.cs - 프로젝트 전체 빌드 설정

**위치**: `Source/MYP.Target.cs`, `Source/MYPEditor.Target.cs`

**역할**:
- 프로젝트 전체의 빌드 타입 정의 (Game, Editor, Server 등)
- 어떤 모듈들을 빌드에 포함할지 결정
- 전역 빌드 설정 (최적화, 플랫폼 등)

**예시 - MYP.Target.cs**:
```csharp
public class MYPTarget : TargetRules
{
    public MYPTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;

        ExtraModuleNames.Add("MYP");   // MYP 모듈 포함
        ExtraModuleNames.Add("AAA");   // AAA 모듈 추가 시
    }
}
```

**AAA 모듈 추가 시**:
```csharp
// MYP.Target.cs에 추가
ExtraModuleNames.Add("AAA");

// MYPEditor.Target.cs에도 추가 (에디터에서 사용하려면)
ExtraModuleNames.Add("AAA");
```

### 2. Module.Build.cs - 각 모듈의 개별 설정

**위치**: `Source/MYP/MYP.Build.cs`, `Source/AAA/AAA.Build.cs`

**역할**:
- 해당 모듈만의 의존성 관리
- 해당 모듈의 include 경로
- 해당 모듈의 컴파일 옵션

**예시 - MYP.Build.cs**:
```csharp
public class MYP : ModuleRules
{
    public MYP(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // MYP 모듈이 의존하는 모듈들
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput",
            "AIModule",
            "StateTreeModule",
            "GameplayStateTreeModule",
            "UMG",
            "Slate"
        });

        // Include 경로 설정
        PublicIncludePaths.Add("MYP/Public");
        PrivateIncludePaths.Add("MYP/Private");
    }
}
```

**예시 - AAA.Build.cs (새 모듈)**:
```csharp
public class AAA : ModuleRules
{
    public AAA(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // AAA 모듈이 의존하는 모듈들
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "MYP"  // MYP 모듈을 사용하려면 추가
        });

        // AAA 모듈의 include 경로
        PublicIncludePaths.Add("AAA/Public");
        PrivateIncludePaths.Add("AAA/Private");
    }
}
```

---

## 모듈 의존성 관리

### 모듈 의존성 = #include와 유사

**C++의 #include**:
```cpp
#include "MYPCharacter.h"  // 헤더 파일 포함
```

**언리얼 모듈 의존성**:
```csharp
// AAA.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "Engine",
    "MYP"  // MYP 모듈 포함
});
```

### 실제 사용 예시

**1단계**: `AAA.Build.cs`에 MYP 모듈 추가
```csharp
// Source/AAA/AAA.Build.cs
public class AAA : ModuleRules
{
    public AAA(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "MYP"  // ← 모듈 의존성 추가
        });
    }
}
```

**2단계**: AAA 모듈의 코드에서 MYP 클래스 사용
```cpp
// Source/AAA/Private/AAAGameMode.cpp
#include "AAAGameMode.h"
#include "MYPCharacter.h"  // ← MYP 모듈의 클래스 include

void AAAAGameMode::BeginPlay()
{
    Super::BeginPlay();

    // MYP 모듈의 클래스 사용 가능
    AMYPCharacter* Character = Cast<AMYPCharacter>(
        GetWorld()->GetFirstPlayerController()->GetPawn()
    );
}
```

### 정리

모듈 간 코드를 사용하려면 **두 단계** 필요:
1. **Build.cs에 모듈 의존성 추가** (모듈 레벨)
2. **.cpp 파일에서 #include** (코드 레벨)

---

## 순환 의존성 문제와 해결

### 문제 상황

AAA 모듈에서 MYP 코드를 사용하고, MYP 모듈에서도 AAA 코드를 사용해야 하는 경우?

### ❌ 잘못된 방법 - 순환 의존성

```csharp
// MYP.Build.cs
PublicDependencyModuleNames.Add("AAA");

// AAA.Build.cs
PublicDependencyModuleNames.Add("MYP");

// → 컴파일 에러!
// 빌드 시스템이 어느 모듈을 먼저 빌드해야 할지 결정 불가
```

**Unreal Engine은 순환 의존성을 허용하지 않습니다!**

### ✅ 해결 방법

#### 1. 인터페이스(Interface) 사용 ⭐ 가장 추천

**개념**: 구체적인 클래스 대신 인터페이스로 추상화

```cpp
// MYP/Public/Interfaces/IInventoryUser.h
UINTERFACE(MinimalAPI, Blueprintable)
class UInventoryUser : public UInterface
{
    GENERATED_BODY()
};

class IInventoryUser
{
    GENERATED_BODY()
public:
    virtual void AddItem(class UItem* Item) = 0;
    virtual void RemoveItem(class UItem* Item) = 0;
};
```

```cpp
// AAA/Public/AAACharacter.h
#include "Interfaces/IInventoryUser.h"  // MYP의 인터페이스만 include

class AAACharacter : public ACharacter, public IInventoryUser
{
    GENERATED_BODY()
public:
    // 인터페이스 구현
    virtual void AddItem(UItem* Item) override;
    virtual void RemoveItem(UItem* Item) override;
};
```

```cpp
// MYP 모듈에서 AAA 캐릭터를 사용할 때
void UInventoryManager::RegisterUser(AActor* Actor)
{
    // 구체적인 AAACharacter 타입 대신 인터페이스 사용
    IInventoryUser* User = Cast<IInventoryUser>(Actor);
    if (User)
    {
        User->AddItem(SomeItem);
    }
}
```

**의존성 구조**:
- `AAA.Build.cs`에만 `"MYP"` 추가
- `MYP.Build.cs`에는 `"AAA"` 추가 안 함
- MYP는 인터페이스(`IInventoryUser`)로만 AAA의 기능 사용

#### 2. 공통 모듈 분리

**개념**: 공통으로 사용하는 인터페이스/타입을 별도 모듈로 분리

```
Source/
├── MYPCore/          # 공통 인터페이스, 데이터 타입
│   ├── MYPCore.Build.cs
│   └── Public/
│       └── Interfaces/
├── MYP/              # MYPCore에 의존
│   └── MYP.Build.cs: PublicDependencyModuleNames.Add("MYPCore")
└── AAA/              # MYPCore에 의존
    └── AAA.Build.cs: PublicDependencyModuleNames.Add("MYPCore")
```

**의존성 구조**:
```
    MYPCore (공통 인터페이스)
      ↑    ↑
      |    |
     MYP  AAA  (서로 독립적)
```

#### 3. 델리게이트/이벤트 시스템

**개념**: 직접 참조 대신 이벤트로 통신

```cpp
// MYP 모듈 - 이벤트 정의
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnItemPickedUp, UItem*, Item);

class UInventoryComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(BlueprintAssignable)
    FOnItemPickedUp OnItemPickedUp;

    void PickupItem(UItem* Item)
    {
        // 아이템 획득 시 이벤트 발생
        OnItemPickedUp.Broadcast(Item);
    }
};
```

```cpp
// AAA 모듈 - 이벤트 구독
void AAACharacter::BeginPlay()
{
    Super::BeginPlay();

    // MYP의 이벤트를 구독만 함 (MYP는 AAA를 몰라도 됨)
    InventoryComponent->OnItemPickedUp.AddDynamic(
        this,
        &AAACharacter::HandleItemPickup
    );
}

void AAACharacter::HandleItemPickup(UItem* Item)
{
    // 이벤트 처리
}
```

**의존성 구조**:
- AAA는 MYP의 이벤트를 구독
- MYP는 AAA를 전혀 알 필요 없음
- `AAA.Build.cs`에만 `"MYP"` 추가

#### 4. 전방 선언 (Forward Declaration)

**개념**: 헤더에서는 포인터만 사용, 실제 정의는 .cpp에서

```cpp
// MYP/Public/MYPInventoryManager.h
class AAACharacter;  // ← 전방 선언 (구체적인 정의 없음)

class UMYPInventoryManager : public UObject
{
    GENERATED_BODY()
public:
    void RegisterCharacter(AAACharacter* Character);  // 포인터만 사용
};
```

```cpp
// MYP/Private/MYPInventoryManager.cpp
#include "MYPInventoryManager.h"
#include "AAACharacter.h"  // ← .cpp에서만 include

void UMYPInventoryManager::RegisterCharacter(AAACharacter* Character)
{
    // 실제 구현
}
```

**주의**: 전방 선언만으로는 모듈 의존성을 완전히 해결할 수 없습니다. `.cpp`에서 실제 헤더를 include하려면 여전히 `Build.cs`에 모듈을 추가해야 합니다.

---

## 실전 권장 구조

대부분의 Unreal 프로젝트는 다음과 같이 구성합니다:

```
Source/
├── MYP/                    # 메인 게임 모듈 (최상위)
│   └── MYP.Build.cs:
│       PublicDependencyModuleNames.Add("AAA")
│       PublicDependencyModuleNames.Add("BBB")
│       PublicDependencyModuleNames.Add("CCC")
│
├── AAA/                    # 기능 모듈 1 (인벤토리)
│   └── AAA.Build.cs:
│       PublicDependencyModuleNames = "Core", "Engine"
│
├── BBB/                    # 기능 모듈 2 (전투)
│   └── BBB.Build.cs:
│       PublicDependencyModuleNames = "Core", "Engine"
│
└── MYPCore/               # 공통 인터페이스/타입
    └── MYPCore.Build.cs:
        PublicDependencyModuleNames = "Core", "Engine"
```

**의존성 방향**: 항상 위에서 아래로만 (MYP → AAA, MYP → BBB)

**장점**:
- 순환 의존성 없음
- 각 기능 모듈은 독립적
- 테스트 및 유지보수 용이

---

## 핵심 정리

### 모듈이란?
- Unreal Engine의 코드 조직 단위
- 독립적으로 컴파일 가능한 C++ 코드 묶음

### 모듈 위치
- **게임 모듈**: `Source/[모듈이름]/`
- **각 모듈**: 자체 `.Build.cs` 파일과 `Public/`, `Private/` 폴더

### 빌드 파일 역할
- **Target.cs**: 프로젝트 전체 빌드 설정, 포함할 모듈 결정
- **Module.Build.cs**: 각 모듈의 의존성 및 설정

### 모듈 의존성
1. `Build.cs`에 모듈 추가 (모듈 레벨)
2. `.cpp`에서 `#include` (코드 레벨)

### 순환 의존성 해결
1. **인터페이스** 사용 ⭐
2. **공통 모듈** 분리
3. **델리게이트/이벤트** 시스템
4. **한방향 의존성** 유지

---

## 참고 자료

- [Unreal Engine 공식 문서 - Modules](https://docs.unrealengine.com/5.6/en-US/modules-in-unreal-engine/)
- [Unreal Engine 공식 문서 - Build Configuration](https://docs.unrealengine.com/5.6/en-US/build-configuration-for-unreal-engine/)
- 프로젝트 파일: `CLAUDE.md`, `MYP.Build.cs`

---

**작성일**: 2025-10-29
**프로젝트**: MYP (Unreal Engine 5.6)