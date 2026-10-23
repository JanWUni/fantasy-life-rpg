#include "Inventory/InventoryItemDefinition.h"
#include "Engine/StaticMesh.h"

bool UInventoryItemDefinition::IsUsable() const
{
	return !DisplayName.IsEmpty() && MaxStack > 0 && IsValid(WorldMesh)
		&& !WorldScale.ContainsNaN() && WorldScale.GetMin() > 0;
}
