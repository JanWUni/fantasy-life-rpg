// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "FantasyLifeRPGGameMode.generated.h"

/**
 *  Simple GameMode for a third person game
 */
UCLASS(abstract)
class AFantasyLifeRPGGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:

	/** Constructor */
	AFantasyLifeRPGGameMode();
};
