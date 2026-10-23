#include "Development/DeveloperToolboxComponent.h"
#include "FantasyLifeRPGCharacter.h"
#include "Development/DeveloperScenario.h"
#include "Development/DeveloperToolboxWidget.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Blueprint/WidgetBlueprintLibrary.h"

#define LOCTEXT_NAMESPACE "DeveloperToolbox"

UDeveloperToolboxComponent::UDeveloperToolboxComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	WidgetClass = UDeveloperToolboxWidget::StaticClass();
	ScenarioClasses.Add(UDeveloperNPCRouteScenario::StaticClass());
}

bool UDeveloperToolboxComponent::CanUse() const
{
#if UE_BUILD_SHIPPING
	return false;
#else
	const APlayerController* Owner = Cast<APlayerController>(GetOwner());
	return bEnabled && Owner && Owner->HasAuthority() && Owner->IsLocalPlayerController()
		&& Owner->GetLocalPlayer() && GetWorld() && GetWorld()->IsGameWorld()
		&& GetWorld()->GetNetMode() == NM_Standalone && !GetWorld()->bIsTearingDown;
#endif
}

void UDeveloperToolboxComponent::BeginPlay()
{
	Super::BeginPlay();
	PC = Cast<APlayerController>(GetOwner());
	if (!CanUse()) { SetComponentTickEnabled(false); return; }
	EffectTester = NewObject<UDeveloperEffectTester>(this);
	for (const TSubclassOf<UDeveloperScenario>& Class : ScenarioClasses)
		if (Class) Scenarios.Add(NewObject<UDeveloperScenario>(this, Class));
	SetupInput();
	Report(LOCTEXT("Ready", "Bereit. F6 öffnet die Toolbox; die Welt läuft weiter."));
}

void UDeveloperToolboxComponent::SetupInput()
{
	UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer());
	if (!Subsystem) return;
	InputContext = NewObject<UInputMappingContext>(this);
	ToolInput = NewObject<UEnhancedInputComponent>(GetOwner(), TEXT("DeveloperToolboxInput"));
	ToolInput->Priority = 100;
	ToolInput->RegisterComponent();
	PC->PushInputComponent(ToolInput);
	auto Action = [this](EInputActionValueType Type, const TCHAR* Name)
	{
		UInputAction* Result = NewObject<UInputAction>(InputContext, Name);
		Result->ValueType = Type;
		// Only this pushed input component consumes these actions; mappings below stay unchanged.
		return Result;
	};
	auto Map = [this](UInputAction* Input, FKey Key, bool bNegative = false)
	{
		FEnhancedActionKeyMapping& Mapping = InputContext->MapKey(Input, Key);
		if (bNegative) Mapping.Modifiers.Add(NewObject<UInputModifierNegate>(InputContext));
	};
	UInputAction* Toggle = Action(EInputActionValueType::Boolean,TEXT("ToolboxToggle"));
	Map(Toggle,EKeys::F6);
	ToolInput->BindAction(Toggle,ETriggerEvent::Started,this,&UDeveloperToolboxComponent::TogglePanel);
	auto Axis = [&](const TCHAR* Name, FKey Positive, FKey Negative, auto Method)
	{
		UInputAction* Input = Action(EInputActionValueType::Axis1D,Name);
		Map(Input,Positive); Map(Input,Negative,true);
		ToolInput->BindAction(Input,ETriggerEvent::Triggered,this,Method);
		ToolInput->BindAction(Input,ETriggerEvent::Completed,this,Method);
		ToolInput->BindAction(Input,ETriggerEvent::Canceled,this,Method);
	};
	Axis(TEXT("ToolboxForward"),EKeys::W,EKeys::S,&UDeveloperToolboxComponent::Forward);
	Axis(TEXT("ToolboxRight"),EKeys::D,EKeys::A,&UDeveloperToolboxComponent::Right);
	Axis(TEXT("ToolboxVertical"),EKeys::SpaceBar,EKeys::LeftControl,&UDeveloperToolboxComponent::Vertical);
	for (const auto& Pair : {TPair<FKey,void(UDeveloperToolboxComponent::*)(const FInputActionValue&)>(EKeys::MouseX,&UDeveloperToolboxComponent::LookYaw),
		TPair<FKey,void(UDeveloperToolboxComponent::*)(const FInputActionValue&)>(EKeys::MouseY,&UDeveloperToolboxComponent::LookPitch)})
	{
		UInputAction* Input = Action(EInputActionValueType::Axis1D, Pair.Key == EKeys::MouseX ? TEXT("ToolboxYaw") : TEXT("ToolboxPitch"));
		Map(Input,Pair.Key);
		ToolInput->BindAction(Input,ETriggerEvent::Triggered,this,Pair.Value);
	}
	UInputAction* Speed = Action(EInputActionValueType::Boolean,TEXT("ToolboxBoost"));
	Map(Speed,EKeys::LeftShift);
	Map(Speed,EKeys::RightShift);
	ToolInput->BindAction(Speed,ETriggerEvent::Triggered,this,&UDeveloperToolboxComponent::Boost);
	ToolInput->BindAction(Speed,ETriggerEvent::Completed,this,&UDeveloperToolboxComponent::Boost);
	ToolInput->BindAction(Speed,ETriggerEvent::Canceled,this,&UDeveloperToolboxComponent::Boost);
	// Initially only F6 is mapped. Movement mappings must not consume normal gameplay actions.
	FModifyContextOptions InitialOptions;
	InitialOptions.bIgnoreAllPressedKeysUntilRelease = false;
	InitialOptions.bForceImmediately = true;
	Subsystem->AddMappingContext(InputContext,100,InitialOptions);
	UpdateInputBlock();
}

