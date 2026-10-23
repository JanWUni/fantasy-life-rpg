#if WITH_DEV_AUTOMATION_TESTS && WITH_EDITOR
#include "Misc/AutomationTest.h"
#include "Inventory/InventoryComponent.h"
#include "Inventory/InventoryItemDefinition.h"
#include "Inventory/InventoryPickup.h"
#include "Inventory/UI/InventoryUIComponent.h"
#include "Inventory/UI/InventoryWidget.h"
#include "Development/DeveloperToolboxComponent.h"
#include "Framework/Application/SlateApplication.h"
#include "Interaction/InteractionComponent.h"
#include "Interaction/InteractionFeedbackComponent.h"
#include "Prototype/PrototypeMessageComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
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
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInventoryRules,"FantasyLifeRPG.Inventory.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FInventoryRules::RunTest(const FString& Parameters)
{
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    World->InitializeActorsForPlay(FURL()); World->BeginPlay();
    ACharacter* Pawn=World->SpawnActor<ACharacter>(FVector(0,0,1000),FRotator::ZeroRotator);
    UInventoryComponent* Inventory=NewObject<UInventoryComponent>(Pawn); Inventory->RegisterComponent();
    UInteractionComponent* Interaction=NewObject<UInteractionComponent>(Pawn); Interaction->RegisterComponent();
    UInventoryItemDefinition* Wood=NewObject<UInventoryItemDefinition>(World);
    Wood->DisplayName=FText::FromString(TEXT("Testressource"));
    Wood->WorldMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube"));
    UInventoryItemDefinition* Other=NewObject<UInventoryItemDefinition>(World);
    Other->DisplayName=Wood->DisplayName; Other->WorldMesh=Wood->WorldMesh; Other->MaxStack=1;
    TestEqual(TEXT("Default capacity is 20"),Inventory->GetCapacity(),20);
    TestFalse(TEXT("Null definitions rejected"),Inventory->TryAdd(nullptr,1));
    TestFalse(TEXT("Zero rejected"),Inventory->TryAdd(Wood,0));
    TestFalse(TEXT("Negative quantity rejected"),Inventory->TryAdd(Wood,-1));
    TestFalse(TEXT("Huge quantity cannot overflow capacity arithmetic"),Inventory->TryAdd(Wood,MAX_int32));
    TestTrue(TEXT("Add 98"),Inventory->TryAdd(Wood,98));
    TestTrue(TEXT("Split across limit 99"),Inventory->TryAdd(Wood,2));
    TestEqual(TEXT("Two slots"),Inventory->GetSlotView().Num(),2);
    TestEqual(TEXT("First stack filled"),Inventory->GetSlotView()[0].Quantity,99);
    TestEqual(TEXT("Remainder in second"),Inventory->GetSlotView()[1].Quantity,1);
    TestTrue(TEXT("Different definition with same name stays separate"),Inventory->TryAdd(Other,18));
    TestEqual(TEXT("All 20 slots occupied"),Inventory->GetSlotView().Num(),20);
    TestTrue(TEXT("Existing stack can fill while all slots occupied"),Inventory->TryAdd(Wood,97));
    TestFalse(TEXT("Reject entire transfer if only part fits"),Inventory->TryAdd(Wood,2));
    TestEqual(TEXT("Rejected transfer did not partially add"),Inventory->GetSlotView()[1].Quantity,98);
    auto Pickup=[&](UInventoryItemDefinition* Item,int32 Count,FVector Location)
    {
        FTransform T(FRotator::ZeroRotator,Location);
        auto* P=World->SpawnActorDeferred<AInventoryPickup>(AInventoryPickup::StaticClass(),T);
        P->Item=Item; P->Quantity=Count; P->FinishSpawning(T); return P;
    };
    AInventoryPickup* Full=Pickup(Other,1,FVector(100,0,1000));
    TestFalse(TEXT("Full pickup stays in world"),IInteractable::Execute_Interact(Full,Pawn));
    TestTrue(TEXT("Rejected pickup still valid"),IsValid(Full));
    TestEqual(TEXT("Rejected world quantity intact"),Full->Quantity,1);
    Full->Destroy();
    AInventoryPickup* Take=Pickup(Wood,1,FVector(100,0,1000));
    Take->SetActorLocation(FVector(600,0,1000));
    TestFalse(TEXT("Out of range cannot take"),IInteractable::Execute_Interact(Take,Pawn));
    Take->SetActorLocation(FVector(100,0,1000));
    AStaticMeshActor* Wall=World->SpawnActor<AStaticMeshActor>(FVector(50,0,1000),FRotator::ZeroRotator);
    Wall->GetStaticMeshComponent()->SetStaticMesh(Wood->WorldMesh);
    Wall->SetActorScale3D(FVector(.2,1,3)); Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    TestFalse(TEXT("Blocked visibility cannot take"),IInteractable::Execute_Interact(Take,Pawn));
    Wall->Destroy();
    TestTrue(TEXT("Existing interaction discovers pickup"),Interaction->FindBestTarget()==Take);
    TestTrue(TEXT("Take fills final space"),Interaction->TryInteract());
    TestFalse(TEXT("Taken world actor destroyed"),IsValid(Take));
    TestEqual(TEXT("Final stack has 99"),Inventory->GetSlotView()[1].Quantity,99);
    TestFalse(TEXT("Missing floor cannot lose item"),Inventory->DropOne(0));
    TestEqual(TEXT("Failed drop preserves count"),Inventory->GetSlotView()[0].Quantity,99);
    AStaticMeshActor* Ground=World->SpawnActor<AStaticMeshActor>(FVector(0,0,850),FRotator::ZeroRotator);
    Ground->GetStaticMeshComponent()->SetStaticMesh(Wood->WorldMesh);
    Ground->SetActorScale3D(FVector(20,20,1)); Ground->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    Wall=World->SpawnActor<AStaticMeshActor>(FVector(65,0,1000),FRotator::ZeroRotator);
    Wall->GetStaticMeshComponent()->SetStaticMesh(Wood->WorldMesh);
    Wall->SetActorScale3D(FVector(.2,1,3)); Wall->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
    TestFalse(TEXT("Cannot drop through a wall"),Inventory->DropOne(0)); Wall->Destroy();
    TestTrue(TEXT("Drop one onto clear floor"),Inventory->DropOne(0));
    TestEqual(TEXT("Exactly one removed"),Inventory->GetSlotView()[0].Quantity,98);
    AInventoryPickup* Dropped=nullptr;
    for(TActorIterator<AInventoryPickup> It(World);It;++It) if(IsValid(*It)) Dropped=*It;
    TestNotNull(TEXT("Dropped actor exists"),Dropped);
    if(Dropped)
    {
        TestEqual(TEXT("Dropped quantity one"),Dropped->Quantity,1);
        TestTrue(TEXT("Same definition used"),Dropped->Item==Wood);
        TestTrue(TEXT("Can pick dropped item back up"),IInteractable::Execute_Interact(Dropped,Pawn));
        TestEqual(TEXT("Round trip conserves quantity"),Inventory->GetSlotView()[0].Quantity,99);
    }
    TestFalse(TEXT("Invalid index rejected"),Inventory->DropOne(-1));
    // Free a slot occupied by a singleton, then use that slot again.
    Pawn->SetActorRotation(FRotator(0,90,0));
    TestTrue(TEXT("Drop singleton"),Inventory->DropOne(19));
    TestEqual(TEXT("Empty stack frees slot"),Inventory->GetSlotView().Num(),19);
    TestTrue(TEXT("Freed slot can be reused"),Inventory->TryAdd(Wood,1));
    Other->MaxStack=0;
    TestFalse(TEXT("Invalid stack size rejected"),Inventory->CanAdd(Other,1));
    GEngine->DestroyWorldContext(World); World->DestroyWorld(false);
    return true;
}

