"""Hash the delivery and prove preservation. Does not save any Unreal packages."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))
def write(n,v):(ROOT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
baseline=read('Evidence/files_before.json');changed=[];missing=[]
for name,h in baseline.items():
    p=REPO/name
    if not p.is_file():missing.append(name)
    elif sha(p)!=h:changed.append(name)
assert not missing and set(changed)<={'Content/Prototype/Maps/Lvl_AssetLab.umap'},(missing,changed)
write('Evidence/file_preservation.json',dict(status='passed',existing_files_checked=len(baseline),changed=changed,missing=missing,
    scope='All files captured before this catalogue; only the authorized Lab map may differ'))
data=read('manifest.json');blender=read('Evidence/blender_verification.json');ue=read('Evidence/unreal_verification.json');session=read('Evidence/session_restored.json')
assert blender['status']==ue['status']==session['status']=='passed'
assert all(l['lumens']==32 and l['temperature']==3000 and l['radius_cm']==240 for l in ue['lamps'])
for n,i in data['assets'].items():assert sha(ROOT/'Exports'/(n+'.fbx'))==i['fbx_sha256']
data.update(status='review_ready',accepted=False,source_sha256=sha(ROOT/data['source']),base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    map='/Game/Prototype/Maps/Lvl_AssetLab',outliner_folder='Lab/Architecture/WallCatalogue01',
    inherited_mesh_helper=dict(path='AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/build_house.py',
        sha256=sha(REPO/'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/build_house.py'),use='Read-only Mesh helper import, no original build invoked'),
    imported_assets_sha256={p.relative_to(REPO).as_posix():sha(p) for kind in ['Architecture','Furniture','Materials','Textures'] for p in (REPO/'Content/Art'/kind/'WallCatalogue01').rglob('*.uasset')},
    lab_map_sha256=sha(REPO/'Content/Prototype/Maps/Lvl_AssetLab.umap'),
    lamp=dict(blueprint='/Game/Art/Furniture/WallCatalogue01/Blueprints/BP_WC01_WallLamp',lumens=32,temperature_kelvin=3000,radius_cm=240,
        inverse_square=True,fixture_self_shadow=False,wall_and_furniture_shadows=True,no_switch_or_fuel_gameplay=True),
    actual_evidence=['Evidence/blender_verification.json','Evidence/unreal_verification.json','Evidence/file_preservation.json','Evidence/session_restored.json'],
    limitations=['Visual selection not yet accepted','Provisional kit, not a replacement for either house','End closing posts/corners, entrance, roof and house generator not supplied',
        'One LOD, Nanite off; no production performance or lightmap acceptance','No clean editor reload while pre-existing dirty packages remain unresolved',
        'Blender night rendering is a separate lighting illustration, not a calibrated Unreal photometric comparison'],
    commit_created=False,pushed=False)
write('manifest.json',data)
write('Evidence/naming_dimensions.json',{n:dict(nominal_name=n,actual_full_bounds_cm=[[round(v*100,5) for v in row] for row in i['bounds_m']],
    note='Names retain nominal design dimensions; full bounds include mounts, catches, pegs, sill and braces. Use measured bounds and wall contract.') for n,i in data['assets'].items()})
(ROOT/'REVIEW.md').write_text('''# Wandkatalog 01 – unabhängige Auswahlmuster

Status **review_ready**, nicht accepted. Refiner-Worktree `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`.

## Auftrag und Ergebnis

Die Häuser sind unveränderte Zusammenbau-Studien. Auf Nutzerauftrag stehen neue, unabhängige Wand- und Einrichtungsassets im nördlichen Lab: Outliner `Lab/Architecture/WallCatalogue01`, ungefähr X−2200 bis1300 / Y2000 bis3800 cm. Kein bestehendes Haus wurde umgebaut oder neu materialisiert.

- A: zurückhaltender Putz mit Holzrahmen; B: stärkeres Holztragbild mit geformten Streben; C: zusätzlich ausgearbeiteter, versetzter Steinsockel. Je eine geschlossene und eine Fensterwand, insgesamt sechs auswählbare Wandmodule.
- Eigenständiger Fensterrahmen einschließlich Fensterbank und Beschlägen sowie ein separates klares Glasmesh, identisch in alle drei Fensteröffnungen einsetzbar.
- Eigenständiger Tisch und Stuhl mit Brettern, Zargen, Streben und Holzverbindungen. Eine wiederverwendbare Wandleuchte mit Wandplatte, Arm, Haube, Käfig und sichtbarem Leuchtkern; drei Instanzen zeigen sie an den Wandmustern.
- Neben Einzelteilen gibt es einen Tisch-/Stuhlvergleich und zwei direkt aneinander gesetzte Wände als Anschlussprobe. Kein neues Haus und kein Gebäude-Generator.

## Anschlussvertrag

Neues **vorläufiges** gerades Kit `EC.WallCatalogue01 / draft_1`: 300 cm Breite, 24 cm Wandkern, 320 cm Höhe. Ursprung untere Startecke; X entlang der Wand, Blender +Y nach innen, Z nach oben. Start `(0,0,0)`, Richtung `(-1,0,0)`; Ende `(300,0,0)`, Richtung `(1,0,0)`. Einheitsskalierung, keine Spiegelung. Startseite besitzt den Pfosten; Endabschluss und Eckmodule fehlen noch. Dekor liegt innerhalb X0..300, seine Tiefe kann zwischen Varianten abweichen. Keine Zusicherung nahtlos gleicher Texturphase.

Fenstereinsatz am lokalen Punkt `(150,0,100)` cm. Reale Öffnung X90..210, Brüstung Z100, Kopf Z224+28*(1-((X−150)/60)^2) cm. Rahmen und Glas verwenden denselben Ursprung. Dieses Set ersetzt weder den 390-cm-Vertrag von Studie A noch ein R255-Modul. Erst nach Auswahl sind weitere Produktionsmaße und Übergänge zu bestimmen.

Nominalmaße in Prop-Dateinamen schließen einzelne Beschläge, Pfosten und Verbindungsdetails nicht vollständig ein. Tatsächliche vollständige Bounds stehen verbindlich in `manifest.json` und `Evidence/naming_dimensions.json`; keine automatische Skalierung aus Dateinamen ableiten.

## Quelle, Materialien und Licht

`WallCatalogue01.blend` enthält `Module_Library` mit allen elf Renderquellen und UCX am Ursprung sowie eine getrennte Szene `Wall_Comparison` mit verlinkten Ansichtsinstanzen. Es wurde keine Hausquelle geöffnet oder gespeichert. Der vorhandene Mesh-Helfer wurde ausschließlich lesend importiert; seine Herkunft ist gehasht.

Fünf eigene Texturfamilien mit BaseColor, Roughness und Tangent-Normal: Holz 2048², Putz/Stein1024², Eisen/Bronze512², insgesamt15 PNG. UV0 nutzt bewusst gekachelte/überlappende Flächen, gewöhnlich eine Wiederholung je Meter; Holz entlang der Bauteilachse. Knoten, Poren, Putzkörnung und Steinstruktur sind eigene prozedurale Quellen. Kanten und größere Fugen sind Geometrie. Keine Fremdtexturen und keine Änderung gemeinsamer Materialien.

Unreal besitzt eigene sieben Materialien, 15 Texturen, elf Meshes und einen Lampen-Blueprint unter den jeweiligen `Content/Art/*/WallCatalogue01`-Pfaden. Klares Glas kopiert den zuvor geprüften eigenen Substrate-Ansatz. Normalmaps werden als Normalmap importiert, Grünkanal für Unreal korrigiert. Ein LOD, Nanite aus. Materialslots beginnen stabil mit `WC01_`.

Wandleuchte: sichtbarer Leuchtkern und am selben Ort eine bewegliche Punktquelle, abschließend32lm/3000K/240cm, invers quadratischer Abfall, Raum-/Möbelschatten. Die zu starke erste Einstellung110lm/2900K/320cm wurde nach der tatsächlichen Unreal-Sichtprüfung reduziert. Gehäuse wirft keinen Schatten auf seine eingeschlossene Quelle; dies ist eine Prototypvereinfachung. Keine unsichtbaren Aufhelllichter und keine Änderung der Lab-Sonne. Brennstoff, Schalter, Feuerpartikel und Tageszeitlogik sind offen. `Blender_lamp_night.png` ist eine getrennte dunkle Lichtillustration, keine photometrische Gleichsetzung mit Unreal.

## Tatsächliche Prüfungen

- Quelle erneut geöffnet, alle externen Texturen aufgelöst, alle elf FBX in Blender zurückimportiert; Bounds, Dreieckzahlen, Materialslots und UCX-Anzahlen erhalten. Geschlossene Teilkörper, positive Gesamtvolumina, keine nichtmannigfaltigen Kanten/Nullflächen oder degenerierten UV-Dreiecke. Geschlossene überlappende Bauteile sind beabsichtigt; kein verschweißtes Einzelvolumen behauptet.
- Kalibriertes FBX_SCALE_NONE und `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Tatsächliche Unreal-Importdaten `FbxStaticMeshImportData`, keine Interchange-Abnahme. Alle Meshbounds, Dreiecke, Slots und konvexen Kollisionsanzahlen mit Quelle verglichen.
- Je Fensterwand echte einfache Sichtbarkeitsabfrage: Scheibe blockiert; nur die Scheibe ignoriert ergibt freien Durchblick durch die reale Öffnung; daneben blockiert die Wand. Anschlussprobe beiderseits X1000 cm trifft die Wand ohne Kollisionslücke.
- Alle401 zuvor vorhandenen Actors mit Position, Rotation, Skalierung, Ordner, Meshreferenzen und Material-Overrides exakt erhalten. Vorhandene nördliche Gebäudegrenze bei Y1900 cm erfasst; die neuen Wandkörper beginnen erst jenseits Y1970 cm.
- Datei-Hashvergleich gegen den kompletten vor diesem Auftrag erfassten Bestand: ausschließlich die autorisierte Lab-Karte darf abweichen. Neue Quellen und Content-Assets liegen in eigenen Bereichen. Keine Änderungen an Config, C++, Tools, Worldbuilding oder bisherigen Hausassets. Kein Commit/Push.
- Tatsächliche Blender- und Unreal-Ansichten unter `Previews/`; Kennzeichnung Blender_/UE_ unterscheidet die Renderer. Fehler in Streben-UVs wurden vor Export behoben; ein nicht exponierter Python-Getter im ersten Prüfaufruf wurde auf den dokumentierten Propertyzugriff korrigiert. Ein vorzeitiger Zwischencheck während der Lampenkorrektur ist kein Abschlussbeleg; maßgeblich ist die danach erneut erfolgreiche `unreal_verification.json`.

## Grenzen und nächste Auswahl

Die Varianten sind zur Auswahl und Weiterentwicklung bereit. Zusätzliche Rendergeometrie gegenüber dem einfachen Wandbudget ist hier bewusst sichtbar: B1012/1048 und C1672/1708 Dreiecke einschließlich Streben, Pfosten und einzelner Sockelsteine. Nach Auswahl Material-/Detailwirkung aus Spielentfernung und Wiederholung beurteilen, dann ggf. vereinfachen; keine Siedlungs-Performancefreigabe. Tisch1120, Stuhl752, Lampe616 Dreiecke. Fehlende Ecken, Endpfosten, Eingänge, Dachanschlüsse und der Hausgenerator sind separate Folgeschritte.

Kein Neustart und kein Verwerfen fremder ungespeicherter Pakete. Importdefaults und sitzungsweiser Interchange-Wert werden wiederhergestellt; Autosave bleibt im bereits zuvor pausierten Sitzungszustand. Gespeicherte Pakete wurden live geprüft, eine saubere Editor-Reload-Abnahme bleibt offen. Keine Gameplayfunktion für Möbel/Leuchte und kein vollständiger manueller Rundgang behauptet.
''',encoding='utf-8')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files),encoding='utf-8')
print('REVIEW_READY',len(data['assets']),'meshes;',len(data['imported_assets_sha256']),'Unreal assets;',len(baseline),'existing files checked;',len(files),'hashes')