void UDeveloperToolboxComponent::UpdateInputBlock()
{
	if (ToolInput) ToolInput->bBlockInput = bPanelOpen || bFlight || bNoClip || FreeCamera;
	if (!InputContext || !PC.IsValid()) return;
	// Enhanced Input consumes keys during mapping evaluation, independently of component blocking.
	// Let normal pawn mappings run when the tools are idle; intercept only while a tool owns input.
	for (const FEnhancedActionKeyMapping& Mapping : InputContext->GetMappings())
		if (Mapping.Action && Mapping.Key != EKeys::F6)
			const_cast<UInputAction*>(Mapping.Action.Get())->bConsumeInput = bPanelOpen || bFlight || bNoClip || FreeCamera;
	if (auto* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
	{
		FModifyContextOptions Options;
		// Explicitly flushing on focus changes prevents stale input. Do not discard a fresh F6 press
		// while a deferred initial/context rebuild is pending (boolean actions default to ignore-held).
		Options.bIgnoreAllPressedKeysUntilRelease = false;
		Subsystem->RequestRebuildControlMappings(Options);
	}
}

void UDeveloperToolboxComponent::ClearAxes() { Axes = FVector::ZeroVector; bBoost = false; }
void UDeveloperToolboxComponent::FlushInput()
{
	ClearAxes();
	RestoreGroundSprint();
	if (PC.IsValid())
	{
		if (PC->PlayerInput) PC->PlayerInput->FlushPressedKeys();
		if (auto* Pawn = Cast<AFantasyLifeRPGCharacter>(PC->GetPawn())) Pawn->RefreshMovementSpeed();
	}
}

void UDeveloperToolboxComponent::TogglePanel()
{
	if (!CanUse()) return;
	if (bPanelOpen) { CloseInternal(); return; }
	if (PC->IsMoveInputIgnored() || PC->IsLookInputIgnored()) return;
	if (!Panel) Panel = CreateWidget<UDeveloperToolboxWidget>(PC.Get(),WidgetClass);
	if (!Panel) return;
	Panel->InitializeToolbox(this);
	bPanelOpen = true;
	bPreviousCursor = PC->bShowMouseCursor;
	PC->SetIgnoreMoveInput(true); bMoveLock = true;
	PC->SetIgnoreLookInput(true); bLookLock = true;
	if (ACharacter* Pawn = Cast<ACharacter>(PC->GetPawn()))
	{
		Pawn->StopJumping(); Pawn->GetCharacterMovement()->StopMovementImmediately();
	}
	FlushInput(); UpdateInputBlock();
	Panel->AddToPlayerScreen(1000);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode;
	Mode.SetWidgetToFocus(Panel->TakeWidget());
	Mode.SetHideCursorDuringCapture(false);
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
	Panel->SetKeyboardFocus();
}

void UDeveloperToolboxComponent::ClosePanel() { if (CanUse()) CloseInternal(); }
void UDeveloperToolboxComponent::CloseInternal()
{
	if (!bPanelOpen) return;
	bPanelOpen = false;
	if (Panel) Panel->RemoveFromParent();
	if (PC.IsValid())
	{
		if (bMoveLock) PC->SetIgnoreMoveInput(false);
		if (bLookLock) PC->SetIgnoreLookInput(false);
		PC->bShowMouseCursor = bPreviousCursor;
		PC->SetInputMode(FInputModeGameOnly());
		UWidgetBlueprintLibrary::SetFocusToGameViewport();
	}
	bMoveLock = bLookLock = false;
	FlushInput(); UpdateInputBlock();
}

bool UDeveloperToolboxComponent::CaptureCharacter()
{
	ACharacter* Pawn = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
	if (!Pawn) return false;
	if (bHasSnapshot) return Character.Get() == Pawn;
	RestoreGroundSprint();
	Character = Pawn;
	UCharacterMovementComponent* Move = Pawn->GetCharacterMovement();
	PreviousMovementMode = Move->MovementMode;
	PreviousCustomMode = Move->CustomMovementMode;
	PreviousFlySpeed = Move->MaxFlySpeed;
	PreviousAcceleration = Move->MaxAcceleration;
	// Read current Enhanced Input axes before CharacterMovement consumes this frame's movement.
	Move->AddTickPrerequisiteComponent(this);
	bPreviousCollision = Pawn->GetActorEnableCollision();
	OriginalTransform = LastSafeTransform = Pawn->GetActorTransform();
	bHasSnapshot = true;
	Pawn->StopJumping(); Move->StopMovementImmediately();
	return true;
}

void UDeveloperToolboxComponent::ApplyMovement()
{
	if (!Character.IsValid()) return;
	Character->GetCharacterMovement()->StopMovementImmediately();
	if (bFlight || bNoClip)
	{
		Character->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
		Character->GetCharacterMovement()->MaxFlySpeed = FlightSpeed * (bBoost ? 3.f : 1.f);
		Character->GetCharacterMovement()->MaxAcceleration = 100000.f;
		Character->SetActorEnableCollision(bNoClip ? false : bPreviousCollision);
	}
	else RestoreCharacter();
	ClearAxes(); UpdateInputBlock();
}

bool UDeveloperToolboxComponent::SetFlight(bool bValue)
{
	if (!CanUse() || (bValue && !CaptureCharacter())) return false;
	bFlight = bValue;
	ApplyMovement();
	return true;
}

bool UDeveloperToolboxComponent::FindSafeLocation(FVector& Location) const
{
	if (!Character.IsValid() || !GetWorld()) return false;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(ToolboxSafeExit),false,Character.Get());
	const UCapsuleComponent* Capsule = Character->GetCapsuleComponent();
	const FCollisionShape Shape = FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight() - .5f);
	for (const FVector& Candidate : {Character->GetActorLocation(),LastSafeTransform.GetLocation(),OriginalTransform.GetLocation()})
	{
		if (!GetWorld()->OverlapBlockingTestByProfile(Candidate,Character->GetActorQuat(),Capsule->GetCollisionProfileName(),Shape,Query))
		{
			Location = Candidate; return true;
		}
	}
	return false;
}

