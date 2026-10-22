#include "Prototype/PrototypeMessageComponent.h"
#include "Prototype/UI/PrototypeMessageWidget.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "TimerManager.h"

UPrototypeMessageComponent::UPrototypeMessageComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UPrototypeMessageComponent::ShowMessageTo(AActor* Recipient, const FText& Message)
{
	if (IsValid(Recipient))
	{
		if (UPrototypeMessageComponent* Component = Recipient->FindComponentByClass<UPrototypeMessageComponent>())
		{
			Component->ShowMessage(Message);
		}
	}
}

void UPrototypeMessageComponent::ShowMessage(const FText& Message)
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (!Pawn || !Pawn->IsLocallyControlled() || !PC || !PC->GetLocalPlayer() || Message.IsEmpty()) return;
	ClearMessage();
	Widget = CreateWidget<UPrototypeMessageWidget>(PC);
	if (!Widget) return;
	Widget->Message = Message;
	Widget->SetIsFocusable(false);
	Widget->SetDesiredSizeInViewport(FVector2D(760, 110));
	Widget->SetAlignmentInViewport(FVector2D(.5, .5));
	Widget->SetAnchorsInViewport(FAnchors(.5f, .69f));
	Widget->AddToPlayerScreen(30);
	Widget->SetVisibility(ESlateVisibility::HitTestInvisible);
	const float Duration = FMath::IsFinite(DisplaySeconds) ? FMath::Max(.1f, DisplaySeconds) : 6.0f;
	GetWorld()->GetTimerManager().SetTimer(MessageTimer, this, &UPrototypeMessageComponent::ClearMessage, Duration, false);
}

bool UPrototypeMessageComponent::IsMessageVisible() const
{
	return Widget && Widget->IsInViewport() && Widget->IsVisible();
}

FText UPrototypeMessageComponent::GetCurrentMessage() const { return Widget ? Widget->Message : FText::GetEmpty(); }

void UPrototypeMessageComponent::ClearMessage()
{
	if (GetWorld()) GetWorld()->GetTimerManager().ClearTimer(MessageTimer);
	if (Widget) Widget->RemoveFromParent();
	Widget = nullptr;
}

void UPrototypeMessageComponent::EndPlay(const EEndPlayReason::Type Reason)
{
	ClearMessage();
	Super::EndPlay(Reason);
}
