#include "Interaction/UI/InteractionPromptWidget.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"

void UInteractionPromptWidget::SetActionText(const FText& Action)
{
	const FText Effective = Action.IsEmpty() ? NSLOCTEXT("Interaction", "DefaultAction", "Interagieren") : Action;
	if (!PromptText.IsEmpty() && ActionText.EqualTo(Effective)) return;
	ActionText = Effective;
	PromptText = FText::Format(NSLOCTEXT("Interaction", "ActionPrompt", "E \u2013 {0}"), ActionText);
	if (Label) Label->SetText(PromptText);
}

void UInteractionPromptWidget::ReleaseSlateResources(bool bReleaseChildren)
{
	Super::ReleaseSlateResources(bReleaseChildren);
	Label.Reset();
}

TSharedRef<SWidget> UInteractionPromptWidget::RebuildWidget()
{
	return SNew(SBorder)
		.HAlign(HAlign_Center)
		.VAlign(VAlign_Center)
		.BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
		.BorderBackgroundColor(FLinearColor(0.015f, 0.02f, 0.03f, 0.9f))
		.Padding(FMargin(20.0f, 12.0f))
		[
			SAssignNew(Label, STextBlock)
			.Text(PromptText)
			.Font(FCoreStyle::GetDefaultFontStyle("Bold", 22))
			.ColorAndOpacity(FLinearColor(1.0f, 0.88f, 0.55f))
		];
}
