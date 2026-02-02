# EnhancedInput C++ 바인딩 가이드

## 개요

EnhancedInput은 언리얼 엔진 5에서 도입된 새로운 입력 시스템입니다. 기존의 Legacy Input 시스템을 대체하며, 더 유연하고 강력한 입력 처리를 제공합니다. 이 문서는 에디터에서 생성한 InputAction과 InputMappingContext를 C++ 코드에서 바인딩하고 연결하는 방법을 다룹니다.

## 에디터에서 에셋 생성

### InputAction 생성

1. **Content Browser**에서 우클릭
2. **Input → Input Action** 선택
3. 이름 지정 (예: `IA_Move`, `IA_Jump`, `IA_Look`)
4. **Value Type** 설정:
   - `Axis1D`: 단일 축 (점프, 발사 등)
   - `Axis2D`: 2D 벡터 (이동, 마우스 등)
   - `Axis3D`: 3D 벡터 (비행 등)

### InputMappingContext 생성

1. **Content Browser**에서 우클릭
2. **Input → Input Mapping Context** 선택
3. 이름 지정 (예: `IMC_Default`)
4. 더블클릭하여 열기
5. **Mappings** 섹션에서 InputAction 추가:
   - **+** 버튼 클릭
   - InputAction 선택 (예: `IA_Move`)
   - 키 바인딩 추가 (예: `W`, `A`, `S`, `D`)
6. **Modifiers** 및 **Triggers** 설정 (선택사항)

## C++ 헤더 설정

### 필수 모듈 추가

먼저 `{ProjectName}.Build.cs` 파일에 EnhancedInput 모듈을 추가해야 합니다:

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "InputCore",
    "EnhancedInput"  // 추가
});
```

### 캐릭터 헤더 파일

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UInputAction;
class UInputMappingContext;

UCLASS()
class MYPROJECT_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    // InputAction 에셋 참조
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* MoveAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputAction* JumpAction;

    // InputMappingContext 에셋 참조
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
    UInputMappingContext* DefaultMappingContext;

    // 입력 처리 함수
    void Move(const struct FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
};
```

**핵심 포인트**:
- `UInputAction*`과 `UInputMappingContext*`를 `UPROPERTY`로 선언하면 에디터에서 에셋을 직접 할당할 수 있습니다.
- `EditAnywhere`로 설정하면 블루프린트 에디터에서도 수정 가능합니다.
- 전방 선언(`class UInputAction;`)을 사용하면 헤더 파일 크기를 줄일 수 있습니다.

## C++ 구현 파일

### 필수 헤더 인클루드

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
```

### 생성자

```cpp
AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
}
```

### BeginPlay - MappingContext 적용

```cpp
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // PlayerController 가져오기
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        // EnhancedInput LocalPlayerSubsystem 가져오기
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            // MappingContext 추가
            if (DefaultMappingContext)
            {
                Subsystem->AddMappingContext(DefaultMappingContext, 0);
            }
        }
    }
}
```

**핵심 개념**:
- `UEnhancedInputLocalPlayerSubsystem`은 로컬 플레이어의 입력을 관리합니다.
- `AddMappingContext()`의 두 번째 매개변수는 우선순위입니다 (높을수록 우선).
- 같은 키에 여러 액션이 바인딩된 경우, 우선순위가 높은 MappingContext가 먼저 처리됩니다.

### SetupPlayerInputComponent - 액션 바인딩

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    // EnhancedInputComponent로 캐스팅
    if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        // Move 액션 바인딩
        if (MoveAction)
        {
            EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        }

        // Look 액션 바인딩
        if (LookAction)
        {
            EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
        }

        // Jump 액션 바인딩
        if (JumpAction)
        {
            EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
            EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
        }
    }
}
```

**ETriggerEvent 종류**:
- `Started`: 입력이 처음 감지될 때
- `Ongoing`: 입력이 진행 중일 때 (매 프레임)
- `Triggered`: 트리거 조건이 충족될 때 (일반적으로 가장 많이 사용)
- `Completed`: 입력이 끝날 때
- `Canceled`: 입력이 취소될 때

### 입력 처리 함수 구현

