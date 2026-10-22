# Interaktionsprototyp

Stand: 21. Oktober 2026. Technischer Prototyp in Unreal Engine 5.8; keine Festlegung der endgültigen Gameplay- oder Netzwerkarchitektur.

## Ausprobieren

1. `/Game/Prototype/Maps/Lvl_Prototype_01` öffnen und **Play** starten.
2. Dem grauen, länglichen Würfel `InteractionTest_E_Toggle` vor dem Startpunkt nähern (Position ungefähr X=300, Y=0, Z=200 cm).
3. Sobald ein gültiges Ziel in Reichweite und mit freier Sichtlinie erreichbar ist, erscheint unten mittig **„E – Interagieren“**. Das ausgewählte Objekt erhält eine goldene Hervorhebung.
4. **E** drücken: Der Würfel dreht sich zwischen 0 und 60 Grad. Erneutes Drücken schaltet zurück.
5. Außerhalb von 200 cm Reichweite oder hinter einer sichtblockierenden Wand verschwinden Hinweis und Hervorhebung; der Zustand darf sich nicht ändern. Gedrückthalten darf nur einmal auslösen.
6. Zur gerahmten Tür `Prototype_Door_E_OpenClose` bei ungefähr `(650, -350, 0)` cm gehen. E öffnet das Blatt um 90 Grad, der nächste Druck schließt es. Beide Seiten verwenden dieselbe Anzeige und Hervorhebung.

Der Prototyp-Level verwendet `BP_PrototypeGameMode`, `BP_PrototypeCharacter` und `BP_PrototypePlayerController`. Die vorhandenen Third-Person-Blueprints wurden dafür kopiert. Standardkarten und ursprüngliche Template-Levels wurden nicht geändert.

## C++-Bausteine

- `Interaction/Interactable.h`: Blueprint-fähiges `IInteractable` mit `GetInteractionPoint`, `GetInteractionRange`, `GetInteractionText`, `CanInteract` und `Interact`. Der auslösende Actor wird explizit übergeben. NPCs können dieses Interface direkt implementieren.
- `Interaction/InteractionComponent.*`: wiederverwendbare Spielerkomponente ohne Tick. Sucht bei einer Anfrage per Kollisionsüberlappung nach Kandidaten, filtert über das Interface und wählt den nächsten zulässigen, sichtbaren Interaktionspunkt. Gleichstände werden nach Objektpfad aufgelöst. Das Ziel wird direkt vor dem Aufruf erneut validiert.
- `Interaction/InteractableActor.*`: optionale Basis für einfache Requisiten mit Mesh, verschiebbarem Interaktionspunkt, `InteractionRange` und `bInteractionEnabled`. Nach Autoritäts-, Reichweiten- und Sichtprüfung wird das Blueprint-Ereignis `OnInteracted` ausgelöst.
- `FantasyLifeRPGCharacter`: besitzt die Komponente und bindet die optionale Action `InteractAction` an Enhanced Inputs `Started`. Die Prototyp-Blueprints weisen `/Game/Prototype/Input/IA_Interact` und `IMC_Interaction` mit Taste E zu. Bestehende Bewegungs- und Kamera-Mappings bleiben enthalten.
- `Interaction/InteractionFeedbackComponent.*`: separate, rein lokale Darstellungskomponente, die nur dem `BP_PrototypeCharacter` hinzugefügt wurde. Aktualisiert nach Bewegung und Kamera pro Frame das Ziel über dieselbe `FindBestTarget`-Prüfung wie E. Steuert Hinweis und Hervorhebung gemeinsam, ohne UI-Abhängigkeiten in der Gameplay-Komponente.
- `Interaction/UI/InteractionPromptWidget.*`: passives C++-/Slate-Widget mit „E – {Aktion}“, unten mittig im jeweiligen Spieler-Viewport. Die Aktion stammt vom Ziel und wird auch bei gleichbleibendem Ziel aktualisiert. Ein leerer Aktionstext verwendet „Interagieren“. Das Widget übernimmt weder Maus- noch Tastaturfokus.

