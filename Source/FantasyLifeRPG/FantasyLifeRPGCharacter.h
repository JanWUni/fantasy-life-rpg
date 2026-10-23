// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Logging/LogMacros.h"
#include "FantasyLifeRPGCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UInputAction;
class UInputMappingContext;
class UEnhancedInputLocalPlayerSubsystem;
class UInteractionComponent;
class UInventoryComponent;
struct FInputActionValue;

DECLARE_LOG_CATEGORY_EXTERN(LogTemplateCharacter, Log, All);

/**
 *  A simple player-controllable third person character
 *  Implements a controllable orbiting camera
 */
UCLASS(abstract)
class AFantasyLifeRPGCharacter : public ACharacter
{
	GENERATED_BODY()

	/** Camera boom positioning the camera behind the character */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	USpringArmComponent* CameraBoom;

	/** Follow camera */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* FollowCamera;

protected:

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Interaction")
	TObjectPtr<UInteractionComponent> InteractionComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Inventory")
	TObjectPtr<UInventoryComponent> InventoryComponent;

	/** Optional; configured only by the interaction prototype Blueprint. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
	TObjectPtr<UInputAction> InteractAction;

	void HandleInteract();

	/** Jump Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* JumpAction;

	/** Move Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* MoveAction;

	/** Look Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* LookAction;

	/** Mouse Look Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* MouseLookAction;

public:

	/** Constructor */
	AFantasyLifeRPGCharacter(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

protected:


	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void UnPossessed() override;
	virtual void OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
	virtual void OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;

	/** Multipliers preserve the run speed configured by the character Blueprint. */
	UPROPERTY(EditDefaultsOnly, Category="Movement", meta=(ClampMin="0.1"))
	float SprintMultiplier = 2.f;
	UPROPERTY(EditDefaultsOnly, Category="Movement", meta=(ClampMin="0.1", ClampMax="1.0"))
	float WalkMultiplier = .4f;
	UPROPERTY(EditDefaultsOnly, Category="Movement", meta=(ClampMin="0.05"))
	float StanceTransitionSeconds = .22f;

	/** Initialize input action bindings */
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

protected:

	/** Called for movement input */
	void Move(const FInputActionValue& Value);

	/** Called for looking input */
	void Look(const FInputActionValue& Value);

public:

	/** Handles move inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoMove(float Right, float Forward);

	/** Handles look inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoLook(float Yaw, float Pitch);

	/** Handles jump pressed inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpStart();

	/** Handles jump pressed inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpEnd();

public:
	/** Re-evaluate immediately after an input/focus flush, without waiting for Tick. */
	void RefreshMovementSpeed();

	/** Smoothed presentation state; collision is always managed by CharacterMovement. */
	float GetCrouchPresentationAlpha() const { return CrouchPresentationAlpha; }
	float GetCrouchPresentationDrop() const { return CrouchPresentationDrop; }

private:
	bool CanUseGameplayMovement() const;
	void ToggleCrouch();
	void RemoveMovementMapping();
	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> MovementMapping;
	UPROPERTY(Transient) TObjectPtr<UInputAction> CrouchAction;
	TWeakObjectPtr<UEnhancedInputLocalPlayerSubsystem> MovementSubsystem;
	float RunSpeed = 500.f;
	float CrouchPresentationAlpha = 0.f;
	float CrouchPresentationDrop = 0.f;
	float CameraHeightCompensation = 0.f;
	FVector StandingCameraOffset = FVector::ZeroVector;

public:
	/** Returns CameraBoom subobject **/
	FORCEINLINE class USpringArmComponent* GetCameraBoom() const { return CameraBoom; }

	/** Returns FollowCamera subobject **/
	FORCEINLINE class UCameraComponent* GetFollowCamera() const { return FollowCamera; }
};
