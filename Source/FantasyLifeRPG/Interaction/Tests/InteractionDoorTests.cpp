#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Misc/AutomationTest.h"
#include "Interaction/InteractableActor.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"
#include "Tests/AutomationEditorCommon.h"
#include "UObject/UnrealType.h"

/** Tests the saved Blueprint door through the existing input/interaction/feedback pipeline. */
class FInteractionDoorPIECommand : public IAutomationLatentCommand
{
public:
	explicit FInteractionDoorPIECommand(FAutomationTestBase* InTest)
		: Test(InTest), StartupDeadline(FPlatformTime::Seconds() + 20.0) {}

	virtual bool Update() override
	{
		if (FPlatformTime::Seconds() < NextStep) return false;
		if (Step == 0)
		{
			for (const FWorldContext& Context : GEngine->GetWorldContexts())
			{
				UWorld* World = Context.World();
				if (Context.WorldType != EWorldType::PIE || !World
					|| !World->GetMapName().Contains(TEXT("Lvl_Prototype_01"))) continue;
				PC = World->GetFirstPlayerController();
				Pawn = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
				for (TActorIterator<AActor> It(World); It; ++It)
				{
					if (It->ActorHasTag(TEXT("InteractionDoor"))) Door = Cast<AInteractableActor>(*It);
					if (It->ActorHasTag(TEXT("InteractionDoorFrame"))) Frame = *It;
				}
				break;
			}
			if ((!Pawn.IsValid() || !Door.IsValid() || !Frame.IsValid()) && FPlatformTime::Seconds() < StartupDeadline) return false;
			if (!Test->TestTrue(TEXT("Prototype player, door and frame are loaded"), Pawn.IsValid() && Door.IsValid() && Frame.IsValid())) return true;
			Feedback = Pawn->FindComponentByClass<UInteractionFeedbackComponent>();
			State = FindFProperty<FBoolProperty>(Door->GetClass(), TEXT("bIsOpen"));
			if (!Test->TestTrue(TEXT("Door exposes state and player has existing feedback"), State && Feedback.IsValid())) return true;
			PawnTransform = Pawn->GetActorTransform();
			ClosedTransform = Door->GetActorTransform();
			FrameTransform = Frame->GetActorTransform();
			FHitResult Ground;
			FCollisionQueryParams GroundQuery(SCENE_QUERY_STAT(DoorGroundTest), false, Pawn.Get());
			const FVector GroundProbe = ClosedTransform.TransformPositionNoScale(FVector(60, -100, 0));
			const bool HasGround = Pawn->GetWorld()->LineTraceSingleByChannel(Ground, GroundProbe + FVector(0, 0, 20),
				GroundProbe - FVector(0, 0, 50), ECC_Visibility, GroundQuery);
			Test->TestTrue(TEXT("Placed door meets the actual approach floor"), HasGround && FMath::IsNearlyEqual(Ground.ImpactPoint.Z, ClosedTransform.GetLocation().Z, 1.0));
			MoveMode = Pawn->GetCharacterMovement()->MovementMode;
			Pawn->GetCharacterMovement()->StopMovementImmediately();
			Pawn->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
			MovePlayer(ClosedTransform, FVector(60, -100, 96));
		}
		else if (!Pawn.IsValid() || !Door.IsValid() || !Frame.IsValid() || !PC.IsValid() || !Feedback.IsValid())
		{
			Test->AddError(TEXT("PIE door fixture was removed during the test"));
			return true;
		}
		else if (Step == 1)
		{
			ExpectDoor(false);
			ExpectFocus(Door.Get());
			ExpectPassage(false);
			Key(IE_Pressed);
		}
		else if (Step == 2)
		{
			ExpectDoor(true);
			ExpectFocus(Door.Get());
			ExpectPassage(true);
		}
		else if (Step == 3)
		{
			Test->TestTrue(TEXT("Holding E leaves door open"), IsOpen(Door.Get()));
			Key(IE_Released);
		}
		else if (Step == 4) Key(IE_Pressed);
		else if (Step == 5)
		{
			ExpectDoor(false);
			ExpectPassage(false);
			Key(IE_Released);
			MovePlayer(ClosedTransform, FVector(60, -420, 96));
		}
		else if (Step == 6)
		{
			ExpectNoFocus(TEXT("Outside door range"));
			Key(IE_Pressed);
		}
		else if (Step == 7)
		{
			Test->TestFalse(TEXT("E outside range cannot open door"), IsOpen(Door.Get()));
			Key(IE_Released);
			MovePlayer(ClosedTransform, FVector(60, -100, 96));
			FActorSpawnParameters Params;
			Params.ObjectFlags |= RF_Transient;
			Wall = Pawn->GetWorld()->SpawnActor<AStaticMeshActor>(
				ClosedTransform.TransformPositionNoScale(FVector(60, -48, 125)), ClosedTransform.Rotator(), Params);
			Wall->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Wall->SetActorScale3D(FVector(0.8, 0.1, 2.3));
			Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
		}
		else if (Step == 8)
		{
			ExpectNoFocus(TEXT("Door hidden behind blocker"));
			Key(IE_Pressed);
		}
		else if (Step == 9)
		{
			Test->TestFalse(TEXT("E through blocker cannot open door"), IsOpen(Door.Get()));
			Key(IE_Released);
			Wall->Destroy();
		}
		else if (Step == 10)
		{
			ExpectFocus(Door.Get());
			Key(IE_Pressed);
		}
		else if (Step == 11)
		{
			ExpectDoor(true);
			ExpectPassage(true);
			Key(IE_Released);
			MovePlayer(ClosedTransform, FVector(60, 80, 96));
		}
		else if (Step == 12)
		{
			ExpectFocus(Door.Get());
			Key(IE_Pressed);
		}
		else if (Step == 13)
		{
			ExpectDoor(false);
			Key(IE_Released);
			FActorSpawnParameters Params;
			Params.ObjectFlags |= RF_Transient;
			CloneTransform = FTransform(FRotator(0, 37, 0), ClosedTransform.GetLocation() + FVector(0, 0, 1500), ClosedTransform.GetScale3D());
			Clone = Pawn->GetWorld()->SpawnActor<AInteractableActor>(Door->GetClass(), CloneTransform, Params);
			if (!Test->TestNotNull(TEXT("Rotated Blueprint door instance spawns"), Clone.Get())) return true;
			MovePlayer(CloneTransform, FVector(60, -100, 96));
		}
		else if (Step == 14)
		{
			ExpectFocus(Clone.Get());
			Key(IE_Pressed);
		}
		else if (Step == 15)
		{
			Test->TestTrue(TEXT("Rotated door instance opens via E"), IsOpen(Clone.Get()));
			const FQuat Expected = CloneTransform.GetRotation() * FQuat(FRotator(0, -90, 0));
			Test->TestTrue(TEXT("Opening respects the placed rotation"), Clone->GetActorQuat().Equals(Expected, 0.001));
			Key(IE_Released);
		}
		else if (Step == 16) Key(IE_Pressed);
		else if (Step == 17)
		{
			Test->TestFalse(TEXT("Rotated instance closes via E"), IsOpen(Clone.Get()));
			Test->TestTrue(TEXT("Closing restores the placed rotation exactly"), Clone->GetActorQuat().Equals(CloneTransform.GetRotation(), 0.001));
			Key(IE_Released);
			Clone->Destroy();
			Pawn->SetActorTransform(PawnTransform, false, nullptr, ETeleportType::TeleportPhysics);
			Pawn->GetCharacterMovement()->SetMovementMode(MoveMode);
			return true;
		}
		++Step;
		NextStep = FPlatformTime::Seconds() + 0.25;
		return false;
	}

private:
	bool IsOpen(AInteractableActor* Actor) const { return State->GetPropertyValue_InContainer(Actor); }
	void Key(EInputEvent Event)
	{
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E, Event, Event == IE_Released ? 0.0f : 1.0f));
	}
	void MovePlayer(const FTransform& Reference, const FVector& Offset)
	{
		Pawn->SetActorLocation(Reference.TransformPositionNoScale(Offset), false, nullptr, ETeleportType::TeleportPhysics);
	}
	void ExpectDoor(bool Open)
	{
		Test->TestEqual(Open ? TEXT("Door is open") : TEXT("Door is closed"), IsOpen(Door.Get()), Open);
		const FQuat Expected = ClosedTransform.GetRotation() * FQuat(FRotator(0, Open ? -90 : 0, 0));
		Test->TestTrue(TEXT("Door leaf has expected hinge rotation"), Door->GetActorQuat().Equals(Expected, 0.001));
		Test->TestTrue(TEXT("Door hinge stays fixed"), Door->GetActorLocation().Equals(ClosedTransform.GetLocation(), 0.001));
		Test->TestTrue(TEXT("Frame stays fixed"), Frame->GetActorTransform().Equals(FrameTransform, 0.001));
	}
	void ExpectFocus(AInteractableActor* Expected)
	{
		Test->TestEqual(TEXT("Existing feedback selects the door"), Feedback->GetFocusedTarget(), static_cast<AActor*>(Expected));
		Test->TestTrue(TEXT("Existing E prompt is visible"), Feedback->IsPromptVisible());
		Test->TestEqual(TEXT("Existing gold highlight is applied"), Expected->Mesh->GetOverlayMaterial(), Feedback->HighlightMaterial.Get());
		TInlineComponentArray<UStaticMeshComponent*> FrameMeshes(Frame.Get());
		for (UStaticMeshComponent* Mesh : FrameMeshes) Test->TestNull(TEXT("Frame is not highlighted"), Mesh->GetOverlayMaterial());
	}
	void ExpectNoFocus(const TCHAR* Context)
	{
		Test->TestNull(FString(Context) + TEXT(": no selected target"), Feedback->GetFocusedTarget());
		Test->TestFalse(FString(Context) + TEXT(": no E prompt"), Feedback->IsPromptVisible());
		Test->TestNull(FString(Context) + TEXT(": no door highlight"), Door->Mesh->GetOverlayMaterial());
	}
	void ExpectPassage(bool Open)
	{
		FHitResult Hit;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(DoorPassageTest), false, Pawn.Get());
		const FVector Start = ClosedTransform.TransformPositionNoScale(FVector(60, -65, 110));
		const FVector End = ClosedTransform.TransformPositionNoScale(FVector(60, 65, 110));
		const bool Blocked = Pawn->GetWorld()->SweepSingleByChannel(Hit, Start, End, ClosedTransform.GetRotation(),
			ECC_Pawn, FCollisionShape::MakeCapsule(42, 90), Query);
		if (Open)
		{
			if (Blocked) Test->AddError(FString::Printf(TEXT("Open passage hit %s / %s at %s, normal %s, penetrating=%d"),
				*GetNameSafe(Hit.GetActor()), *GetNameSafe(Hit.GetComponent()), *Hit.ImpactPoint.ToString(),
				*Hit.ImpactNormal.ToString(), Hit.bStartPenetrating));
			Test->TestFalse(TEXT("Open doorway permits a player-sized capsule"), Blocked);
		}
		else
		{
			Test->TestTrue(TEXT("Closed door blocks a player-sized capsule"), Blocked);
			Test->TestEqual(TEXT("Door leaf is the blocking actor"), Hit.GetActor(), static_cast<AActor*>(Door.Get()));
		}
	}

	FAutomationTestBase* Test;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Pawn;
	TWeakObjectPtr<AInteractableActor> Door, Clone;
	TWeakObjectPtr<AActor> Frame;
	TWeakObjectPtr<AStaticMeshActor> Wall;
	TWeakObjectPtr<UInteractionFeedbackComponent> Feedback;
	FBoolProperty* State = nullptr;
	FTransform PawnTransform, ClosedTransform, FrameTransform, CloneTransform;
	EMovementMode MoveMode = MOVE_Walking;
	int32 Step = 0;
	double NextStep = 0;
	double StartupDeadline;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInteractionDoorPIETest, "FantasyLifeRPG.Interaction.DoorPIE",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FInteractionDoorPIETest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_Prototype_01")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FInteractionDoorPIECommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
