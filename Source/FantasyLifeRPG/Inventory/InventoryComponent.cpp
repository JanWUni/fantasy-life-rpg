#include "Inventory/InventoryComponent.h"
#include "Inventory/InventoryItemDefinition.h"
#include "Inventory/InventoryPickup.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"

#define LOCTEXT_NAMESPACE "Inventory"

UInventoryComponent::UInventoryComponent() { PrimaryComponentTick.bCanEverTick = false; }

bool UInventoryComponent::CanAdd(UInventoryItemDefinition* Item, int32 Quantity) const
{
	if (!IsValid(Item) || !Item->IsUsable() || Quantity <= 0) return false;
	int64 Space = int64(FMath::Max(0, GetCapacity() - Slots.Num())) * Item->MaxStack;
	for (const FInventorySlot& Slot : Slots)
		if (Slot.Item == Item) Space += FMath::Max(0, Item->MaxStack - Slot.Quantity);
	return Space >= Quantity;
}

bool UInventoryComponent::TryAdd(UInventoryItemDefinition* Item, int32 Quantity)
{
	if (!GetOwner() || !GetOwner()->HasAuthority() || bMutating || !IsValid(Item) || !Item->IsUsable() || Quantity <= 0) return false;
	TGuardValue<bool> Guard(bMutating, true);
	if (!CanAdd(Item, Quantity))
	{
		OnNotice.Broadcast(LOCTEXT("Full", "Inventar voll – nicht genug Platz für diesen Gegenstand."));
		return false;
	}
	int32 Remaining = Quantity;
	for (FInventorySlot& Slot : Slots)
	{
		if (Slot.Item != Item) continue;
		const int32 Added = FMath::Min(Remaining, FMath::Max(0, Item->MaxStack - Slot.Quantity));
		Slot.Quantity += Added;
		Remaining -= Added;
	}
	while (Remaining > 0)
	{
		FInventorySlot& Slot = Slots.AddDefaulted_GetRef();
		Slot.Item = Item;
		Slot.Quantity = FMath::Min(Remaining, Item->MaxStack);
		Remaining -= Slot.Quantity;
	}
	OnChanged.Broadcast();
	return true;
}

bool UInventoryComponent::DropOne(int32 SlotIndex)
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	UWorld* World = GetWorld();
	if (!Pawn || !Pawn->HasAuthority() || !World || World->bIsTearingDown || bMutating || !Slots.IsValidIndex(SlotIndex)) return false;
	UInventoryItemDefinition* Item = Slots[SlotIndex].Item;
	if (!IsValid(Item) || !Item->IsUsable() || Slots[SlotIndex].Quantity <= 0) return false;
	TGuardValue<bool> Guard(bMutating, true);
	const FVector Extent = Item->WorldMesh->GetBoundingBox().GetExtent() * Item->WorldScale;
	const FVector BoundsOffset = Item->WorldMesh->GetBoundingBox().GetCenter() * Item->WorldScale;
	const FVector Forward = Pawn->GetActorForwardVector().GetSafeNormal2D();
	const FVector Ahead = Pawn->GetActorLocation() + Forward * (110.f + Extent.GetMax());
	FCollisionQueryParams Params(SCENE_QUERY_STAT(InventoryDrop), false, Pawn);
	FCollisionObjectQueryParams Objects;
	Objects.AddObjectTypesToQuery(ECC_WorldStatic);
	Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
	Objects.AddObjectTypesToQuery(ECC_Pawn);
	FHitResult Floor;
	const bool bFloor = World->LineTraceSingleByObjectType(Floor, Ahead + FVector(0,0,80), Ahead - FVector(0,0,350), Objects, Params);
	const FVector Center = Floor.ImpactPoint + FVector(0,0,Extent.Z + 3.f);
	FHitResult Path;
	const bool bBlocked = !bFloor || Floor.ImpactNormal.Z < .7f
		|| World->SweepSingleByObjectType(Path, Pawn->GetActorLocation(), Center, FQuat::Identity,
			Objects, FCollisionShape::MakeBox(Extent + FVector(1)), Params)
		|| World->OverlapAnyTestByObjectType(Center, FQuat::Identity, Objects,
			FCollisionShape::MakeBox(Extent + FVector(1)), Params);
	if (bBlocked)
	{
		OnNotice.Broadcast(LOCTEXT("DropBlocked", "Hier ist kein freier Platz zum Ablegen. Geh etwas weiter."));
		return false;
	}
	const FTransform Transform(FRotator::ZeroRotator, Center - BoundsOffset);
	AInventoryPickup* Pickup = World->SpawnActorDeferred<AInventoryPickup>(AInventoryPickup::StaticClass(), Transform,
		nullptr, nullptr, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Pickup) return false;
	Pickup->Item = Item;
	Pickup->Quantity = 1;
	Pickup->FinishSpawning(Transform);
	if (!IsValid(Pickup)) return false;
	if (--Slots[SlotIndex].Quantity == 0) Slots.RemoveAt(SlotIndex);
	OnChanged.Broadcast();
	OnNotice.Broadcast(FText::Format(LOCTEXT("Dropped", "1 × {0} abgelegt."), Item->DisplayName));
	return true;
}

#undef LOCTEXT_NAMESPACE
