#include "Interaction/InteractionComponent.h"
#include "Interaction/Interactable.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "CollisionQueryParams.h"
#include "Engine/OverlapResult.h"

UInteractionComponent::UInteractionComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool UInteractionComponent::IsInteractionValid(AActor* Interactor, AActor* Target)
{
	if (!IsValid(Interactor) || !IsValid(Target) || Interactor == Target
		|| !Interactor->GetWorld() || Interactor->GetWorld() != Target->GetWorld()
		|| !Target->Implements<UInteractable>())
	{
		return false;
	}

	const float Range = IInteractable::Execute_GetInteractionRange(Target);
	const FVector Point = IInteractable::Execute_GetInteractionPoint(Target);
	if (!FMath::IsFinite(Range) || Range <= 0.0f || Point.ContainsNaN()
		|| FVector::DistSquared(Interactor->GetActorLocation(), Point) > FMath::Square(Range)
		|| !IInteractable::Execute_CanInteract(Target, Interactor))
	{
		return false;
	}

	const APawn* Pawn = Cast<APawn>(Interactor);
	const FVector SightOrigin = Pawn ? Pawn->GetPawnViewLocation() : Interactor->GetActorLocation();
	FCollisionQueryParams Query(SCENE_QUERY_STAT(InteractionVisibility), false, Interactor);
	FHitResult Hit;
	const bool bBlocked = Interactor->GetWorld()->LineTraceSingleByChannel(Hit, SightOrigin, Point, ECC_Visibility, Query);
	return !bBlocked || Hit.GetActor() == Target;
}

AActor* UInteractionComponent::FindBestTarget() const
{
	AActor* Interactor = GetOwner();
	if (!IsValid(Interactor) || !GetWorld() || !FMath::IsFinite(SearchRadius) || SearchRadius <= 0.0f)
	{
		return nullptr;
	}

	FCollisionObjectQueryParams Objects;
	Objects.AddObjectTypesToQuery(ECC_WorldStatic);
	Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
	Objects.AddObjectTypesToQuery(ECC_Pawn);
	FCollisionQueryParams Query(SCENE_QUERY_STAT(InteractionSearch), false, Interactor);
	TArray<FOverlapResult> Overlaps;
	GetWorld()->OverlapMultiByObjectType(Overlaps, Interactor->GetActorLocation(), FQuat::Identity,
		Objects, FCollisionShape::MakeSphere(SearchRadius), Query);

	AActor* Best = nullptr;
	double BestDistance = TNumericLimits<double>::Max();
	TSet<AActor*> Visited;
	for (const FOverlapResult& Overlap : Overlaps)
	{
		AActor* Candidate = Overlap.GetActor();
		if (!Candidate || Visited.Contains(Candidate)) continue;
		Visited.Add(Candidate);
		if (!IsInteractionValid(Interactor, Candidate)) continue;
		const double Distance = FVector::DistSquared(Interactor->GetActorLocation(),
			IInteractable::Execute_GetInteractionPoint(Candidate));
		if (Distance < BestDistance || (Distance == BestDistance && Best && Candidate->GetPathName() < Best->GetPathName()))
		{
			Best = Candidate;
			BestDistance = Distance;
		}
	}
	return Best;
}

bool UInteractionComponent::TryInteract()
{
	if (!IsValid(GetOwner()) || !GetOwner()->HasAuthority()) return false;
	AActor* Target = FindBestTarget();
	// Recheck immediately before execution. Never store a stale target across frames.
	return IsInteractionValid(GetOwner(), Target) && IInteractable::Execute_Interact(Target, GetOwner());
}
