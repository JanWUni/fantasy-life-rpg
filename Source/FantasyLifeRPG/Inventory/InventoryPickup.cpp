#include "Inventory/InventoryPickup.h"
#include "Inventory/InventoryComponent.h"
#include "Inventory/InventoryItemDefinition.h"
#include "Interaction/InteractionComponent.h"
#include "Components/StaticMeshComponent.h"

#define LOCTEXT_NAMESPACE "InventoryPickup"

AInventoryPickup::AInventoryPickup()
{
	Mesh->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore);
	Mesh->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
}

void AInventoryPickup::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	Mesh->SetStaticMesh(Item ? Item->WorldMesh.Get() : nullptr);
	if (Item && Item->IsUsable()) Mesh->SetWorldScale3D(Item->WorldScale);
}

FText AInventoryPickup::GetInteractionText_Implementation() const
{
	return Item ? FText::Format(LOCTEXT("Take", "{0} aufheben"), Item->DisplayName) : FText::GetEmpty();
}

bool AInventoryPickup::CanInteract_Implementation(AActor* Interactor) const
{
	return Super::CanInteract_Implementation(Interactor) && !bTransferring && Quantity > 0
		&& IsValid(Item) && Item->IsUsable() && Interactor->FindComponentByClass<UInventoryComponent>();
}

bool AInventoryPickup::Interact_Implementation(AActor* Interactor)
{
	if (!HasAuthority() || !IsValid(Interactor) || !Interactor->HasAuthority()
		|| !UInteractionComponent::IsInteractionValid(Interactor, this)) return false;
	UInventoryComponent* Inventory = Interactor->FindComponentByClass<UInventoryComponent>();
	TGuardValue<bool> Guard(bTransferring, true);
	if (!Inventory || !Inventory->TryAdd(Item, Quantity)) return false;
	Quantity = 0;
	bInteractionEnabled = false;
	Destroy();
	return true;
}

#undef LOCTEXT_NAMESPACE
