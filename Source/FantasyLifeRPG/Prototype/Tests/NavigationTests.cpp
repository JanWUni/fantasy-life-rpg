#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "AIController.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/TargetPoint.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "NPC/PrototypeNPC.h"
#include "NPC/PrototypeLocomotionComponent.h"
#include "NPC/WaypointMovementComponent.h"
#include "Prototype/PrototypeMessageComponent.h"
#include "Tests/AutomationEditorCommon.h"

class FNavigationPIECommand : public IAutomationLatentCommand
{
public:
	explicit FNavigationPIECommand(FAutomationTestBase* InTest) : Test(InTest), Deadline(FPlatformTime::Seconds() + 20) {}
	virtual bool Update() override
	{
		const double Now = FPlatformTime::Seconds();
		if (World.IsValid() && Step > 0)
		{
			const double Delta = World->GetDeltaSeconds();
			FrameTotal += Delta; FrameMax = FMath::Max(FrameMax, Delta); ++Frames;
			if (Delta > .1) ++SlowFrames;
		}
		if (Now < NextStep) return false;
		if (Step == 0)
		{
			for (const FWorldContext& Context : GEngine->GetWorldContexts())
			{
				if (Context.WorldType != EWorldType::PIE || !Context.World() || !Context.World()->GetMapName().Contains(TEXT("Lvl_EnvironmentTest_01"))) continue;
				World = Context.World(); PC = World->GetFirstPlayerController();
				Player = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
				for (TActorIterator<APrototypeNPC> It(World.Get()); It; ++It) if (It->ActorHasTag(TEXT("EnvironmentNPC"))) NPC = *It;
			}
			UNavigationSystemV1* Nav = World.IsValid() ? FNavigationSystem::GetCurrent<UNavigationSystemV1>(World.Get()) : nullptr;
			if ((!Player.IsValid() || !NPC.IsValid() || !Nav || UNavigationSystemV1::IsNavigationBeingBuilt(World.Get())) && Now < Deadline) return false;
			if (!Test->TestTrue(TEXT("Saved environment has player, NPC and ready navigation system"), Player.IsValid() && NPC.IsValid() && Nav)) return true;
			Route = NPC->FindComponentByClass<UWaypointMovementComponent>();
			Locomotion = NPC->FindComponentByClass<UPrototypeLocomotionComponent>();
			Feedback = Player->FindComponentByClass<UInteractionFeedbackComponent>();
			Messages = Player->FindComponentByClass<UPrototypeMessageComponent>();
			if (!Test->TestTrue(TEXT("NPC has modular route/animation and player has shared feedback"), Route.IsValid() && Locomotion.IsValid() && Feedback.IsValid() && Messages.IsValid())) return true;
			if (!Test->TestEqual(TEXT("Saved NPC references three editable waypoints"), Route->Waypoints.Num(), 3)) return true;
			for (AActor* Point : Route->Waypoints)
			{
				FNavLocation Projected;
				if (!Test->TestTrue(TEXT("Waypoint is valid and projects onto NavMesh"), IsValid(Point) && Nav->ProjectPointToNavigation(Point->GetActorLocation(), Projected, FVector(80, 80, 220)))) return true;
			}
			Route->StopRoute();
			NPC->SetActorLocation(Route->Waypoints[0]->GetActorLocation() + FVector(0, 0, 98), false, nullptr, ETeleportType::TeleportPhysics);
			Player->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
			Player->SetActorLocation(FVector(-1800, -3000, 400));
			const FVector From = Route->Waypoints[2]->GetActorLocation(), To = Route->Waypoints[0]->GetActorLocation();
			FHitResult Obstacle;
			FCollisionQueryParams Query(SCENE_QUERY_STAT(RouteObstacle), false, NPC.Get());
			Test->TestTrue(TEXT("Existing bench blocks the direct route segment"), World->LineTraceSingleByChannel(Obstacle, From + FVector(0, 0, 50), To + FVector(0, 0, 50), ECC_Visibility, Query));
			UNavigationPath* Path = UNavigationSystemV1::FindPathToLocationSynchronously(World.Get(), From, To, NPC.Get());
			Test->TestTrue(TEXT("NavMesh finds a complete detour around the bench"), Path && Path->IsValid() && !Path->IsPartial() && Path->PathPoints.Num() > 2);
			Route->StartRoute();
			// The first waypoint is already reached synchronously. Observe its wait
			// now; starting the clock next frame loses that frame's game time.
			ObserveRoute(Now);
			Deadline = Now + 45;
			++Step;
			return false;
		}
		if (!World.IsValid() || !NPC.IsValid() || !Route.IsValid() || !Player.IsValid()) { Test->AddError(TEXT("Navigation fixture disappeared")); return true; }
		if (Now > Deadline) { Test->AddError(FString::Printf(TEXT("Route timed out: state=%d, visits=%d, point=%d, location=%s"), int32(Route->GetRouteState()), Route->GetCompletedVisits(), Route->GetWaypointIndex(), *NPC->GetActorLocation().ToString())); return true; }
		if (Step <= 5) ObserveRoute(Now);
		if (Step == 1)
		{
			if (Route->GetRouteState() != EWaypointMovementState::Moving || NPC->GetVelocity().Size2D() < 70) return false;
			Player->SetActorLocation(NPC->GetActorLocation() + FVector(0, -125, 0));
			++Step; NextStep = Now + .15; return false;
		}
		if (Step == 2)
		{
			Test->TestEqual(TEXT("Moving NPC is selected by the existing interaction system"), Feedback->GetFocusedTarget(), static_cast<AActor*>(NPC.Get()));
			Test->TestEqual(TEXT("Moving NPC offers E - Sprechen"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 Sprechen")));
			Key(IE_Pressed); ++Step; NextStep = Now + .2; return false;
		}
		if (Step == 3)
		{
			Test->TestEqual(TEXT("Speaking pauses the active route"), Route->GetRouteState(), EWaypointMovementState::Paused);
			Test->TestTrue(TEXT("NPC stops to display its greeting"), Messages->IsMessageVisible() && NPC->GetVelocity().IsNearlyZero(1));
			Test->TestTrue(TEXT("NPC faces the speaker while paused"), FVector::DotProduct(NPC->GetActorForwardVector(), (Player->GetActorLocation() - NPC->GetActorLocation()).GetSafeNormal2D()) > .99);
			PausedAt = NPC->GetActorLocation(); PausedVisit = Route->GetCompletedVisits();
			Key(IE_Released); ++Step; NextStep = Now + 1; return false;
		}
		if (Step == 4)
		{
			Test->TestTrue(TEXT("Interaction pause holds position and does not advance the route"), Route->GetRouteState() == EWaypointMovementState::Paused && NPC->GetActorLocation().Equals(PausedAt, 1) && Route->GetCompletedVisits() == PausedVisit);
			Player->SetActorLocation(FVector(-1800, -3000, 400));
			++Step; return false;
		}
		if (Step == 5)
		{
			if (Route->GetCompletedVisits() < 7) return false;
			Test->TestTrue(TEXT("Idle and walking assets both played during the repeated route"), SawIdle && SawWalk);
			Test->TestTrue(TEXT("NPC uses a native AIController"), Cast<AAIController>(NPC->GetController()) != nullptr);
			WaitVisit = Route->GetCompletedVisits();
			Route->PauseFor(.5f); ++Step; NextStep = Now + .6; return false;
		}
		if (Step == 6)
		{
			Test->TestTrue(TEXT("Pausing at a waypoint preserves its remaining waiting time"), Route->GetRouteState() == EWaypointMovementState::Waiting && Route->GetCompletedVisits() == WaitVisit);
			Route->StopRoute(); SavedPoints = Route->Waypoints;
			Unreachable = World->SpawnActor<ATargetPoint>(FVector(20000, 20000, 80), FRotator::ZeroRotator);
			Route->Waypoints = { Unreachable.Get() };
			Route->StartRoute(); ++Step; NextStep = Now + .35; return false;
		}
		if (Step == 7)
		{
			Test->TestTrue(TEXT("Unreachable destination retries without counting a false arrival"), Route->GetRouteState() == EWaypointMovementState::Retrying && Route->GetCompletedVisits() == 0);
			Route->StopRoute(); Route->Waypoints = SavedPoints; Unreachable->Destroy();
			Route->StartRoute(); ++Step; NextStep = Now + .25; return false;
		}
		if (Step == 8)
		{
			Test->TestTrue(TEXT("Route can restart after an invalid destination"), Route->GetRouteState() != EWaypointMovementState::Stopped && Route->GetRouteState() != EWaypointMovementState::Retrying);
			Route->StopRoute(); StoppedAt = NPC->GetActorLocation(); ++Step; NextStep = Now + 1.2; return false;
		}
		Test->TestTrue(TEXT("StopRoute cancels outstanding movement and timers"), Route->GetRouteState() == EWaypointMovementState::Stopped && NPC->GetActorLocation().Equals(StoppedAt, 1));
		Test->AddInfo(FString::Printf(TEXT("NavigationPIE frame samples: n=%d mean=%.2fms max=%.2fms over100ms=%d (editor observation, not benchmark)"), Frames, FrameTotal * 1000 / FMath::Max(Frames, 1), FrameMax * 1000, SlowFrames));
		return true;
	}
private:
	void Key(EInputEvent Event) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E, Event, Event == IE_Released ? 0.f : 1.f)); }
	void ObserveRoute(double Now)
	{
		const EWaypointMovementState State = Route->GetRouteState();
		if (Route->GetCompletedVisits() != LastVisit)
		{
			Test->TestEqual(TEXT("Waypoints are visited in configured cyclic order"), Route->GetWaypointIndex(), LastVisit % 3);
			Test->TestEqual(TEXT("A completed move counts one arrival"), Route->GetCompletedVisits(), LastVisit + 1);
			LastVisit = Route->GetCompletedVisits(); WaitBegan = World->GetTimeSeconds(); ExpectedWait = Route->WaitSeconds;
			const FVector Target = Route->Waypoints[Route->GetWaypointIndex()]->GetActorLocation();
			Test->TestTrue(TEXT("Arrival is within the configured acceptance distance"), FVector::Dist2D(NPC->GetActorLocation(), Target) <= Route->AcceptanceRadius + 15);
		}
		if (LastState == EWaypointMovementState::Waiting && State == EWaypointMovementState::Moving)
		{
			const double Elapsed = World->GetTimeSeconds() - WaitBegan;
			if (LastVisit == 1) Test->AddInfo(FString::Printf(TEXT("First waypoint observed wait: %.3fs (configured %.3fs)"), Elapsed, ExpectedWait));
			Test->TestTrue(FString::Printf(TEXT("Waypoint wait uses game time (visit %d: %.3fs / %.3fs)"), LastVisit, Elapsed, ExpectedWait),
				Elapsed >= ExpectedWait - FMath::Max(.15, double(World->GetDeltaSeconds()) + .03));
			// First wait exercises the saved 1.5s default; subsequent waits exercise an editor-configurable value.
			Route->WaitSeconds = .4f;
		}
		LastState = State;
		UAnimSingleNodeInstance* Instance = NPC->GetMesh()->GetSingleNodeInstance();
		if (Instance) { SawIdle |= Instance->GetCurrentAsset() == Locomotion->IdleAnimation.Get(); SawWalk |= Instance->GetCurrentAsset() == Locomotion->WalkAnimation.Get(); }
	}
	FAutomationTestBase* Test;
	TWeakObjectPtr<UWorld> World;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Player;
	TWeakObjectPtr<APrototypeNPC> NPC;
	TWeakObjectPtr<UWaypointMovementComponent> Route;
	TWeakObjectPtr<UPrototypeLocomotionComponent> Locomotion;
	TWeakObjectPtr<UInteractionFeedbackComponent> Feedback;
	TWeakObjectPtr<UPrototypeMessageComponent> Messages;
	TWeakObjectPtr<ATargetPoint> Unreachable;
	TArray<TObjectPtr<AActor>> SavedPoints;
	EWaypointMovementState LastState = EWaypointMovementState::Stopped;
	FVector PausedAt, StoppedAt;
	int32 Step = 0, LastVisit = 0, PausedVisit = 0, WaitVisit = 0, Frames = 0, SlowFrames = 0;
	double Deadline, NextStep = 0, WaitBegan = 0, ExpectedWait = 0, FrameTotal = 0, FrameMax = 0;
	bool SawIdle = false, SawWalk = false;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNavigationPIETest, "FantasyLifeRPG.Environment.NavigationPIE", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FNavigationPIETest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_EnvironmentTest_01")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FNavigationPIECommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}
#endif
