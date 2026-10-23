#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "FantasyLifeRPGCharacter.h"
#include "Movement/CrouchPoseMeshComponent.h"
#include "Development/DeveloperToolboxComponent.h"
#include "Inventory/UI/InventoryUIComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "InputKeyEventArgs.h"
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "Editor/EditorPerformanceSettings.h"

namespace MovementTests
{
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


class FExercise : public IAutomationLatentCommand
{
public:
	explicit FExercise(FAutomationTestBase* InTest, float InOriginY = 3000.f) : Test(InTest), OriginY(InOriginY)
	{
		auto* Settings=GetMutableDefault<UEditorPerformanceSettings>();
		bPreviousThrottle=Settings->bThrottleCPUWhenNotForeground;
		Settings->bThrottleCPUWhenNotForeground=false;
		TickHandle=FWorldDelegates::OnWorldPostActorTick.AddRaw(this,&FExercise::ObserveWorld);
	}
	virtual ~FExercise() override
	{
		FWorldDelegates::OnWorldPostActorTick.Remove(TickHandle);
		GetMutableDefault<UEditorPerformanceSettings>()->bThrottleCPUWhenNotForeground=bPreviousThrottle;
	}
	virtual bool Update() override
	{
		const double Now = FPlatformTime::Seconds();
		if (!Deadline) Deadline = Now + 50;
		if (Now > Deadline) { Test->AddError(TEXT("Movement PIE timed out")); return true; }
if (Now < Next) return false;
		// GPU screenshot readback can stall a frame. Observe the 220 ms transition
		// only after rendering has returned to a stable cadence.
		if (bWaitForStableFrames && StableFrames < 8) return false;
		bWaitForStableFrames=false;
		if (Step == 0)
		{
			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			PC = World ? World->GetFirstPlayerController() : nullptr;
			Pawn = PC.IsValid() ? Cast<AFantasyLifeRPGCharacter>(PC->GetPawn()) : nullptr;
			if (!Pawn.IsValid() || World->GetTimeSeconds() < .5f || !Pawn->GetCharacterMovement()->IsMovingOnGround()) return false;
			Movement = Pawn->GetCharacterMovement();
			Tools = PC->FindComponentByClass<UDeveloperToolboxComponent>();
			UI = PC->FindComponentByClass<UInventoryUIComponent>();
			if (!Test->TestTrue(TEXT("Prototype movement, toolbox and inventory available"),Tools.IsValid() && UI.IsValid())) return true;
			Test->TestNotNull(TEXT("Inherited Blueprint uses procedural crouch mesh"),Cast<UCrouchPoseMeshComponent>(Pawn->GetMesh()));
			Floor = Box(FVector(0,OriginY,0),FVector(40,40,1));
			Pawn->SetActorLocation(FVector(0,OriginY,150),false,nullptr,ETeleportType::TeleportPhysics);
			Pawn->SetActorRotation(FRotator::ZeroRotator); PC->SetControlRotation(FRotator::ZeroRotator);
			RunSpeed = Movement->MaxWalkSpeed;
			StandingHeight = Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
			BuildSteps(); ++Step; Next=Now+.4; return false;
		}
		if (!Pawn.IsValid() || !PC.IsValid() || !Movement.IsValid() || !GEditor->PlayWorld)
		{ Test->AddError(TEXT("Lost movement PIE fixture")); return true; }
		const int32 Index = Step - 1;
		if (!Actions.IsValidIndex(Index)) return true;
		Actions[Index].Function();
		Next = Now + Actions[Index].Delay;
		++Step;
		return false;
	}
private:
	void ObserveWorld(UWorld* World,ELevelTick TickType,float DeltaSeconds)
	{
		if (!Pawn.IsValid() || World!=Pawn->GetWorld()) return;
		StableFrames=DeltaSeconds < .05f ? StableFrames+1 : 0;
		if (!Pawn->bIsCrouched) return;
		const float Alpha=Pawn->GetCrouchPresentationAlpha();
		bSawIntermediate |= Alpha>0 && Alpha<1;
		const float Z=Pawn->GetCameraBoom()->GetComponentLocation().Z+Pawn->GetCameraBoom()->TargetOffset.Z;
		bSawCameraIntermediate |= Z<CameraZ-.1f && Z>CameraZ-(StandingHeight-65.f)+.1f;
		MinimumTickDelta=FMath::Min(MinimumTickDelta,DeltaSeconds);
	}
	struct FAction { TFunction<void()> Function; float Delay; };
	void Add(TFunction<void()> Function,float Delay=.2f) { Actions.Add({MoveTemp(Function),Delay}); }
	void Key(FKey InKey,EInputEvent Event) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(InKey,Event,Event==IE_Released?0.f:1.f)); }
	void Press(FKey InKey) { Key(InKey,IE_Pressed); }
	void Release(FKey InKey) { Key(InKey,IE_Released); }
	AStaticMeshActor* Box(FVector Location,FVector Scale)
	{
		auto* Actor = Pawn->GetWorld()->SpawnActor<AStaticMeshActor>(Location,FRotator::ZeroRotator);
		Actor->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
		Actor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
		Actor->SetActorScale3D(Scale); Actor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
		return Actor;
	}
	void Capture(const TCHAR* Name) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("InteractionDev")/Name,true,false); }
	void BuildSteps()
	{
		Add([this]{ Start=Pawn->GetActorLocation(); Press(EKeys::W); },.65f);
		Add([this]{ Test->AddInfo(FString::Printf(TEXT("Run: start=%s now=%s velocity=%s yaw=%.2f runSpeed=%.2f"),*Start.ToString(),*Pawn->GetActorLocation().ToString(),*Movement->Velocity.ToString(),PC->GetControlRotation().Yaw,RunSpeed)); Test->TestTrue(TEXT("W runs forward at configured speed"),Movement->Velocity.X > RunSpeed*.9f && Pawn->GetActorLocation().X > Start.X+150); Press(EKeys::LeftShift); },.6f);
		Add([this]{ Test->TestEqual(TEXT("Shift sprint is exactly twofold, not toolbox doubled again"),Movement->MaxWalkSpeed,RunSpeed*2); Test->TestTrue(TEXT("Sprint changes actual movement velocity"),Movement->Velocity.Size2D()>RunSpeed*1.8f); Release(EKeys::LeftShift); Press(EKeys::LeftAlt); },.55f);
		Add([this]{ Test->TestTrue(TEXT("Held Alt walks slowly"),FMath::IsNearlyEqual(Movement->Velocity.Size2D(),RunSpeed*.4f,5.f)); Press(EKeys::RightShift); },.2f);
		Add([this]{ Test->TestEqual(TEXT("Slow walk takes priority over sprint"),Movement->MaxWalkSpeed,RunSpeed*.4f); Release(EKeys::LeftAlt); },.45f);
		Add([this]{ Test->TestEqual(TEXT("Right Shift also sprints"),Movement->MaxWalkSpeed,RunSpeed*2); Release(EKeys::RightShift); Release(EKeys::W); },.45f);
		Add([this]{ Test->TestTrue(TEXT("Releasing direction stops movement"),Movement->Velocity.Size2D()<2); PC->SetControlRotation(FRotator(0,90,0)); Start=Pawn->GetActorLocation(); Press(EKeys::W); },.5f);
		Add([this]{ Test->TestTrue(TEXT("Movement follows camera yaw and character turns toward movement"),Pawn->GetActorLocation().Y > Start.Y+80 && FMath::Abs(Pawn->GetActorForwardVector().Y)>.9f); Release(EKeys::W); },.3f);
		Add([this]{ Press(EKeys::SpaceBar); },.12f);
		Add([this]{ Test->TestTrue(TEXT("Space starts grounded jump"),Movement->IsFalling() && Movement->Velocity.Z>100); JumpVelocity=Movement->Velocity.Z; Release(EKeys::SpaceBar); },.08f);
		Add([this]{ Press(EKeys::SpaceBar); },.1f);
		Add([this]{ Test->TestTrue(TEXT("Airborne Space cannot restart jump"),Movement->Velocity.Z<JumpVelocity); Release(EKeys::SpaceBar); },1.2f);
		Add([this]{
			Test->TestTrue(TEXT("Jump lands on the floor"),Movement->IsMovingOnGround());
			Pawn->SetActorLocation(FVector(0,OriginY,50+StandingHeight+2),false,nullptr,ETeleportType::TeleportPhysics);
			Pawn->SetActorRotation(FRotator::ZeroRotator); PC->SetControlRotation(FRotator(-12,-135,0));
		},.4f);
		Add([this]{
			FootZ=Pawn->GetMesh()->GetSocketLocation(TEXT("foot_l")).Z;
			PelvisZ=Pawn->GetMesh()->GetSocketLocation(TEXT("pelvis")).Z;
			BaseZ=Pawn->GetActorLocation().Z-StandingHeight;
			CameraZ=Pawn->GetCameraBoom()->GetComponentLocation().Z+Pawn->GetCameraBoom()->TargetOffset.Z;
			Capture(TEXT("movement_standing.png"));
			StableFrames=0; bWaitForStableFrames=true;
		},.2f);
		Add([this]{ Press(EKeys::LeftControl); },.08f);
		Add([this]{
			Test->TestTrue(TEXT("Ctrl starts crouch with a smaller collision capsule"),Pawn->bIsCrouched && Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<StandingHeight-20);
			Test->AddInfo(FString::Printf(TEXT("Transition: alpha=%.2f minDelta=%.3f actorInterval=%.3f"),Pawn->GetCrouchPresentationAlpha(),MinimumTickDelta,Pawn->GetActorTickInterval()));
			Test->TestTrue(TEXT("Body transition has intermediate values"),bSawIntermediate);

			Test->TestTrue(TEXT("Camera moves partway instead of snapping to crouched height"),bSawCameraIntermediate);
		},.4f);
		Add([this]{
			Test->TestTrue(TEXT("Holding Ctrl does not repeatedly toggle"),Pawn->bIsCrouched);
			Test->TestTrue(TEXT("Crouch keeps capsule feet on floor"),FMath::IsNearlyEqual(Pawn->GetActorLocation().Z-Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),BaseZ,2.f));
			Test->AddInfo(FString::Printf(TEXT("Pose: alpha=%.3f drop=%.2f pelvisBefore=%.2f pelvisNow=%.2f footBefore=%.2f footNow=%.2f left=%s/%s/%s right=%s/%s/%s"),Pawn->GetCrouchPresentationAlpha(),Pawn->GetCrouchPresentationDrop(),PelvisZ,Pawn->GetMesh()->GetSocketLocation(TEXT("pelvis")).Z,FootZ,Pawn->GetMesh()->GetSocketLocation(TEXT("foot_l")).Z,*Pawn->GetMesh()->GetSocketLocation(TEXT("thigh_l")).ToString(),*Pawn->GetMesh()->GetSocketLocation(TEXT("calf_l")).ToString(),*Pawn->GetMesh()->GetSocketLocation(TEXT("foot_l")).ToString(),*Pawn->GetMesh()->GetSocketLocation(TEXT("thigh_r")).ToString(),*Pawn->GetMesh()->GetSocketLocation(TEXT("calf_r")).ToString(),*Pawn->GetMesh()->GetSocketLocation(TEXT("foot_r")).ToString()));
			Test->TestTrue(TEXT("Crouch pose lowers hips while keeping feet planted"),Pawn->GetMesh()->GetSocketLocation(TEXT("pelvis")).Z<PelvisZ-45 && FMath::IsNearlyEqual(Pawn->GetMesh()->GetSocketLocation(TEXT("foot_l")).Z,FootZ,5.f));
			Test->TestTrue(TEXT("Pose bends the knees rather than scaling the body"),Pawn->GetMesh()->GetComponentScale().Equals(FVector::OneVector) && Pawn->GetMesh()->GetSocketLocation(TEXT("calf_l")).X > Pawn->GetMesh()->GetSocketLocation(TEXT("thigh_l")).X+15);
			Capture(TEXT("movement_crouched.png")); Release(EKeys::LeftControl);
			Press(EKeys::SpaceBar); Press(EKeys::LeftShift);
		},.3f);
		Add([this]{
			Test->TestTrue(TEXT("Crouch blocks jump and sprint"),Pawn->bIsCrouched && Movement->IsMovingOnGround() && Movement->Velocity.Z<1 && Movement->MaxWalkSpeed==RunSpeed);
			Release(EKeys::SpaceBar); Release(EKeys::LeftShift);
			// A 145 cm opening: crouched capsule fits, standing capsule does not.
			Roof=Box(FVector(150,OriginY,205),FVector(6,4,.2));
			PC->SetControlRotation(FRotator::ZeroRotator); Start=Pawn->GetActorLocation(); Press(EKeys::W);
		},.55f);
		Add([this]{
			Test->TestTrue(TEXT("Crouched player actually traverses a low opening"),Pawn->GetActorLocation().X > Start.X+50 && Movement->Velocity.Size2D()>RunSpeed*.35f);
			Release(EKeys::W); Press(EKeys::LeftControl);
		},.4f);
		Add([this]{
			Test->AddInfo(FString::Printf(TEXT("Roof: pawn=%s halfHeight=%.2f standing=%.2f crouch=%d wants=%d roof=%s bounds=%s"),*Pawn->GetActorLocation().ToString(),Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),StandingHeight,Pawn->bIsCrouched,Movement->bWantsToCrouch,*Roof->GetActorLocation().ToString(),*Roof->GetComponentsBoundingBox().ToString()));
			Test->TestTrue(TEXT("Native headroom check rejects standing under the roof"),Pawn->bIsCrouched && Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<StandingHeight);
			Release(EKeys::LeftControl); Roof->Destroy();
		},.4f);
		Add([this]{
			Test->TestFalse(TEXT("Pending stand completes when there is room"),Pawn->bIsCrouched);
			Test->TestTrue(TEXT("Standing restores capsule, body and camera"),FMath::IsNearlyEqual(Pawn->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),StandingHeight) && Pawn->GetCrouchPresentationAlpha()==0 && Pawn->GetCameraBoom()->TargetOffset.IsNearlyZero());
			Press(EKeys::LeftShift);
		},.15f);
		Add([this]{ Test->TestEqual(TEXT("Sprint before inventory opens"),Movement->MaxWalkSpeed,RunSpeed*2); UI->TogglePanel(); Release(EKeys::LeftShift); Press(EKeys::LeftControl); Press(EKeys::LeftAlt); },.3f);
		Add([this]{ Test->TestTrue(TEXT("Inventory blocks crouch and clears sprint speed"),UI->IsPanelOpen() && !Pawn->bIsCrouched && Movement->MaxWalkSpeed==RunSpeed); Release(EKeys::LeftControl); Release(EKeys::LeftAlt); UI->ClosePanel(); },.2f);
		Add([this]{
			Test->TestEqual(TEXT("No held speed sticks after inventory closes"),Movement->MaxWalkSpeed,RunSpeed);
			Pawn->SetActorLocation(Pawn->GetActorLocation()+FVector(0,0,300),false,nullptr,ETeleportType::TeleportPhysics);
			Tools->SetFlight(true); Start=Pawn->GetActorLocation(); Press(EKeys::LeftControl);
		},.3f);
		Add([this]{
			Test->TestTrue(TEXT("Flight Ctrl descends without toggling crouch"),!Pawn->bIsCrouched && Pawn->GetActorLocation().Z<Start.Z-10);
			Release(EKeys::LeftControl); Tools->SetFlight(false);
			Tools->Cleanup(); Tools->bEnabled=false;
			Press(EKeys::LeftShift);
		},.2f);
		Add([this]{
			Test->TestEqual(TEXT("Gameplay sprint works with toolbox disabled"),Movement->MaxWalkSpeed,RunSpeed*2);
			Release(EKeys::LeftShift); Press(EKeys::RightControl);
		},.3f);
		Add([this]{ Test->TestTrue(TEXT("Right Ctrl crouches without toolbox"),Pawn->bIsCrouched); Release(EKeys::RightControl); },.1f);
		Add([this]{ Press(EKeys::RightControl); },.35f);
		Add([this]{ Test->TestFalse(TEXT("Second Ctrl press stands up in open space"),Pawn->bIsCrouched); Release(EKeys::RightControl); Floor->Destroy(); });
	}
	FAutomationTestBase* Test;
	FDelegateHandle TickHandle;
	float MinimumTickDelta=100.f;
	TArray<FAction> Actions;
	TWeakObjectPtr<AFantasyLifeRPGCharacter> Pawn;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<UCharacterMovementComponent> Movement;
	TWeakObjectPtr<UDeveloperToolboxComponent> Tools;
	TWeakObjectPtr<UInventoryUIComponent> UI;
	TWeakObjectPtr<AStaticMeshActor> Floor,Roof;
	int32 Step=0;
	double Next=0,Deadline=0;
	int32 StableFrames=0;
	bool bWaitForStableFrames=false;
	bool bPreviousThrottle=false;
	bool bSawIntermediate=false,bSawCameraIntermediate=false;
	float RunSpeed=0,StandingHeight=0,FootZ=0,PelvisZ=0,BaseZ=0,CameraZ=0,JumpVelocity=0;
	FVector Start;
	float OriginY;
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMovementPIE,"FantasyLifeRPG.Movement.PlayablePIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FMovementPIE::RunTest(const FString& Parameters)
{
	AddCommand(new MovementTests::FEndPIE(this));
	AddCommand(new FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_InventoryTest_01")));
	AddCommand(new MovementTests::FStartPIE());
	AddCommand(new MovementTests::FExercise(this));
	AddCommand(new MovementTests::FEndPIE(this));
	return true;
}

// Use the saved Asset Lab's own GameMode/pawn, with transient fixtures away from its assets.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMovementAssetLabPIE,"FantasyLifeRPG.Movement.AssetLabPIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FMovementAssetLabPIE::RunTest(const FString& Parameters)
{
	AddCommand(new MovementTests::FEndPIE(this));
	AddCommand(new FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_AssetLab")));
	AddCommand(new MovementTests::FStartPIE());
	AddCommand(new MovementTests::FExercise(this,50000.f));
	AddCommand(new MovementTests::FEndPIE(this));
	return true;
}
#endif