```cpp
void AMyCharacter::Move(const FInputActionValue& Value)
{
    // FInputActionValue에서 Vector2D 추출
    const FVector2D MovementVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        // 전진/후진
        AddMovementInput(GetActorForwardVector(), MovementVector.Y);
        // 좌/우
        AddMovementInput(GetActorRightVector(), MovementVector.X);
    }
}

void AMyCharacter::Look(const FInputActionValue& Value)
{
    // FInputActionValue에서 Vector2D 추출
    const FVector2D LookAxisVector = Value.Get<FVector2D>();

    if (Controller != nullptr)
    {
        // 좌우 회전
        AddControllerYawInput(LookAxisVector.X);
        // 상하 회전
        AddControllerPitchInput(LookAxisVector.Y);
    }
}
```

**FInputActionValue 타입 추출**:
- `Value.Get<float>()`: Axis1D용
- `Value.Get<FVector2D>()`: Axis2D용
- `Value.Get<FVector>()`: Axis3D용
- `Value.Get<bool>()`: Digital (버튼)용

## 에디터에서 에셋 할당

1. 캐릭터 블루프린트를 엽니다 (또는 월드에 배치된 캐릭터 선택)
2. **Details** 패널에서 **Input** 섹션을 찾습니다
3. 각 변수에 에셋을 할당:
   - `Move Action` → `IA_Move`
   - `Look Action` → `IA_Look`
   - `Jump Action` → `IA_Jump`
   - `Default Mapping Context` → `IMC_Default`

## 블루프린트 연동

### C++에서 BlueprintCallable 함수 노출

C++ 코드로 작성된 입력 처리 로직을 블루프린트에서도 호출할 수 있도록 노출할 수 있습니다:

```cpp
// MyCharacter.h
UCLASS()
class MYPROJECT_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    // 블루프린트에서 호출 가능한 함수
    UFUNCTION(BlueprintCallable, Category = "Input")
    void AddCustomMappingContext(UInputMappingContext* MappingContext, int32 Priority);

    UFUNCTION(BlueprintCallable, Category = "Input")
    void RemoveCustomMappingContext(UInputMappingContext* MappingContext);

protected:
    // 블루프린트에서 구현 가능한 이벤트
    UFUNCTION(BlueprintImplementableEvent, Category = "Input")
    void OnMoveInput(const FVector2D& MovementVector);

    UFUNCTION(BlueprintImplementableEvent, Category = "Input")
    void OnJumpInput();
};
```

### C++ 구현

```cpp
// MyCharacter.cpp
void AMyCharacter::AddCustomMappingContext(UInputMappingContext* MappingContext, int32 Priority)
{
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            if (MappingContext)
            {
                Subsystem->AddMappingContext(MappingContext, Priority);
            }
        }
    }
}

void AMyCharacter::RemoveCustomMappingContext(UInputMappingContext* MappingContext)
{
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            if (MappingContext)
            {
                Subsystem->RemoveMappingContext(MappingContext);
            }
        }
    }
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D MovementVector = Value.Get<FVector2D>();

    // C++ 로직 처리
    if (Controller != nullptr)
    {
        AddMovementInput(GetActorForwardVector(), MovementVector.Y);
        AddMovementInput(GetActorRightVector(), MovementVector.X);
    }

    // 블루프린트 이벤트 호출
    OnMoveInput(MovementVector);
}
```

### 블루프린트에서 활용

블루프린트 이벤트 그래프에서:

1. **OnMoveInput** 이벤트 노드가 자동으로 생성됩니다
2. `MovementVector` 출력 핀을 사용하여 커스텀 로직 추가 가능
3. 예: 이동 시 파티클 효과, 사운드 재생 등

## 고급 설정

### 1. MappingContext 우선순위 관리

여러 MappingContext를 동적으로 추가/제거하여 상황별 입력을 관리할 수 있습니다:

```cpp
// MyCharacter.h
UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
UInputMappingContext* CombatMappingContext;

UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
UInputMappingContext* VehicleMappingContext;
```

