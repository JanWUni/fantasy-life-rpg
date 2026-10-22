#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Interaction/Interactable.h"
#include "PrototypeNPC.generated.h"

/** Interaction fixture. Optional movement and appearance are separate components/Blueprints. */
UCLASS(Blueprintable)
class FANTASYLIFERPG_API APrototypeNPC : public ACharacter, public IInteractable
{
	GENERATED_BODY()
public:
	APrototypeNPC();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="0", Units="cm"))
	float InteractionRange = 230.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	bool bInteractionEnabled = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	bool bFaceInteractor = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	FVector InteractionPointOffset = FVector(0, 0, 35);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Prototype")
	FText Greeting;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
	FText InteractionAction;

	virtual FText GetInteractionText_Implementation() const override;
	virtual FVector GetInteractionPoint_Implementation() const override;
	virtual float GetInteractionRange_Implementation() const override;
	virtual bool CanInteract_Implementation(AActor* Interactor) const override;
	virtual bool Interact_Implementation(AActor* Interactor) override;

	/** Runs only after the common authority, range and visibility checks. */
	UFUNCTION(BlueprintImplementableEvent, Category="Interaction")
	void OnSpokenTo(AActor* Interactor);
};
