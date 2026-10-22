#include "NPC/WaypointMovementComponent.h"
#include "AIController.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Navigation/PathFollowingComponent.h"
#include "TimerManager.h"

UWaypointMovementComponent::UWaypointMovementComponent() { PrimaryComponentTick.bCanEverTick = false; }

void UWaypointMovementComponent::BeginPlay()
{
	Super::BeginPlay();
	if (bAutoStart && GetOwner()->HasAuthority())
		StepTimer = GetWorld()->GetTimerManager().SetTimerForNextTick(this, &UWaypointMovementComponent::StartRoute);
}

void UWaypointMovementComponent::StartRoute()
{
	StopRoute();
	Character = Cast<ACharacter>(GetOwner());
	if (!Character.IsValid() || !Character->HasAuthority() || Waypoints.IsEmpty()) return;
	if (!Character->GetController()) Character->SpawnDefaultController();
	Controller = Cast<AAIController>(Character->GetController());
	if (!Controller.IsValid() || !Controller->GetPathFollowingComponent()) return;
	MoveFinishedHandle = Controller->GetPathFollowingComponent()->OnRequestFinished.AddUObject(this, &UWaypointMovementComponent::OnMoveFinished);
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	Movement->SetMovementMode(MOVE_Walking);
	Movement->MaxWalkSpeed = FMath::IsFinite(WalkSpeed) ? FMath::Max(1.f, WalkSpeed) : 160.f;
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0, 360, 0);
	WaypointIndex = CompletedVisits = 0;
	RequestMove();
}

void UWaypointMovementComponent::StopRoute()
{
	State = EWaypointMovementState::Stopped;
	if (GetWorld()) GetWorld()->GetTimerManager().ClearTimer(StepTimer);
	if (Controller.IsValid())
	{
		if (UPathFollowingComponent* Following = Controller->GetPathFollowingComponent()) Following->OnRequestFinished.Remove(MoveFinishedHandle);
		Controller->StopMovement();
	}
	MoveFinishedHandle.Reset();
	if (Character.IsValid()) Character->GetCharacterMovement()->StopMovementImmediately();
}

void UWaypointMovementComponent::RequestMove()
{
	if (!Character.IsValid() || !Character->HasAuthority() || !Controller.IsValid() || Waypoints.IsEmpty()) { StopRoute(); return; }
	WaypointIndex %= Waypoints.Num();
	int32 Checked = 0;
	while (!IsValid(Waypoints[WaypointIndex]) && Checked++ < Waypoints.Num()) WaypointIndex = (WaypointIndex + 1) % Waypoints.Num();
	if (!IsValid(Waypoints[WaypointIndex])) { StopRoute(); return; }
	// Ignore a completion/abort for an older request while the new one is submitted.
	State = EWaypointMovementState::Retrying;
	FAIMoveRequest Request(Waypoints[WaypointIndex]);
	Request.SetUsePathfinding(true);
	Request.SetAllowPartialPath(false);
	Request.SetAcceptanceRadius(FMath::IsFinite(AcceptanceRadius) ? FMath::Max(1.f, AcceptanceRadius) : 25.f);
	Request.SetReachTestIncludesAgentRadius(false);
	Request.SetReachTestIncludesGoalRadius(false);
	const FPathFollowingRequestResult Result = Controller->MoveTo(Request);
	MoveID = Result.MoveId;
	if (Result.Code == EPathFollowingRequestResult::AlreadyAtGoal) Arrive();
	else if (Result.Code == EPathFollowingRequestResult::RequestSuccessful) State = EWaypointMovementState::Moving;
	else ScheduleRetry();
}

void UWaypointMovementComponent::OnMoveFinished(FAIRequestID ID, const FPathFollowingResult& Result)
{
	if (State != EWaypointMovementState::Moving || ID != MoveID) return;
	if (Result.IsSuccess()) Arrive();
	else ScheduleRetry();
}

void UWaypointMovementComponent::Arrive()
{
	State = EWaypointMovementState::Waiting;
	++CompletedVisits;
	const float Delay = FMath::IsFinite(WaitSeconds) ? FMath::Max(.05f, WaitSeconds) : 1.5f;
	GetWorld()->GetTimerManager().SetTimer(StepTimer, this, &UWaypointMovementComponent::Advance, Delay, false);
}

void UWaypointMovementComponent::Advance()
{
	if (Waypoints.IsEmpty()) { StopRoute(); return; }
	WaypointIndex = (WaypointIndex + 1) % Waypoints.Num();
	RequestMove();
}

void UWaypointMovementComponent::ScheduleRetry()
{
	State = EWaypointMovementState::Retrying;
	const float Delay = FMath::IsFinite(RetrySeconds) ? FMath::Max(.2f, RetrySeconds) : 1.f;
	GetWorld()->GetTimerManager().SetTimer(StepTimer, this, &UWaypointMovementComponent::RequestMove, Delay, false);
}

void UWaypointMovementComponent::PauseFor(float Seconds)
{
	if (!GetOwner()->HasAuthority() || State == EWaypointMovementState::Stopped || !FMath::IsFinite(Seconds) || Seconds <= 0) return;
	if (State != EWaypointMovementState::Paused)
	{
		bResumeWait = State == EWaypointMovementState::Waiting;
		RemainingWait = bResumeWait ? FMath::Max(.05f, GetWorld()->GetTimerManager().GetTimerRemaining(StepTimer)) : 0.f;
	}
	else Seconds = FMath::Max(Seconds, GetWorld()->GetTimerManager().GetTimerRemaining(StepTimer));
	State = EWaypointMovementState::Paused;
	if (Controller.IsValid()) Controller->StopMovement();
	if (Character.IsValid()) Character->GetCharacterMovement()->StopMovementImmediately();
	GetWorld()->GetTimerManager().SetTimer(StepTimer, this, &UWaypointMovementComponent::Resume, Seconds, false);
}

void UWaypointMovementComponent::Resume()
{
	if (bResumeWait)
	{
		State = EWaypointMovementState::Waiting;
		GetWorld()->GetTimerManager().SetTimer(StepTimer, this, &UWaypointMovementComponent::Advance, RemainingWait, false);
	}
	else RequestMove();
}

void UWaypointMovementComponent::EndPlay(const EEndPlayReason::Type Reason) { StopRoute(); Super::EndPlay(Reason); }
