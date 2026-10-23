from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;repo=R.parents[6]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((R/n).read_text(encoding='utf8'))
def write(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
base=read('Evidence/files_before.json');changed=[p for p,h in base.items() if not (repo/p).exists() or sha(repo/p)!=h];assert changed==['Content/Prototype/Maps/Lvl_AssetLab.umap'],changed
for n in ['blender_verification','unreal_verification','white_unreal']:assert read('Evidence/'+n+'.json')['status']=='passed'
d=read('manifest.json');assert sha(R/d['source'])==d['source_sha256'];assert sha(Path(d['input_source']))==d['input_sha256']
packages={p:sha(repo/('Content/'+p.removeprefix('/Game/')+'.uasset')) for p in read('Evidence/white_unreal.json')['new_materials']}
write('Evidence/preservation.json',dict(status='passed',files_checked=len(base),changed=changed,new_materials=packages))
d.update(status='review_ready',accepted=False,scope='Detailed white stone on former left BEFORE comparison actor only; warm comparison on right and all houses preserved.',unreal_materials=packages,texture_mesh_imports=0,geometry_uv_collision='unchanged',pending=['User visual review','Inherited production/performance and clean editor reload checks'])
write('manifest.json',d)
(R/'REVIEW.md').write_text('''# Weiße Steindetails – Variante 03

Status: **review_ready**. Nutzerauftrag: die helle Farbe der bisherigen linken Wand mit den Oberflächendetails der neuen Materialstudie verbinden.

Links im Refiner-Lab steht nun „WEISS / MIT DETAILS“. Die warme Variante rechts bleibt unverändert. Drei eigene Steinmaterialien korrigieren ausschließlich die Grundfarbe der detaillierten Texturen auf eine visuell neutralweiße Abstimmung: Zielwerte Ivory (0.82, 0.83, 0.82), CarvedStone (0.86, 0.87, 0.86), RecessStone (0.60, 0.64, 0.64), jeweils linear mit 0.96 Helligkeitsfaktor. Faktoren anhand der gemessenen Texturmittelwerte kalibriert; Farbdetails bleiben erhalten. Fugen, mineralische Variation, Normalen und Rauheit der Materialstudie 02 bleiben erhalten. Gold, Azur und Glas verwenden deren bestehende Materialreferenzen. Keine zusätzlichen Texturen, Meshes oder Importe.

Eigene Blender-Kopie mit weißer Variante links und warmer rechts. Bestehende Quelldateien unverändert, Texturpfade relativ auf MaterialStudy_02. Geometrie und UVs nach erneutem Öffnen für alle sechs Komponenten verglichen; Texturpfade geprüft. Unreal-Meshes und Kollisionskörper unverändert. Alle vorhandenen Actors auf Transform, Meshreferenzen und Overrides geprüft: ausschließlich Material-Overrides der linken Vergleichswand sowie deren Beschriftung geändert. Alle vorher vorhandenen Dateien bytegleich außer der ausdrücklich bearbeiteten Lab-Karte. Belege und Hashes in Evidence/, manifest.json und SHA256SUMS.

Ansichten in Previews/ zeigen den tatsächlichen Blender-/Unreal-Vergleich. Häuser und bestehende gemeinsame Materialien bleiben unverändert. Kein Commit oder Push. Künstlerische Abnahme und die bisherigen Produktions-/Performanceprüfungen sowie ein späterer sauberer Editor-Neustart bleiben offen; kein Verwerfen vorhandener ungespeicherter Editorzustände.
''',encoding='utf8')
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and p.suffix not in ['.pyc','.blend1'])
(R/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in files))
print('WHITE_STONE_REVIEW_READY',len(files),'files;',len(base),'existing files checked')

