#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InventoryComponent.generated.h"

class UInventoryItemDefinition;
class AInventoryPickup;

USTRUCT(BlueprintType)
struct FInventorySlot
{
	GENERATED_BODY()
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Inventory")
	TObjectPtr<UInventoryItemDefinition> Item;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Inventory")
	int32 Quantity = 0;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FInventoryChanged);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FInventoryNotice, const FText&, Message);

/** Session-only storage. Mutations require authority; no client RPC or replication yet. */
UCLASS(ClassGroup=(Inventory), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UInventoryComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UInventoryComponent();
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Inventory", meta=(ClampMin="1", ClampMax="200"))
	int32 SlotCapacity = 20;
	UPROPERTY(BlueprintAssignable, Category="Inventory") FInventoryChanged OnChanged;
	UPROPERTY(BlueprintAssignable, Category="Inventory") FInventoryNotice OnNotice;

	UFUNCTION(BlueprintPure, Category="Inventory") bool CanAdd(UInventoryItemDefinition* Item, int32 Quantity) const;
	/** Atomic: either the complete quantity fits, or both inventory and world stay unchanged. */
	UFUNCTION(BlueprintCallable, Category="Inventory") bool TryAdd(UInventoryItemDefinition* Item, int32 Quantity);
	/** Creates a grounded, collision-checked pickup before removing one unit. */
	UFUNCTION(BlueprintCallable, Category="Inventory") bool DropOne(int32 SlotIndex);
	UFUNCTION(BlueprintPure, Category="Inventory") TArray<FInventorySlot> GetSlots() const { return Slots; }
	const TArray<FInventorySlot>& GetSlotView() const { return Slots; }
	UFUNCTION(BlueprintPure, Category="Inventory") int32 GetCapacity() const { return FMath::Clamp(SlotCapacity, 1, 200); }

private:
	UPROPERTY(Transient) TArray<FInventorySlot> Slots;
	bool bMutating = false;
};
