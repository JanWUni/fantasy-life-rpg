#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR

#include "Misc/AutomationTest.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputKeyEventArgs.h"
#include "Interaction/InteractableActor.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "PhysicsEngine/BodySetup.h"
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"
#include "UObject/UnrealType.h"

namespace AssetWorkspaceTests
{
const TCHAR* WallPath = TEXT("/Game/Art/Architecture/SM_Wall_Test_400x20x300.SM_Wall_Test_400x20x300");

class FEndPIE : public IAutomationLatentCommand
{
public:
	explicit FEndPIE(FAutomationTestBase* InTest) : Test(InTest) {}
	virtual bool Update() override
	{
		if (!GEditor) { Test->AddError(TEXT("Workspace editor unavailable")); return true; }
		if (!bRequested)
		{
			bRequested = true;
			Deadline = FPlatformTime::Seconds() + 20;
			if (GEditor->IsPlaySessionRequestQueued() && !GEditor->PlayWorld) GEditor->CancelRequestPlaySession();
			if (GEditor->PlayWorld) GEditor->RequestEndPlayMap();
		}
		bool bHasWorld = false;
		for (const FWorldContext& Context : GEngine->GetWorldContexts()) bHasWorld |= Context.WorldType == EWorldType::PIE;
		if (!GEditor->IsPlaySessionInProgress() && !GEditor->PlayWorld && !bHasWorld) return true;
		if (FPlatformTime::Seconds() < Deadline) return false;
		Test->AddError(TEXT("Workspace PIE teardown timed out"));
		return true;
	}
private:
	FAutomationTestBase* Test;
	bool bRequested = false;
	double Deadline = 0;
};

class FReadyPIE : public FStartPIEForAutomationCommand
{
public:
	explicit FReadyPIE(const FRequestPlaySessionParams& Params) : FStartPIEForAutomationCommand(Params) {}
	virtual bool Update() override
	{
		if (StartTime == 0) StartTime = FPlatformTime::Seconds();
		return FStartPIEForAutomationCommand::Update();
	}
};

class FStartPIE : public IAutomationLatentCommand
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
			Settings->AddToRoot(); // Released by the engine command's destructor.
			Params.EditorPlaySettings = Settings;
			Start = MakeUnique<FReadyPIE>(Params);
		}
		return Start->Update();
	}
private:
	TUniquePtr<FReadyPIE> Start;
};

