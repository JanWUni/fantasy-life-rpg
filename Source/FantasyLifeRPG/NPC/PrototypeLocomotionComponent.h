#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PrototypeLocomotionComponent.generated.h"

class UAnimSequenceBase;

/** Optional placeholder presentation driven solely by owner velocity. No navigation dependency. */
UCLASS(ClassGroup=(Prototype), meta=(BlueprintSpawnableComponent))
class FANTASYLIFERPG_API UPrototypeLocomotionComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UPrototypeLocomotionComponent();
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Animation")
	TObjectPtr<UAnimSequenceBase> IdleAnimation;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Animation")
	TObjectPtr<UAnimSequenceBase> WalkAnimation;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Animation", meta=(ClampMin="1"))
	float WalkReferenceSpeed = 150.f;
protected:
	virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
};
