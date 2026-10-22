#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AITypes.h"
#include "WaypointMovementComponent.generated.h"

class AAIController;
class ACharacter;
struct FPathFollowingResult;

UENUM(BlueprintType)
enum class EWaypointMovementState : uint8 { Stopped, Moving, Waiting, Paused, Retrying };

/** Small authority-only route runner. No dependency on NPC interaction or presentation. */
UCLASS(ClassGroup=(Prototype), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UWaypointMovementComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UWaypointMovementComponent();
	UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Route")
	TArray<TObjectPtr<AActor>> Waypoints;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Route")
	bool bAutoStart = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Route", meta=(ClampMin="0", Units="s"))
	float WaitSeconds = 1.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Route", meta=(ClampMin="1", Units="cm/s"))
	float WalkSpeed = 160.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Route", meta=(ClampMin="1", Units="cm"))
	float AcceptanceRadius = 25.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Route", meta=(ClampMin="0.2", Units="s"))
	float RetrySeconds = 1.f;

	UFUNCTION(BlueprintCallable, Category="Route")
	void StartRoute();
	UFUNCTION(BlueprintCallable, Category="Route")
	void StopRoute();
	/** Pause/resume the current leg or the remaining wait; repeated calls extend the pause. */
	UFUNCTION(BlueprintCallable, Category="Route")
	void PauseFor(float Seconds = 3.f);
	UFUNCTION(BlueprintPure, Category="Route")
	EWaypointMovementState GetRouteState() const { return State; }
	UFUNCTION(BlueprintPure, Category="Route")
	int32 GetWaypointIndex() const { return WaypointIndex; }
	UFUNCTION(BlueprintPure, Category="Route")
	int32 GetCompletedVisits() const { return CompletedVisits; }
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	void RequestMove();
	void OnMoveFinished(FAIRequestID ID, const FPathFollowingResult& Result);
	void Arrive();
	void Advance();
	void Resume();
	void ScheduleRetry();
	TWeakObjectPtr<ACharacter> Character;
	TWeakObjectPtr<AAIController> Controller;
	FDelegateHandle MoveFinishedHandle;
	FAIRequestID MoveID;
	FTimerHandle StepTimer;
	EWaypointMovementState State = EWaypointMovementState::Stopped;
	int32 WaypointIndex = 0;
	int32 CompletedVisits = 0;
	bool bResumeWait = false;
	float RemainingWait = 0.f;
};
