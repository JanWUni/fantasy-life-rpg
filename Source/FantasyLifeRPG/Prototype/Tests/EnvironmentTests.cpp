#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Misc/AutomationTest.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
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
#include "Interaction/InteractableActor.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "NPC/PrototypeNPC.h"
#include "NPC/WaypointMovementComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Prototype/PrototypeMessageComponent.h"
#include "Prototype/UI/PrototypeMessageWidget.h"
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"
#include "UObject/UnrealType.h"

namespace
{
/** A queued end request is not a completed teardown. Do not load/start another world yet. */
class FEnvironmentEndPIECommand : public IAutomationLatentCommand
{
public:
	explicit FEnvironmentEndPIECommand(FAutomationTestBase* InTest) : Test(InTest) {}
	virtual bool Update() override
	{
		if (!GEditor) { Test->AddError(TEXT("Environment PIE teardown: editor unavailable")); return true; }
		if (!bRequested)
		{
			bRequested = true;
			Deadline = FPlatformTime::Seconds() + 20;
			if (GEditor->IsPlaySessionRequestQueued() && !GEditor->PlayWorld) GEditor->CancelRequestPlaySession();
			if (GEditor->PlayWorld) GEditor->RequestEndPlayMap();
		}
		bool bHasPIEContext = false;
		for (const FWorldContext& Context : GEngine->GetWorldContexts())
			bHasPIEContext |= Context.WorldType == EWorldType::PIE;
		if (!GEditor->IsPlaySessionInProgress() && !GEditor->PlayWorld && !bHasPIEContext) return true;
		if (FPlatformTime::Seconds() < Deadline) return false;
		Test->AddError(TEXT("Environment PIE teardown did not finish within 20 seconds"));
		return true;
	}
private:
	FAutomationTestBase* Test;
	bool bRequested = false;
	double Deadline = 0;
};

class FEnvironmentReadyPIECommand : public FStartPIEForAutomationCommand
{
public:
	explicit FEnvironmentReadyPIECommand(const FRequestPlaySessionParams& Params) : FStartPIEForAutomationCommand(Params) {}
	virtual bool Update() override
	{
		// This command is delegated to, so the framework does not initialize its timer.
		if (StartTime == 0) StartTime = FPlatformTime::Seconds();
		return FStartPIEForAutomationCommand::Update();
	}
};

/** Construct the engine's readiness watcher only after the previous session has ended. */
class FEnvironmentStartPIECommand : public IAutomationLatentCommand
{
public:
	virtual bool Update() override
	{
		if (!Start)
		{
			FRequestPlaySessionParams Params;
			ULevelEditorPlaySettings* Settings = DuplicateObject<ULevelEditorPlaySettings>(GetDefault<ULevelEditorPlaySettings>(), GetTransientPackage());
			Settings->SetPlayNetMode(PIE_Standalone);
			Settings->SetPlayNumberOfClients(1);
			// FStartPIEForAutomationCommand releases this root on destruction.
			Settings->AddToRoot();
			Params.EditorPlaySettings = Settings;
			Start = MakeUnique<FEnvironmentReadyPIECommand>(Params);
		}
		return Start->Update();
	}
private:
	TUniquePtr<FStartPIEForAutomationCommand> Start;
};
}

