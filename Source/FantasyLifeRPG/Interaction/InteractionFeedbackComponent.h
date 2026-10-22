#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InteractionFeedbackComponent.generated.h"

class UMaterialInterface;
class UMeshComponent;
class UInteractionPromptWidget;

USTRUCT()
struct FInteractionMeshHighlight
{
	GENERATED_BODY()

	UPROPERTY()
	TWeakObjectPtr<UMeshComponent> Mesh;

	UPROPERTY()
	TObjectPtr<UMaterialInterface> PreviousOverlay;

	UPROPERTY()
	float PreviousDrawDistance = 0.0f;

	UPROPERTY()
	bool bPreviousForceDisableNanite = false;
};

/** Local presentation only; attach alongside UInteractionComponent on the player pawn. */
UCLASS(ClassGroup=(Interaction), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UInteractionFeedbackComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UInteractionFeedbackComponent();

	/** Translucent overlay, configured in the prototype Blueprint. Base materials remain intact. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Interaction|Feedback")
	TObjectPtr<UMaterialInterface> HighlightMaterial;

	UFUNCTION(BlueprintPure, Category="Interaction|Feedback")
	AActor* GetFocusedTarget() const { return FocusedTarget.Get(); }

	UFUNCTION(BlueprintPure, Category="Interaction|Feedback")
	bool IsPromptVisible() const;
	FText GetPromptText() const;

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void OnUnregister() override;

private:
	void SetFocusedTarget(AActor* Target);
	void ClearHighlight();
	void ReleaseFeedback();

	UPROPERTY(Transient)
	TObjectPtr<UInteractionPromptWidget> PromptWidget;

	UPROPERTY(Transient)
	TWeakObjectPtr<AActor> FocusedTarget;

	UPROPERTY(Transient)
	TArray<FInteractionMeshHighlight> HighlightedMeshes;
};
