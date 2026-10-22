#include "NPC/PrototypeLocomotionComponent.h"
#include "Animation/AnimSequenceBase.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"

UPrototypeLocomotionComponent::UPrototypeLocomotionComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = .1f;
}

void UPrototypeLocomotionComponent::TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* TickFunction)
{
	Super::TickComponent(Delta, TickType, TickFunction);
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	if (!Mesh) return;
	const float Speed = Character->GetVelocity().Size2D();
	const bool Walking = Speed > 5.f;
	UAnimSequenceBase* Animation = Walking ? WalkAnimation.Get() : IdleAnimation.Get();
	if (!Animation) return;
	UAnimSingleNodeInstance* Instance = Mesh->GetSingleNodeInstance();
	if (!Instance || Instance->GetCurrentAsset() != Animation) Mesh->PlayAnimation(Animation, true);
	Instance = Mesh->GetSingleNodeInstance();
	if (Instance) Instance->SetPlayRate(Walking ? FMath::Clamp(Speed / FMath::Max(1.f, WalkReferenceSpeed), .5f, 1.5f) : 1.f);
}
