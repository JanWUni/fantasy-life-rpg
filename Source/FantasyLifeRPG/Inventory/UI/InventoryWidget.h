#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "InventoryWidget.generated.h"

class UInventoryUIComponent;
class UInventoryWidget;
class UTextBlock;

UCLASS()
class UInventorySlotButton : public UButton
{
	GENERATED_BODY()
public:
	void Setup(UInventoryWidget* InPanel, int32 InIndex);
private:
	UFUNCTION() void Select();
	TWeakObjectPtr<UInventoryWidget> Panel;
	int32 Index = INDEX_NONE;
};

/** Passive inventory view. All mutations are validated by the inventory component. */
UCLASS()
class FANTASYLIFERPG_API UInventoryWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeInventory(UInventoryUIComponent* InUI);
	void Refresh();
	void SelectSlot(int32 Index);
	int32 GetSelectedSlot() const { return SelectedSlot; }
	void ShowStatus(const FText& Message);
	virtual FReply NativeOnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
protected:
	virtual void NativeOnInitialized() override;
private:
	UFUNCTION() void Drop();
	UFUNCTION() void Close();
	UPROPERTY(Transient) TObjectPtr<UTextBlock> CapacityLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> SelectionLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> StatusLabel;
	UPROPERTY(Transient) TObjectPtr<UButton> DropButton;
	UPROPERTY(Transient) TArray<TObjectPtr<UInventorySlotButton>> Rows;
	UPROPERTY(Transient) TArray<TObjectPtr<UTextBlock>> Labels;
	TWeakObjectPtr<UInventoryUIComponent> UI;
	int32 SelectedSlot = INDEX_NONE;
};