bool UDeveloperToolboxComponent::SetNoClip(bool bValue)
{
	if (!CanUse() || (bValue && !CaptureCharacter())) return false;
	if (!bValue && bNoClip && bPreviousCollision)
	{
		FVector Safe;
		if (!FindSafeLocation(Safe))
		{
			Report(LOCTEXT("NoSafeExit","Kein freier Rückkehrpunkt. NoClip bleibt aktiv; erst aus dem Hindernis bewegen."));
			return false;
		}
		Character->SetActorLocation(Safe,false,nullptr,ETeleportType::TeleportPhysics);
	}
	bNoClip = bValue;
	ApplyMovement();
	return true;
}

void UDeveloperToolboxComponent::RestoreCharacter()
{
	if (!bHasSnapshot) return;
	if (Character.IsValid())
	{
		Character->SetActorEnableCollision(bPreviousCollision);
		UCharacterMovementComponent* Move = Character->GetCharacterMovement();
		Move->StopMovementImmediately();
		Move->MaxFlySpeed = PreviousFlySpeed;
		Move->MaxAcceleration = PreviousAcceleration;
		Move->SetMovementMode(static_cast<EMovementMode>(PreviousMovementMode),PreviousCustomMode);
		Move->RemoveTickPrerequisiteComponent(this);
	}
	bHasSnapshot = false;
}

