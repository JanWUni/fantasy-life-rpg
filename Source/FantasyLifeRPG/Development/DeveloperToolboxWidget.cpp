#include "Development/DeveloperToolboxWidget.h"
#include "Development/DeveloperToolboxComponent.h"
#include "Development/DeveloperScenario.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ComboBoxString.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/ScrollBox.h"
#include "Components/SpinBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Styling/CoreStyle.h"

void UDeveloperToolboxWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	SetIsFocusable(true);
	BuildPanel();
}

UTextBlock* UDeveloperToolboxWidget::Text(UVerticalBox* Parent,const FString& Caption,int32 Size)
{
	UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
	Label->SetText(FText::FromString(Caption));
	Label->SetFont(FCoreStyle::GetDefaultFontStyle(Size>=20 ? "Bold" : "Regular",Size));
	Label->SetColorAndOpacity(FLinearColor(.86f,.9f,.96f));
	Label->SetAutoWrapText(true);
	Parent->AddChildToVerticalBox(Label)->SetPadding(FMargin(0,4));
	return Label;
}

UButton* UDeveloperToolboxWidget::Button(UVerticalBox* Parent,const FString& Caption,FName Name)
{
	UButton* Result = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),Name);
	Result->SetBackgroundColor(FLinearColor(.12f,.26f,.38f));
	UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
	Label->SetText(FText::FromString(Caption));
	Label->SetFont(FCoreStyle::GetDefaultFontStyle("Bold",13));
	Label->SetColorAndOpacity(FLinearColor::White);
	Label->SetAutoWrapText(true);
	Label->SetMargin(FMargin(10,9));
	Result->AddChild(Label);
	Parent->AddChildToVerticalBox(Result)->SetPadding(FMargin(0,5));
	return Result;
}

