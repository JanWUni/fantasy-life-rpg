#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "Interactable.generated.h"

UINTERFACE(BlueprintType, Blueprintable)
class FANTASYLIFERPG_API UInteractable : public UInterface
{
	GENERATED_BODY()
};

/** Actor contract; no dependency on the player, inventory, dialogue or UI. */
class FANTASYLIFERPG_API IInteractable
{
	GENERATED_BODY()

public:
	/** Action only, without an input key. An empty result uses the UI's generic fallback. */
	UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category="Interaction")
	FText GetInteractionText() const;

	UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category="Interaction")
	FVector GetInteractionPoint() const;

	/** Distance in centimetres from the interactor's actor origin to the interaction point. */
	UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category="Interaction")
	float GetInteractionRange() const;

	UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category="Interaction")
	bool CanInteract(AActor* Interactor) const;

	/** Called after validation, on authority only. Return whether the action was accepted. */
	UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category="Interaction")
	bool Interact(AActor* Interactor);
};
