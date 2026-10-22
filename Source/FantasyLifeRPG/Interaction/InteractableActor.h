#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/Interactable.h"
#include "InteractableActor.generated.h"

class UStaticMeshComponent;
class USceneComponent;

/** Optional convenience base for simple props. NPCs can implement IInteractable directly. */
UCLASS(Blueprintable)
class FANTASYLIFERPG_API AInteractableActor : public AActor, public IInteractable
{
	GENERATED_BODY()

public:
	AInteractableActor();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Interaction")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Interaction")
	TObjectPtr<USceneComponent> InteractionPoint;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="0.0", Units="cm"))
	float InteractionRange = 200.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	bool bInteractionEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	FText InteractionAction;

	virtual FText GetInteractionText_Implementation() const override;
	virtual FVector GetInteractionPoint_Implementation() const override;
	virtual float GetInteractionRange_Implementation() const override;
	virtual bool CanInteract_Implementation(AActor* Interactor) const override;
	virtual bool Interact_Implementation(AActor* Interactor) override;

	/** Implement the prop's state change here; the base checks authority/range/visibility first. */
	UFUNCTION(BlueprintImplementableEvent, Category="Interaction")
	void OnInteracted(AActor* Interactor);
};
