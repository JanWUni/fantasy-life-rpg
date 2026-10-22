#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Misc/AutomationTest.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "Interaction/UI/InteractionPromptWidget.h"
#include "Blueprint/WidgetLayoutLibrary.h"
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
#include "Tests/AutomationEditorCommon.h"
#include "UObject/UObjectIterator.h"

/** Exercises the real local-player widget and mesh overlays in the saved prototype map. */
class FInteractionFeedbackPIECommand : public IAutomationLatentCommand
{
public:
	explicit FInteractionFeedbackPIECommand(FAutomationTestBase* InTest)
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
				for (TActorIterator<AInteractableActor> It(World); It; ++It)
				{
					if (It->ActorHasTag(TEXT("InteractionPrototype"))) { Target = *It; break; }
				}
				break;
			}
			if ((!Pawn.IsValid() || !Target.IsValid()) && FPlatformTime::Seconds() < StartupDeadline) return false;
			if (!Test->TestTrue(TEXT("Prototype player and test prop are ready"), Pawn.IsValid() && Target.IsValid())) return true;
			Feedback = Pawn->FindComponentByClass<UInteractionFeedbackComponent>();
			if (!Test->TestNotNull(TEXT("Prototype has the local feedback component"), Feedback.Get())) return true;
			if (!Test->TestNotNull(TEXT("Highlight overlay is configured"), Feedback->HighlightMaterial.Get())) return true;
			PawnTransform = Pawn->GetActorTransform();
			TargetTransform = Target->GetActorTransform();
			PreviousOverlay = Target->Mesh->GetOverlayMaterial();
			PreviousDrawDistance = Target->Mesh->GetOverlayMaterialMaxDrawDistance();
			PreviousForceDisableNanite = Target->Mesh->IsForceDisableNanite();
			TargetWasEnabled = Target->bInteractionEnabled;
			MoveMode = Pawn->GetCharacterMovement()->MovementMode;
			Pawn->GetCharacterMovement()->StopMovementImmediately();
			Pawn->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
			Target->bInteractionEnabled = true;
			PlaceTarget(400);
		}
		else if (!Pawn.IsValid() || !Target.IsValid() || !PC.IsValid() || !Feedback.IsValid())
		{
			Test->AddError(TEXT("PIE feedback fixture was removed during the test"));
			return true;
		}
		else if (Step == 1)
		{
			ExpectNoFocus(TEXT("Outside range"));
			PlaceTarget(140);
		}
		else if (Step == 2)
		{
			ExpectFocus(Target.Get(), TEXT("Visible target in range"));
			CheckPromptPlacement();
			FActorSpawnParameters Params;
			Params.ObjectFlags |= RF_Transient;
			Secondary = Pawn->GetWorld()->SpawnActor<AInteractableActor>(
				Pawn->GetActorLocation() + FVector(0, 180, -20), FRotator::ZeroRotator, Params);
			Secondary->Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			// Also exercise restoration of an already-enabled fallback override.
			Secondary->Mesh->SetForceDisableNanite(true);
		}
		else if (Step == 3)
		{
			ExpectFocus(Target.Get(), TEXT("Nearest of two targets"));
			Test->TestNull(TEXT("Other target has no highlight"), Secondary->Mesh->GetOverlayMaterial());
			PlaceTarget(400);
		}
		else if (Step == 4)
		{
			ExpectFocus(Secondary.Get(), TEXT("Selection switches to second target"));
			ExpectOriginalOverlay();
			Secondary->bInteractionEnabled = false;
		}
		else if (Step == 5)
		{
			ExpectNoFocus(TEXT("Disabled target"));
			Test->TestNull(TEXT("Disabled target overlay restored"), Secondary->Mesh->GetOverlayMaterial());
			Test->TestTrue(TEXT("Existing fallback override is preserved"), Secondary->Mesh->IsForceDisableNanite());
			PlaceTarget(140);
			FActorSpawnParameters Params;
			Params.ObjectFlags |= RF_Transient;
			Wall = Pawn->GetWorld()->SpawnActor<AStaticMeshActor>(
				Pawn->GetActorLocation() + FVector(70, 0, 30), FRotator::ZeroRotator, Params);
			Wall->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
			Wall->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
			Wall->SetActorScale3D(FVector(0.2, 2, 3));
			Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
		}
		else if (Step == 6)
		{
			ExpectNoFocus(TEXT("Target occluded by wall"));
			ExpectOriginalOverlay();
			Wall->Destroy();
		}
		else if (Step == 7)
		{
			ExpectFocus(Target.Get(), TEXT("Sight restored"));
			Target->bInteractionEnabled = false;
			Secondary->bInteractionEnabled = true;
		}
		else if (Step == 8)
		{
			ExpectFocus(Secondary.Get(), TEXT("Alternative target becomes valid"));
			Secondary->Destroy();
		}
		else if (Step == 9)
		{
			ExpectNoFocus(TEXT("Selected target destroyed"));
			Target->bInteractionEnabled = true;
		}
		else if (Step == 10)
		{
			ExpectFocus(Target.Get(), TEXT("Remaining target reacquired"));
			PC->UnPossess();
		}
		else if (Step == 11)
		{
			ExpectNoFocus(TEXT("Player unpossessed"));
			ExpectOriginalOverlay();
			PC->Possess(Pawn.Get());
		}
		else if (Step == 12)
		{
			ExpectFocus(Target.Get(), TEXT("Player possession restored"));
			Pawn->SetActorTransform(PawnTransform, false, nullptr, ETeleportType::TeleportPhysics);
			Pawn->GetCharacterMovement()->SetMovementMode(MoveMode);
			Target->SetActorTransform(TargetTransform, false, nullptr, ETeleportType::TeleportPhysics);
			Target->bInteractionEnabled = TargetWasEnabled;
			return true;
		}
		++Step;
		NextStep = FPlatformTime::Seconds() + 0.25;
		return false;
	}