void UDeveloperToolboxComponent::UpdateGroundSprint()
{
	// Gameplay characters own their ground speed, including crouch/slow walk/UI gates.
	// Keep the toolbox fallback for the unrelated template character variants.
	if (PC.IsValid() && Cast<AFantasyLifeRPGCharacter>(PC->GetPawn()))
	{
		RestoreGroundSprint();
		return;
	}

	ACharacter* Pawn = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
	const bool bWantsSprint = bBoost && !bPanelOpen && !bFlight && !bNoClip && !FreeCamera && Pawn
		&& !PC->IsMoveInputIgnored() && (Pawn->GetCharacterMovement()->IsMovingOnGround() || Pawn->GetCharacterMovement()->IsFalling());
	if (SprintCharacter.IsValid() && (SprintCharacter.Get() != Pawn || !bWantsSprint)) RestoreGroundSprint();
	if (bWantsSprint && !SprintCharacter.IsValid())
	{
		SprintCharacter = Pawn;
		UCharacterMovementComponent* Move = Pawn->GetCharacterMovement();
		PreviousWalkSpeed = Move->MaxWalkSpeed;
		Move->MaxWalkSpeed = PreviousWalkSpeed * 2.f;
		Move->AddTickPrerequisiteComponent(this);
	}
}

void UDeveloperToolboxComponent::RestoreGroundSprint()
{
	if (SprintCharacter.IsValid())
	{
		UCharacterMovementComponent* Move = SprintCharacter->GetCharacterMovement();
		Move->MaxWalkSpeed = PreviousWalkSpeed;
		if (!bHasSnapshot) Move->RemoveTickPrerequisiteComponent(this);
	}
	SprintCharacter.Reset();
}

bool UDeveloperToolboxComponent::SetFreeCamera(bool bValue)
{
	if (!CanUse()) return false;
	if (bValue == IsFreeCamera()) return true;
	if (!bValue) { EndFreeCamera(); return true; }
	if (!PC->GetPawn()) return false;
	FVector Location; FRotator Rotation;
	PC->GetPlayerViewPoint(Location,Rotation);
	FActorSpawnParameters Params; Params.ObjectFlags |= RF_Transient;
	FreeCamera = GetWorld()->SpawnActor<ACameraActor>(Location,Rotation,Params);
	if (!FreeCamera) return false;
	FreeCamera->SetActorEnableCollision(false);
	if (PC->PlayerCameraManager) FreeCamera->GetCameraComponent()->FieldOfView = PC->PlayerCameraManager->GetFOVAngle();
	PreviousViewTarget = PC->GetViewTarget();
	CameraPawn = PC->GetPawn();
	PreviousControlRotation = PC->GetControlRotation();
	PC->SetViewTarget(FreeCamera);
	if (ACharacter* Pawn = Cast<ACharacter>(PC->GetPawn())) Pawn->GetCharacterMovement()->StopMovementImmediately();
	FlushInput(); UpdateInputBlock();
	return true;
}