Das Feedback verwendet die vorhandenen UMG-/Slate-Module und ergänzt `SlateCore` als private Abhängigkeit. `UnrealEd` wird ausschließlich für Editor-Builds privat eingebunden, damit die automatisierten Integrationstests PIE starten und beenden können.

## Zielanzeige und Hervorhebung

Aktueller Ausbau: Türen zeigen je nach Zustand „E – Tür öffnen“ oder „E – Tür schließen“, der NPC „E – Sprechen“. Einfache Actors können `InteractionAction` setzen oder `GetInteractionText` im Blueprint überschreiben. Die bestehende Anzeige wurde auf 360 × 56 UI-Einheiten verbreitert. Details und aktuelle Testergebnisse einschließlich NPC-Navigation: [NPC_MOVEMENT.md](NPC_MOVEMENT.md).

Das Overlay-Material `/Game/Prototype/Materials/M_InteractionHighlight` färbt die sichtbaren Mesh-Komponenten des ausgewählten Actors vorübergehend gold. Es ist ein transparentes, unbeleuchtetes Material; ein globales Outline-Postprocessing wird nicht benötigt. Die Basismaterialien werden nicht verändert.

Die vorhandenen Nanite-Platzhalter zeigen dieses transparente Overlay im Nanite-Renderpfad nicht an. Für ausgewählte Static-Mesh-Komponenten aktiviert das Feedback deshalb vorübergehend `SetForceDisableNanite(true)` und verwendet deren vorhandenes Fallback-Mesh. Danach wird der vorherige Laufzeitwert wiederhergestellt. Mesh-Assets und globale Nanite-Einstellungen bleiben unverändert. Bei komplexeren Assets kann das Fallback eine andere Geometriequalität besitzen; diese Prototyp-Lösung ist am vorhandenen Würfel und Türblatt geprüft.

Beim Zielwechsel, Verlassen der Reichweite, Sichtverlust oder Deaktivieren des Ziels werden Hinweis und Hervorhebung entfernt. Vorherige Overlay-Materialien und deren Sichtweite werden wiederhergestellt. Das gilt auch bei Verlust der Spielersteuerung, beim Entfernen der Feedback-Komponente und beim Beenden von PIE. Schwache Referenzen verhindern, dass ein zerstörtes Ziel festgehalten wird. Eine zwischenzeitlich durch ein anderes System ersetzte Overlay-Zuweisung wird beim Aufräumen nicht überschrieben.

Beim Test-Blueprint und dessen platziertem Actor liegt der Interaktionspunkt bei lokal `(10, 50, 50)` innerhalb des Platzhaltermeshes. Der vorherige Punkt direkt auf der Bodenfläche konnte eine Bodenberührung als Sichtblockierung liefern. Der Hinweis erhält seine feste Größe vor dem Setzen des unteren Bildschirmankers, da `SetDesiredSizeInViewport` in UE 5.8 den Anker zurücksetzt.

Die Anzeige läuft nur für einen lokal kontrollierten Spieler-Pawn. Andere Spieler und ein dedizierter Server erzeugen auf dieser Instanz kein Widget. Die Darstellung wird nicht repliziert. Getrennte Client-Prozesse und Split-Screen sind bisher nicht getestet; Overlay-Zuweisungen an gemeinsam gerenderten Meshes sind noch keine Lösung für getrennte Split-Screen-Hervorhebungen.

## Reichweite und Kollision

