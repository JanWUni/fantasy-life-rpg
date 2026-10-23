#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Development/DeveloperToolboxComponent.h"
#include "Development/DeveloperToolboxWidget.h"
#include "Development/DeveloperScenario.h"
#include "NPC/WaypointMovementComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Framework/Application/SlateApplication.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "EnhancedPlayerInput.h"
#include "EnhancedActionKeyMapping.h"
#include "Camera/CameraActor.h"
#include "Components/Button.h"
#include "Components/SpinBox.h"
#include "Components/CapsuleComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"
namespace DeveloperToolboxTests
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

class FCheckTools : public IAutomationLatentCommand
{
public:
	FCheckTools(FAutomationTestBase* InTest,bool bInDetailed) : Test(InTest),bDetailed(bInDetailed) {}
	virtual bool Update() override
	{
		const double WallNow = FPlatformTime::Seconds();
		// Input assertions must wait for simulated world frames, including cold maps.
		const double Now = GEditor && GEditor->PlayWorld ? GEditor->PlayWorld->GetTimeSeconds() : 0.;
		if (Deadline == 0) Deadline = WallNow+45; // Includes cold Niagara compilation and the rendered UI capture.
		if (WallNow > Deadline) { Test->AddError(TEXT("Toolbox test timed out")); return true; }
		if (Now < Next) return false;
		if (Step == 0)
		{
			UWorld* World = GEditor ? GEditor->PlayWorld.Get() : nullptr;
			PC = World ? World->GetFirstPlayerController() : nullptr;
			Player = PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
			if ((!Player.IsValid() || !Player->GetCharacterMovement()->IsMovingOnGround()) && WallNow < Deadline) return false;
			if (!Test->TestTrue(TEXT("Toolbox map has a grounded player"),Player.IsValid() && Player->GetCharacterMovement()->IsMovingOnGround())) return true;
			Tools = PC->FindComponentByClass<UDeveloperToolboxComponent>();
			if (!Test->TestTrue(TEXT("Opt-in prototype controller provides usable toolbox"),Tools.IsValid() && Tools->CanUse())) return true;
			// BeginPlay/grounded is earlier than the initial viewport-focus input flush. Allow the
			// initial game/input frames to settle before sending one deliberate key press (no retry).
			if (World->GetTimeSeconds() < .35f) return false;
			if (const UEnhancedPlayerInput* Input = Cast<UEnhancedPlayerInput>(PC->PlayerInput))
				for (const FEnhancedActionKeyMapping& Mapping : Input->GetEnhancedActionMappingsView())
					if (Mapping.Key==EKeys::F6) Test->AddInfo(FString::Printf(TEXT("F6 ready at world time %.3f; ignored=%d"),World->GetTimeSeconds(),Mapping.bShouldBeIgnored));
			Original = Player->GetActorLocation();
			OriginalFlySpeed = Player->GetCharacterMovement()->MaxFlySpeed;
			Cursor = PC->bShowMouseCursor;
			Key(EKeys::F6,IE_Pressed); ++Step; Next=Now+.2; return false;
		}
		if (!PC.IsValid() || !Player.IsValid() || !Tools.IsValid() || !GEditor->PlayWorld)
		{ Test->AddError(TEXT("Toolbox test lost PIE fixture")); return true; }
		if (Step == 1)
		{
			Key(EKeys::F6,IE_Released);
			if (!Test->TestTrue(TEXT("F6 opens the UMG panel"),Tools->IsPanelOpen() && Tools->GetPanel() && Tools->GetPanel()->IsInViewport())) return true;
			Test->TestTrue(TEXT("Menu unlocks cursor and blocks movement/look"),PC->bShowMouseCursor && PC->IsMoveInputIgnored() && PC->IsLookInputIgnored());
			Test->TestFalse(TEXT("Opening tools leaves simulation unpaused"),GEditor->PlayWorld->IsPaused());
			if (bDetailed) FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("InteractionDev/toolbox_panel.png"),true,false);
			Key(EKeys::W,IE_Pressed); Key(EKeys::SpaceBar,IE_Pressed); Key(EKeys::MouseX,IE_Axis,20);
			++Step; Next=Now+.25; return false;
		}
		if (Step == 2)
		{
			Test->TestTrue(TEXT("Menu suppresses movement and jump"),Player->GetActorLocation().Equals(Original,2));
			Key(EKeys::W,IE_Released); Key(EKeys::SpaceBar,IE_Released); Key(EKeys::MouseX,IE_Axis,0);
			const bool bEnvironment = GEditor->PlayWorld->GetMapName().Contains(TEXT("EnvironmentTest"));
			Test->TestTrue(TEXT("NPC route availability matches the saved map"),Tools->GetScenarios().Num()==1 && Tools->GetScenarios()[0]->IsAvailable()==bEnvironment);
			if (bEnvironment)
			{
				UWaypointMovementComponent* Route=nullptr;
				for (TActorIterator<AActor> It(GEditor->PlayWorld); It; ++It) if (auto* Found=It->FindComponentByClass<UWaypointMovementComponent>()) { Route=Found; break; }
				if (Test->TestNotNull(TEXT("Existing NPC route found"),Route))
				{
					Test->TestTrue(TEXT("Existing route adapter stops route"),Tools->GetScenarios()[0]->Stop());
					Test->TestEqual(TEXT("Route stopped"),Route->GetRouteState(),EWaypointMovementState::Stopped);
					Test->TestTrue(TEXT("Existing route adapter starts route"),Tools->GetScenarios()[0]->Start());
					Test->TestTrue(TEXT("Route running again"),Route->GetRouteState()!=EWaypointMovementState::Stopped);
					Tools->GetScenarios()[0]->Stop(); Tools->ResetTools();
					Test->TestTrue(TEXT("Reset restores initially running NPC route"),Route->GetRouteState()!=EWaypointMovementState::Stopped);
					Route->StopRoute();
					Tools->GetScenarios()[0]->Start(); Tools->ResetTools();
					Test->TestEqual(TEXT("Reset also preserves an initially stopped route"),Route->GetRouteState(),EWaypointMovementState::Stopped);
					Route->StartRoute();
				}
			}
			if (!bDetailed)
			{
				Key(EKeys::F6,IE_Pressed); ++Step; Next=Now+.2; return false;
			}
			Click(TEXT("FlightButton"));
			Test->TestTrue(TEXT("UMG flight button enables flight independently"),Tools->IsFlying() && !Tools->IsNoClip());
			Cast<USpinBox>(Tools->GetPanel()->WidgetTree->FindWidget(TEXT("FlightSpeed")))->SetValue(1800);
			Test->TestEqual(TEXT("UMG spin box updates backend speed"),Tools->GetFlightSpeed(),1800.f);
			Click(TEXT("NoClipButton"));
			Test->TestFalse(TEXT("NoClip disables actor collision"),Player->GetActorEnableCollision());
			Click(TEXT("NoClipButton"));
			Test->TestTrue(TEXT("NoClip can stop without stopping flight"),Tools->IsFlying() && !Tools->IsNoClip() && Player->GetActorEnableCollision());
			const FKeyEvent Escape(EKeys::Escape,FModifierKeysState(),0,false,0,0);
			Test->TestTrue(TEXT("Actual Slate Escape is handled by the focused UMG panel"),FSlateApplication::Get().ProcessKeyDownEvent(Escape));
			FSlateApplication::Get().ProcessKeyUpEvent(FKeyEvent(EKeys::Escape,FModifierKeysState(),0,false,0,0));
			Test->TestFalse(TEXT("Escape closes menu"),Tools->IsPanelOpen());
			Test->TestTrue(TEXT("Escape leaves PIE running"),GEditor->PlayWorld!=nullptr);
			Key(EKeys::W,IE_Pressed); Key(EKeys::SpaceBar,IE_Pressed);
			Start = Player->GetActorLocation();
			++Step; Next=Now+.6; return false;
		}
		if (!bDetailed)
		{
			Key(EKeys::F6,IE_Released);
			Test->TestFalse(TEXT("F6 closes panel again"),Tools->IsPanelOpen());
			Test->TestTrue(TEXT("Normal focus/cursor input restored"),!PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && PC->bShowMouseCursor==Cursor);
			Tools->SetFlight(true); Tools->SetNoClip(true); Tools->SetFreeCamera(true);
			Tools->GetEffectTester()->Trigger(0,true);
			Tools->TogglePanel(); // End PIE with active tools to exercise teardown from each saved map.
			return true;
		}
		if (Step == 3)
		{
			Test->TestTrue(TEXT("Flight W and Space produce horizontal and vertical movement"),Player->GetActorLocation().Y > Start.Y+50 && Player->GetActorLocation().Z > Start.Z+100);
			Test->TestTrue(TEXT("Closed panel restores look/move input and cursor"),!PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && PC->bShowMouseCursor==Cursor);
			Key(EKeys::W,IE_Released); Key(EKeys::SpaceBar,IE_Released);
			Player->GetCharacterMovement()->StopMovementImmediately();
			Start = Player->GetActorLocation();
			Key(EKeys::LeftControl,IE_Pressed); Key(EKeys::LeftShift,IE_Pressed);
			++Step; Next=Now+.35; return false;
		}
		if (Step == 4)
		{
			Test->TestTrue(TEXT("Control descends in flight"),Player->GetActorLocation().Z < Start.Z-20);
			Test->TestEqual(TEXT("Shift applies temporary threefold flight limit"),Player->GetCharacterMovement()->MaxFlySpeed,5400.f);
			Key(EKeys::LeftControl,IE_Released); Key(EKeys::LeftShift,IE_Released);
			Tools->SetFlight(false);
			Test->TestEqual(TEXT("Original fly speed restored"),Player->GetCharacterMovement()->MaxFlySpeed,OriginalFlySpeed);
			Test->TestTrue(TEXT("Original walking mode restored"),Player->GetCharacterMovement()->MovementMode==MOVE_Walking);
			const FVector SafeBeforeNoClip = Player->GetActorLocation();
			Test->TestTrue(TEXT("NoClip can start without user flight mode"),Tools->SetNoClip(true) && !Tools->IsFlying());
			AActor* Wall=nullptr;
			for (TActorIterator<AActor> It(GEditor->PlayWorld); It; ++It) if (It->ActorHasTag(TEXT("WorkspaceWallA"))) { Wall=*It; break; }
			if (Test->TestNotNull(TEXT("Saved wall fixture found"),Wall))
			{
				Player->SetActorLocation(Wall->GetActorTransform().TransformPosition(FVector(200,10,120)),false,nullptr,ETeleportType::TeleportPhysics);
				Test->TestTrue(TEXT("NoClip safely restores collision from inside a wall"),Tools->SetNoClip(false));
				Test->TestTrue(TEXT("Character recovered to the previous free point"),Player->GetActorEnableCollision() && !Tools->IsNoClip() && Player->GetActorLocation().Equals(SafeBeforeNoClip,1));
			}
			Player->SetActorLocation(Original,false,nullptr,ETeleportType::TeleportPhysics);
			Player->GetCharacterMovement()->StopMovementImmediately();
			PreviousView = PC->GetViewTarget(); BeforeLook = PC->GetControlRotation();
			Tools->SetCameraSpeed(2000); Test->TestTrue(TEXT("Free camera activates"),Tools->SetFreeCamera(true));
			Test->TestEqual(TEXT("Camera speed setting accepted"),Tools->GetCameraSpeed(),2000.f);
			CameraStart = Tools->GetFreeCamera()->GetActorLocation();
			Key(EKeys::W,IE_Pressed); Key(EKeys::SpaceBar,IE_Pressed); Key(EKeys::MouseX,IE_Axis,10);
			++Step; Next=Now+.35; return false;
		}
		if (Step == 5)
		{
			Test->TestTrue(TEXT("Free camera moves independently"),FVector::Dist(Tools->GetFreeCamera()->GetActorLocation(),CameraStart)>200 && FVector::Dist2D(Player->GetActorLocation(),Original)<2);
			Key(EKeys::W,IE_Released); Key(EKeys::SpaceBar,IE_Released); Key(EKeys::MouseX,IE_Axis,0);
			Tools->SetFreeCamera(false);
			Test->TestTrue(TEXT("Camera target and control rotation restored"),PC->GetViewTarget()==PreviousView.Get() && PC->GetControlRotation().Equals(BeforeLook,.01));
			Tools->TogglePanel();
			Click(TEXT("TriggerEffectButton"));
			Test->TestTrue(TEXT("UMG triggers configured existing Niagara effect"),Tools->GetEffectTester()->GetActiveCount()>0);
			Test->TestTrue(TEXT("Second existing Niagara system also starts at a ground test position"),Tools->GetEffectTester()->Trigger(1,false));
			for (int32 I=0; I<10; ++I) Test->TestTrue(TEXT("Repeated test effect starts"),Tools->GetEffectTester()->Trigger(0,I%2==0));
			Test->TestTrue(TEXT("Effect tester bounds active systems"),Tools->GetEffectTester()->GetActiveCount()<=8);
			Click(TEXT("StopEffectsButton")); Test->TestEqual(TEXT("Stop removes all test effects"),Tools->GetEffectTester()->GetActiveCount(),0);
			Tools->ClosePanel();
			Tools->bEnabled=false;
			Test->TestFalse(TEXT("Backend gate rejects flight with tools disabled"),Tools->SetFlight(true));
			Test->TestFalse(TEXT("Backend gate rejects NoClip"),Tools->SetNoClip(true));
			Test->TestFalse(TEXT("Backend gate rejects free camera"),Tools->SetFreeCamera(true));
			Test->TestFalse(TEXT("Effect service also validates backend gate"),Tools->GetEffectTester()->Trigger(0,true));
			Tools->bEnabled=true;
			PC->SetIgnoreMoveInput(true); PC->SetIgnoreLookInput(true);
			Tools->TogglePanel(); Tools->ClosePanel();
			Test->TestTrue(TEXT("Closing preserves external input locks"),PC->IsMoveInputIgnored() && PC->IsLookInputIgnored());
			PC->SetIgnoreMoveInput(false); PC->SetIgnoreLookInput(false);
			Tools->SetFlight(true); Tools->SetNoClip(true); Tools->SetFreeCamera(true); Tools->TogglePanel();
			Tools->GetEffectTester()->Trigger(0,true);
			Tools->Cleanup();
			Test->TestTrue(TEXT("Cleanup restores character, collision, view and input"),!Tools->IsFlying() && !Tools->IsNoClip() && !Tools->IsFreeCamera() && !Tools->IsPanelOpen() && Player->GetActorEnableCollision() && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored() && PC->GetViewTarget()==PreviousView.Get());
			Test->TestEqual(TEXT("Cleanup stops transient effects"),Tools->GetEffectTester()->GetActiveCount(),0);
			return true;
		}
		return true;
	}
