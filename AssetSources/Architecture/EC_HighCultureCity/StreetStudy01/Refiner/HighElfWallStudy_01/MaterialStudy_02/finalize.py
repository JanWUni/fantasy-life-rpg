from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[6]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text(encoding='utf8'))
def write(n,v):(ROOT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
assert REPO==Path('E:/Business/fantasy-rpg-refiner')
assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()=='assets/refiner'
base=read('Evidence/files_before.json');changed=[p for p,h in base.items() if not (REPO/p).is_file() or sha(REPO/p)!=h]
assert changed==['Content/Prototype/Maps/Lvl_AssetLab.umap'],changed
for n in ['blender_verification','unreal_verification','import_materials','place_comparison','tint_glass']:
    assert read('Evidence/'+n+'.json')['status']=='passed',n
packages={p:sha(REPO/('Content/'+p.removeprefix('/Game/')+'.uasset')) for p in read('Evidence/import_materials.json')['saved']}
assert len(packages)==24
write('Evidence/preservation.json',dict(status='passed',existing_files_checked=len(base),existing_files_changed=changed,existing_actors_preserved=read('Evidence/unreal_verification.json')['existing_actors_preserved'],new_package_hashes=packages,map_sha256=sha(REPO/changed[0])))
m=read('manifest.json');assert sha(ROOT/m['source'])==m['source_sha256'];assert sha(ROOT.parent/'HighElf_WallVariants_01.blend')==m['input_sha256']
m.update(status='review_ready',accepted=False,base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),unreal=dict(blueprint=read('Evidence/import_materials.json')['blueprint'],map='/Game/Prototype/Maps/Lvl_AssetLab',new_packages=packages,mesh_imports=0,old_geometry_reused=True),pending=['Artist review of stone tone/grain and still subtle glass readability under lab daylight','Transfer to ornate B, solid wall and door wall only after material direction review','Clean editor/map reload after preexisting dirty packages are resolved; no forced restart','Production lighting including indoor daylight, texture budget/performance, LOD/cook validation'])
write('manifest.json',m)
review='''# Materialstudie 02 – einfache Hochelfenwand

Status: **review_ready**, keine Abnahme und keine Produktionsfreigabe.

## Ergebnis

Eigene A-Wand als Vorher-/Nachhervergleich in Blender und im Refiner-Lab. Heller Werkstein mit fein gefugten 75 × 50 cm Steinlagen, mineralischer Farbvariation, Poren und separaten Normal-/Rauheitskarten. Geschnitzte Profile haben eine eigene Oberfläche ohne Mauerfugen; Gold hat leichte Rauheitsvariation. Die beiden bestehenden Wandvarianten und Häuser behalten ihre bisherigen Materialien.

Das Fenster enthält eine echte geschlossene Glasscheibe: 104 Dreiecke, etwa 1 cm Dicke und separate Kollision. Die neue Glasoberfläche verwendet Substrate SimpleVolume, F0 0.045, Transmittance RGB 0.78/0.89/0.94, Normal- und Rauheitskarten, SSR sowie PixelNormalOffset 1.06. Durchsicht bleibt erhalten. Die Glaswirkung ist im hellen offenen Lab weiterhin zurückhaltend; Nahaufnahmen zeigen leichte Lichtbrechung. Kräftige Spiegelungen oder ein bereits abgestimmtes finales Glas werden nicht behauptet. Glas wirft vorläufig keinen Schatten, damit Tageslicht passieren kann; physikalische Innenraumbeleuchtung ist damit nicht nachgewiesen.

## Umfang und Vorher/Nachher

| Merkmal | Vorher | Materialstudie |
|---|---|---|
| Wandgeometrie | 3.912 Dreiecke, 6 Komponenten | identisch |
| Kern / Fensteröffnung | 300 × 24 × 320 cm / 65 × 90 cm | identisch |
| Pivot, UV0, Profile, Kollision | vorhandener A-Stand | identisch wiederverwendet |
| Stein | weitgehend gleichfarbig | Farb-, Rauheits- und Normaldetails |
| Materialzuweisung | vorhandene HE01-Materialien | eigene HE02-Komponenten-Overrides |

Keine neuen Meshimporte oder Reimports. 24 neue Unreal-Pakete: 17 Texturen, 6 Materialien, 1 Blueprint. Steintexturen 2048², Gold/Azur/Glas 1024². 18 Quell-PNGs; die unbenutzte Glas-BaseColor-Vorschau wird nicht in Unreal importiert. Blender verwendet für die Glastönung einen konstanten Farbwert und IOR 1.52, Unreal eine engineeigene transparente Schattierung; keine Pixelgleichheit zugesichert.

## Nachweise

- `Evidence/blender_verification.json`: gespeicherte Quelle erneut geöffnet; Geometrie und UVs aller sechs Komponenten exakt gegenüber dem enthaltenen Vorherstand verglichen; Texturpfade aufgelöst.
- `Evidence/unreal_verification.json`: sechs unveränderte Meshreferenzen, eigene Material-Overrides, Einheitsskalierung, Texturfarbräume und Normal-Konvention geprüft. Kollisionstraces treffen die Scheibe von beiden Seiten sowie Wandkörper an Seiten, Brüstung und Sturz.
- `Evidence/inspect_glass.json`: tatsächliche Verdrahtung und finale Parameter des Glasmaterials gelesen. `refine_glass.json` und `tint_glass.json` dokumentieren die Materialkorrekturen.
- `Previews/UE_Vergleich.png`, `UE_Glas_Aussen.png`, `UE_Glas_Innen.png`: tatsächliche Unreal-Ansichten. `Blender_Materialvergleich.png`: gerenderte eigene Quelle. Bilder visuell geprüft.
- `Evidence/preservation.json`: alle vorhandenen geprüften Dateien unverändert außer der ausdrücklich bearbeiteten Lab-Karte; 441 vorhandene Actors samt Transform, Ordner, Meshreferenzen und Overrides erhalten. Vier neue Actors: zwei Vergleichswände und zwei Beschriftungen bei X 1600/2200, Y 1500 cm.
- Eingangs-/Quellhash, Ausgangscommit und neue Unreal-Pakethashes stehen in `manifest.json`; lokale Lieferung in `SHA256SUMS`.

## Offen

Künstlerische Beurteilung der Steinfarbe/-körnung und der noch dezenten Glaswirkung. Erst danach Übertragung auf die prachtvolle Variante sowie Ausbau zur geschlossenen Wand und Türwand. Noch keine Änderung an den Häusern. Produktionsbudget, LOD/Cook und Innenraumlicht bleiben offen.

Ein sauberer Editor-/Kartenneustart wurde wegen bereits bestehender ungespeicherter Pakete nicht erzwungen. Nur eigene neue Pakete und die Lab-Karte gespeichert; kein Save-All, kein Verwerfen fremder Zustände, kein Commit oder Push. Projektkonfiguration und gemeinsame Meshes/Materialien unverändert.
'''
(ROOT/'REVIEW.md').write_text(review,encoding='utf8')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and p.suffix not in ['.pyc','.blend1'])
(ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf8')
print(json.dumps(dict(status='review_ready',files=len(files),preserved_existing_files=len(base)-1,new_packages=len(packages))))