void UDeveloperToolboxWidget::BuildPanel()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Root;
	UBorder* Backdrop = WidgetTree->ConstructWidget<UBorder>();
	Backdrop->SetBrushColor(FLinearColor(0,0,0,.45f));
	UCanvasPanelSlot* BackdropSlot = Root->AddChildToCanvas(Backdrop);
	BackdropSlot->SetAnchors(FAnchors(0,0,1,1)); BackdropSlot->SetOffsets(FMargin(0));
	UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
	Panel->SetBrushColor(FLinearColor(.018f,.027f,.045f,.98f));
	Panel->SetPadding(FMargin(20));
	UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
	PanelSlot->SetAnchors(FAnchors(.035f,.05f,.965f,.95f)); PanelSlot->SetOffsets(FMargin(0));
	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Panel->AddChild(Scroll);
	UVerticalBox* Main = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(Main);
	Text(Main,TEXT("DEVELOPER TOOLBOX"),24);
	Text(Main,TEXT("V1  /  LOKALER ENTWICKLUNGSMODUS     •     F6 oder ESC: schließen"),12);
	Text(Main,TEXT("Die Welt läuft weiter. Nach dem Schließen bleiben gewählte Werkzeuge aktiv."),13);
	UHorizontalBox* Columns = WidgetTree->ConstructWidget<UHorizontalBox>();
	Main->AddChildToVerticalBox(Columns)->SetPadding(FMargin(0,14));
	auto Card = [&](const FString& Title)
	{
		UBorder* Border = WidgetTree->ConstructWidget<UBorder>();
		Border->SetBrushColor(FLinearColor(.035f,.055f,.08f)); Border->SetPadding(FMargin(14));
		UHorizontalBoxSlot* Slot = Columns->AddChildToHorizontalBox(Border);
		Slot->SetSize(FSlateChildSize(ESlateSizeRule::Fill)); Slot->SetPadding(FMargin(4));
		UVerticalBox* Content = WidgetTree->ConstructWidget<UVerticalBox>(); Border->AddChild(Content);
		Text(Content,Title,20);
		return Content;
	};
	UVerticalBox* Player = Card(TEXT("Spieler"));
	UButton* FlightButton = Button(Player,TEXT("Flugmodus"),TEXT("FlightButton"));
	FlightLabel = Cast<UTextBlock>(FlightButton->GetChildAt(0));
	FlightButton->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::Flight);
	UButton* NoClipButton = Button(Player,TEXT("NoClip"),TEXT("NoClipButton"));
	NoClipLabel = Cast<UTextBlock>(NoClipButton->GetChildAt(0));
	NoClipButton->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::NoClip);
	Text(Player,TEXT("Flugtempo / cm pro Sekunde"),12);
	USpinBox* FlightSpin = WidgetTree->ConstructWidget<USpinBox>(USpinBox::StaticClass(),TEXT("FlightSpeed"));
	FlightSpin->SetMinValue(100); FlightSpin->SetMaxValue(5000); FlightSpin->SetDelta(100); FlightSpin->SetValue(900);
	Player->AddChildToVerticalBox(FlightSpin); FlightSpin->OnValueChanged.AddDynamic(this,&UDeveloperToolboxWidget::FlightSpeed);
	UButton* CameraButton = Button(Player,TEXT("Freie Kamera"),TEXT("CameraButton"));
	CameraLabel = Cast<UTextBlock>(CameraButton->GetChildAt(0));
	CameraButton->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::Camera);
	Text(Player,TEXT("Kameratempo / cm pro Sekunde"),12);
	USpinBox* CameraSpin = WidgetTree->ConstructWidget<USpinBox>(USpinBox::StaticClass(),TEXT("CameraSpeed"));
	CameraSpin->SetMinValue(100); CameraSpin->SetMaxValue(5000); CameraSpin->SetDelta(100); CameraSpin->SetValue(1200);
	Player->AddChildToVerticalBox(CameraSpin); CameraSpin->OnValueChanged.AddDynamic(this,&UDeveloperToolboxWidget::CameraSpeed);
	Text(Player,TEXT("WASD horizontal • Maus: Blick\nFlug/Kamera: Leertaste ↑, Strg ↓\nShift halten: Sprint 2×, Flug/Kamera 3×\nFlug/NoClip: Loslassen stoppt sofort\nNoClip allein: horizontal, ohne Schwerkraft"),12);

	UVerticalBox* VFX = Card(TEXT("Effekte"));
	Text(VFX,TEXT("Vorhandenes Niagara-Asset"),12);
	EffectList = WidgetTree->ConstructWidget<UComboBoxString>(UComboBoxString::StaticClass(),TEXT("EffectList"));
	VFX->AddChildToVerticalBox(EffectList);
	EffectPosition = WidgetTree->ConstructWidget<UComboBoxString>();
	EffectPosition->AddOption(TEXT("Am Spieler")); EffectPosition->AddOption(TEXT("Testposition vor Kamera")); EffectPosition->SetSelectedIndex(0);
	VFX->AddChildToVerticalBox(EffectPosition)->SetPadding(FMargin(0,8));
	EffectStart = Button(VFX,TEXT("Effekt auslösen"),TEXT("TriggerEffectButton"));
	EffectStart->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::TriggerEffect);
	Button(VFX,TEXT("Alle Testeffekte stoppen"),TEXT("StopEffectsButton"))->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::StopEffects);
	EffectCount = Text(VFX,TEXT("Keine Testeffekte aktiv"),12);
	Text(VFX,TEXT("Nur Toolbox-Effekte werden beendet. Maximal acht gleichzeitig; keine Gameplay-Wirkung."),12);

	UVerticalBox* Simulation = Card(TEXT("Simulationen"));
	ScenarioList = WidgetTree->ConstructWidget<UComboBoxString>(); Simulation->AddChildToVerticalBox(ScenarioList);
	ScenarioStart = Button(Simulation,TEXT("Vorhandene Route neu starten"),TEXT("StartScenarioButton"));
	ScenarioStart->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::StartScenario);
	ScenarioStop = Button(Simulation,TEXT("Route stoppen"),TEXT("StopScenarioButton"));
	ScenarioStop->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::StopScenario);
	ScenarioStatus = Text(Simulation,TEXT("Verfügbarkeit wird geprüft"),12);
	Text(Simulation,TEXT("Nicht verfügbar in V1:\nNPC-Spawn • Tageszeit • Wetter • Zeitraffer\n\nKeine neue Simulation. Verwendet nur vorhandene Routen; Neustart beginnt an Wegpunkt 1."),12);
	StatusLabel = Text(Main,TEXT("Bereit"),13);
	Button(Main,TEXT("Werkzeuge zurücksetzen"),TEXT("ResetToolsButton"))->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::Reset);
	Button(Main,TEXT("Schließen und weiter testen  [F6 / ESC]"),TEXT("CloseToolboxButton"))->OnClicked.AddDynamic(this,&UDeveloperToolboxWidget::Close);
}

void UDeveloperToolboxWidget::InitializeToolbox(UDeveloperToolboxComponent* Component)
{
	Tools = Component;
	EffectList->ClearOptions();
	for (const FDeveloperEffectEntry& Entry : Component->Effects) EffectList->AddOption(Entry.Label.ToString());
	if (!Component->Effects.IsEmpty()) EffectList->SetSelectedIndex(0);
	ScenarioList->ClearOptions();
	for (const auto& Scenario : Component->GetScenarios()) ScenarioList->AddOption(Scenario->GetTitle().ToString());
	if (!Component->GetScenarios().IsEmpty()) ScenarioList->SetSelectedIndex(0);
	Cast<USpinBox>(WidgetTree->FindWidget(TEXT("FlightSpeed")))->SetValue(Component->GetFlightSpeed());
	Cast<USpinBox>(WidgetTree->FindWidget(TEXT("CameraSpeed")))->SetValue(Component->GetCameraSpeed());
	Refresh();
}