class FCheckWorkspace : public IAutomationLatentCommand
{
public:
	FCheckWorkspace(FAutomationTestBase* InTest, bool bInLab) : Test(InTest), bLab(bInLab) {}
	virtual bool Update() override
	{
		const double Now = FPlatformTime::Seconds();
		if (Deadline == 0) Deadline = Now + 20;
		if (Now < NextStep) return false;
		if (Step == 0)
		{
			UWorld* Candidate = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			if (Candidate && Candidate->HasBegunPlay() && !Candidate->bIsTearingDown
				&& Candidate->GetMapName().Contains(bLab ? TEXT("Lvl_AssetLab") : TEXT("Lvl_WorldSandbox")))
			{
				World = Candidate;
				PC = World->GetFirstPlayerController();
				Player = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
			}
			if ((!Player.IsValid() || !Player->GetCharacterMovement()->IsMovingOnGround()) && Now < Deadline) return false;
			if (!Test->TestTrue(TEXT("Saved workspace spawns a grounded third-person player"), Player.IsValid() && Player->GetCharacterMovement()->IsMovingOnGround())) return true;
			if (!CheckAssetsAndCollision()) return true;
			StartPosition = Player->GetActorLocation();
			Key(EKeys::W, IE_Pressed);
			++Step; NextStep = Now + .7; return false;
		}
		if (!World.IsValid() || World->bIsTearingDown || !PC.IsValid() || !Player.IsValid())
		{
			Test->AddError(TEXT("Workspace PIE fixture disappeared")); return true;
		}
		if (Now > Deadline) { Test->AddError(TEXT("Workspace interaction test timed out")); return true; }
		if (Step == 1)
		{
			Key(EKeys::W, IE_Released);
			Test->TestTrue(TEXT("Enhanced Input W moves the character across the saved floor"), Player->GetActorLocation().Y > StartPosition.Y + 100);
			Player->GetCharacterMovement()->StopMovementImmediately();
			JumpStartZ = Player->GetActorLocation().Z;
			BeforeLook = PC->GetControlRotation();
			Key(EKeys::MouseX, IE_Axis, 15);
			Key(EKeys::SpaceBar, IE_Pressed);
			++Step; NextStep = Now + .15; return false;
		}
		if (Step == 2)
		{
			Test->TestTrue(TEXT("Enhanced Input Space makes the character jump"), Player->GetActorLocation().Z > JumpStartZ + 10);
			Test->TestTrue(TEXT("Enhanced Input mouse changes the third-person camera yaw"), FMath::Abs(FMath::FindDeltaAngleDegrees(BeforeLook.Yaw, PC->GetControlRotation().Yaw)) > .1);
			Key(EKeys::MouseX, IE_Axis, 0);
			Key(EKeys::SpaceBar, IE_Released);
			++Step; NextStep = Now + 1.6; return false;
		}
		if (Step == 3)
		{
			Test->TestTrue(TEXT("The player lands on the colliding workspace floor"), Player->GetCharacterMovement()->IsMovingOnGround());
			if (!bLab) return true;
			if (!Test->TestTrue(TEXT("Lab reuses the existing interactive door and player feedback"), Door.IsValid() && Feedback.IsValid() && DoorState)) return true;
			Player->GetCharacterMovement()->SetMovementMode(MOVE_Flying);
			Player->SetActorLocation(Door->GetActorTransform().TransformPositionNoScale(FVector(60,-100,96)), false, nullptr, ETeleportType::TeleportPhysics);
			++Step; NextStep = Now + .25; return false;
		}
		if (Step == 4)
		{
			Test->TestEqual(TEXT("Lab door is selected by the inherited feedback"), Feedback->GetFocusedTarget(), static_cast<AActor*>(Door.Get()));
			Test->TestTrue(TEXT("Lab door has its inherited prompt"), Feedback->IsPromptVisible());
			Test->TestFalse(TEXT("Lab door starts closed"), DoorState->GetPropertyValue_InContainer(Door.Get()));
			Key(EKeys::E, IE_Pressed);
		}
		else if (Step == 5)
		{
			Test->TestTrue(TEXT("Existing lab door opens through Enhanced Input E"), DoorState->GetPropertyValue_InContainer(Door.Get()));
			Test->TestEqual(TEXT("Lab door updates the existing action text"), Feedback->GetPromptText().ToString(), FString(TEXT("E \u2013 T\u00fcr schlie\u00dfen")));
			Key(EKeys::E, IE_Released);
		}
		else if (Step == 6) Key(EKeys::E, IE_Pressed);
		else
		{
			Test->TestFalse(TEXT("Existing lab door closes through Enhanced Input E"), DoorState->GetPropertyValue_InContainer(Door.Get()));
			Key(EKeys::E, IE_Released);
			return true;
		}
		++Step; NextStep = Now + .2; return false;
	}
private:
	void Key(FKey Input, EInputEvent Event, float Amount = 1)
	{
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(Input, Event, Event == IE_Released ? 0.f : Amount));
	}
	bool CheckAssetsAndCollision()
	{
		UStaticMesh* Expected = LoadObject<UStaticMesh>(nullptr, WallPath);
		if (!Test->TestNotNull(TEXT("Standalone library wall asset loads"), Expected)) return false;
		const FBox Bounds = Expected->GetBoundingBox();
		Test->TestTrue(TEXT("Wall has baked 400x20x300cm dimensions and a lower corner pivot"), Bounds.Min.Equals(FVector::ZeroVector,.1) && Bounds.Max.Equals(FVector(400,20,300),.1));
		Test->TestTrue(TEXT("Wall supplies simple collision geometry"), Expected->GetBodySetup() && Expected->GetBodySetup()->AggGeom.GetElementCount() > 0);
		AStaticMeshActor* Ground = nullptr;
		TArray<AStaticMeshActor*> Walls;
		int32 Categories = 0, Pedestals = 0;
		for (TActorIterator<AActor> It(World.Get()); It; ++It)
		{
			if (It->ActorHasTag(TEXT("WorkspaceGround"))) Ground = Cast<AStaticMeshActor>(*It);
			if (It->ActorHasTag(TEXT("WorkspaceWall")))
			{
				AStaticMeshActor* Wall = Cast<AStaticMeshActor>(*It);
				if (Wall) Walls.Add(Wall);
			}
			if (It->ActorHasTag(TEXT("LabPedestal"))) ++Pedestals;
			if (It->ActorHasTag(TEXT("LabCategoryArchitecture")) || It->ActorHasTag(TEXT("LabCategoryFurniture")) || It->ActorHasTag(TEXT("LabCategoryNature")))
			{
				++Categories;
				ATextRenderActor* Label = Cast<ATextRenderActor>(*It);
				Test->TestTrue(TEXT("Lab area has a saved visible text label"), Label && !Label->GetTextRender()->Text.IsEmpty() && Label->GetTextRender()->IsVisible());
			}
			if (It->ActorHasTag(TEXT("WorkspaceDoor"))) Door = Cast<AInteractableActor>(*It);
		}
		if (!Test->TestNotNull(TEXT("Workspace contains its saved ground"), Ground)) return false;
		Test->TestTrue(TEXT("Both maps reference the one library mesh; lab has multiple instances"), Walls.Num() >= (bLab ? 2 : 1));
		if (Walls.IsEmpty()) return false;
		for (AStaticMeshActor* Wall : Walls)
		{
			Test->TestTrue(TEXT("Wall instance reuses the canonical mesh object"), Wall->GetStaticMeshComponent()->GetStaticMesh() == Expected);
			Test->TestTrue(TEXT("Baked wall instances retain unit scale"), Wall->GetActorScale3D().Equals(FVector::OneVector,.001));
			FHitResult Hit;
			FCollisionQueryParams Query(SCENE_QUERY_STAT(WorkspaceWall), false, Player.Get());
			const FTransform Xform = Wall->GetActorTransform();
			const bool Blocked = World->SweepSingleByChannel(Hit, Xform.TransformPosition(FVector(200,-100,120)), Xform.TransformPosition(FVector(200,120,120)), FQuat::Identity, ECC_Pawn, FCollisionShape::MakeCapsule(42,96), Query);
			Test->TestTrue(TEXT("A player capsule is blocked by each wall's simple collision"), Blocked && Hit.GetActor() == Wall);
		}
		const FVector FloorSize = Ground->GetComponentsBoundingBox(true).GetSize();
		Test->TestTrue(TEXT("Saved workspace floor has the intended dimensions"), FMath::IsNearlyEqual(FloorSize.X,12000.0,1.0) && FMath::IsNearlyEqual(FloorSize.Y,bLab ? 8000.0 : 12000.0,1.0));
		FHitResult GroundHit;
		FCollisionQueryParams GroundQuery(SCENE_QUERY_STAT(WorkspaceFloor), false, Player.Get());
		Test->TestTrue(TEXT("Spawn approach has continuous ground collision"), World->LineTraceSingleByChannel(GroundHit,FVector(0,-1200,400),FVector(0,-1200,-100),ECC_Visibility,GroundQuery) && GroundHit.GetActor() == Ground && FMath::Abs(GroundHit.ImpactPoint.Z) < 1);
		Test->TestTrue(TEXT("Inherited third-person camera and collision arm are present"), Player->FindComponentByClass<UCameraComponent>() && Player->FindComponentByClass<USpringArmComponent>() && Player->FindComponentByClass<USpringArmComponent>()->bDoCollisionTest);
		if (bLab)
		{
			Test->TestEqual(TEXT("Lab contains three distinct tagged areas"), Categories, 3);
			Test->TestTrue(TEXT("Lab contains presentation pedestals"), Pedestals >= 3);
			float GridSize = 0;
			Test->TestTrue(TEXT("Existing grid material uses a 100cm major grid"), Ground->GetStaticMeshComponent()->GetMaterial(0)->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Grid Size")),GridSize) && FMath::IsNearlyEqual(GridSize,100.f));
			Feedback = Player->FindComponentByClass<UInteractionFeedbackComponent>();
			DoorState = Door.IsValid() ? FindFProperty<FBoolProperty>(Door->GetClass(),TEXT("bIsOpen")) : nullptr;
			Test->TestTrue(TEXT("Second lab instance demonstrates a material override"), Walls[0]->GetStaticMeshComponent()->GetMaterial(0) != Walls.Last()->GetStaticMeshComponent()->GetMaterial(0));
		}
		// Change only a transient component instance: shared geometry and other materials must remain intact.
		UStaticMeshComponent* Component = Walls[0]->GetStaticMeshComponent();
		UMaterialInterface* Before = Component->GetMaterial(0);
		UMaterialInterface* MeshDefault = Expected->GetMaterial(0);
		UMaterialInterface* OtherBefore = Walls.Last()->GetStaticMeshComponent()->GetMaterial(0);
		UMaterialInstanceDynamic* Dynamic = UMaterialInstanceDynamic::Create(Before,Component);
		Component->SetMaterial(0,Dynamic);
		Dynamic->SetVectorParameterValue(TEXT("Base Color"),FLinearColor(.8f,.05f,.05f));
		FLinearColor Color;
		Test->TestTrue(TEXT("Material color can change independently from the wall mesh"), Dynamic->GetVectorParameterValue(FMaterialParameterInfo(TEXT("Base Color")),Color) && Color.Equals(FLinearColor(.8f,.05f,.05f),.001f));
		Test->TestEqual(TEXT("Per-instance editing leaves the mesh material default unchanged"),Expected->GetMaterial(0),MeshDefault);
		if (Walls.Num() > 1) Test->TestEqual(TEXT("Per-instance editing leaves the other wall material unchanged"),Walls.Last()->GetStaticMeshComponent()->GetMaterial(0),OtherBefore);
		Component->SetMaterial(0,Before);
		return true;
	}
	FAutomationTestBase* Test;
	bool bLab;
	int32 Step = 0;
	double Deadline = 0, NextStep = 0, JumpStartZ = 0;
	FVector StartPosition;
	FRotator BeforeLook;
	TWeakObjectPtr<UWorld> World;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Player;
	TWeakObjectPtr<AInteractableActor> Door;
	TWeakObjectPtr<UInteractionFeedbackComponent> Feedback;
	FBoolProperty* DoorState = nullptr;
};

void Queue(FAutomationTestBase* Test, bool bLab)
{
	Test->AddCommand(new FEndPIE(Test));
	Test->AddCommand(new FEditorLoadMap(bLab ? TEXT("/Game/Prototype/Maps/Lvl_AssetLab") : TEXT("/Game/Prototype/Maps/Lvl_WorldSandbox")));
	Test->AddCommand(new FStartPIE());
	Test->AddCommand(new FCheckWorkspace(Test,bLab));
	Test->AddCommand(new FEndPIE(Test));
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAssetLabPIETest,"FantasyLifeRPG.AssetWorkspace.AssetLabPIE",EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FAssetLabPIETest::RunTest(const FString& Parameters) { AssetWorkspaceTests::Queue(this,true); return true; }

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWorldSandboxPIETest,"FantasyLifeRPG.AssetWorkspace.WorldSandboxPIE",EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FWorldSandboxPIETest::RunTest(const FString& Parameters) { AssetWorkspaceTests::Queue(this,false); return true; }

#endif
