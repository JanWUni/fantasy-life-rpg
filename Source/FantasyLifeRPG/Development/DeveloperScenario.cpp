#include "Development/DeveloperScenario.h"
#include "Development/DeveloperToolboxComponent.h"
#include "NPC/WaypointMovementComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"

namespace
{
	TArray<UWaypointMovementComponent*> FindRoutes(UWorld* World)
	{
		TArray<UWaypointMovementComponent*> Routes;
		if (World && !World->bIsTearingDown)
			for (TActorIterator<AActor> It(World); It; ++It)
				if (UWaypointMovementComponent* Route = It->FindComponentByClass<UWaypointMovementComponent>())
					if (It->HasAuthority() && Route->Waypoints.Num() > 0) Routes.Add(Route);
		return Routes;
	}
}
UWorld* UDeveloperScenario::GetWorld() const { return GetOuter() ? GetOuter()->GetWorld() : nullptr; }
FText UDeveloperScenario::GetTitle() const { return NSLOCTEXT("DeveloperToolbox","Scenario","Testszenario"); }
bool UDeveloperScenario::IsAvailable() const
{
	const UDeveloperToolboxComponent* Tools = GetTypedOuter<UDeveloperToolboxComponent>();
	return Tools && Tools->CanUse() && CanRun();
}
bool UDeveloperScenario::Start() { return IsAvailable() && OnStart(); }
bool UDeveloperScenario::Stop() { return IsAvailable() && OnStop(); }
bool UDeveloperScenario::CanRun_Implementation() const { return false; }
bool UDeveloperScenario::OnStart_Implementation() { return false; }
bool UDeveloperScenario::OnStop_Implementation() { return false; }
FText UDeveloperNPCRouteScenario::GetTitle() const { return NSLOCTEXT("DeveloperToolbox","Routes","Vorhandene NPC-Routen"); }
bool UDeveloperNPCRouteScenario::CanRun_Implementation() const { return !FindRoutes(GetWorld()).IsEmpty(); }
void UDeveloperNPCRouteScenario::Remember(UWaypointMovementComponent* Route)
{
	if (!Previous.Contains(Route)) Previous.Add(Route,Route->GetRouteState() != EWaypointMovementState::Stopped);
}
bool UDeveloperNPCRouteScenario::OnStart_Implementation()
{
	for (UWaypointMovementComponent* Route : FindRoutes(GetWorld())) { Remember(Route); Route->StartRoute(); }
	return true;
}
bool UDeveloperNPCRouteScenario::OnStop_Implementation()
{
	for (UWaypointMovementComponent* Route : FindRoutes(GetWorld())) { Remember(Route); Route->StopRoute(); }
	return true;
}
void UDeveloperNPCRouteScenario::Cleanup()
{
	if (GetWorld() && !GetWorld()->bIsTearingDown)
		for (const auto& Pair : Previous)
			if (Pair.Key.IsValid() && Pair.Key->GetOwner()->HasAuthority())
			{
				if (Pair.Value) Pair.Key->StartRoute(); else Pair.Key->StopRoute();
			}
	Previous.Empty();
}
