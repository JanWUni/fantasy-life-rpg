#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "Interaction/InteractionComponent.h"
#include "Interaction/InteractableActor.h"
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
#include "UObject/UnrealType.h"
#if WITH_EDITOR
#include "Tests/AutomationEditorCommon.h"
#endif

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInteractionRulesTest, "FantasyLifeRPG.Interaction.Rules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FInteractionRulesTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
	World->InitializeActorsForPlay(FURL());
	World->BeginPlay();
	ACharacter* Pawn = World->SpawnActor<ACharacter>(FVector(0, 0, 1000), FRotator::ZeroRotator);
	UInteractionComponent* Component = NewObject<UInteractionComponent>(Pawn);
	Component->RegisterComponent();
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!TestNotNull(TEXT("Placeholder cube loads"), Cube))
	{
		GEngine->DestroyWorldContext(World);
		World->DestroyWorld(false);
		return false;
	}
	auto SpawnProp = [&](const FVector& Location)
	{
		AInteractableActor* Prop = World->SpawnActor<AInteractableActor>(Location, FRotator::ZeroRotator);
		Prop->Mesh->SetStaticMesh(Cube);
		return Prop;
	};
	AInteractableActor* Near = SpawnProp(FVector(150, 0, 1000));
	AInteractableActor* Far = SpawnProp(FVector(0, 180, 1000));
	TestTrue(TEXT("In-range target is valid"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	TestEqual(TEXT("Nearest eligible target wins"), Component->FindBestTarget(), static_cast<AActor*>(Near));
	TestTrue(TEXT("Valid interaction succeeds"), Component->TryInteract());
	Near->bInteractionEnabled = false;
	TestEqual(TEXT("Disabled nearest target is skipped"), Component->FindBestTarget(), static_cast<AActor*>(Far));
	Near->bInteractionEnabled = true;
	Near->InteractionRange = 149.0f;
	TestFalse(TEXT("Object-specific range is enforced"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	Near->InteractionRange = 150.0f;
	TestTrue(TEXT("Exact range boundary is inclusive"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	Near->InteractionRange = 0.0f;
	TestFalse(TEXT("Zero range cannot interact"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	Near->InteractionRange = 200.0f;
	AStaticMeshActor* Wall = World->SpawnActor<AStaticMeshActor>(FVector(75, 0, 1030), FRotator::ZeroRotator);
	Wall->GetStaticMeshComponent()->SetStaticMesh(Cube);
	Wall->SetActorScale3D(FVector(0.2, 1.0, 2.0));
	Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
	TestFalse(TEXT("Visibility blocker rejects interaction"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	Wall->Destroy();
	TestTrue(TEXT("Interaction recovers after blocker removal"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	Near->Destroy();
	TestFalse(TEXT("Destroyed target is rejected"), UInteractionComponent::IsInteractionValid(Pawn, Near));
	TestEqual(TEXT("Destroyed target is skipped during discovery"), Component->FindBestTarget(), static_cast<AActor*>(Far));
	Far->SetActorLocation(FVector(0, 400, 1000));
	TestFalse(TEXT("No in-range target produces no action"), Component->TryInteract());
	TestFalse(TEXT("Null target is safe"), UInteractionComponent::IsInteractionValid(Pawn, nullptr));
	TestFalse(TEXT("Self interaction is rejected"), UInteractionComponent::IsInteractionValid(Far, Far));
	GEngine->DestroyWorldContext(World);
	World->DestroyWorld(false);
	return true;
}

#if WITH_EDITOR
/** Starts on Lvl_Prototype_01 and drives E through the real input pipeline. */
class FPrototypeInputCommand : public IAutomationLatentCommand
{
public:
	explicit FPrototypeInputCommand(FAutomationTestBase* InTest)
		: Test(InTest), StartupDeadline(FPlatformTime::Seconds() + 15.0) {}
	virtual bool Update() override
	{
		if (FPlatformTime::Seconds() < NextStep) return false;
		if (Step == 0)
		{
			for (const FWorldContext& Context : GEngine->GetWorldContexts())
			{
				if (Context.WorldType == EWorldType::PIE && Context.World()
					&& Context.World()->GetMapName().Contains(TEXT("Lvl_Prototype_01")))
				{
					PC = Context.World()->GetFirstPlayerController();
					for (TActorIterator<AInteractableActor> It(Context.World()); It; ++It)
					{
						if (It->ActorHasTag(TEXT("InteractionPrototype"))) { Target = *It; break; }
					}
					break;
				}
			}
			Pawn = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
			// RequestPlaySession is asynchronous; allow PIE and World Partition to finish starting.
			if ((!Pawn.IsValid() || !Target.IsValid()) && FPlatformTime::Seconds() < StartupDeadline) return false;
			if (!Test->TestTrue(TEXT("Prototype PIE has player and tagged test prop"), Pawn.IsValid() && Target.IsValid())) return true;
			State = FindFProperty<FBoolProperty>(Target->GetClass(), TEXT("bIsActive"));
			if (!Test->TestNotNull(TEXT("Blueprint owns visible toggle state"), State)) return true;
			PawnTransform = Pawn->GetActorTransform();
			TargetTransform = Target->GetActorTransform();
			MoveMode = Pawn->GetCharacterMovement()->MovementMode;
			InitialState = State->GetPropertyValue_InContainer(Target.Get());
			Pawn->GetCharacterMovement()->StopMovementImmediately();
			Pawn->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
			Target->SetActorLocation(Pawn->GetActorLocation() + FVector(140, 0, -20));
			Key(IE_Pressed);
		}
		else if (!Pawn.IsValid() || !Target.IsValid() || !PC.IsValid())
		{
			Test->AddError(TEXT("PIE ended during the input test"));
			return true;
		}
		else if (Step == 1)
		{
			Test->TestTrue(TEXT("E via Enhanced Input toggles Blueprint state"), State->GetPropertyValue_InContainer(Target.Get()) != InitialState);
			Test->TestFalse(TEXT("Blueprint visibly rotates the mesh"), Target->GetActorRotation().Equals(TargetTransform.Rotator()));
		}
		else if (Step == 2)
		{
			Test->TestTrue(TEXT("Holding E does not toggle repeatedly"), State->GetPropertyValue_InContainer(Target.Get()) != InitialState);
			Key(IE_Released);
		}
		else if (Step == 3) Key(IE_Pressed);
		else if (Step == 4)
		{
			Test->TestEqual(TEXT("Second press toggles state back"), State->GetPropertyValue_InContainer(Target.Get()), InitialState);
			Key(IE_Released);
			Target->SetActorLocation(Pawn->GetActorLocation() + FVector(400, 0, -20));
		}
		else if (Step == 5) Key(IE_Pressed);
		else if (Step == 6)
		{
			Test->TestEqual(TEXT("E outside range leaves state unchanged"), State->GetPropertyValue_InContainer(Target.Get()), InitialState);
			Key(IE_Released);
			Pawn->SetActorTransform(PawnTransform, false, nullptr, ETeleportType::TeleportPhysics);
			Pawn->GetCharacterMovement()->SetMovementMode(MoveMode);
			Target->SetActorTransform(TargetTransform, false, nullptr, ETeleportType::TeleportPhysics);
			return true;
		}
		++Step;
		NextStep = FPlatformTime::Seconds() + 0.3;
		return false;
	}
private:
	void Key(EInputEvent Event)
	{
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::E, Event, Event == IE_Released ? 0.0f : 1.0f));
	}
	FAutomationTestBase* Test;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Pawn;
	TWeakObjectPtr<AInteractableActor> Target;
	FBoolProperty* State = nullptr;
	FTransform PawnTransform, TargetTransform;
	EMovementMode MoveMode = MOVE_Walking;
	bool InitialState = false;
	int32 Step = 0;
	double NextStep = 0;
	double StartupDeadline;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPrototypeInputTest, "FantasyLifeRPG.Interaction.PrototypePIE",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FPrototypeInputTest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_Prototype_01")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FPrototypeInputCommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
#endif