private:
	void Key(FKey Input,EInputEvent Event,float Amount=1) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Input,Event,Event==IE_Released ? 0.f : Amount)); }
	void Click(FName Name)
	{
		UButton* Button = Cast<UButton>(Tools->GetPanel()->WidgetTree->FindWidget(Name));
		if (Test->TestNotNull(TEXT("UMG tool button exists"),Button)) Button->OnClicked.Broadcast();
	}
	FAutomationTestBase* Test;
	bool bDetailed, Cursor=false;
	int32 Step=0;
	double Deadline=0,Next=0;
	float OriginalFlySpeed=0;
	FVector Original, Start, CameraStart;
	FRotator BeforeLook;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Player;
	TWeakObjectPtr<UDeveloperToolboxComponent> Tools;
	TWeakObjectPtr<AActor> PreviousView;
};
/** Actual velocity/position checks, including releases; does not manually brake the character. */
class FCheckHandling : public IAutomationLatentCommand
{
public:
	explicit FCheckHandling(FAutomationTestBase* InTest) : Test(InTest) {}
	virtual bool Update() override
	{
		const double Now=FPlatformTime::Seconds();
		if (Deadline==0) Deadline=Now+35;
		if (Now<Next) return false;
		if (Step==0)
		{
			UWorld* World=GEditor ? GEditor->PlayWorld.Get() : nullptr;
			PC=World ? World->GetFirstPlayerController() : nullptr;
			Pawn=PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
			if ((!Pawn.IsValid() || !Pawn->GetCharacterMovement()->IsMovingOnGround() || World->GetTimeSeconds()<.4f) && Now<Deadline) return false;
			if (!Test->TestTrue(TEXT("Handling fixture ready"),Pawn.IsValid() && PC.IsValid())) return true;
			Tools=PC->FindComponentByClass<UDeveloperToolboxComponent>();
			if (!Test->TestTrue(TEXT("Handling toolbox available"),Tools.IsValid() && Tools->CanUse())) return true;
			Ground=Pawn->GetActorLocation(); WalkSpeed=Pawn->GetCharacterMovement()->MaxWalkSpeed;
			// Non-default values detect an incorrect hard-coded restore.
			Pawn->GetCharacterMovement()->MaxAcceleration=2333.f;
			Pawn->GetCharacterMovement()->MaxFlySpeed=637.f;
			PC->SetControlRotation(FRotator(0,90,0));
			Tools->SetFlightSpeed(600); Tools->SetFlight(true);
			Key(EKeys::W,IE_Pressed); Advance(Now,.25); return false;
		}
		if (!Pawn.IsValid() || !PC.IsValid() || !Tools.IsValid() || !GEditor->PlayWorld || Now>Deadline)
		{ Test->AddError(TEXT("Handling fixture lost or timed out")); return true; }
		UCharacterMovementComponent* Move=Pawn->GetCharacterMovement();
		switch (Step)
		{
		case 1:
			Test->TestTrue(TEXT("Flight reaches configured speed"),Move->Velocity.Size()>550 && Move->Velocity.Size()<=601);
			Key(EKeys::W,IE_Released); Stopped=Pawn->GetActorLocation(); Advance(Now,.25); break;
		case 2:
			StoppedCheck(TEXT("Flight release stops without drifting"));
			Key(EKeys::W,IE_Pressed); Key(EKeys::LeftShift,IE_Pressed); Advance(Now,.25); break;
		case 3:
			Test->TestTrue(TEXT("Left Shift increases actual flight speed, not just the limit"),Move->Velocity.Size()>1700);
			Key(EKeys::LeftShift,IE_Released); Advance(Now,.15); break;
		case 4:
			Test->TestTrue(TEXT("Shift release returns actual flight speed to normal"),Move->Velocity.Size()>550 && Move->Velocity.Size()<=601);
			Key(EKeys::W,IE_Released); Tools->SetNoClip(true); Tools->SetFlight(false);
			Test->TestTrue(TEXT("NoClip handling tested independently from flight"),Tools->IsNoClip() && !Tools->IsFlying() && !Pawn->GetActorEnableCollision());
			Key(EKeys::D,IE_Pressed); Advance(Now,.25); break;
		case 5:
			Test->TestTrue(TEXT("NoClip moves at configured speed"),Move->Velocity.Size()>550);
			Key(EKeys::D,IE_Released); Stopped=Pawn->GetActorLocation(); Advance(Now,.25); break;
		case 6:
			StoppedCheck(TEXT("NoClip release stops without drifting"));
			Key(EKeys::D,IE_Pressed); Key(EKeys::RightShift,IE_Pressed); Advance(Now,.25); break;
		case 7:
			Test->TestTrue(TEXT("Right Shift increases actual NoClip speed"),Move->Velocity.Size()>1700);
			Key(EKeys::D,IE_Released); Key(EKeys::RightShift,IE_Released); Tools->SetNoClip(false);
			Test->TestEqual(TEXT("Original acceleration restored after debug movement"),Move->MaxAcceleration,2333.f);
			Test->TestEqual(TEXT("Original fly speed restored after debug movement"),Move->MaxFlySpeed,637.f);
			Pawn->SetActorLocation(Ground,false,nullptr,ETeleportType::TeleportPhysics);
			Key(EKeys::W,IE_Pressed); Advance(Now,.65); break;
		case 8:
			Test->TestTrue(TEXT("Normal walking remains at original speed"),Move->Velocity.Size2D()>WalkSpeed*.9 && Move->Velocity.Size2D()<=WalkSpeed+1);
			Key(EKeys::LeftShift,IE_Pressed); Advance(Now,.4); break;
		case 9:
			Test->TestEqual(TEXT("Ground sprint doubles the original walking limit"),Move->MaxWalkSpeed,WalkSpeed*2);
			Test->TestTrue(TEXT("Shift makes actual walking faster"),Move->Velocity.Size2D()>WalkSpeed*1.8);
			Key(EKeys::LeftShift,IE_Released); Advance(Now,.2); break;
		case 10:
			Test->TestEqual(TEXT("Ground sprint release restores original walking limit"),Move->MaxWalkSpeed,WalkSpeed);
			Key(EKeys::W,IE_Released); Key(EKeys::RightShift,IE_Pressed); Advance(Now,.15); break;
		case 11:
			Test->TestEqual(TEXT("Right Shift also supports ground sprint"),Move->MaxWalkSpeed,WalkSpeed*2);
			Tools->TogglePanel(); Test->TestEqual(TEXT("Opening menu restores ground speed"),Move->MaxWalkSpeed,WalkSpeed);
			Tools->ClosePanel(); Key(EKeys::RightShift,IE_Released);
			Tools->SetFreeCamera(true); Pitch=Tools->GetFreeCamera()->GetActorRotation().Pitch;
			Key(EKeys::MouseY,IE_Axis,-12); Advance(Now,.15); break;
		case 12:
			Test->TestTrue(TEXT("Mouse down (negative Unreal MouseY) looks down in free camera"),FMath::FindDeltaAngleDegrees(Pitch,Tools->GetFreeCamera()->GetActorRotation().Pitch)<-.05);
			Key(EKeys::MouseY,IE_Axis,0); Pitch=Tools->GetFreeCamera()->GetActorRotation().Pitch;
			Key(EKeys::MouseY,IE_Axis,12); Advance(Now,.15); break;
		case 13:
			Test->TestTrue(TEXT("Mouse up looks up in free camera"),FMath::FindDeltaAngleDegrees(Pitch,Tools->GetFreeCamera()->GetActorRotation().Pitch)>.05);
			Key(EKeys::MouseY,IE_Axis,0); CameraStart=Tools->GetFreeCamera()->GetActorLocation(); SampleTime=GEditor->PlayWorld->GetTimeSeconds();
			Key(EKeys::W,IE_Pressed); Advance(Now,.25); break;
		case 14:
			NormalCameraRate=FVector::Dist(CameraStart,Tools->GetFreeCamera()->GetActorLocation())/(GEditor->PlayWorld->GetTimeSeconds()-SampleTime);
			CameraStart=Tools->GetFreeCamera()->GetActorLocation(); SampleTime=GEditor->PlayWorld->GetTimeSeconds();
			Key(EKeys::LeftShift,IE_Pressed); Advance(Now,.25); break;
		case 15:
			Test->TestTrue(TEXT("Shift triples actual free-camera movement rate"),FVector::Dist(CameraStart,Tools->GetFreeCamera()->GetActorLocation())/(GEditor->PlayWorld->GetTimeSeconds()-SampleTime)>NormalCameraRate*2.5);
			Key(EKeys::W,IE_Released); Key(EKeys::LeftShift,IE_Released); CameraStart=Tools->GetFreeCamera()->GetActorLocation(); Advance(Now,.2); break;
		case 16:
			Test->TestTrue(TEXT("Free camera remains stationary on release"),Tools->GetFreeCamera()->GetActorLocation().Equals(CameraStart,1));
			Tools->SetFreeCamera(false); Key(EKeys::RightShift,IE_Pressed); Advance(Now,.15); break;
		case 17:
			Test->TestEqual(TEXT("Ground sprint still works after camera return"),Move->MaxWalkSpeed,WalkSpeed*2);
			Tools->Cleanup();
			Test->TestEqual(TEXT("Cleanup restores sprint speed"),Move->MaxWalkSpeed,WalkSpeed);
			Test->TestEqual(TEXT("Cleanup preserves original acceleration"),Move->MaxAcceleration,2333.f);
			Key(EKeys::RightShift,IE_Released); return true;
		}
		return false;
	}
private:
	void Advance(double Now,double Seconds) { ++Step; Next=Now+Seconds; }
	void Key(FKey Input,EInputEvent Event,float Amount=1) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Input,Event,Event==IE_Released ? 0.f : Amount)); }
	void StoppedCheck(const TCHAR* Label)
	{
		Test->TestTrue(Label,Pawn->GetCharacterMovement()->Velocity.IsNearlyZero(.01f) && Pawn->GetActorLocation().Equals(Stopped,1));
	}
	FAutomationTestBase* Test;
	int32 Step=0;
	double Deadline=0,Next=0,SampleTime=0,NormalCameraRate=0;
	float WalkSpeed=0,Pitch=0;
	FVector Ground,Stopped,CameraStart;
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<ACharacter> Pawn;
	TWeakObjectPtr<UDeveloperToolboxComponent> Tools;
};

