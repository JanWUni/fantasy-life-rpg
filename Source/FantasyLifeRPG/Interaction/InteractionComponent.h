#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InteractionComponent.generated.h"

/** On-demand discovery and validation. Attach to any pawn; input stays with the pawn. */
UCLASS(ClassGroup=(Interaction), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UInteractionComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UInteractionComponent();

	/** Broad-phase radius only. Each target still controls its own usable distance. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="1.0", Units="cm"))
	float SearchRadius = 1000.0f;

	UFUNCTION(BlueprintCallable, Category="Interaction")
	AActor* FindBestTarget() const;

	/** Future RPC boundary: clients currently cannot modify gameplay state. */
	UFUNCTION(BlueprintCallable, Category="Interaction")
	bool TryInteract();

	/** Shared validation, also usable by an authoritative interaction implementation. */
	static bool IsInteractionValid(AActor* Interactor, AActor* Target);
};