class FEnvironmentPIECommand : public IAutomationLatentCommand
{
public:
	explicit FEnvironmentPIECommand(FAutomationTestBase* InTest) : Test(InTest) {}
	virtual bool Update() override
	{
		if (FPlatformTime::Seconds() < NextStep) return false;
		if (Step == 0)
		{
			if (Deadline == 0) Deadline = FPlatformTime::Seconds() + 20;
			// Bind only to the active, initialized session, never an arbitrary matching context.
			UWorld* Candidate = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			if (Candidate && Candidate->WorldType == EWorldType::PIE && !Candidate->bIsTearingDown
				&& Candidate->AreActorsInitialized() && Candidate->HasBegunPlay()
				&& Candidate->GetMapName().Contains(TEXT("Lvl_EnvironmentTest_01")))
			{
				World = Candidate;
				PC = World->GetFirstPlayerController();
				Player = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
				for (TActorIterator<AActor> It(World.Get()); It; ++It)
				{
					if (It->ActorHasTag(TEXT("EnvironmentNPC"))) NPC = Cast<APrototypeNPC>(*It);
					if (It->ActorHasTag(TEXT("EnvironmentDoor"))) Door = Cast<AInteractableActor>(*It);
					if (It->ActorHasTag(TEXT("EnvironmentHouse"))) House = *It;
					if (It->ActorHasTag(TEXT("EnvironmentTerrain"))) Terrain = *It;
					if (It->ActorHasTag(TEXT("EnvironmentPath"))) Path = *It;
				}
			}
			if ((!Player.IsValid() || !NPC.IsValid() || !Door.IsValid() || !Terrain.IsValid() || !House.IsValid())
				&& FPlatformTime::Seconds() < Deadline) return false;
			if (!Test->TestTrue(TEXT("Saved environment, player, terrain, house, door and NPC load"),
				Player.IsValid() && NPC.IsValid() && Door.IsValid() && Terrain.IsValid() && House.IsValid())) return true;
			Feedback = Player->FindComponentByClass<UInteractionFeedbackComponent>();
			Messages = Player->FindComponentByClass<UPrototypeMessageComponent>();
			State = FindFProperty<FBoolProperty>(Door->GetClass(), TEXT("bIsOpen"));
			if (!Test->TestTrue(TEXT("Environment inherits interaction feedback and has local messages"), Feedback.IsValid() && Messages.IsValid() && State)) return true;
			// Keep this original interaction/collision fixture deterministic. Navigation
			// is exercised independently in NavigationPIE with the saved route enabled.
			if (UWaypointMovementComponent* Route = NPC->FindComponentByClass<UWaypointMovementComponent>()) Route->StopRoute();
			NPCPosition = NPC->GetActorLocation();
			Test->AddInfo(FString::Printf(TEXT("Environment fixture acquired: world=%s player=%s at %s NPC=%s at %s tearingDown=%d begunPlay=%d"),
				*World->GetPathName(), *Player->GetPathName(), *Player->GetActorLocation().ToString(),
				*NPC->GetPathName(), *NPCPosition.ToString(), World->bIsTearingDown, World->HasBegunPlay()));
			DoorClosed = Door->GetActorTransform();
			FVector Origin, Extent;
			Terrain->GetActorBounds(false, Origin, Extent);
			Test->TestTrue(TEXT("Terrain covers 80 by 80 metres"), FMath::IsNearlyEqual(Extent.X, 4000.0, 1.0) && FMath::IsNearlyEqual(Extent.Y, 4000.0, 1.0));
			int32 Trees = 0, Rocks = 0;
			for (TActorIterator<AActor> It(World.Get()); It; ++It)
			{
				Trees += It->ActorHasTag(TEXT("EnvironmentTree")) ? 1 : 0;
				Rocks += It->ActorHasTag(TEXT("EnvironmentRock")) ? 1 : 0;
			}
			Test->TestTrue(TEXT("Forest and rock placeholders are present"), Trees >= 50 && Rocks >= 20);
			for (int32 Y = -3250; Y <= 1150; Y += 100)
			{
				FHitResult Ground;
				FCollisionQueryParams Query(SCENE_QUERY_STAT(EnvironmentPathGround), false, Player.Get());
				const FVector Probe(PathX(Y), Y, 800);
				const bool Hit = World->LineTraceSingleByChannel(Ground, Probe, Probe - FVector(0, 0, 1600), ECC_Visibility, Query);
				Test->TestTrue(FString::Printf(TEXT("Path ground is continuous and walkable at Y=%d (hit %s, normal %s)"),
					Y, *GetNameSafe(Ground.GetActor()), *Ground.ImpactNormal.ToString()),
					Hit && (Ground.GetActor() == Terrain.Get() || Ground.GetActor() == Path.Get()) && Ground.ImpactNormal.Z > .71f);
			}
			Deadline = FPlatformTime::Seconds() + 30;
			PathY = -3050;
			++Step;
			return false;
		}
		if (!World.IsValid() || World->bIsTearingDown || !GEditor || GEditor->PlayWorld != World.Get()
			|| !PC.IsValid() || !Player.IsValid() || !NPC.IsValid() || !Door.IsValid() || !Feedback.IsValid() || !Messages.IsValid())
		{
			Test->AddError(FString::Printf(TEXT("Environment PIE fixture disappeared at step %d: world=%d controller=%d player=%d NPC=%d door=%d; last player=%s NPC=%s"),
				Step, World.IsValid(), PC.IsValid(), Player.IsValid(), NPC.IsValid(), Door.IsValid(),
				*LastPlayerPosition.ToString(), *LastNPCPosition.ToString()));
			return true;
		}
		LastPlayerPosition = Player->GetActorLocation();
		LastNPCPosition = NPC->GetActorLocation();
		if (Step == 1)
		{
			// Exercise actual CharacterMovement along the whole path; do not teleport this phase.
			FVector Target(PathX(PathY), PathY, Player->GetActorLocation().Z);
			if (FVector::Dist2D(Player->GetActorLocation(), Target) < 80)
			{
				PathY += 150;
				if (PathY > 1150)
				{
					Test->TestTrue(TEXT("Character walked from spawn to the house clearing"), Player->GetActorLocation().Y > 1000);
					Player->GetCharacterMovement()->StopMovementImmediately();
					MovePlayer(FVector(900, 1180, 178));
					++Step;
					NextStep = FPlatformTime::Seconds() + .4;
					return false;
				}
				Target = FVector(PathX(PathY), PathY, Player->GetActorLocation().Z);
			}
			if (FPlatformTime::Seconds() > Deadline)
			{
				Test->AddError(FString::Printf(TEXT("Walking path timed out at %s toward %s"), *Player->GetActorLocation().ToString(), *Target.ToString()));
				return true;
			}
			Player->AddMovementInput((Target - Player->GetActorLocation()).GetSafeNormal2D());
			return false;
		}
		if (Step == 2)
		{
			ExpectFocus(Door.Get());
			Test->TestEqual(TEXT("Closed house door offers opening"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 T\u00fcr \u00f6ffnen")));
			Test->TestFalse(TEXT("Reused house door starts closed"), IsDoorOpen());
			Passage(false);
			Key(IE_Pressed);
		}
		else if (Step == 3)
		{
			Test->TestTrue(TEXT("Reused house door opens via Enhanced Input E"), IsDoorOpen());
			Test->TestEqual(TEXT("Same focused door updates to closing"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 T\u00fcr schlie\u00dfen")));
			Passage(true);
			Key(IE_Released);
		}
		else if (Step == 4) Key(IE_Pressed);
		else if (Step == 5)
		{
			Test->TestFalse(TEXT("House door closes again via E"), IsDoorOpen());
			Key(IE_Released);
			MovePlayer(NPCPosition + FVector(0, -170, 0));
			Messages->DisplaySeconds = .6f;
		}
		else if (Step == 6)
		{
			ExpectFocus(NPC.Get());
			Test->TestEqual(TEXT("NPC offers speaking in the existing widget"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 Sprechen")));
			UAnimSingleNodeInstance* Idle = NPC->GetMesh()->GetSingleNodeInstance();
			Test->TestTrue(TEXT("Existing idle animation is playing on the humanoid"), Idle && Idle->IsPlaying() && Idle->GetCurrentTime() > .01f);
			Key(IE_Pressed);
		}
		else if (Step == 7)
		{
			Test->TestTrue(TEXT("E on NPC shows a local response"), Messages->IsMessageVisible());
			Test->TestEqual(TEXT("Response matches configured greeting"), Messages->GetCurrentMessage().ToString(), NPC->Greeting.ToString());
			Test->TestTrue(TEXT("NPC turns horizontally toward the player"), FVector::DotProduct(NPC->GetActorForwardVector(),
				(Player->GetActorLocation() - NPCPosition).GetSafeNormal2D()) > .999f);
			int32 VisibleMessages = 0;
			for (TObjectIterator<UPrototypeMessageWidget> It; It; ++It)
				if (It->GetOwningPlayer() == PC.Get() && It->IsInViewport() && It->IsVisible()) ++VisibleMessages;
			Test->TestEqual(TEXT("Exactly one response is displayed"), VisibleMessages, 1);
			Player->SetActorLocation(NPCPosition + FVector(100, -140, 0));
			FacingAfterGreeting = NPC->GetActorQuat();
		}
		else if (Step == 8)
		{
			Test->TestTrue(TEXT("Holding E does not repeatedly turn the NPC"), NPC->GetActorQuat().Equals(FacingAfterGreeting, .001));
			Key(IE_Released);
		}
		else if (Step == 9)
		{
			Test->TestFalse(TEXT("Local response automatically expires"), Messages->IsMessageVisible());
			MovePlayer(NPCPosition + FVector(0, -500, 0));
		}
		else if (Step == 10)
		{
			ExpectNoFocus(TEXT("NPC outside range"));
			Key(IE_Pressed);
		}
		else if (Step == 11)
		{
			Test->TestFalse(TEXT("E outside NPC range produces no response"), Messages->IsMessageVisible());
			Key(IE_Released);
			MovePlayer(NPCPosition + FVector(0, -170, 0));
			FActorSpawnParameters Params;
			Params.ObjectFlags |= RF_Transient;
			Wall = World->SpawnActor<AStaticMeshActor>(NPCPosition + FVector(0, -85, 20), FRotator::ZeroRotator, Params);
			Wall->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Wall->SetActorScale3D(FVector(1.4, .1, 2.5));
			Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
		}
		else if (Step == 12)
		{
			ExpectNoFocus(TEXT("NPC occluded"));
			Key(IE_Pressed);
		}
		else if (Step == 13)
		{
			Test->TestFalse(TEXT("E through a wall produces no response"), Messages->IsMessageVisible());
			Key(IE_Released);
			Wall->Destroy();
		}
		else if (Step == 14)
		{
			ExpectFocus(NPC.Get());
			NPC->bInteractionEnabled = false;
		}
		else if (Step == 15)
		{
			ExpectNoFocus(TEXT("NPC disabled"));
			NPC->bInteractionEnabled = true;
		}
		else if (Step == 16)
		{
			Key(IE_Pressed);
		}
		else if (Step == 17)
		{
			Test->TestTrue(TEXT("NPC can be spoken to again"), Messages->IsMessageVisible());
			Test->TestTrue(TEXT("NPC remains at its fixed location"), NPC->GetActorLocation().Equals(NPCPosition, .1));
			Key(IE_Released);
			MovePlayer(FVector(900, 1600, 180));
			PC->SetControlRotation(FRotator(0, 90, 0));
		}
		else if (Step == 18)
		{
			USpringArmComponent* Arm = Player->FindComponentByClass<USpringArmComponent>();
			UCameraComponent* Camera = Player->FindComponentByClass<UCameraComponent>();
			Test->TestTrue(TEXT("Camera retracts inside the house instead of crossing the closed door"),
				Arm && Camera && Arm->bDoCollisionTest && FVector::Dist(Camera->GetComponentLocation(), Arm->GetComponentLocation()) < Arm->TargetArmLength - 40);
			return true;
		}
		++Step;
		NextStep = FPlatformTime::Seconds() + .25;
		return false;
	}
private:
	static double PathX(double Y)
	{
		const double T = FMath::Clamp((Y + 3300) / 4500, 0.0, 1.0);
		return -1700 + 2600 * T + 300 * FMath::Sin(T * UE_DOUBLE_PI * 2);
	}
	void MovePlayer(const FVector& Location)
	{
		Player->GetCharacterMovement()->StopMovementImmediately();
		Player->SetActorLocation(Location, false, nullptr, ETeleportType::TeleportPhysics);
	}
	void Key(EInputEvent Event) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E, Event, Event == IE_Released ? 0.f : 1.f)); }
	bool IsDoorOpen() const { return State->GetPropertyValue_InContainer(Door.Get()); }
	void ExpectFocus(AActor* Actor)
	{
		Test->TestEqual(TEXT("Shared feedback selects the expected actor"), Feedback->GetFocusedTarget(), Actor);
		Test->TestTrue(TEXT("Shared E prompt is visible"), Feedback->IsPromptVisible());
		TInlineComponentArray<UMeshComponent*> Meshes(Actor);
		for (UMeshComponent* Mesh : Meshes) if (Mesh->IsVisible())
			Test->TestEqual(TEXT("Selected mesh has shared gold highlight"), Mesh->GetOverlayMaterial(), Feedback->HighlightMaterial.Get());
	}
	void ExpectNoFocus(const TCHAR* Context)
	{
		Test->TestNull(FString(Context) + TEXT(": no focus"), Feedback->GetFocusedTarget());
		Test->TestFalse(FString(Context) + TEXT(": no prompt"), Feedback->IsPromptVisible());
		Test->TestNull(FString(Context) + TEXT(": no NPC overlay"), NPC->GetMesh()->GetOverlayMaterial());
	}
	void Passage(bool Open)
	{
		FHitResult Hit;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(EnvironmentDoorPassage), false, Player.Get());
		const bool Blocked = World->SweepSingleByChannel(Hit, FVector(900, 1285, 190), FVector(900, 1415, 190),
			FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(42, 96), Query);
		Test->TestEqual(Open ? TEXT("Open house doorway is passable") : TEXT("Closed house doorway blocks the player"), Blocked, !Open);
		if (!Open) Test->TestEqual(TEXT("Reused door is the blocking collider"), Hit.GetActor(), static_cast<AActor*>(Door.Get()));
	}
	FAutomationTestBase* Test;
	TWeakObjectPtr<UWorld> World;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Player;
	TWeakObjectPtr<APrototypeNPC> NPC;
	TWeakObjectPtr<AInteractableActor> Door;
	TWeakObjectPtr<AActor> House, Terrain, Path;
	TWeakObjectPtr<AStaticMeshActor> Wall;
	TWeakObjectPtr<UInteractionFeedbackComponent> Feedback;
	TWeakObjectPtr<UPrototypeMessageComponent> Messages;
	FBoolProperty* State = nullptr;
	FVector NPCPosition;
	FVector LastPlayerPosition = FVector::ZeroVector, LastNPCPosition = FVector::ZeroVector;
	FTransform DoorClosed;
	FQuat FacingAfterGreeting;
	int32 Step = 0;
	double Deadline = 0, NextStep = 0, PathY = 0;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEnvironmentPIETest, "FantasyLifeRPG.Environment.PlayablePIE",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEnvironmentPIETest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FEnvironmentEndPIECommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_EnvironmentTest_01")));
	ADD_LATENT_AUTOMATION_COMMAND(FEnvironmentStartPIECommand());
	ADD_LATENT_AUTOMATION_COMMAND(FEnvironmentPIECommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEnvironmentEndPIECommand(this));
	return true;
}
#endif
