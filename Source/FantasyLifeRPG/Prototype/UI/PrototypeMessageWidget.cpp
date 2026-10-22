#include "Prototype/UI/PrototypeMessageWidget.h"
#include "Styling/CoreStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"

TSharedRef<SWidget> UPrototypeMessageWidget::RebuildWidget()
{
	return SNew(SBorder)
		.BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
		.BorderBackgroundColor(FLinearColor(.015f, .022f, .02f, .95f))
		.Padding(FMargin(24, 16))
		.HAlign(HAlign_Center).VAlign(VAlign_Center)
		[
			SNew(STextBlock).Text(Message).AutoWrapText(true)
			.Font(FCoreStyle::GetDefaultFontStyle("Regular", 22))
			.ColorAndOpacity(FLinearColor(1, .92f, .74f))
		];
}
