#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "PrototypeMessageWidget.generated.h"

/** Passive local message; no dialogue state or input handling. */
UCLASS()
class FANTASYLIFERPG_API UPrototypeMessageWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	FText Message;
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
};
