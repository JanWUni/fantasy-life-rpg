# Grundbewegung und Ducken V1

Arbeitsort: `E:/Business/fantasy-rpg-gameplay`, Branch `gameplay/development`. Standalone-Prototyp auf der bestehenden Third-Person-Charakterbasis; bestätigte Regeln stehen in [GAME_SYSTEMS.md](GAME_SYSTEMS.md).

| Eingabe | Verhalten |
| --- | --- |
| WASD / Maus | Kamerarelative Bewegung / freie Kameradrehung |
| Shift halten, links oder rechts | Sprint |
| Alt halten, links oder rechts | Langsam gehen; hat Vorrang vor Sprint |
| Strg drücken, links oder rechts | Ducken umschalten |
| Leertaste | Ein Bodensprung; geduckt gesperrt |
| I / F6 | Vorhandenes Inventar / Entwickler-Toolbox |

Die Grundgeschwindigkeit übernimmt den vorhandenen Blueprintwert (derzeit 500 cm/s). Sprint ist 2× so schnell, langsames Gehen und Ducken jeweils 0,4×. Die geduckte Kapsel hat 65 cm Halbhöhe, die Haltungsdarstellung wechselt in etwa 0,22 s. Die Werte sind Prototypabstimmung und über native Defaults/Charakter-Blueprint einstellbar. Sprunggeschwindigkeit 500 cm/s und Luftsteuerung 0,35 bleiben erhalten.

Ein Strg-Tastendruck im Stand fordert Ducken an, der nächste Aufstehen. CharacterMovement prüft den verfügbaren Raum: Unter einer niedrigen Decke bleibt die Figur geduckt. Ein bereits angefordertes Aufstehen wird ausgeführt, sobald wieder Platz besteht. Halten wiederholt die Umschaltung nicht. In der Luft kann kein neuer Duckenwechsel begonnen werden. Der Fußpunkt der Kapsel bleibt beim Haltungswechsel am Boden.

`AFantasyLifeRPGCharacter` besitzt normale Geh-/Sprintgeschwindigkeit und die lokale Strg-Eingabe. Gehaltene Shift-/Alt-Tasten werden am PlayerController abgefragt und durch UI-/Toolzustände gesperrt; dadurch bleiben nach dem Leeren des Eingabepuffers keine zwischengespeicherten Sprintzustände zurück. Toolbox-Fokuswechsel und einmaliges Aufräumen aktualisieren die Gehgeschwindigkeit sofort nach dem Leeren der Eingaben. Wiederholtes Aufräumen einer bereits deaktivierten Toolbox leert keine Gameplay-Tasten. Der transiente Strg-MappingContext wird bei erneutem Setup, Entbesitz und EndPlay entfernt; sein Aufbau verwirft keine frischen Tastendrücke anderer Aktionen. Keine gespeicherten Input-/Blueprint-Assets müssen dafür geändert werden.

Die Entwickler-Toolbox behält Flug, NoClip und freie Kamera mit ihrer bisherigen Steuerung. Bei Gameplay-Charakteren multipliziert sie den Bodensprint nicht zusätzlich; für unabhängige Template-Charaktere bleibt der bisherige Fallback bestehen. Inventar-/Toolfenster sperren Gameplay-Bewegung und Ducken. Im Flugmodus dient Strg weiterhin zum Absteigen. Normaler Sprint und Ducken funktionieren auch bei deaktivierter Toolbox.

Mangels vorhandener Ducken-Clips ergänzt `UCrouchPoseMeshComponent` eine vorläufige Pose: Nach der vorhandenen Animationsauswertung werden Becken/Oberkörper abgesenkt und die Hüfte leicht nach hinten verlagert und die Beine per Zwei-Knochen-IK an den animierten Fußpositionen gebeugt. Körpermaßstab und vorhandene Animationsgraphen bleiben erhalten. Die Pose wird vor Veröffentlichung des Mesh-Transformpuffers erzeugt; keine Änderung an Animationsassets. Sie setzt die Mannequin-Knochen `pelvis`, `thigh_*`, `calf_*`, `foot_*` voraus; bei fehlenden Knochen bleibt die ursprüngliche Animation erhalten. Für andere Skelette sowie endgültige Ducken-Laufanimationen sind passende Assets/Anpassungen erforderlich. Ragdolls erhalten diese Pose nicht. Die Darstellung ist ein Prototyp und ersetzt keine fertig animierte Schleichbewegung.

