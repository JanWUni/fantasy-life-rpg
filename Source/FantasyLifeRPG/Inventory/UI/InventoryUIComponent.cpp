#include "Inventory/UI/InventoryUIComponent.h"
#include "Inventory/UI/InventoryWidget.h"
#include "Inventory/InventoryComponent.h"
#include "Prototype/PrototypeMessageComponent.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"

UInventoryUIComponent::UInventoryUIComponent() { PrimaryComponentTick.bCanEverTick = false; }

void UInventoryUIComponent::BeginPlay()
{
	Super::BeginPlay();
	PC = Cast<APlayerController>(GetOwner());
	if (!PC.IsValid() || !PC->IsLocalPlayerController() || !PC->GetLocalPlayer()) return;
	PC->OnPossessedPawnChanged.AddDynamic(this,&UInventoryUIComponent::PawnChanged);
	PawnChanged(nullptr,PC->GetPawn());
	UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer());
	if (!Subsystem) return;
	InputContext = NewObject<UInputMappingContext>(this);
	UInputAction* Toggle = NewObject<UInputAction>(InputContext,TEXT("InventoryToggle"));
	Toggle->ValueType = EInputActionValueType::Boolean;
	InputContext->MapKey(Toggle,EKeys::I);
	InventoryInput = NewObject<UEnhancedInputComponent>(GetOwner(),TEXT("InventoryInput"));
	InventoryInput->Priority = 200;
	InventoryInput->RegisterComponent(); PC->PushInputComponent(InventoryInput);
	InventoryInput->BindAction(Toggle,ETriggerEvent::Started,this,&UInventoryUIComponent::TogglePanel);
	FModifyContextOptions Options; Options.bIgnoreAllPressedKeysUntilRelease = false; Options.bForceImmediately = true;
	Subsystem->AddMappingContext(InputContext,90,Options);
}

UInventoryComponent* UInventoryUIComponent::GetInventory() const
{
	return PC.IsValid() && PC->GetPawn() ? PC->GetPawn()->FindComponentByClass<UInventoryComponent>() : nullptr;
}

void UInventoryUIComponent::PawnChanged(APawn* Previous, APawn* Current)
{
	ClosePanel();
	if (BoundInventory.IsValid())
	{
		BoundInventory->OnChanged.RemoveDynamic(this,&UInventoryUIComponent::Changed);
		BoundInventory->OnNotice.RemoveDynamic(this,&UInventoryUIComponent::Notice);
	}
	BoundInventory = GetInventory();
	if (BoundInventory.IsValid())
	{
		BoundInventory->OnChanged.AddDynamic(this,&UInventoryUIComponent::Changed);
		BoundInventory->OnNotice.AddDynamic(this,&UInventoryUIComponent::Notice);
	}
}

void UInventoryUIComponent::Changed() { if (bPanelOpen && Panel) Panel->Refresh(); }
void UInventoryUIComponent::Notice(const FText& Message)
{
	if (bPanelOpen && Panel) Panel->ShowStatus(Message);
	else if (PC.IsValid()) UPrototypeMessageComponent::ShowMessageTo(PC->GetPawn(),Message);
}

void UInventoryUIComponent::TogglePanel()
{
	if (bPanelOpen) { ClosePanel(); return; }
	// An existing UI/tool owns focus; it must release its input locks first.
	if (!PC.IsValid() || !PC->IsLocalPlayerController() || !GetInventory() || !InventoryInput
		|| PC->IsMoveInputIgnored() || PC->IsLookInputIgnored()) return;
	if (!Panel) Panel = CreateWidget<UInventoryWidget>(PC.Get());
	if (!Panel) return;
	Panel->InitializeInventory(this);
	bPanelOpen = true;
	bPreviousCursor = PC->bShowMouseCursor;
	PC->SetIgnoreMoveInput(true); PC->SetIgnoreLookInput(true);
	if (ACharacter* Character = Cast<ACharacter>(PC->GetPawn()))
	{
		Character->StopJumping(); Character->GetCharacterMovement()->StopMovementImmediately();
	}
	InventoryInput->bBlockInput = true;
	if (PC->PlayerInput) PC->PlayerInput->FlushPressedKeys();
	Panel->AddToPlayerScreen(500);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode; Mode.SetWidgetToFocus(Panel->TakeWidget());
	Mode.SetHideCursorDuringCapture(false); Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode); Panel->SetKeyboardFocus();
}

void UInventoryUIComponent::ClosePanel()
{
	if (!bPanelOpen) return;
	bPanelOpen = false;
	if (Panel) Panel->RemoveFromParent();
	if (InventoryInput) InventoryInput->bBlockInput = false;
	if (PC.IsValid())
	{
		PC->SetIgnoreMoveInput(false); PC->SetIgnoreLookInput(false);
		PC->bShowMouseCursor = bPreviousCursor;
		PC->SetInputMode(FInputModeGameOnly());
		if (PC->PlayerInput) PC->PlayerInput->FlushPressedKeys();
		UWidgetBlueprintLibrary::SetFocusToGameViewport();
	}
}

void UInventoryUIComponent::EndPlay(const EEndPlayReason::Type Reason)
{
	ClosePanel();
	if (BoundInventory.IsValid())
	{
		BoundInventory->OnChanged.RemoveDynamic(this,&UInventoryUIComponent::Changed);
		BoundInventory->OnNotice.RemoveDynamic(this,&UInventoryUIComponent::Notice);
	}
	if (PC.IsValid())
	{
		PC->OnPossessedPawnChanged.RemoveDynamic(this,&UInventoryUIComponent::PawnChanged);
		if (InventoryInput) PC->PopInputComponent(InventoryInput);
		if (PC->GetLocalPlayer())
			if (auto* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
				if (InputContext) Subsystem->RemoveMappingContext(InputContext);
	}
	if (InventoryInput) InventoryInput->DestroyComponent();
	InventoryInput = nullptr; InputContext = nullptr; Panel = nullptr;
	Super::EndPlay(Reason);
}
