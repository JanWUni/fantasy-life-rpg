// Copyright Epic Games, Inc. All Rights Reserved.

#include "FantasyLifeRPGCharacter.h"
#include "Engine/LocalPlayer.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/Controller.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "GameFramework/PlayerController.h"
#include "Development/DeveloperToolboxComponent.h"
#include "Movement/CrouchPoseMeshComponent.h"
#include "FantasyLifeRPG.h"
#include "Interaction/InteractionComponent.h"
#include "Inventory/InventoryComponent.h"

AFantasyLifeRPGCharacter::AFantasyLifeRPGCharacter(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer.SetDefaultSubobjectClass<UCrouchPoseMeshComponent>(ACharacter::MeshComponentName))
{
	PrimaryActorTick.bCanEverTick = true;
	GetCharacterMovement()->GetNavAgentPropertiesRef().bCanCrouch = true;
	GetCharacterMovement()->SetCrouchedHalfHeight(65.f);
	InteractionComponent = CreateDefaultSubobject<UInteractionComponent>(TEXT("InteractionComponent"));
	InventoryComponent = CreateDefaultSubobject<UInventoryComponent>(TEXT("InventoryComponent"));
	// Set size for collision capsule
	GetCapsuleComponent()->InitCapsuleSize(42.f, 96.0f);

	// Don't rotate when the controller rotates. Let that just affect the camera.
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	// Configure character movement
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 500.0f, 0.0f);

	// Note: For faster iteration times these variables, and many more, can be tweaked in the Character Blueprint
	// instead of recompiling to adjust them
	GetCharacterMovement()->JumpZVelocity = 500.f;
	GetCharacterMovement()->AirControl = 0.35f;
	GetCharacterMovement()->MaxWalkSpeed = 500.f;
	GetCharacterMovement()->MinAnalogWalkSpeed = 20.f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2000.f;
	GetCharacterMovement()->BrakingDecelerationFalling = 1500.0f;

	// Create a camera boom (pulls in towards the player if there is a collision)
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 400.0f;
	CameraBoom->bUsePawnControlRotation = true;

	// Create a follow camera
	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	// Note: The skeletal mesh and anim blueprint references on the Mesh component (inherited from Character)
	// are set in the derived blueprint asset named ThirdPersonCharacter (to avoid direct content references in C++)
}

void AFantasyLifeRPGCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	// Mapping is local to the possessed character; no Blueprint/input asset edits required.
	RemoveMovementMapping();
	if (const APlayerController* PC = Cast<APlayerController>(Controller))
		if (ULocalPlayer* LocalPlayer = PC->GetLocalPlayer())
			if (auto* Subsystem = LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
			{
				MovementMapping = NewObject<UInputMappingContext>(this);
				CrouchAction = NewObject<UInputAction>(this);
				CrouchAction->ValueType = EInputActionValueType::Boolean;
				MovementMapping->MapKey(CrouchAction, EKeys::LeftControl);
				MovementMapping->MapKey(CrouchAction, EKeys::RightControl);
				FModifyContextOptions Options;
				Options.bIgnoreAllPressedKeysUntilRelease = false;
				Subsystem->AddMappingContext(MovementMapping, 10, Options);
				MovementSubsystem = Subsystem;
			}
	// Set up action bindings
	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent)) {
		if (InteractAction)
		{
			EnhancedInputComponent->BindAction(InteractAction, ETriggerEvent::Started, this, &AFantasyLifeRPGCharacter::HandleInteract);
		}

		if (CrouchAction)
			EnhancedInputComponent->BindAction(CrouchAction, ETriggerEvent::Started, this, &AFantasyLifeRPGCharacter::ToggleCrouch);

		// Jumping
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &AFantasyLifeRPGCharacter::DoJumpStart);
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &AFantasyLifeRPGCharacter::DoJumpEnd);

		// Moving
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AFantasyLifeRPGCharacter::Move);
		EnhancedInputComponent->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &AFantasyLifeRPGCharacter::Look);

		// Looking
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AFantasyLifeRPGCharacter::Look);
	}
	else
	{
		UE_LOG(LogFantasyLifeRPG, Error, TEXT("'%s' Failed to find an Enhanced Input component! This template is built to use the Enhanced Input system. If you intend to use the legacy system, then you will need to update this C++ file."), *GetNameSafe(this));
	}
}

void AFantasyLifeRPGCharacter::HandleInteract()
{
	InteractionComponent->TryInteract();
}

void AFantasyLifeRPGCharacter::Move(const FInputActionValue& Value)
{
	// input is a Vector2D
	FVector2D MovementVector = Value.Get<FVector2D>();

	// route the input
	DoMove(MovementVector.X, MovementVector.Y);
}

void AFantasyLifeRPGCharacter::Look(const FInputActionValue& Value)
{
	// input is a Vector2D
	FVector2D LookAxisVector = Value.Get<FVector2D>();

	// route the input
	DoLook(LookAxisVector.X, LookAxisVector.Y);
}

