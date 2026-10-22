#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "DeveloperEffectTester.generated.h"

class UNiagaraSystem;
class UNiagaraComponent;

USTRUCT(BlueprintType)
struct FDeveloperEffectEntry
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FText Label;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) TSoftObjectPtr<UNiagaraSystem> System;
};

/** Local, bounded VFX test service; does not implement gameplay effects. */
UCLASS(BlueprintType)
class FANTASYLIFERPG_API UDeveloperEffectTester : public UObject
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category="Development") bool Trigger(int32 Index, bool bAtPlayer);
	UFUNCTION(BlueprintCallable, Category="Development") void StopAll();
	int32 GetActiveCount() const;
	void Cleanup();
private:
	UPROPERTY(Transient) TArray<TWeakObjectPtr<UNiagaraComponent>> Spawned;
};
