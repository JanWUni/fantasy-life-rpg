#include "CrouchPoseMeshComponent.h"
#include "FantasyLifeRPGCharacter.h"
#include "Engine/SkeletalMesh.h"
#include "TwoBoneIK.h"

void UCrouchPoseMeshComponent::FinalizeBoneTransform()
{
	// Finalize runs after parallel animation evaluation and before the render buffer
	// is published. Do not modify animation assets or the graph's local pose buffer.
	const auto* Character = Cast<AFantasyLifeRPGCharacter>(GetOwner());
	const float Drop = Character ? Character->GetCrouchPresentationAlpha() * Character->GetCrouchPresentationDrop() : 0.f;
	TArray<FTransform>& Pose = GetEditableComponentSpaceTransforms();
	if (Drop > KINDA_SMALL_NUMBER && GetSkeletalMeshAsset() && !IsSimulatingPhysics())
	{
		const FReferenceSkeleton& Skeleton = GetSkeletalMeshAsset()->GetRefSkeleton();
		const int32 Pelvis = GetBoneIndex(TEXT("pelvis"));
		const int32 Thighs[] = {GetBoneIndex(TEXT("thigh_l")), GetBoneIndex(TEXT("thigh_r"))};
		const int32 Calves[] = {GetBoneIndex(TEXT("calf_l")), GetBoneIndex(TEXT("calf_r"))};
		const int32 Feet[] = {GetBoneIndex(TEXT("foot_l")), GetBoneIndex(TEXT("foot_r"))};
		bool bValid = Pose.IsValidIndex(Pelvis) && Pose.Num() == Skeleton.GetNum();
		for (int32 Side = 0; Side < 2; ++Side)
			bValid &= Pose.IsValidIndex(Thighs[Side]) && Pose.IsValidIndex(Calves[Side]) && Pose.IsValidIndex(Feet[Side]);
		if (bValid)
		{
			const TArray<FTransform> Original = Pose;
			TArray<FTransform> Local;
			Local.SetNumUninitialized(Pose.Num());
			for (int32 Bone = 0; Bone < Pose.Num(); ++Bone)
			{
				const int32 Parent = Skeleton.GetParentIndex(Bone);
				Local[Bone] = Parent != INDEX_NONE ? Original[Bone].GetRelativeTransform(Original[Parent]) : Original[Bone];
			}
			const FVector Forward = GetComponentTransform().InverseTransformVectorNoScale(Character->GetActorForwardVector());
			const FVector HipOffset = (FVector::DownVector - Forward * .5f) * Drop;
			const int32 HipParent = Skeleton.GetParentIndex(Pelvis);
			Local[Pelvis].AddToTranslation(HipParent != INDEX_NONE ? Original[HipParent].InverseTransformVector(HipOffset) : HipOffset);
			for (int32 Bone = 0; Bone < Pose.Num(); ++Bone)
			{
				const int32 Parent = Skeleton.GetParentIndex(Bone);
				Pose[Bone] = Parent != INDEX_NONE ? Local[Bone] * Pose[Parent] : Local[Bone];
			}
			for (int32 Side = 0; Side < 2; ++Side)
			{
				FTransform Thigh = Pose[Thighs[Side]], Calf = Pose[Calves[Side]], Foot = Pose[Feet[Side]];
				AnimationCore::SolveTwoBoneIK(Thigh, Calf, Foot, Thigh.GetLocation() + Forward * 100.f, Original[Feet[Side]].GetLocation(), false, 1., 1.);
				Foot.SetRotation(Original[Feet[Side]].GetRotation());
				Pose[Thighs[Side]] = Thigh;
				Pose[Calves[Side]] = Calf;
				Pose[Feet[Side]] = Foot;
			}
			// Update twist bones, toes and other descendants from their original local
			// transforms, preserving the solved hip/knee/ankle chain itself.
			for (int32 Bone = 1; Bone < Pose.Num(); ++Bone)
			{
				if (Bone == Thighs[0] || Bone == Thighs[1] || Bone == Calves[0] || Bone == Calves[1] || Bone == Feet[0] || Bone == Feet[1]) continue;
				Pose[Bone] = Local[Bone] * Pose[Skeleton.GetParentIndex(Bone)];
			}
		}
	}
	Super::FinalizeBoneTransform();
}
