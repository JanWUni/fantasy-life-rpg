#pragma once

#include "CoreMinimal.h"
#include "Components/SkeletalMeshComponent.h"
#include "CrouchPoseMeshComponent.generated.h"

/** Temporary mannequin leg IK until authored crouch locomotion clips are available. */
UCLASS()
class UCrouchPoseMeshComponent : public USkeletalMeshComponent
{
	GENERATED_BODY()
public:
	virtual void FinalizeBoneTransform() override;
};
