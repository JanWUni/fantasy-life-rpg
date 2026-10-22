#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PrototypeMessageComponent.generated.h"

class UPrototypeMessageWidget;

/** Local player's replaceable presentation endpoint; deliberately separate from NPC gameplay. */
UCLASS(ClassGroup=(Prototype), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UPrototypeMessageComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UPrototypeMessageComponent();
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Prototype", meta=(ClampMin="0.1"))
	float DisplaySeconds = 6.0f;
	/** Blueprint glue finds the recipient's existing presentation component. No network transport. */
	UFUNCTION(BlueprintCallable, Category="Prototype")
	static void ShowMessageTo(AActor* Recipient, const FText& Message);
	UFUNCTION(BlueprintPure, Category="Prototype")
	bool IsMessageVisible() const;
	FText GetCurrentMessage() const;
protected:
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	void ShowMessage(const FText& Message);
	void ClearMessage();
	UPROPERTY(Transient)
	TObjectPtr<UPrototypeMessageWidget> Widget;
	FTimerHandle MessageTimer;
};