```cpp
// MyCharacter.cpp
void AMyCharacter::EnterCombatMode()
{
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            // 기본 MappingContext 우선순위: 0
            // 전투 MappingContext 우선순위: 1 (더 높음)
            Subsystem->AddMappingContext(CombatMappingContext, 1);
        }
    }
}

void AMyCharacter::ExitCombatMode()
{
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
            ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
        {
            Subsystem->RemoveMappingContext(CombatMappingContext);
        }
    }
}
```

**실전 활용**:
- 기본 이동: `DefaultMappingContext` (우선순위 0)
- 전투 모드: `CombatMappingContext` (우선순위 1) - 스킬 키 활성화
- 탈것 탑승: `VehicleMappingContext` (우선순위 2) - 이동 키 재정의

### 2. 조건부 바인딩

특정 조건에서만 입력을 처리하도록 구현:

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        // 스킬 액션 바인딩 (조건부 처리)
        if (SkillAction)
        {
            EnhancedInputComponent->BindAction(SkillAction, ETriggerEvent::Started, this, &AMyCharacter::OnSkillInputStarted);
        }
    }
}

void AMyCharacter::OnSkillInputStarted(const FInputActionValue& Value)
{
    // 조건 체크: 스태미나, 쿨다운 등
    if (CurrentStamina < SkillStaminaCost)
    {
        // 스태미나 부족 - 입력 무시
        return;
    }

    if (bIsSkillOnCooldown)
    {
        // 쿨다운 중 - 입력 무시
        return;
    }

    // 조건 충족 - 스킬 실행
    ExecuteSkill();
}
```

### 3. InputModifier 활용

InputModifier는 입력 값을 변환하는 기능입니다. C++에서 커스텀 Modifier를 만들 수 있습니다:

```cpp
// CustomInputModifier.h
#pragma once

#include "CoreMinimal.h"
#include "InputModifiers.h"
#include "CustomInputModifier.generated.h"

UCLASS()
class MYPROJECT_API UCustomDeadzoneModifier : public UInputModifier
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float DeadzoneLower = 0.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float DeadzoneUpper = 0.8f;

protected:
    virtual FInputActionValue ModifyRaw_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue CurrentValue, float DeltaTime) override;
};
```

```cpp
// CustomInputModifier.cpp
#include "CustomInputModifier.h"

FInputActionValue UCustomDeadzoneModifier::ModifyRaw_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue CurrentValue, float DeltaTime)
{
    FVector2D Value = CurrentValue.Get<FVector2D>();
    float Magnitude = Value.Size();

    // 데드존 처리
    if (Magnitude < DeadzoneLower)
    {
        return FInputActionValue(FVector2D::ZeroVector);
    }

    if (Magnitude > DeadzoneUpper)
    {
        Value.Normalize();
    }

    return FInputActionValue(Value);
}
```

**에디터에서 적용**:
1. InputMappingContext 열기
2. 해당 InputAction의 Modifiers 섹션에서 **+** 클릭
3. `CustomDeadzoneModifier` 선택
4. `Deadzone Lower`, `Deadzone Upper` 값 조정

### 4. InputTrigger 커스터마이징

InputTrigger는 입력이 "발동"되는 조건을 정의합니다:

```cpp
// CustomInputTrigger.h
#pragma once

#include "CoreMinimal.h"
#include "InputTriggers.h"
#include "CustomInputTrigger.generated.h"

// 더블탭 감지 트리거
UCLASS()
class MYPROJECT_API UInputTriggerDoubleTap : public UInputTrigger
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float DoubleTapTime = 0.3f;

protected:
    virtual ETriggerState UpdateState_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue ModifiedValue, float DeltaTime) override;

private:
    float LastTapTime = 0.0f;
};
```

```cpp
// CustomInputTrigger.cpp
#include "CustomInputTrigger.h"

