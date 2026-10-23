#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "InventoryItemDefinition.generated.h"

class UStaticMesh;

/** One shared asset per item type. Runtime quantities belong to inventory slots/pickups. */
UCLASS(BlueprintType)
class FANTASYLIFERPG_API UInventoryItemDefinition : public UDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Item")
	FText DisplayName;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Item", meta=(ClampMin="1"))
	int32 MaxStack = 99;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Item")
	TObjectPtr<UStaticMesh> WorldMesh;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Item")
	FVector WorldScale = FVector(0.25);

	bool IsUsable() const;
};
