#include "Interaction/InteractionFeedbackComponent.h"
#include "Interaction/InteractionComponent.h"
#include "Interaction/Interactable.h"
#include "Interaction/UI/InteractionPromptWidget.h"
#include "Components/MeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"

UInteractionFeedbackComponent::UInteractionFeedbackComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
}

bool UInteractionFeedbackComponent::IsPromptVisible() const
{
	return FocusedTarget.IsValid() && IsValid(PromptWidget)
		&& PromptWidget->IsInViewport() && PromptWidget->IsVisible();
}

FText UInteractionFeedbackComponent::GetPromptText() const
{
	return IsPromptVisible() ? PromptWidget->GetPromptText() : FText::GetEmpty();
}

void UInteractionFeedbackComponent::TickComponent(float DeltaTime, ELevelTick TickType,
	FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	UInteractionComponent* Interaction = Pawn ? Pawn->FindComponentByClass<UInteractionComponent>() : nullptr;
	if (!Pawn || !Pawn->IsLocallyControlled() || !PC || !PC->GetLocalPlayer() || !Interaction)
	{
		ReleaseFeedback();
		return;
	}

	AActor* Target = Interaction->FindBestTarget();
	if (!IsValid(Target))
	{
		ClearHighlight();
		if (PromptWidget) PromptWidget->SetVisibility(ESlateVisibility::Collapsed);
		return;
	}

	SetFocusedTarget(Target);
	if (!IsValid(PromptWidget))
	{
		PromptWidget = CreateWidget<UInteractionPromptWidget>(PC, UInteractionPromptWidget::StaticClass());
		if (PromptWidget)
		{
			PromptWidget->SetIsFocusable(false);
			// SetDesiredSizeInViewport resets anchors in UE 5.8, so assign anchors last.
			PromptWidget->SetDesiredSizeInViewport(FVector2D(360.0f, 56.0f));
			PromptWidget->SetAlignmentInViewport(FVector2D(0.5f, 0.5f));
			PromptWidget->SetAnchorsInViewport(FAnchors(0.5f, 0.86f));
		}
	}
	if (PromptWidget)
	{
		PromptWidget->SetActionText(IInteractable::Execute_GetInteractionText(Target));
		if (!PromptWidget->IsInViewport()) PromptWidget->AddToPlayerScreen(20);
		PromptWidget->SetVisibility(ESlateVisibility::HitTestInvisible);
	}
}

void UInteractionFeedbackComponent::SetFocusedTarget(AActor* Target)
{
	if (FocusedTarget.Get() == Target) return;
	ClearHighlight();
	FocusedTarget = Target;
	if (!HighlightMaterial) return;

	TInlineComponentArray<UMeshComponent*> Meshes(Target);
	for (UMeshComponent* Mesh : Meshes)
	{
		if (!IsValid(Mesh) || !Mesh->IsVisible()) continue;
		FInteractionMeshHighlight& Highlight = HighlightedMeshes.AddDefaulted_GetRef();
		Highlight.Mesh = Mesh;
		Highlight.PreviousOverlay = Mesh->GetOverlayMaterial();
		Highlight.PreviousDrawDistance = Mesh->GetOverlayMaterialMaxDrawDistance();
		Mesh->SetOverlayMaterial(HighlightMaterial);
		Mesh->SetOverlayMaterialMaxDrawDistance(0.0f);
		if (UStaticMeshComponent* StaticMesh = Cast<UStaticMeshComponent>(Mesh))
		{
			// The prototype's Nanite meshes do not render translucent overlays on the Nanite path.
			// Use the existing fallback geometry locally while selected; never edit the mesh asset.
			Highlight.bPreviousForceDisableNanite = StaticMesh->IsForceDisableNanite();
			StaticMesh->SetForceDisableNanite(true);
		}
	}
}

void UInteractionFeedbackComponent::ClearHighlight()
{
	for (const FInteractionMeshHighlight& Highlight : HighlightedMeshes)
	{
		UMeshComponent* Mesh = Highlight.Mesh.Get();
		// Do not overwrite an overlay that another system replaced while the object was focused.
		if (Mesh && Mesh->GetOverlayMaterial() == HighlightMaterial)
		{
			Mesh->SetOverlayMaterial(Highlight.PreviousOverlay);
			Mesh->SetOverlayMaterialMaxDrawDistance(Highlight.PreviousDrawDistance);
		}
		if (UStaticMeshComponent* StaticMesh = Cast<UStaticMeshComponent>(Mesh))
		{
			StaticMesh->SetForceDisableNanite(Highlight.bPreviousForceDisableNanite);
		}
	}
	HighlightedMeshes.Reset();
	FocusedTarget.Reset();
}

void UInteractionFeedbackComponent::ReleaseFeedback()
{
	ClearHighlight();
	if (PromptWidget)
	{
		PromptWidget->RemoveFromParent();
		PromptWidget = nullptr;
	}
}

void UInteractionFeedbackComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	ReleaseFeedback();
	Super::EndPlay(EndPlayReason);
}

void UInteractionFeedbackComponent::OnUnregister()
{
	ReleaseFeedback();
	Super::OnUnregister();
}
