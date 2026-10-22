#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "DeveloperScenario.generated.h"

class UWaypointMovementComponent;

/** Add a small adapter for an existing test function, not a simulation framework. */
UCLASS(Abstract, Blueprintable)
class FANTASYLIFERPG_API UDeveloperScenario : public UObject
{
	GENERATED_BODY()
public:
	virtual UWorld* GetWorld() const override;
	UFUNCTION(BlueprintPure, Category="Development") virtual FText GetTitle() const;
	UFUNCTION(BlueprintPure, Category="Development") bool IsAvailable() const;
	UFUNCTION(BlueprintCallable, Category="Development") bool Start();
	UFUNCTION(BlueprintCallable, Category="Development") bool Stop();
	virtual void Cleanup() {}
protected:
	UFUNCTION(BlueprintNativeEvent, Category="Development") bool CanRun() const;
	UFUNCTION(BlueprintNativeEvent, Category="Development") bool OnStart();
	UFUNCTION(BlueprintNativeEvent, Category="Development") bool OnStop();
};

/** Adapter to the existing route component. No NPC spawning or new AI. */
UCLASS()
class FANTASYLIFERPG_API UDeveloperNPCRouteScenario : public UDeveloperScenario
{
	GENERATED_BODY()
public:
	virtual FText GetTitle() const override;
	virtual void Cleanup() override;
protected:
	virtual bool CanRun_Implementation() const override;
	virtual bool OnStart_Implementation() override;
	virtual bool OnStop_Implementation() override;
private:
	void Remember(UWaypointMovementComponent* Route);
	TMap<TWeakObjectPtr<UWaypointMovementComponent>, bool> Previous;
};
