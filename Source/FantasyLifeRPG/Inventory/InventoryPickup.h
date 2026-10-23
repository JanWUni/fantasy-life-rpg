#pragma once

#include "CoreMinimal.h"
#include "Interaction/InteractableActor.h"
#include "InventoryPickup.generated.h"

class UInventoryItemDefinition;

UCLASS(Blueprintable)
class FANTASYLIFERPG_API AInventoryPickup : public AInteractableActor
{
	GENERATED_BODY()
public:
	AInventoryPickup();
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Pickup") TObjectPtr<UInventoryItemDefinition> Item;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Pickup", meta=(ClampMin="1")) int32 Quantity = 1;
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual FText GetInteractionText_Implementation() const override;
	virtual bool CanInteract_Implementation(AActor* Interactor) const override;
	virtual bool Interact_Implementation(AActor* Interactor) override;
private:
	bool bTransferring = false;
};