private:
	void PlaceTarget(float Distance)
	{
		Target->SetActorLocation(Pawn->GetActorLocation() + FVector(Distance, 0, -20));
	}
	void ExpectFocus(AInteractableActor* Expected, const TCHAR* Context)
	{
		Test->TestEqual(FString(Context) + TEXT(": correct target"), Feedback->GetFocusedTarget(), static_cast<AActor*>(Expected));
		Test->TestTrue(FString(Context) + TEXT(": prompt visible in player viewport"), Feedback->IsPromptVisible());
		Test->TestEqual(FString(Context) + TEXT(": highlight overlay applied"), Expected->Mesh->GetOverlayMaterial(), Feedback->HighlightMaterial.Get());
		Test->TestTrue(FString(Context) + TEXT(": translucent overlay uses fallback rendering"), Expected->Mesh->IsForceDisableNanite());
	}
	void ExpectNoFocus(const TCHAR* Context)
	{
		Test->TestNull(FString(Context) + TEXT(": no focused target"), Feedback->GetFocusedTarget());
		Test->TestFalse(FString(Context) + TEXT(": prompt hidden"), Feedback->IsPromptVisible());
	}
	void ExpectOriginalOverlay()
	{
		Test->TestEqual(TEXT("Previous mesh overlay restored"), Target->Mesh->GetOverlayMaterial(), PreviousOverlay);
		Test->TestEqual(TEXT("Previous overlay draw distance restored"), Target->Mesh->GetOverlayMaterialMaxDrawDistance(), PreviousDrawDistance);
		Test->TestEqual(TEXT("Previous Nanite fallback override restored"), Target->Mesh->IsForceDisableNanite(), PreviousForceDisableNanite);
	}
	void CheckPromptPlacement()
	{
		Test->TestEqual(TEXT("An object without a custom action keeps the generic prompt"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 Interagieren")));
		int32 VisiblePrompts = 0;
		const FGeometry Screen = UWidgetLayoutLibrary::GetPlayerScreenWidgetGeometry(PC.Get());
		for (TObjectIterator<UInteractionPromptWidget> It; It; ++It)
		{
			if (It->GetOwningPlayer() != PC.Get() || !It->IsInViewport() || !It->IsVisible()) continue;
			++VisiblePrompts;
			const FGeometry Prompt = It->GetCachedGeometry();
			const FVector2D Center = Screen.AbsoluteToLocal(Prompt.LocalToAbsolute(Prompt.GetLocalSize() * 0.5f));
			const FVector2D ScreenSize = Screen.GetLocalSize();
			Test->TestTrue(TEXT("Prompt has a rendered size"), Prompt.GetLocalSize().X > 100 && Prompt.GetLocalSize().Y > 20);
			Test->TestTrue(TEXT("Prompt is horizontally centred"), ScreenSize.X > 0 && FMath::IsNearlyEqual(Center.X / ScreenSize.X, 0.5, 0.03));
			Test->TestTrue(TEXT("Prompt is in the lower screen area"), ScreenSize.Y > 0 && FMath::IsNearlyEqual(Center.Y / ScreenSize.Y, 0.86, 0.03));
		}
		Test->TestEqual(TEXT("Exactly one visible prompt belongs to this player"), VisiblePrompts, 1);
	}

	FAutomationTestBase* Test;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Pawn;
	TWeakObjectPtr<AInteractableActor> Target, Secondary;
	TWeakObjectPtr<AStaticMeshActor> Wall;
	TWeakObjectPtr<UInteractionFeedbackComponent> Feedback;
	UMaterialInterface* PreviousOverlay = nullptr;
	float PreviousDrawDistance = 0;
	FTransform PawnTransform, TargetTransform;
	EMovementMode MoveMode = MOVE_Walking;
	bool TargetWasEnabled = true;
	bool PreviousForceDisableNanite = false;
	int32 Step = 0;
	double NextStep = 0;
	double StartupDeadline;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInteractionFeedbackPIETest, "FantasyLifeRPG.Interaction.FeedbackPIE",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FInteractionFeedbackPIETest::RunTest(const FString& Parameters)
{
	ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_Prototype_01")));
	ADD_LATENT_AUTOMATION_COMMAND(FStartPIECommand(false));
	ADD_LATENT_AUTOMATION_COMMAND(FInteractionFeedbackPIECommand(this));
	ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
	return true;
}

#endif