void UDeveloperToolboxWidget::Refresh()
{
	if (!Tools.IsValid()) return;
	FlightLabel->SetText(FText::FromString(Tools->IsFlying() ? TEXT("Flugmodus: AN") : TEXT("Flugmodus: AUS")));
	NoClipLabel->SetText(FText::FromString(Tools->IsNoClip() ? TEXT("NoClip: AN") : TEXT("NoClip: AUS")));
	CameraLabel->SetText(FText::FromString(Tools->IsFreeCamera() ? TEXT("Freie Kamera: AN") : TEXT("Freie Kamera: AUS")));
	StatusLabel->SetText(Tools->GetStatus());
	EffectStart->SetIsEnabled(Tools->Effects.IsValidIndex(EffectList->GetSelectedIndex()) && !Tools->Effects[EffectList->GetSelectedIndex()].System.IsNull());
	EffectCount->SetText(FText::FromString(FString::Printf(TEXT("Aktive Toolbox-Effekte: %d"),Tools->GetEffectTester() ? Tools->GetEffectTester()->GetActiveCount() : 0)));
	const auto& Scenarios = Tools->GetScenarios();
	const bool bAvailable = Scenarios.IsValidIndex(ScenarioList->GetSelectedIndex()) && Scenarios[ScenarioList->GetSelectedIndex()]->IsAvailable();
	ScenarioStart->SetIsEnabled(bAvailable); ScenarioStop->SetIsEnabled(bAvailable);
	ScenarioStatus->SetText(FText::FromString(bAvailable ? TEXT("Vorhandene NPC-Route verfügbar") : TEXT("Nicht verfügbar: keine passende Route in dieser Karte")));
}
void UDeveloperToolboxWidget::NativeTick(const FGeometry& Geometry,float DeltaTime)
{
	Super::NativeTick(Geometry,DeltaTime);
	RefreshTime += DeltaTime;
	if (RefreshTime >= .15f) { RefreshTime = 0; Refresh(); }
}
FReply UDeveloperToolboxWidget::NativeOnPreviewKeyDown(const FGeometry& Geometry,const FKeyEvent& Event)
{
	if (Event.GetKey() == EKeys::F6 || Event.GetKey() == EKeys::Escape)
	{
		Close(); return FReply::Handled();
	}
	return Super::NativeOnPreviewKeyDown(Geometry,Event);
}
void UDeveloperToolboxWidget::Flight() { if (Tools.IsValid()) Tools->SetFlight(!Tools->IsFlying()); Refresh(); }
void UDeveloperToolboxWidget::NoClip() { if (Tools.IsValid()) Tools->SetNoClip(!Tools->IsNoClip()); Refresh(); }
void UDeveloperToolboxWidget::Camera() { if (Tools.IsValid()) Tools->SetFreeCamera(!Tools->IsFreeCamera()); Refresh(); }
void UDeveloperToolboxWidget::FlightSpeed(float Value) { if (Tools.IsValid()) Tools->SetFlightSpeed(Value); }
void UDeveloperToolboxWidget::CameraSpeed(float Value) { if (Tools.IsValid()) Tools->SetCameraSpeed(Value); }
void UDeveloperToolboxWidget::TriggerEffect() { if (Tools.IsValid() && Tools->GetEffectTester()) Tools->GetEffectTester()->Trigger(EffectList->GetSelectedIndex(),EffectPosition->GetSelectedIndex()==0); Refresh(); }
void UDeveloperToolboxWidget::StopEffects() { if (Tools.IsValid() && Tools->GetEffectTester()) Tools->GetEffectTester()->StopAll(); Refresh(); }
void UDeveloperToolboxWidget::StartScenario() { if (Tools.IsValid() && Tools->GetScenarios().IsValidIndex(ScenarioList->GetSelectedIndex())) { Tools->GetScenarios()[ScenarioList->GetSelectedIndex()]->Start(); Tools->Report(FText::FromString(TEXT("Vorhandene NPC-Route neu gestartet."))); } Refresh(); }
void UDeveloperToolboxWidget::StopScenario() { if (Tools.IsValid() && Tools->GetScenarios().IsValidIndex(ScenarioList->GetSelectedIndex())) { Tools->GetScenarios()[ScenarioList->GetSelectedIndex()]->Stop(); Tools->Report(FText::FromString(TEXT("Vorhandene NPC-Route gestoppt."))); } Refresh(); }
void UDeveloperToolboxWidget::Close() { if (Tools.IsValid()) Tools->ClosePanel(); }
void UDeveloperToolboxWidget::Reset() { if (Tools.IsValid()) { Tools->ResetTools(); InitializeToolbox(Tools.Get()); } }