namespace InventoryTests
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


class FCheckInventory : public IAutomationLatentCommand
{
public:
    explicit FCheckInventory(FAutomationTestBase* InTest):Test(InTest) {}
    virtual bool Update() override
    {
        double Now=FPlatformTime::Seconds();
        if(Deadline==0) Deadline=Now+25;
        if(Now<Next) return false;
        if(Step==0)
        {
            UWorld* World=GEditor ? GEditor->PlayWorld.Get() : nullptr;
            PC=World ? World->GetFirstPlayerController() : nullptr;
            Pawn=PC.IsValid() ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
            if((!Pawn.IsValid() || World->GetTimeSeconds()<.5f) && Now<Deadline) return false;
            if(!Test->TestTrue(TEXT("Inventory map has player"),Pawn.IsValid())) return true;
            Inventory=Pawn->FindComponentByClass<UInventoryComponent>();
            UI=PC->FindComponentByClass<UInventoryUIComponent>();
            for(TActorIterator<AInventoryPickup> It(World);It;++It)
                if(It->ActorHasTag(TEXT("InventoryTestPickup"))) { Target=*It; break; }
            if(!Test->TestTrue(TEXT("Saved map has configured pickup and inventory UI"),Inventory.IsValid() && UI.IsValid() && Target.IsValid() && Target->Item)) return true;
            Test->TestEqual(TEXT("Fresh session begins empty"),Inventory->GetSlotView().Num(),0);
            Pawn->SetActorLocation(FVector(0,0,100)); Pawn->SetActorRotation(FRotator::ZeroRotator);
            Pawn->GetCharacterMovement()->StopMovementImmediately();
            Item=Target->Item; InitialQuantity=Target->Quantity;
            Target->SetActorLocation(FVector(130,0,20));
            // Other samples must not win the nearest-target query.
            for(TActorIterator<AInventoryPickup> It(World);It;++It)
                if(*It!=Target.Get()) It->SetActorLocation(FVector(1000,1000,30));
            Key(EKeys::E,IE_Pressed); Advance(Now,.25); return false;
        }
        if(!Pawn.IsValid() || !PC.IsValid() || !Inventory.IsValid() || !UI.IsValid())
        { Test->AddError(TEXT("Inventory PIE fixture lost")); return true; }
        switch(Step)
        {
        case 1:
            Test->TestFalse(TEXT("E consumes saved pickup"),Target.IsValid());
            if(!Test->TestEqual(TEXT("Picked stack exists"),Inventory->GetSlotView().Num(),1)) return true;
            Test->TestEqual(TEXT("Correct quantity transferred"),Inventory->GetSlotView()[0].Quantity,InitialQuantity);
            Advance(Now,.2); break;
        case 2:
            Test->TestEqual(TEXT("Holding E cannot duplicate"),Inventory->GetSlotView()[0].Quantity,InitialQuantity);
            Key(EKeys::E,IE_Released); Key(EKeys::I,IE_Pressed); Advance(Now,.2); break;
        case 3:
            Key(EKeys::I,IE_Released);
            if(!Test->TestTrue(TEXT("I opens visible inventory"),UI->IsPanelOpen() && UI->GetPanel() && UI->GetPanel()->IsInViewport())) return true;
            Test->TestTrue(TEXT("Menu owns movement, camera and cursor"),PC->IsMoveInputIgnored() && PC->IsLookInputIgnored() && PC->bShowMouseCursor);
            UI->GetPanel()->SelectSlot(0);
            Start=Pawn->GetActorLocation(); Key(EKeys::W,IE_Pressed); Key(EKeys::E,IE_Pressed); Advance(Now,.3); break;
        case 4:
            FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("InteractionDev/inventory_panel.png"),true,false);
            Advance(Now,.2); break;
        case 5:
            Test->TestTrue(TEXT("Menu blocks movement"),Pawn->GetActorLocation().Equals(Start,3));
            Test->TestEqual(TEXT("Menu blocks interaction"),Inventory->GetSlotView()[0].Quantity,InitialQuantity);
            Key(EKeys::W,IE_Released); Key(EKeys::E,IE_Released);
            if(UButton* Button=Cast<UButton>(UI->GetPanel()->WidgetTree->FindWidget(TEXT("InventoryDropOne")))) Button->OnClicked.Broadcast();
            else Test->AddError(TEXT("Drop button missing"));
            Test->TestEqual(TEXT("Real drop button removes one"),Inventory->GetSlotView()[0].Quantity,InitialQuantity-1);
            for(TActorIterator<AInventoryPickup> It(Pawn->GetWorld());It;++It) if(It->Quantity==1 && It->Item==Item.Get()) Dropped=*It;
            Test->TestTrue(TEXT("Button creates world pickup"),Dropped.IsValid());
            { FKeyEvent Event(EKeys::Escape,FModifierKeysState(),0,false,0,0); Test->TestTrue(TEXT("Focused Slate widget handles close"),FSlateApplication::Get().ProcessKeyDownEvent(Event)); FSlateApplication::Get().ProcessKeyUpEvent(Event); }
            Test->TestFalse(TEXT("Escape closes inventory"),UI->IsPanelOpen());
            Test->TestFalse(TEXT("Input locks released"),PC->IsMoveInputIgnored() || PC->IsLookInputIgnored() || PC->bShowMouseCursor);
            Advance(Now,.15); break;
        case 6:
            Key(EKeys::E,IE_Pressed); Advance(Now,.25); break;
        case 7:
            Key(EKeys::E,IE_Released);
            Test->TestFalse(TEXT("E picks up dropped object"),Dropped.IsValid());
            Test->TestEqual(TEXT("UI drop and re-pickup conserve quantity"),Inventory->GetSlotView()[0].Quantity,InitialQuantity);
            // Fill inventory, then verify the complete failed pickup and visible feedback.
            Test->TestTrue(TEXT("Fill capacity"),Inventory->TryAdd(Item.Get(),20*Item->MaxStack-InitialQuantity));
            { FTransform T(FRotator::ZeroRotator,Pawn->GetActorLocation()+FVector(125,0,-70));
              AInventoryPickup* P=Pawn->GetWorld()->SpawnActorDeferred<AInventoryPickup>(AInventoryPickup::StaticClass(),T);
              P->Item=Item.Get(); P->FinishSpawning(T); Target=P; }
            Advance(Now,.15); break;
        case 8:
            Key(EKeys::E,IE_Pressed); Advance(Now,.25); break;
        case 9:
            Key(EKeys::E,IE_Released);
            Test->TestTrue(TEXT("Full inventory leaves item in world"),Target.IsValid() && Target->Quantity==1);
            if(auto* Message=Pawn->FindComponentByClass<UPrototypeMessageComponent>())
                Test->TestTrue(TEXT("Inventory full feedback visible"),Message->IsMessageVisible() && Message->GetCurrentMessage().ToString().Contains(TEXT("Inventar voll")));
            else Test->AddError(TEXT("Prototype feedback component missing"));
            Key(EKeys::I,IE_Pressed); Advance(Now,.15); break;
        case 10:
            Key(EKeys::I,IE_Released);
            Test->TestTrue(TEXT("Can reopen after drop"),UI->IsPanelOpen());
            { FKeyEvent Event(EKeys::I,FModifierKeysState(),0,false,0,0); Test->TestTrue(TEXT("Focused Slate widget handles close"),FSlateApplication::Get().ProcessKeyDownEvent(Event)); FSlateApplication::Get().ProcessKeyUpEvent(Event); }
            Test->TestFalse(TEXT("I closes inventory"),UI->IsPanelOpen());
            Key(EKeys::W,IE_Pressed); Start=Pawn->GetActorLocation(); Advance(Now,.3); break;
        case 11:
            Key(EKeys::W,IE_Released);
            Test->TestTrue(TEXT("Movement works after closing"),FVector::Dist2D(Start,Pawn->GetActorLocation())>10);
            WalkSpeed=Pawn->GetCharacterMovement()->MaxWalkSpeed;
            Key(EKeys::LeftShift,IE_Pressed); Advance(Now,.15); break;
        case 12:
            Test->TestEqual(TEXT("Toolbox sprint works before inventory"),Pawn->GetCharacterMovement()->MaxWalkSpeed,WalkSpeed*2);
            UI->TogglePanel(); Start=Pawn->GetActorLocation();
            Key(EKeys::LeftShift,IE_Released); Key(EKeys::W,IE_Pressed); Advance(Now,.2); break;
        case 13:
            Test->TestEqual(TEXT("Inventory restores ordinary sprint speed"),Pawn->GetCharacterMovement()->MaxWalkSpeed,WalkSpeed);
            Test->TestTrue(TEXT("Sprint cannot move player in menu"),Pawn->GetActorLocation().Equals(Start,3));
            UI->ClosePanel(); Key(EKeys::W,IE_Released); Advance(Now,.15); break;
        case 14:
            Test->TestEqual(TEXT("Released Shift does not stick after closing"),Pawn->GetCharacterMovement()->MaxWalkSpeed,WalkSpeed);
            Tools=PC->FindComponentByClass<UDeveloperToolboxComponent>();
            if(!Test->TestTrue(TEXT("Prototype toolbox available"),Tools.IsValid() && Tools->CanUse())) return true;
            Tools->SetFlight(true); Key(EKeys::W,IE_Pressed); Advance(Now,.15); break;
        case 15:
            UI->TogglePanel(); Start=Pawn->GetActorLocation(); Key(EKeys::W,IE_Released);
            Advance(Now,.2); break;
        case 16:
            Test->TestTrue(TEXT("Flight stays still while inventory owns input"),UI->IsPanelOpen() && Pawn->GetActorLocation().Equals(Start,3));
            Tools->TogglePanel(); Test->TestFalse(TEXT("Toolbox cannot steal inventory focus"),Tools->IsPanelOpen());
            UI->ClosePanel(); Advance(Now,.2); break;
        case 17:
            Test->TestTrue(TEXT("Released flight input does not stick after menu"),Pawn->GetActorLocation().Equals(Start,3));
            Tools->SetFlight(false);
            PC->SetIgnoreMoveInput(true); UI->TogglePanel();
            Test->TestFalse(TEXT("Existing external input lock prevents opening"),UI->IsPanelOpen());
            Test->TestTrue(TEXT("Existing input lock preserved"),PC->IsMoveInputIgnored());
            PC->SetIgnoreMoveInput(false);
            Tools->TogglePanel(); UI->TogglePanel();
            Test->TestFalse(TEXT("Inventory cannot steal toolbox focus"),UI->IsPanelOpen());
            Tools->ClosePanel(); UI->TogglePanel(); // Test teardown with an open menu.
            return true;
        }
        return false;
    }
