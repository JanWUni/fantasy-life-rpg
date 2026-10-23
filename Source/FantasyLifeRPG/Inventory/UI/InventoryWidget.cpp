#include "Inventory/UI/InventoryWidget.h"
#include "Inventory/UI/InventoryUIComponent.h"
#include "Inventory/InventoryComponent.h"
#include "Inventory/InventoryItemDefinition.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ScrollBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "InputCoreTypes.h"

void UInventorySlotButton::Setup(UInventoryWidget* InPanel, int32 InIndex)
{
	Panel = InPanel; Index = InIndex;
	OnClicked.AddDynamic(this, &UInventorySlotButton::Select);
}
void UInventorySlotButton::Select() { if (Panel.IsValid()) Panel->SelectSlot(Index); }

void UInventoryWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	SetIsFocusable(true);
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Root;
	UBorder* Background = WidgetTree->ConstructWidget<UBorder>();
	Background->SetBrushColor(FLinearColor(.025f,.035f,.05f,.98f));
	Background->SetPadding(FMargin(22));
	UCanvasPanelSlot* Position = Root->AddChildToCanvas(Background);
	Position->SetAnchors(FAnchors(.5f)); Position->SetAlignment(FVector2D(.5f));
	Position->SetAutoSize(true);
	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(550); Size->SetHeightOverride(620); Background->SetContent(Size);
	UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(); Size->SetContent(Column);
	auto Text = [&](const FString& Caption, int32 FontSize)
	{
		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
		Label->SetText(FText::FromString(Caption));
		FSlateFontInfo Font = Label->GetFont(); Font.Size = FontSize; Label->SetFont(Font);
		Label->SetColorAndOpacity(FSlateColor(FLinearColor(.9f,.92f,.95f)));
		Label->SetAutoWrapText(true);
		Column->AddChildToVerticalBox(Label)->SetPadding(FMargin(0,0,0,10));
		return Label;
	};
	Text(TEXT("Inventar"),28);
	CapacityLabel = Text(TEXT("0 / 20 Plätze belegt"),16);
	Text(TEXT("Gegenstand wählen · I / Esc zum Schließen"),14);
	UScrollBox* List = WidgetTree->ConstructWidget<UScrollBox>(UScrollBox::StaticClass(),TEXT("InventoryList"));
	Column->AddChildToVerticalBox(List)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	// The model supports configurable capacities; rebuild rows when bound to the inventory.
	SelectionLabel = Text(TEXT("Kein Gegenstand ausgewählt."),16);
	DropButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),TEXT("InventoryDropOne"));
	UTextBlock* DropLabel = WidgetTree->ConstructWidget<UTextBlock>();
	DropLabel->SetText(FText::FromString(TEXT("1 Stück ablegen"))); DropButton->SetContent(DropLabel);
	Column->AddChildToVerticalBox(DropButton)->SetPadding(FMargin(0,4,0,10));
	DropButton->OnClicked.AddDynamic(this,&UInventoryWidget::Drop);
	StatusLabel = Text(TEXT("Lose Gegenstände lassen sich mit E aufheben."),14);
	UButton* CloseButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),TEXT("InventoryClose"));
	UTextBlock* CloseLabel = WidgetTree->ConstructWidget<UTextBlock>();
	CloseLabel->SetText(FText::FromString(TEXT("Schließen"))); CloseButton->SetContent(CloseLabel);
	Column->AddChildToVerticalBox(CloseButton);
	CloseButton->OnClicked.AddDynamic(this,&UInventoryWidget::Close);
}

void UInventoryWidget::InitializeInventory(UInventoryUIComponent* InUI)
{
	UI = InUI;
	SelectedSlot = INDEX_NONE;
	UInventoryComponent* Inventory = InUI ? InUI->GetInventory() : nullptr;
	UScrollBox* List = Cast<UScrollBox>(WidgetTree->FindWidget(TEXT("InventoryList")));
	if (!Inventory || !List) return;
	List->ClearChildren(); Rows.Reset(); Labels.Reset();
	for (int32 Index=0; Index<Inventory->GetCapacity(); ++Index)
	{
		UInventorySlotButton* Row = WidgetTree->ConstructWidget<UInventorySlotButton>();
		Row->Setup(this,Index); List->AddChild(Row); Rows.Add(Row);
		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
		FSlateFontInfo Font = Label->GetFont(); Font.Size = 16; Label->SetFont(Font);
		Label->SetMargin(FMargin(10,6)); Row->SetContent(Label); Labels.Add(Label);
	}
	ShowStatus(FText::FromString(TEXT("Lose Gegenstände lassen sich mit E aufheben.")));
	Refresh();
}

void UInventoryWidget::Refresh()
{
	const UInventoryComponent* Inventory = UI.IsValid() ? UI->GetInventory() : nullptr;
	if (!Inventory || !CapacityLabel) return;
	const TArray<FInventorySlot>& Slots = Inventory->GetSlotView();
	if (!Slots.IsValidIndex(SelectedSlot)) SelectedSlot = INDEX_NONE;
	CapacityLabel->SetText(FText::FromString(FString::Printf(TEXT("%d / %d Plätze belegt"),Slots.Num(),Inventory->GetCapacity())));
	for (int32 Index=0; Index<Rows.Num(); ++Index)
	{
		const bool bOccupied = Slots.IsValidIndex(Index);
		Labels[Index]->SetText(FText::FromString(bOccupied ? FString::Printf(TEXT("%02d   %s   × %d"),Index+1,
			*Slots[Index].Item->DisplayName.ToString(),Slots[Index].Quantity) : FString::Printf(TEXT("%02d   — leer —"),Index+1)));
		Rows[Index]->SetIsEnabled(bOccupied);
		Rows[Index]->SetBackgroundColor(Index==SelectedSlot ? FLinearColor(.2f,.5f,.55f) : FLinearColor(.13f,.16f,.2f));
	}
	DropButton->SetIsEnabled(SelectedSlot != INDEX_NONE);
	SelectionLabel->SetText(SelectedSlot == INDEX_NONE ? FText::FromString(TEXT("Kein Gegenstand ausgewählt."))
		: FText::Format(FText::FromString(TEXT("Ausgewählt: {0}")),Slots[SelectedSlot].Item->DisplayName));
}

void UInventoryWidget::SelectSlot(int32 Index) { SelectedSlot = Index; Refresh(); }
void UInventoryWidget::ShowStatus(const FText& Message) { if (StatusLabel) StatusLabel->SetText(Message); }
void UInventoryWidget::Drop() { if (UI.IsValid() && UI->GetInventory()) UI->GetInventory()->DropOne(SelectedSlot); }
void UInventoryWidget::Close() { if (UI.IsValid()) UI->ClosePanel(); }
FReply UInventoryWidget::NativeOnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (Event.GetKey()==EKeys::I || Event.GetKey()==EKeys::Escape)
	{
		if (!Event.IsRepeat()) Close();
		return FReply::Handled();
	}
	if (Event.GetKey()==EKeys::E || Event.GetKey()==EKeys::F6 || Event.GetKey()==EKeys::SpaceBar
		|| Event.GetKey()==EKeys::W || Event.GetKey()==EKeys::A || Event.GetKey()==EKeys::S || Event.GetKey()==EKeys::D)
		return FReply::Handled();
	return Super::NativeOnPreviewKeyDown(Geometry,Event);
}
