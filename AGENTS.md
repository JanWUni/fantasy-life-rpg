# Arbeitsregeln für ChatGPT und Codex

Diese Regeln gelten für das gesamte Repository. Maßgebliche Projekt- und Designinformationen stehen in den versionierten Dokumenten unter `docs/`.

## Verbindliche Quellen

- [Spielvision](docs/GAME_VISION.md)
- [Weltrahmen](docs/WORLD_SETTING.md)
- [Spielsysteme](docs/GAME_SYSTEMS.md)
- [Entscheidungsregister](docs/DECISIONS.md)
- [Technischer Ansatz](docs/IMPLEMENTATION_APPROACH.md)
- [Technischer Ist-Zustand](docs/TECHNICAL_STATUS.md)
- [Worldbuilding der Völker](docs/worldbuilding/voelker/README.md)

Spezifische Worldbuilding-Regeln in untergeordneten Verzeichnissen ergänzen diese Datei. Bei inhaltlichen Widersprüchen haben ausdrücklich bestätigte Entscheidungen im Entscheidungsregister und in den zugehörigen Sachdateien Vorrang.

## Worldbuilding und Game Design

- Bestätigte Worldbuilding- und Game-Design-Entscheidungen sind verbindlich.
- Offene Fragen, Richtungen und Vorschläge sind kein Kanon und dürfen nicht als festgelegt dargestellt werden.
- ChatGPT unterstützt Worldbuilding und Game Design auf Grundlage der bestehenden Dokumente und ausdrücklicher Nutzerentscheidungen.
- Codex trifft keine eigenständigen Lore- oder Game-Design-Entscheidungen. Technische Annahmen dürfen keine offenen Designfragen stillschweigend festlegen.
- Worldbuilding-Änderungen müssen in der passenden Sachdatei und im zentralen `docs/DECISIONS.md` konsistent dokumentiert werden.
- Bestehende Worldbuilding-Dateien und ihre Struktur dürfen nicht durch parallele Dokumente oder Verzeichnisstrukturen ersetzt werden.

## Technische Entwicklung

- Technische Änderungen erfolgen modular und in kleinen, überprüfbaren Schritten.
- Vorhandene Unreal-Assets, Blueprints, Maps und Levels dürfen nur auf ausdrücklichen Auftrag verändert, verschoben oder gelöscht werden.
- Für unterstützte Editoroperationen soll die Unreal-MCP-Anbindung verwendet werden. Die lokale MCP-Konfiguration bleibt rechnerbezogen und wird nicht versioniert.
- Unreal Engine 5.8 ist die derzeit eingesetzte Prototyp-Engine. Dies legt die endgültige Spielarchitektur, Networking-, Persistenz- oder Simulationslösung nicht automatisch fest.
- Generierte Dateien, Build-Artefakte, Editor-Zustände und Shader-Caches bleiben außerhalb der Versionsverwaltung.
- Binäre Unreal- und Quell-Assets werden entsprechend `.gitattributes` über Git LFS verwaltet.

## Parallele 3D-Asset-Arbeit

- Asset Creator und Asset Refiner lesen vor Arbeitsbeginn die gemeinsame [Asset-Pipeline](docs/technical/ASSET_PIPELINE.md), insbesondere „Paralleler Creator-/Refiner-Workflow“. Dort stehen Rollen, Startaufträge, Dateizuständigkeiten, Übergabe und Qualitätskontrollen.
- Parallelität nur für getrennte Module bzw. getrennte Creator-/Refiner-Dateien. Pro Datei genau ein Schreibverantwortlicher; übergebene Creator-Stände bleiben unverändert. Gemeinsame Unreal-Imports, Materialien, Blueprints und Karten werden nacheinander durch einen im Auftrag benannten Integrationsverantwortlichen bearbeitet.
- Das vorhandene Elfenhaus ist visuelle Referenz, keine Erlaubnis für neue Kultur-/Architekturfestlegungen. Bestehende Assets und Level nur im ausdrücklich beauftragten Umfang bearbeiten.

## Vor jeder Änderung

1. Die betroffenen Sach- und Entscheidungsdokumente lesen.
2. Prüfen, ob der Auftrag bestehende Assets, Levels oder bestätigte Entscheidungen berührt.
3. Den Umfang klein halten und den relevanten technischen Zustand anschließend prüfen.
