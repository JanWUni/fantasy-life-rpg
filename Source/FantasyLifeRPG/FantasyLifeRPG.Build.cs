// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class FantasyLifeRPG : ModuleRules
{
	public FantasyLifeRPG(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"FantasyLifeRPG",
			"FantasyLifeRPG/Variant_Platforming",
			"FantasyLifeRPG/Variant_Platforming/Animation",
			"FantasyLifeRPG/Variant_Combat",
			"FantasyLifeRPG/Variant_Combat/AI",
			"FantasyLifeRPG/Variant_Combat/Animation",
			"FantasyLifeRPG/Variant_Combat/Gameplay",
			"FantasyLifeRPG/Variant_Combat/Interfaces",
			"FantasyLifeRPG/Variant_Combat/UI",
			"FantasyLifeRPG/Variant_SideScrolling",
			"FantasyLifeRPG/Variant_SideScrolling/AI",
			"FantasyLifeRPG/Variant_SideScrolling/Gameplay",
			"FantasyLifeRPG/Variant_SideScrolling/Interfaces",
			"FantasyLifeRPG/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
