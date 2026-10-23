#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InventoryUIComponent.generated.h"

class APlayerController;
class APawn;
class UInventoryComponent;
class UInventoryWidget;
class UInputMappingContext;
class UEnhancedInputComponent;

/** Local keyboard/mouse view with scoped input ownership; no inventory state lives here. */
UCLASS(ClassGroup=(Inventory), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UInventoryUIComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UInventoryUIComponent();
	UFUNCTION(BlueprintCallable, Category="Inventory") void TogglePanel();
	UFUNCTION(BlueprintCallable, Category="Inventory") void ClosePanel();
	UFUNCTION(BlueprintPure, Category="Inventory") bool IsPanelOpen() const { return bPanelOpen; }
	UInventoryComponent* GetInventory() const;
	UInventoryWidget* GetPanel() const { return Panel; }
protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	UFUNCTION() void PawnChanged(APawn* Previous, APawn* Current);
	UFUNCTION() void Changed();
	UFUNCTION() void Notice(const FText& Message);
	TWeakObjectPtr<APlayerController> PC;
	TWeakObjectPtr<UInventoryComponent> BoundInventory;
	UPROPERTY(Transient) TObjectPtr<UInventoryWidget> Panel;
	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> InputContext;
	UPROPERTY(Transient) TObjectPtr<UEnhancedInputComponent> InventoryInput;
	bool bPanelOpen = false;
	bool bPreviousCursor = false;
};