- Die Reichweite wird in **cm vom Actor-Ursprung des Interaktors zum Interaktionspunkt des Ziels** gemessen. Sie hängt nicht vom Abstand der Third-Person-Kamera ab. Der Grenzwert ist eingeschlossen; Reichweite null oder ungültige Werte sperren die Interaktion.
- Die Sichtlinie verläuft vom Augenpunkt des Pawns zum Interaktionspunkt. Eine blockierende `Visibility`-Kollision eines anderen Actors verhindert die Benutzung.
- Die Kandidatensuche berücksichtigt `WorldStatic`, `WorldDynamic` und `Pawn`. Ziele benötigen eine für Abfragen aktivierte Kollisionskomponente auf einem dieser Objektkanäle. `Generate Overlap Events` wird für diese direkte Physikabfrage nicht benötigt.
- `SearchRadius` der Spielerkomponente beträgt zunächst 1000 cm und begrenzt die Kandidatensuche. Für größere Objekt-Reichweiten muss dieser Suchradius mit angehoben werden. Der Interaktionspunkt sollte innerhalb der Kollisionsgeometrie liegen; große Offsets außerhalb dieser Geometrie können die Kandidatensuche und Sichtprüfung verfälschen.
- Hinweis, Hervorhebung und E verwenden das nächste zulässige Ziel in der Umgebung. „Sichtbar“ bedeutet hier eine freie Sichtlinie vom Augenpunkt zum Interaktionspunkt; die bisherige Auswahl ist weiterhin unabhängig von der Kamerablickrichtung und wird nicht zusätzlich auf das Bildschirm-Sichtfeld eingeschränkt.

## Neue Objekte erstellen

Für einfache Requisiten einen Blueprint von `InteractableActor` ableiten, ein vorhandenes Mesh zuweisen, Interaktionspunkt und Reichweite einstellen und `OnInteracted` implementieren. Der Test-Blueprint hält dazu `bIsActive` und setzt nach dem Umschalten die Actor-Drehung auf 0 oder 60 Grad. Die Darstellung ist ausschließlich im Blueprint umgesetzt.

Für Türen, Gegenstände oder NPCs kann `CanInteract` zusätzliche Bedingungen liefern. Das Interface setzt weder Inventar-, Dialog- noch Türklassen voraus. Bei einer eigenen `Interact`-Implementierung müssen Autorität und aktuelle Bedingungen ebenfalls geprüft werden; die optionale Basisklasse übernimmt diese Prüfung bereits.

## Interaktive Prototyp-Tür

`BP_PrototypeDoor` steht in `Lvl_Prototype_01` auf dem Boden bei ungefähr `(650, -350, 0)` cm und ist mit `InteractionDoor` markiert. Das Türblatt ist 120 cm breit, 12 cm dick und 220 cm hoch; Blatt und Griff verwenden vorhandene Würfel-/Kugel-Platzhalter. `BP_PrototypeDoorFrame` bildet mit drei Mesh-Komponenten den festen Rahmen und ist ein separater Actor mit Tag `InteractionDoorFrame`.

Die Tür erbt direkt von `InteractableActor`. Im Blueprint-Ereignis `OnInteracted` wird `bIsOpen` umgeschaltet und die Actor-Drehung auf die gespeicherte geschlossene Drehung oder einen lokalen Yaw-Versatz von -90 Grad gesetzt. Die ursprüngliche Drehung wird bei BeginPlay erfasst, damit weitere Instanzen auch mit anderer Ausrichtung funktionieren. Der Ursprung des Türblatts liegt seitlich unten am Anschlag; seine Position und der separate Rahmen bewegen sich nicht.

Die Reichweite beträgt 200 cm zum mitbewegten Interaktionspunkt bei lokal `(50, 50, 50)`. Anzeige und goldene Hervorhebung kommen unverändert vom Spieler-Feedback. Nur Türblatt und Griff werden hervorgehoben; der Rahmen ist kein Interaktionsziel. Die geschlossene Tür blockiert Pawn-Kollisionen, die offene gibt den Durchgang frei. Der Griff hat keine eigene Kollision.

Die Zustandsänderung erfolgt für diesen einfachen Prototyp sofort. Es gibt noch keine Bewegungsanimation, Schwenkbereichsprüfung, Schlösser oder Zustandsreplikation. E verwendet weiterhin die server-/autoritätsgeprüfte Ausführung der vorhandenen Basisklasse; es wurde keine zusätzliche Eingabebelegung oder Runtime-C++-Türklasse angelegt.