void Queue(FAutomationTestBase* Test,const FString& Map,bool bDetailed)
{
	Test->AddCommand(new FEndPIE(Test));
	Test->AddCommand(new FEditorLoadMap(Map));
	Test->AddCommand(new FStartPIE());
	Test->AddCommand(new FCheckTools(Test,bDetailed));
	Test->AddCommand(new FEndPIE(Test));
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDeveloperToolsControls,"FantasyLifeRPG.DeveloperToolbox.ControlsPIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDeveloperToolsControls::RunTest(const FString& Parameters) { DeveloperToolboxTests::Queue(this,TEXT("/Game/Prototype/Maps/Lvl_AssetLab"),true); return true; }
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDeveloperToolsHandling,"FantasyLifeRPG.DeveloperToolbox.HandlingPIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDeveloperToolsHandling::RunTest(const FString& Parameters)
{
	AddCommand(new DeveloperToolboxTests::FEndPIE(this));
	AddCommand(new FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_AssetLab")));
	AddCommand(new DeveloperToolboxTests::FStartPIE());
	AddCommand(new DeveloperToolboxTests::FCheckHandling(this));
	AddCommand(new DeveloperToolboxTests::FEndPIE(this));
	return true;
}
IMPLEMENT_COMPLEX_AUTOMATION_TEST(FDeveloperToolsMaps,"FantasyLifeRPG.DeveloperToolbox.MapsPIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
void FDeveloperToolsMaps::GetTests(TArray<FString>& Names,TArray<FString>& Commands) const
{
	for (const TCHAR* Name : {TEXT("Lvl_AssetLab"),TEXT("Lvl_WorldSandbox"),TEXT("Lvl_Prototype_01"),TEXT("Lvl_EnvironmentTest_01")})
	{ Names.Add(Name); Commands.Add(FString(TEXT("/Game/Prototype/Maps/"))+Name); }
}
bool FDeveloperToolsMaps::RunTest(const FString& Parameters) { DeveloperToolboxTests::Queue(this,Parameters,false); return true; }
#endif

