#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "InteractionPromptWidget.generated.h"

class STextBlock;

/** Small, passive prompt. Gameplay and target acquisition stay outside the widget. */
UCLASS()
class FANTASYLIFERPG_API UInteractionPromptWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void SetActionText(const FText& Action);
	FText GetPromptText() const { return PromptText; }
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void ReleaseSlateResources(bool bReleaseChildren) override;
private:
	FText ActionText;
	FText PromptText;
	TSharedPtr<STextBlock> Label;
};
