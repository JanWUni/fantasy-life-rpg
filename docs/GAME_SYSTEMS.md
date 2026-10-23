# Spielsysteme — Leitlinien und offene Details

## Weltsimulation (FEST)
NPCs verfolgen eigene Interessen, Berufe, Beziehungen, Institutionen und Macht. Wirtschaft, Handel und Politik entwickeln sich ohne Spielerintervention; der Spieler kann bedeutende Entwicklungen verändern. Weltzustand überlebt Tod und Charakterwechsel. Genaues Simulationsmodell offen.

## Berufe und Aufstieg (FEST)
Freie Lebenswege, mehrere Berufe und Spezialisierungen; friedliche Tätigkeiten haben eigenständigen Wert. Gesellschaftlicher, wirtschaftlicher, militärischer und politischer Aufstieg bis zur Spitze möglich, jedoch nicht garantiert. Klassen-/Skillstruktur offen.

## Koop und PvP (FEST)
Primär Koop mit Freunden. PvP prinzipiell auch in Städten möglich. Kein absoluter technischer Stadtschutz als Kernidee; Wachen, Recht, Verfolgung, Kopfgeld, Ächtung/Stadtverbote, unterschiedliche Rechtsräume und soziale Reaktionen machen Gewalt riskant. Fernstraßen und Wildnis weniger geschützt. Konkrete Anti-Grief-, Zeugen-, Beweis-, Loot- und Strafregeln offen.

## Tod (Normalmodus FEST, Details offen)
Der Normalmodus ist auf lange Spielzeit mit demselben Charakter ausgelegt. Tod zerstört weder gesamten Charakter noch langfristigen Fortschritt, verursacht aber spürbaren **Soft-Reset**, eventuell Verlust von Inventar/Ausrüstung, Verletzungen oder Bergungsaufgaben. Genaues Rückkehr-/Wiederbelebungssystem und Itemverlust noch nicht beschlossen.

**Diskutiert, nicht vollständig festgelegt:** Kampf-unfähigkeit und Rettung vor endgültigem Tod; NPCs können grundsätzlich dauerhaft sterben und Mord hat gesellschaftliche Folgen. Seltene aufwendige Wiederbelebung für wichtige, ressourcenreiche NPCs sowie göttliche Spieler-Reinkarnation sind mögliche Erklärungen, nicht beschlossene Lore. Optional schwerere Spielmodi/Hardcore mit größerem Verlustrisiko; konkrete Modi offen. Götter/Weltursprung bleiben mystisch.

## Noch offen
Fairness gegen Griefing, Konsequenzen für Reinkarnation einer gesuchten Person, Loot-/Bergungssystem, Strafrecht, NPC-Resurrection, Heilmöglichkeiten, technische Server-/Save-Architektur.

## Aufsammeln und Inventar – bestätigter Prototypumfang, 23. Oktober 2026

Vom Nutzer für den ersten spielbaren Ausbau bestätigt; einstellbare Startregeln, keine endgültige Balance:

- Lose, zunächst neutrale Testgegenstände werden über die bestehende E-Interaktion aufgenommen.
- 20 Inventarplätze; vorerst kein Gewichtssystem.
- Gleiche Gegenstandsarten stapeln sich zunächst bis 99. Das Maximum ist je Art einstellbar.
- Ist für die gesamte aufzunehmende Menge kein Platz, bleibt der Weltgegenstand vollständig liegen. Eine kurze Meldung erklärt den Platzmangel. Freie Plätze in vorhandenen Stapeln können auch bei 20 belegten Inventarplätzen genutzt werden.
- Das einfache Inventar zeigt Name und Anzahl. Nach Auswahl wird zunächst genau ein Stück vor der Figur abgelegt und kann erneut aufgenommen werden.
- Inventar und abgelegte Gegenstände bestehen nur während der laufenden Sitzung. Dauerhaftes Speichern wird später gemeinsam für Inventar und Weltzustand ergänzt.

Ausrüstung, Benutzen, Gewicht, Diebstahl-/Eigentumsregeln und Inventarfolgen beim Tod sind damit nicht festgelegt. Bedienung und technischer Prüfstand: [INVENTORY_SYSTEM.md](INVENTORY_SYSTEM.md).

## Bewegung und Ducken – bestätigter Prototypumfang, 23. Oktober 2026

- Third-Person-Kamera mit freier Mausrotation. WASD bewegt relativ zur Kamera; die Figur dreht sich in Bewegungsrichtung.
- Standardmäßig laufen, mit gehaltenem Shift sprinten. Ein langsamer Gehmodus gehört zum Umfang. Sprint verbraucht im ersten Prototyp keine Ausdauer.
- Leertaste springt vom Boden; kein Doppelsprung. Höhe und Luftsteuerung bleiben einstellbare Prototypwerte.
- Strg schaltet Ducken um. Geduckt sind Körperhaltung und Kollisionskapsel niedriger; die Figur bewegt sich langsamer. Körper und Kamera wechseln weich zwischen den Haltungen.
- Geduckt sind Springen und Sprinten gesperrt; zuvor aufstehen. Aufstehen benötigt ausreichend Kopffreiheit.
- Hindernisbewegung ist für einen späteren Schritt auf niedrige Hindernisse und Hochziehen an Kanten begrenzt. Freies Klettern ist vertagt; dieser Bewegungsausbau implementiert noch kein Übersteigen/Hochziehen.

Technische Erstbelegung für langsames Gehen: Alt halten. Zahlenwerte, Animationen und diese zusätzliche Belegung sind veränderbare Implementierungsdetails. Bedienung und Prüfumfang: [MOVEMENT_SYSTEM.md](MOVEMENT_SYSTEM.md). Lebenspunkte, Mana und Kampfregeln werden separat geklärt.
