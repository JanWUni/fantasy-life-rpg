#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DeveloperToolboxWidget.generated.h"

class UDeveloperToolboxComponent;
class UTextBlock;
class UButton;
class UComboBoxString;
class UVerticalBox;

/** UMG view only. The component/services own state and validate every operation. */
UCLASS()
class FANTASYLIFERPG_API UDeveloperToolboxWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeToolbox(UDeveloperToolboxComponent* Component);
	virtual FReply NativeOnPreviewKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
protected:
	virtual void NativeOnInitialized() override;
	virtual void NativeTick(const FGeometry& Geometry,float DeltaTime) override;
private:
	void BuildPanel();
	UButton* Button(UVerticalBox* Parent,const FString& Caption,FName Name);
	UTextBlock* Text(UVerticalBox* Parent,const FString& Caption,int32 Size=14);
	void Refresh();
	UFUNCTION() void Flight();
	UFUNCTION() void NoClip();
	UFUNCTION() void Camera();
	UFUNCTION() void FlightSpeed(float Value);
	UFUNCTION() void CameraSpeed(float Value);
	UFUNCTION() void TriggerEffect();
	UFUNCTION() void StopEffects();
	UFUNCTION() void StartScenario();
	UFUNCTION() void StopScenario();
	UFUNCTION() void Close();
	UFUNCTION() void Reset();
	UPROPERTY(Transient) TWeakObjectPtr<UDeveloperToolboxComponent> Tools;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> StatusLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> FlightLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> NoClipLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> CameraLabel;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> EffectCount;
	UPROPERTY(Transient) TObjectPtr<UTextBlock> ScenarioStatus;
	UPROPERTY(Transient) TObjectPtr<UComboBoxString> EffectList;
	UPROPERTY(Transient) TObjectPtr<UComboBoxString> EffectPosition;
	UPROPERTY(Transient) TObjectPtr<UComboBoxString> ScenarioList;
	UPROPERTY(Transient) TObjectPtr<UButton> EffectStart;
	UPROPERTY(Transient) TObjectPtr<UButton> ScenarioStart;
	UPROPERTY(Transient) TObjectPtr<UButton> ScenarioStop;
	float RefreshTime = 0.f;
};