private:
    void Key(FKey Key,EInputEvent Event) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,Event,Event==IE_Released?0.f:1.f)); }
    void Advance(double Now,double Delay) { ++Step; Next=Now+Delay; }
    FAutomationTestBase* Test; int32 Step=0,InitialQuantity=0; double Next=0,Deadline=0; float WalkSpeed=0; FVector Start;
    TWeakObjectPtr<APlayerController> PC; TWeakObjectPtr<ACharacter> Pawn;
    TWeakObjectPtr<UInventoryComponent> Inventory; TWeakObjectPtr<UInventoryUIComponent> UI;
    TWeakObjectPtr<UDeveloperToolboxComponent> Tools;
    TWeakObjectPtr<UInventoryItemDefinition> Item; TWeakObjectPtr<AInventoryPickup> Target,Dropped;
};
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FInventoryPIE,"FantasyLifeRPG.Inventory.PlayablePIE",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FInventoryPIE::RunTest(const FString& Parameters)
{
    AddCommand(new InventoryTests::FEndPIE(this));
    AddCommand(new FEditorLoadMap(TEXT("/Game/Prototype/Maps/Lvl_InventoryTest_01")));
    AddCommand(new InventoryTests::FStartPIE());
    AddCommand(new InventoryTests::FCheckInventory(this));
    AddCommand(new InventoryTests::FEndPIE(this)); return true;
}
#endif