Die Kamera kompensiert den sofortigen Kollisionshöhenwechsel und fährt anschließend zur neuen Höhe. Die Kollisionskapsel selbst wechselt sofort auf die sichere Form; eine interpolierte, zeitweise zu große Kapsel würde niedrige Öffnungen blockieren.

Der neue Test `FantasyLifeRPG.Movement.PlayablePIE` benutzt die gespeicherte Inventarkarte und erzeugt Boden/Decke ausschließlich in der PIE-Welt. Er prüft Controller-/Enhanced-Input-Eingaben, tatsächliche Geschwindigkeiten, kamerarelative Bewegung, Bodensprung ohne Doppelsprung, Strg-Umschaltung, Haltungs-/Kameraübergang, Fußpunkt, Körperpose, niedrige Öffnung, blockiertes und später mögliches Aufstehen sowie UI-/Toolbox-Rückgabe und Betrieb ohne Toolbox. Die Testgeometrie wird nicht als Content gespeichert. Der Test deaktiviert die Editor-Hintergrunddrosselung nur vorübergehend und stellt sie beim Aufräumen wieder her, ohne Einstellungen zu speichern. Kurze Übergänge werden pro Welt-Tick beobachtet; nach dem GPU-Screenshot-Readback wird zunächst eine stabile Framefolge abgewartet. Gerenderte Stand-/Duckenbilder werden unter `Saved/InteractionDev/` abgelegt.

Die vorhandenen Asset-Workspace- und Toolbox-Kartentests warten zwischen Eingabe und Prüfung nun anhand der Spielweltzeit. Reale Zeit begrenzt weiterhin die Gesamtlaufzeit. Eine kurze Anfangsphase im Asset-Workspace verhindert die anfängliche Fokus-/Eingabepufferleerung. Eingaben und Assertions bleiben unverändert; es gibt keine Wiederholung eines fehlgeschlagenen Tastendrucks.

**Prüfstand:** Editor-Build erfolgreich; abschließend 17/17 Projekttests in 109,10 s bestanden, neuer Bewegungstest ohne Warnungen. Vollständige Belege und Grenzen: [TECHNICAL_STATUS.md](TECHNICAL_STATUS.md). Keine Aussage zur Netzwerksynchronisierung, Gamepad-Belegung, Packaging, fertigen Animationen oder abschließenden Bewegungsbalance. Speichern, Ausdauer, Kampf, Gesundheit/Mana, Übersteigen und Hochziehen sind nicht Bestandteil dieser Änderung.

## Das richtige Asset-Lab verwenden

Die Karte `Lvl_AssetLab` existiert in mehreren Worktrees. Der Fenstertitel `FantasyLifeRPG - Unreal Editor` unterscheidet diese nicht. Die neuen Bewegungsmechaniken sind im Projekt `E:/Business/fantasy-rpg-gameplay/FantasyLifeRPG.uproject` eingebaut. Ein aus `fantasy-rpg-refiner` gestartetes Lab enthält sie vor der gemeinsamen Integration noch nicht.

Bei einer Übergabe Projektpfad, geladenes Projektmodul und aktive Spielvorschau gemeinsam prüfen und das Gameplay-Spielfenster in den Vordergrund holen. Die bisher verwendete Portnummer ist keine feste Projektkennung: In der aktuellen Sitzung belegt der Refiner Port 8001, Gameplay benutzt deshalb Port 8002. Die aktuelle Zuordnung liegt lokal unter `Saved/InteractionDev/current_editor_identity.json`.

Am 23.10.2026 wurde nach der gemeldeten Verwechslung nur eine noch laufende Refiner-Instanz vorgefunden; das Gameplay-Log belegt ein reguläres Schließen der vorherigen Gameplay-Instanz. Das Gameplay-Asset-Lab wurde erneut gestartet. Strg wurde diesmal per Windows-Tastatureingabe im sichtbaren Spielfenster getestet: Ducken und Aufstehen sind visuell bestätigt, zusätzlich wurde `bIsCrouched=true` am tatsächlichen Lab-Spieler gelesen. Die Sitzung bleibt zur Übergabe in der Duckhaltung. Ein kurzer Alt+W-Automationstastendruck konnte keine gehaltene Alt-Eingabe messen; für diesen Modus gilt weiterhin der zuvor erfolgreiche automatisierte Test mit frameübergreifend gehaltenem Alt. Keine neue physische Alt-Dauerprüfung behauptet und keine Gameplay-Quellen/Assets für die Fensterverwechslung verändert.