## Multiplayer-Grenze

`TryInteract` führt Gameplay-Änderungen nur auf einem Actor mit Autorität aus. Die Basisklasse prüft zusätzlich die Autorität des Ziels. Standalone und der lokale Host können interagieren; für einen entfernten Client ist noch keine Interaktionsanfrage implementiert.

Eine spätere Erweiterung kann am besessenen Pawn bzw. dessen Komponente einen Server-RPC ergänzen. Der Server muss Ziel, Distanz, Sicht und Berechtigungen selbst erneut prüfen. Der persistente Objektzustand muss dann repliziert werden; die Darstellung kann daraus etwa über RepNotify aktualisiert werden. Aktuell gibt es keine RPCs, Zustandsreplikation, Vorhersage oder Multiplayer-Zusage.

## Tatsächlich geprüfter Stand

Die folgenden vier Testberichte beschreiben den ursprünglichen Interaktions-/Feedback-/Tür-Ausbau. Der aktuelle Ausbau mit sechs erfolgreichen Tests und den inzwischen beobachteten Navigations-Warnungen ist in [NPC_MOVEMENT.md](NPC_MOVEMENT.md) dokumentiert.

- Vollständiger `FantasyLifeRPGEditor Win64 Development`-Build: erfolgreich, einschließlich Unreal Header Tool, C++-Kompilierung und Link.
- Alle vier neuen Prototyp-Blueprints über Unreal MCP kompiliert und gespeichert; Input-Assets, Level-Override und externer Test-Actor gespeichert. Nach Editor-Neustart und erneutem Laden war das Testobjekt vorhanden.
- `FantasyLifeRPG.Interaction.Rules`: **Success**, keine Fehler oder Warnungen. Prüft Reichweite pro Objekt, eingeschlossenen Grenzwert, Reichweite null, nächstes Ziel, deaktiviertes Ziel, erfolgreiche Ausführung, Sichtblockierung und Wiederfreigabe, zerstörtes Ziel, kein erreichbares Ziel sowie Null- und Selbstreferenzen. Dieser Test verwendet eine isolierte temporäre Spielwelt.
- `FantasyLifeRPG.Interaction.PrototypePIE`: **Success**, keine Fehler oder Warnungen. Lädt `Lvl_Prototype_01`, startet PIE und sendet simulierte E-Tastenereignisse durch den tatsächlichen PlayerController-/Enhanced-Input-Pfad. Prüft Blueprint-Zustandswechsel, geänderte Drehung, kein wiederholtes Umschalten beim Halten, Zurückschalten bei zweitem Druck und unveränderten Zustand außerhalb der Reichweite. Temporäre Transformationsänderungen werden zurückgesetzt; anschließend endet PIE.
- `FantasyLifeRPG.Interaction.FeedbackPIE`: **Success**, keine Fehler oder Warnungen. Lädt den gespeicherten Prototyp-Level und prüft das tatsächliche Widget im Spieler-Viewport, dessen gerenderte Größe und Position unten mittig sowie genau eine sichtbare Anzeige. Prüft Hinweis und Mesh-Overlay bei gültigem Ziel, Zielwechsel, Reichweitenverlust, Deaktivierung, Sichtblockierung und Wiederfreigabe, Zielzerstörung, Verlust und Wiedererlangen der Spielersteuerung. Prüft die Wiederherstellung vorheriger Overlay- und Nanite-Fallback-Werte, einschließlich eines bereits gesetzten Fallback-Overrides.
- `FantasyLifeRPG.Interaction.DoorPIE`: **Success**, keine Fehler oder Warnungen. Lädt die gespeicherte Tür und den Rahmen in `Lvl_Prototype_01`. Prüft Öffnen/Schließen über simulierte E-Ereignisse im vorhandenen Enhanced-Input-Pfad, kein wiederholtes Umschalten beim Halten, Benutzung von beiden Seiten, Reichweiten- und Sichtblockierung einschließlich fehlendem Hinweis/Overlay, Wiederfreigabe und unveränderten Rahmen. Eine spielergroße Kapsel wird durch den Durchgang geprüft: geschlossen blockiert das Blatt, geöffnet ist der Weg frei. Zusätzlich werden Bodenkontakt an der Annäherungsseite und eine temporäre zweite Türinstanz mit 37 Grad Ausgangsdrehung geprüft. Die Instanz schwenkt relativ zu ihrer Ausrichtung und kehrt exakt zurück; temporäre Actors werden entfernt.
- Tür- und Rahmen-Blueprint über Unreal MCP kompiliert und gespeichert; beide externen Actors im Prototyp-Level gespeichert. Beim Versetzen wurde eine versehentlich zurückgesetzte Türblatt-Skalierung erkannt und vor dem abschließenden Testlauf korrigiert.
- Gemeinsamer abschließender Testlauf: **4 erfolgreich, 0 fehlgeschlagen, 0 übersprungen**, keine Fehler oder Warnungen.
- Testobjekt im Editor-Viewport visuell auf sichtbare Platzierung geprüft.
- Im gerenderten PIE-Spielfenster zusätzlich optisch geprüft: erreichbarer Würfel mit goldener Hervorhebung und vollständig sichtbarem Hinweis unten mittig; nach Versetzen außerhalb der Reichweite wieder grauer Würfel ohne Hinweis. Screenshots liegen lokal unter `Saved/InteractionDev/feedback_visible_final.png` und `feedback_out_of_range_final.png` (ignorierte Prüfartefakte).
- Im gerenderten PIE-Spielfenster Tür auf dem Boden, geschlossen und nach per Unreal MCP ausgelöstem E geöffnet sowie erneut geschlossen optisch geprüft. Blatt und Griff sind gold hervorgehoben, der feste Rahmen bleibt grau und „E – Interagieren“ bleibt lesbar. Lokale Screenshots: `Saved/InteractionDev/door_closed_final.png` und `door_open_final.png` (ignorierte Prüfartefakte).