void AFantasyLifeRPGCharacter::DoMove(float Right, float Forward)
{
	if (CanUseGameplayMovement())
	{
		// find out which way is forward
		const FRotator Rotation = GetController()->GetControlRotation();
		const FRotator YawRotation(0, Rotation.Yaw, 0);

		// get forward vector
		const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);

		// get right vector
		const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

		// add movement
		AddMovementInput(ForwardDirection, Forward);
		AddMovementInput(RightDirection, Right);
	}
}

void AFantasyLifeRPGCharacter::DoLook(float Yaw, float Pitch)
{
	if (CanUseGameplayMovement())
	{
		// add yaw and pitch input to controller
		AddControllerYawInput(Yaw);
		AddControllerPitchInput(Pitch);
	}
}

void AFantasyLifeRPGCharacter::DoJumpStart()
{
	if (CanUseGameplayMovement() && GetCharacterMovement()->IsMovingOnGround()
		&& !bIsCrouched && !GetCharacterMovement()->bWantsToCrouch)
		Jump();
}

void AFantasyLifeRPGCharacter::DoJumpEnd()
{
	// signal the character to stop jumping
	StopJumping();
}

void AFantasyLifeRPGCharacter::BeginPlay()
{
	Super::BeginPlay();
	RunSpeed = GetCharacterMovement()->MaxWalkSpeed;
	GetCharacterMovement()->MaxWalkSpeedCrouched = RunSpeed * WalkMultiplier;
	StandingCameraOffset = CameraBoom->TargetOffset;
	CrouchPresentationDrop = 2.f * FMath::Max(0.f, GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight() - GetCharacterMovement()->GetCrouchedHalfHeight());
}

bool AFantasyLifeRPGCharacter::CanUseGameplayMovement() const
{
	const auto* PC = Cast<APlayerController>(Controller);
	if (!PC || PC->IsMoveInputIgnored() || PC->IsLookInputIgnored()) return false;
	if (const auto* Tools = PC->FindComponentByClass<UDeveloperToolboxComponent>())
		if (Tools->IsPanelOpen() || Tools->IsFlying() || Tools->IsNoClip() || Tools->IsFreeCamera()) return false;
	return true;
}

void AFantasyLifeRPGCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	RefreshMovementSpeed();
	CrouchPresentationAlpha = FMath::FInterpConstantTo(CrouchPresentationAlpha, bIsCrouched ? 1.f : 0.f, DeltaSeconds, 1.f / FMath::Max(.05f, StanceTransitionSeconds));
	CameraHeightCompensation = FMath::FInterpConstantTo(CameraHeightCompensation, 0.f, DeltaSeconds,
		FMath::Max(1.f, CrouchPresentationDrop * .5f) / FMath::Max(.05f, StanceTransitionSeconds));
	CameraBoom->TargetOffset = StandingCameraOffset + FVector(0, 0, CameraHeightCompensation);
}

void AFantasyLifeRPGCharacter::RefreshMovementSpeed()
{
	auto* Movement = GetCharacterMovement();
	const auto* PC = Cast<APlayerController>(Controller);
	const bool bGroundControls = CanUseGameplayMovement();
	const bool bWalk = bGroundControls && (PC->IsInputKeyDown(EKeys::LeftAlt) || PC->IsInputKeyDown(EKeys::RightAlt));
	const bool bSprint = bGroundControls && !bIsCrouched && !Movement->bWantsToCrouch
		&& (PC->IsInputKeyDown(EKeys::LeftShift) || PC->IsInputKeyDown(EKeys::RightShift));
	Movement->MaxWalkSpeed = RunSpeed * (bWalk ? WalkMultiplier : bSprint ? SprintMultiplier : 1.f);
	Movement->MaxWalkSpeedCrouched = RunSpeed * WalkMultiplier;
}

void AFantasyLifeRPGCharacter::ToggleCrouch()
{
	if (!CanUseGameplayMovement() || !GetCharacterMovement()->IsMovingOnGround()) return;
	StopJumping();
	if (GetCharacterMovement()->bWantsToCrouch) UnCrouch();
	else Crouch();
}

void AFantasyLifeRPGCharacter::OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnStartCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	CameraHeightCompensation += ScaledHalfHeightAdjust;
	CameraBoom->TargetOffset = StandingCameraOffset + FVector(0, 0, CameraHeightCompensation);
}

void AFantasyLifeRPGCharacter::OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnEndCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	CameraHeightCompensation -= ScaledHalfHeightAdjust;
	CameraBoom->TargetOffset = StandingCameraOffset + FVector(0, 0, CameraHeightCompensation);
}

void AFantasyLifeRPGCharacter::RemoveMovementMapping()
{
	if (MovementSubsystem.IsValid() && MovementMapping) MovementSubsystem->RemoveMappingContext(MovementMapping);
	MovementSubsystem.Reset();
	MovementMapping = nullptr;
}

void AFantasyLifeRPGCharacter::UnPossessed()
{
	RemoveMovementMapping();
	Super::UnPossessed();
}

void AFantasyLifeRPGCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
	RemoveMovementMapping();
	Super::EndPlay(Reason);
}