void UDeveloperToolboxComponent::EndFreeCamera()
{
	if (!FreeCamera) return;
	if (PC.IsValid())
	{
		if (PC->GetViewTarget() == FreeCamera)
			PC->SetViewTarget(PreviousViewTarget.IsValid() && CameraPawn.Get() == PC->GetPawn() ? PreviousViewTarget.Get() : PC->GetPawn());
		PC->SetControlRotation(PreviousControlRotation);
	}
	FreeCamera->Destroy(); FreeCamera = nullptr;
	PreviousViewTarget.Reset(); CameraPawn.Reset();
	FlushInput(); UpdateInputBlock();
}

void UDeveloperToolboxComponent::SetFlightSpeed(float Value)
{
	if (!CanUse() || !FMath::IsFinite(Value)) return;
	FlightSpeed = FMath::Clamp(Value,100.f,5000.f);
	if (bHasSnapshot && Character.IsValid()) Character->GetCharacterMovement()->MaxFlySpeed = FlightSpeed;
}
void UDeveloperToolboxComponent::SetCameraSpeed(float Value)
{
	if (CanUse() && FMath::IsFinite(Value)) CameraSpeed = FMath::Clamp(Value,100.f,5000.f);
}
void UDeveloperToolboxComponent::Forward(const FInputActionValue& Value) { Axes.X = Value.Get<float>(); }
void UDeveloperToolboxComponent::Right(const FInputActionValue& Value) { Axes.Y = Value.Get<float>(); }
void UDeveloperToolboxComponent::Vertical(const FInputActionValue& Value) { Axes.Z = Value.Get<float>(); }
void UDeveloperToolboxComponent::Boost(const FInputActionValue& Value) { bBoost = Value.Get<bool>(); }
void UDeveloperToolboxComponent::LookYaw(const FInputActionValue& Value)
{
	if (bPanelOpen || !CanUse()) return;
	if (FreeCamera) FreeCamera->AddActorWorldRotation(FRotator(0,Value.Get<float>(),0));
	else if (bFlight || bNoClip) PC->AddYawInput(Value.Get<float>());
}
void UDeveloperToolboxComponent::LookPitch(const FInputActionValue& Value)
{
	if (bPanelOpen || !CanUse()) return;
	if (FreeCamera)
	{
		FRotator Rotation = FreeCamera->GetActorRotation();
		// Unreal reports MouseY positive upward; camera pitch uses the same convention.
		Rotation.Pitch = FMath::Clamp(FRotator::NormalizeAxis(Rotation.Pitch) + Value.Get<float>(),-89.f,89.f);
		FreeCamera->SetActorRotation(Rotation);
	}
	else if (bFlight || bNoClip) PC->AddPitchInput(-Value.Get<float>());
}

void UDeveloperToolboxComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* Function)
{
	Super::TickComponent(DeltaTime,TickType,Function);
	if (!CanUse()) { Cleanup(); return; }
	// Another local UI can own input too. Do not retain axes/boost when its
	// higher-priority input component prevents delivery of release callbacks.
	if (PC->IsMoveInputIgnored() || PC->IsLookInputIgnored()) ClearAxes();
	UpdateGroundSprint();
	if (bHasSnapshot && (!Character.IsValid() || PC->GetPawn() != Character.Get()))
	{
		if (Character.IsValid() && bNoClip)
		{
			FVector Safe;
			if (FindSafeLocation(Safe)) Character->SetActorLocation(Safe,false,nullptr,ETeleportType::TeleportPhysics);
		}
		bNoClip = bFlight = false; RestoreCharacter(); EndFreeCamera();
		FlushInput(); UpdateInputBlock(); return;
	}
	if (FreeCamera && CameraPawn.Get() != PC->GetPawn()) { EndFreeCamera(); return; }
	if (FreeCamera && PC->GetViewTarget() != FreeCamera) { EndFreeCamera(); return; }
	if (bPanelOpen || PC->IsMoveInputIgnored() || PC->IsLookInputIgnored()) { ClearAxes(); return; }
	if (FreeCamera)
	{
		const FRotator Rotation(0,FreeCamera->GetActorRotation().Yaw,0);
		const FVector Direction = FRotationMatrix(Rotation).GetUnitAxis(EAxis::X)*Axes.X + FRotationMatrix(Rotation).GetUnitAxis(EAxis::Y)*Axes.Y + FVector::UpVector*Axes.Z;
		FreeCamera->AddActorWorldOffset(Direction.GetClampedToMaxSize(1.f)*CameraSpeed*(bBoost ? 3.f : 1.f)*DeltaTime);
	}
	else if ((bFlight || bNoClip) && Character.IsValid())
	{
		const FRotator Rotation(0,PC->GetControlRotation().Yaw,0);
		UCharacterMovementComponent* Move = Character->GetCharacterMovement();
		Move->MaxFlySpeed = FlightSpeed*(bBoost ? 3.f : 1.f);
		Move->Velocity = Move->Velocity.GetClampedToMaxSize(Move->MaxFlySpeed);
		const FVector MovementAxes(Axes.X,Axes.Y,bFlight ? Axes.Z : 0.f);
		if (MovementAxes.IsNearlyZero())
		{
			// Flying defaults to gradual braking. The developer controls should hold position instead.
			Character->ConsumeMovementInputVector();
			Move->StopMovementImmediately();
		}
		else
		{
			Character->AddMovementInput(FRotationMatrix(Rotation).GetUnitAxis(EAxis::X),MovementAxes.X);
			Character->AddMovementInput(FRotationMatrix(Rotation).GetUnitAxis(EAxis::Y),MovementAxes.Y);
			Character->AddMovementInput(FVector::UpVector,MovementAxes.Z);
		}
	}
	if (bHasSnapshot && Character.IsValid() && !bNoClip) LastSafeTransform = Character->GetActorTransform();
}

void UDeveloperToolboxComponent::ResetTools()
{
	if (!CanUse()) return;
	EndFreeCamera();
	if (!SetNoClip(false)) return;
	SetFlight(false);
	if (EffectTester) EffectTester->StopAll();
	for (UDeveloperScenario* Scenario : Scenarios) if (Scenario) Scenario->Cleanup();
	FlightSpeed = 900.f; CameraSpeed = 1200.f;
	FlushInput();
	Report(LOCTEXT("Reset","Werkzeuge zurückgesetzt. Ursprüngliche Bewegungswerte wiederhergestellt."));
}

void UDeveloperToolboxComponent::Cleanup()
{
	if (bCleaning) return;
	bCleaning = true;
	RestoreGroundSprint();
	CloseInternal(); EndFreeCamera();
	// During world teardown no collision resolution is needed; in a live world still try the safe exit.
	if (bNoClip && Character.IsValid() && GetWorld() && !GetWorld()->bIsTearingDown)
	{
		FVector Safe;
		if (FindSafeLocation(Safe)) Character->SetActorLocation(Safe,false,nullptr,ETeleportType::TeleportPhysics);
	}
	bNoClip = bFlight = false; RestoreCharacter();
	if (EffectTester) EffectTester->Cleanup();
	for (UDeveloperScenario* Scenario : Scenarios) if (Scenario) Scenario->Cleanup();
	if (PC.IsValid())
	{
		if (ToolInput) PC->PopInputComponent(ToolInput);
		if (auto* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
			if (InputContext) Subsystem->RemoveMappingContext(InputContext);
	}
	// Only flush a live tool input once; repeated disabled-tool cleanup must not
	// swallow the independent gameplay movement keys on subsequent frames.
	if (ToolInput) FlushInput();
	if (ToolInput) ToolInput->DestroyComponent();
	ToolInput = nullptr; InputContext = nullptr; Panel = nullptr;
	ClearAxes();
	bCleaning = false;
}
void UDeveloperToolboxComponent::EndPlay(const EEndPlayReason::Type Reason) { Cleanup(); Super::EndPlay(Reason); }
void UDeveloperToolboxComponent::OnUnregister() { Cleanup(); Super::OnUnregister(); }

#undef LOCTEXT_NAMESPACE