Die Tests stehen in `Source/FantasyLifeRPG/Interaction/Tests/InteractionTests.cpp`, `InteractionFeedbackTests.cpp` und `InteractionDoorTests.cpp` und können im Automation-/Session-Frontend unter `FantasyLifeRPG.Interaction` erneut ausgeführt werden. Die PIE-Tests laden den gespeicherten Prototyp-Level; eigene Editoränderungen vorher speichern.

## Noch manuell prüfen

- Mit echter Tastatur zum Würfel laufen, E drücken, halten, loslassen und erneut drücken; Wirkung und Erreichbarkeit aus verschiedenen Richtungen beurteilen.
- Mit echter Tastatur zur Tür laufen, öffnen, hindurchgehen und von der anderen Seite schließen. Auch das Schließen bei einem Spieler im Türbereich beurteilen; eine Prüfung auf belegten Schwenkbereich ist noch nicht implementiert. Der automatisierte Kapseltest ersetzt diese Bedienungsprüfung nicht.
- Lesbarkeit und Größe des Hinweises sowie die goldene Hervorhebung bei der eigenen Bildschirmauflösung und Kameraführung beurteilen.
- Bewegung mit WASD, Maus-Kamera und Sprung im Prototyp nach eigenem Spielgefühl prüfen. Diese Bedienungsprüfung wurde nicht automatisiert durchgeführt.
- Nach Wunsch weitere Blueprint-Instanzen mit unterschiedlichen Reichweiten platzieren. Mehrfachzielwahl und Blockierung werden sowohl im Regeltest als auch mit temporären Actors im PIE-Feedbacktest geprüft; die gewünschte Bedienwirkung im eigenen Levelaufbau bleibt manuell zu beurteilen.
- Ein paketierter Build, Controller-/Touch-Belegung und Multiplayer wurden nicht getestet bzw. sind noch nicht umgesetzt.
