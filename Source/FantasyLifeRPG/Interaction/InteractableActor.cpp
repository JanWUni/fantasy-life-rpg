#include "Interaction/InteractableActor.h"
#include "Interaction/InteractionComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"

AInteractableActor::AInteractableActor()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	SetRootComponent(Mesh);
	Mesh->SetMobility(EComponentMobility::Movable);
	Mesh->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	InteractionPoint = CreateDefaultSubobject<USceneComponent>(TEXT("InteractionPoint"));
	InteractionPoint->SetupAttachment(Mesh);
}

FVector AInteractableActor::GetInteractionPoint_Implementation() const
{
	return InteractionPoint->GetComponentLocation();
}

FText AInteractableActor::GetInteractionText_Implementation() const { return InteractionAction; }

float AInteractableActor::GetInteractionRange_Implementation() const
{
	return InteractionRange;
}

bool AInteractableActor::CanInteract_Implementation(AActor* Interactor) const
{
	return bInteractionEnabled && IsValid(Interactor) && Interactor != this;
}

bool AInteractableActor::Interact_Implementation(AActor* Interactor)
{
	if (!HasAuthority() || !UInteractionComponent::IsInteractionValid(Interactor, this)) return false;
	OnInteracted(Interactor);
	return true;
}
