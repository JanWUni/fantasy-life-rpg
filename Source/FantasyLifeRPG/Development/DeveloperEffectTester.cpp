#include "Development/DeveloperEffectTester.h"
#include "Development/DeveloperToolboxComponent.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"

bool UDeveloperEffectTester::Trigger(int32 Index, bool bAtPlayer)
{
	UDeveloperToolboxComponent* Tools = GetTypedOuter<UDeveloperToolboxComponent>();
	if (!Tools || !Tools->CanUse() || !Tools->Effects.IsValidIndex(Index)) return false;
	APlayerController* PC = Cast<APlayerController>(Tools->GetOwner());
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	if (!Pawn) return false;
	UNiagaraSystem* System = Tools->Effects[Index].System.LoadSynchronous();
	if (!System) { Tools->Report(NSLOCTEXT("DeveloperToolbox","EffectMissing","Effekt-Asset nicht verfügbar.")); return false; }
	FVector Location = Pawn->GetActorLocation();
	if (!bAtPlayer)
	{
		FVector Camera; FRotator Rotation; PC->GetPlayerViewPoint(Camera,Rotation);
		FCollisionQueryParams Query(SCENE_QUERY_STAT(ToolboxEffect),false,Pawn);
		FHitResult Hit;
		if (Tools->GetWorld()->LineTraceSingleByChannel(Hit,Camera,Camera + Rotation.Vector()*2000.f,ECC_Visibility,Query))
			Location = Hit.ImpactPoint + Hit.ImpactNormal*10.f;
		else
		{
			Location += FRotator(0,Rotation.Yaw,0).Vector()*300.f;
			if (Tools->GetWorld()->LineTraceSingleByChannel(Hit,Location+FVector(0,0,200),Location-FVector(0,0,1500),ECC_Visibility,Query))
				Location = Hit.ImpactPoint+FVector(0,0,10);
		}
	}
	Spawned.RemoveAll([](const auto& Component) { return !Component.IsValid() || !Component->IsActive(); });
	// Bounded test scope, including indefinitely looping systems.
	if (Spawned.Num() >= 8) { Spawned[0]->DestroyComponent(); Spawned.RemoveAt(0); }
	UNiagaraComponent* Effect = UNiagaraFunctionLibrary::SpawnSystemAtLocation(Tools->GetWorld(),System,Location,FRotator::ZeroRotator,FVector::OneVector,true,true,ENCPoolMethod::None,false);
	if (!Effect) return false;
	Spawned.Add(Effect);
	Tools->Report(FText::Format(NSLOCTEXT("DeveloperToolbox","EffectStarted","Testeffekt ausgelöst: {0}"),Tools->Effects[Index].Label));
	return true;
}

int32 UDeveloperEffectTester::GetActiveCount() const
{
	return Spawned.FilterByPredicate([](const auto& Component) { return Component.IsValid() && Component->IsActive(); }).Num();
}
void UDeveloperEffectTester::StopAll()
{
	const UDeveloperToolboxComponent* Tools = GetTypedOuter<UDeveloperToolboxComponent>();
	if (Tools && Tools->CanUse()) Cleanup();
}
void UDeveloperEffectTester::Cleanup()
{
	for (const auto& Component : Spawned)
		if (UNiagaraComponent* Instance = Component.Get())
		{
			// DeactivateImmediate can synchronously auto-destroy the component and invalidate its weak pointer.
			Instance->SetAutoDestroy(false);
			Instance->DeactivateImmediate();
			if (IsValid(Instance)) Instance->DestroyComponent();
		}
	Spawned.Empty();
}
