#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DeveloperEffectTester.h"
#include "DeveloperToolboxComponent.generated.h"

class ACharacter;
class ACameraActor;
class APlayerController;
class APawn;
class UDeveloperToolboxWidget;
class UDeveloperScenario;
class UEnhancedInputComponent;
class UInputMappingContext;
class UInputAction;
struct FInputActionValue;

/** Opt-in local development tools. Every public mutation checks the runtime gate. */
UCLASS(ClassGroup=(Development), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UDeveloperToolboxComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UDeveloperToolboxComponent();
	UPROPERTY(EditDefaultsOnly, Category="Development") bool bEnabled = false;
	UPROPERTY(EditDefaultsOnly, Category="Development") TSubclassOf<UDeveloperToolboxWidget> WidgetClass;
	UPROPERTY(EditDefaultsOnly, Category="Development") TArray<FDeveloperEffectEntry> Effects;
	UPROPERTY(EditDefaultsOnly, Category="Development") TArray<TSubclassOf<UDeveloperScenario>> ScenarioClasses;

	UFUNCTION(BlueprintPure, Category="Development") bool CanUse() const;
	UFUNCTION(BlueprintCallable, Category="Development") void TogglePanel();
	UFUNCTION(BlueprintCallable, Category="Development") void ClosePanel();
	UFUNCTION(BlueprintCallable, Category="Development") bool SetFlight(bool bValue);
	UFUNCTION(BlueprintCallable, Category="Development") bool SetNoClip(bool bValue);
	UFUNCTION(BlueprintCallable, Category="Development") bool SetFreeCamera(bool bValue);
	UFUNCTION(BlueprintCallable, Category="Development") void SetFlightSpeed(float Value);
	UFUNCTION(BlueprintCallable, Category="Development") void SetCameraSpeed(float Value);
	UFUNCTION(BlueprintCallable, Category="Development") void ResetTools();
	bool IsPanelOpen() const { return bPanelOpen; }
	bool IsFlying() const { return bFlight; }
	bool IsNoClip() const { return bNoClip; }
	bool IsFreeCamera() const { return FreeCamera != nullptr; }
	float GetFlightSpeed() const { return FlightSpeed; }
	float GetCameraSpeed() const { return CameraSpeed; }
	FText GetStatus() const { return Status; }
	void Report(const FText& Message) { Status = Message; }
	UDeveloperToolboxWidget* GetPanel() const { return Panel; }
	UDeveloperEffectTester* GetEffectTester() const { return EffectTester; }
	const TArray<TObjectPtr<UDeveloperScenario>>& GetScenarios() const { return Scenarios; }
	ACameraActor* GetFreeCamera() const { return FreeCamera; }
	/** Used for pawn changes, teardown, and explicit controller cleanup. */
	void Cleanup();
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void OnUnregister() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* Function) override;
private:
	void SetupInput();
	void UpdateInputBlock();
	void ClearAxes();
	void FlushInput();
	void CloseInternal();
	bool CaptureCharacter();
	void ApplyMovement();
	void RestoreCharacter();
	void UpdateGroundSprint();
	void RestoreGroundSprint();
	bool FindSafeLocation(FVector& Location) const;
	void EndFreeCamera();
	void Forward(const FInputActionValue& Value);
	void Right(const FInputActionValue& Value);
	void Vertical(const FInputActionValue& Value);
	void LookYaw(const FInputActionValue& Value);
	void LookPitch(const FInputActionValue& Value);
	void Boost(const FInputActionValue& Value);
	UPROPERTY(Transient) TObjectPtr<UEnhancedInputComponent> ToolInput;
	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> InputContext;
	UPROPERTY(Transient) TObjectPtr<UDeveloperToolboxWidget> Panel;
	UPROPERTY(Transient) TObjectPtr<UDeveloperEffectTester> EffectTester;
	UPROPERTY(Transient) TArray<TObjectPtr<UDeveloperScenario>> Scenarios;
	UPROPERTY(Transient) TObjectPtr<ACameraActor> FreeCamera;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Character;
	TWeakObjectPtr<ACharacter> SprintCharacter;
	TWeakObjectPtr<AActor> PreviousViewTarget;
	TWeakObjectPtr<APawn> CameraPawn;
	FRotator PreviousControlRotation;
	FTransform LastSafeTransform;
	FTransform OriginalTransform;
	uint8 PreviousMovementMode = 0, PreviousCustomMode = 0;
	float PreviousFlySpeed = 0;
	float PreviousAcceleration = 0;
	float PreviousWalkSpeed = 0;
	bool bPreviousCollision = true;
	bool bHasSnapshot = false;
	bool bFlight = false, bNoClip = false, bPanelOpen = false, bBoost = false;
	bool bPreviousCursor = false, bMoveLock = false, bLookLock = false;
	bool bCleaning = false;
	float FlightSpeed = 900.f, CameraSpeed = 1200.f;
	FVector Axes = FVector::ZeroVector;
	FText Status;
};
