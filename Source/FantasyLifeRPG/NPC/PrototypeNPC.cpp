#include "NPC/PrototypeNPC.h"
#include "Interaction/InteractionComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

APrototypeNPC::APrototypeNPC()
{
	PrimaryActorTick.bCanEverTick = false;
	bReplicates = false;
	AutoPossessAI = EAutoPossessAI::Disabled;
	GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);
	GetMesh()->SetRelativeLocationAndRotation(FVector(0, 0, -96), FRotator(0, -90, 0));
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetCharacterMovement()->SetMovementMode(MOVE_None);
	GetCharacterMovement()->DefaultLandMovementMode = MOVE_None;
	bUseControllerRotationYaw = false;
	Greeting = NSLOCTEXT("PrototypeNPC", "Greeting", "Hallo, Reisender! Willkommen in unserer Testwelt.");
	InteractionAction = NSLOCTEXT("PrototypeNPC", "Speak", "Sprechen");
}

FText APrototypeNPC::GetInteractionText_Implementation() const { return InteractionAction; }

FVector APrototypeNPC::GetInteractionPoint_Implementation() const
{
	return GetActorLocation() + InteractionPointOffset;
}

float APrototypeNPC::GetInteractionRange_Implementation() const { return InteractionRange; }

bool APrototypeNPC::CanInteract_Implementation(AActor* Interactor) const
{
	return bInteractionEnabled && IsValid(Interactor) && Interactor != this;
}

bool APrototypeNPC::Interact_Implementation(AActor* Interactor)
{
	if (!HasAuthority() || !UInteractionComponent::IsInteractionValid(Interactor, this)) return false;
	// Blueprint glue can pause an optional route before the facing update.
	OnSpokenTo(Interactor);
	const FVector Direction = Interactor->GetActorLocation() - GetActorLocation();
	if (bFaceInteractor && !Direction.IsNearlyZero(0.1f) && Direction.SizeSquared2D() > 0.01f)
	{
		SetActorRotation(FRotator(0, Direction.Rotation().Yaw, 0));
	}
	return true;
}