ETriggerState UInputTriggerDoubleTap::UpdateState_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue ModifiedValue, float DeltaTime)
{
    // 입력이 눌렸는지 확인
    if (IsActuated(ModifiedValue))
    {
        float CurrentTime = PlayerInput->GetWorld()->GetTimeSeconds();

        // 더블탭 시간 내에 두 번째 탭이 감지되면 Triggered
        if (CurrentTime - LastTapTime <= DoubleTapTime)
        {
            LastTapTime = 0.0f;  // 리셋
            return ETriggerState::Triggered;
        }

        // 첫 번째 탭 기록
        LastTapTime = CurrentTime;
        return ETriggerState::Ongoing;
    }

    return ETriggerState::None;
}
```

**실전 활용**:
- 더블탭으로 대시
- 길게 누르기로 차징 스킬
- 연타로 콤보 공격

### 5. 동적 InputAction 생성 (런타임)

런타임에 InputAction을 동적으로 생성하고 바인딩할 수 있습니다:

```cpp
void AMyCharacter::CreateDynamicInputAction()
{
    // 런타임에 InputAction 생성
    UInputAction* DynamicAction = NewObject<UInputAction>(this, UInputAction::StaticClass());
    DynamicAction->ValueType = EInputActionValueType::Axis1D;

    // MappingContext에 추가
    if (DefaultMappingContext && DynamicAction)
    {
        // 주의: 런타임 수정은 에디터 에셋에는 저장되지 않음
        FEnhancedActionKeyMapping& Mapping = DefaultMappingContext->MapKey(DynamicAction, EKeys::E);

        // PlayerController에 다시 적용
        if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
        {
            if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
                ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
            {
                // MappingContext 재적용
                Subsystem->RemoveMappingContext(DefaultMappingContext);
                Subsystem->AddMappingContext(DefaultMappingContext, 0);
            }
        }
    }

    // 바인딩
    if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(InputComponent))
    {
        EnhancedInputComponent->BindAction(DynamicAction, ETriggerEvent::Triggered, this, &AMyCharacter::OnDynamicAction);
    }
}

void AMyCharacter::OnDynamicAction(const FInputActionValue& Value)
{
    // 동적 액션 처리
    UE_LOG(LogTemp, Warning, TEXT("Dynamic Action Triggered!"));
}
```

**주의사항**:
- 런타임 생성은 복잡도를 높이므로 꼭 필요한 경우에만 사용
- 에디터 에셋으로 관리하는 것이 일반적으로 더 안전하고 디버깅하기 쉬움

## 주요 함수 레퍼런스

| 함수 | 설명 |
|------|------|
| `AddMappingContext(Context, Priority)` | MappingContext 추가 (우선순위 지정) |
| `RemoveMappingContext(Context)` | MappingContext 제거 |
| `ClearAllMappings()` | 모든 MappingContext 제거 |
| `BindAction(Action, Event, Object, Function)` | InputAction을 함수에 바인딩 |
| `Value.Get<T>()` | FInputActionValue에서 타입별 값 추출 |

## 문제 해결

### 입력이 동작하지 않는 경우

1. **MappingContext가 추가되었는지 확인**:
   ```cpp
   // BeginPlay에서 로그 추가
   UE_LOG(LogTemp, Warning, TEXT("MappingContext Added: %s"), DefaultMappingContext ? TEXT("Yes") : TEXT("No"));
   ```

2. **InputAction이 null이 아닌지 확인**:
   ```cpp
   // SetupPlayerInputComponent에서 체크
   if (!MoveAction)
   {
       UE_LOG(LogTemp, Error, TEXT("MoveAction is null!"));
   }
   ```

3. **EnhancedInput 플러그인 활성화 확인**:
   - Edit → Plugins → "Enhanced Input" 검색 → 체크박스 활성화
   - 프로젝트 재시작

4. **Project Settings 확인**:
   - Edit → Project Settings → Input
   - **Default Classes** → `Default Player Input Class`: `EnhancedPlayerInput`
   - **Default Input Component Class**: `EnhancedInputComponent`

### Hot Reload 후 입력이 사라지는 경우

Hot Reload는 UPROPERTY 참조를 초기화할 수 있습니다. 이 경우:
- 에디터 재시작
- 또는 블루프린트를 다시 컴파일

## 마치며

EnhancedInput은 강력하고 유연한 입력 시스템이지만, 초기 설정이 Legacy Input보다 복잡합니다. 하지만 일단 구조를 이해하면:
- 여러 입력 컨텍스트를 쉽게 전환 가능
- Modifier와 Trigger로 정교한 입력 처리
- 블루프린트와 C++ 간 매끄러운 연동

이 가이드를 참고하여 프로젝트에 맞는 입력 시스템을 구축하시기 바랍니다.
