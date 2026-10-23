"""Seal B independently, proving that the completed A delivery stayed frozen."""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[4];CREATOR=ROOT.parent/'Creator'
A=REPO/'AssetSources/Architecture/EC_HighCultureCity/StreetStudy01/Refiner'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
m=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));assert m['status']=='refiner_verified'
for name in ['verification.json','Evidence/independent_verification.json','Evidence/openings_and_floor.json','Evidence/intake_verification.json','Evidence/interior_root_cleanup.json','Evidence/study_a_revalidation.json']:
    assert json.loads((ROOT/name).read_text())['status']=='passed',name
assert sha(ROOT/m['source_blend'])==m['source_blend_sha256']
for entry in m['exports']:assert sha(ROOT/entry['path'])==entry['sha256']
for name in ['01_eye_overview','02_house','03_plan','04_interior','05_connected_plan']:assert (ROOT/'Previews'/(name+'.png')).is_file()
baseline=json.loads((ROOT/'Evidence/preservation_before.json').read_text());changed=[];missing=[]
for name,digest in baseline['files'].items():
    p=REPO/name
    if not p.is_file():missing.append(name)
    elif sha(p)!=digest:changed.append(name)
assert not changed and not missing,(changed,missing)
a_files={}
for line in (A/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split(maxsplit=1);name=name.lstrip('* ');assert sha(A/name)==digest,('A changed',name);a_files[name]=digest
assert json.loads((A/'manifest.json').read_text())['status']=='review_ready'
creator_files={}
for line in (CREATOR/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split(maxsplit=1);name=name.lstrip('* ');assert sha(CREATOR/name)==digest;creator_files[name]=digest
preserved=dict(status='passed',files_before=len(baseline['files']),files_unchanged=len(baseline['files']),changed_existing=[],deleted_existing=[],
    creator_files_unchanged=len(creator_files),completed_study_a_unchanged=True,study_a_sha256sums_sha256=sha(A/'SHA256SUMS'),
    study_a_files_verified=len(a_files),existing_refiner_work_preserved=True,no_unreal_operations=True)
write('Evidence/preservation_after.json',preserved)
changes=m['refiner_changes'];before=sum(v['before']['triangles'] for v in changes.values());after=sum(v['after']['triangles'] for v in changes.values())
hulls=sum(len(e['collision_names']) for e in m['exports']);bevels={n:v['controlled_bevel_m'] for n,v in changes.items() if v['controlled_bevel_m']}
rejected=[n for n,v in changes.items() if v['bevel_rejected_to_preserve_contract']]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
proof=json.loads((ROOT/'Evidence/openings_and_floor.json').read_text());check=json.loads((ROOT/'verification.json').read_text())
cleanup=json.loads((ROOT/'Evidence/interior_root_cleanup.json').read_text())
assert m['refiner_revision']==2
for name,values in cleanup['changes'].items():
    m['refiner_changes'][name]['bounds_error_m']=values['bounds_error_m']
reference_file=m['reference_image'].get('file') or '../Creator/'+m['reference_image']['local_copy']
m.update(status='review_ready',accepted=False,refiner_revision=2,refiner_intake_head=head,
    status_note='Refiner source and all Blender FBX roundtrips verified; no Unreal or production acceptance',
    generator=dict(file='refine_study.py',sha256=sha(ROOT/'refine_study.py')),
    creator_verifier_dependency=dict(file='../Creator/build_study.py',sha256=sha(CREATOR/'build_study.py'),read_only=True),
    previews=[dict(file=p.relative_to(ROOT).as_posix(),sha256=sha(p),renderer='Actual Blender Cycles / AgX / 24 samples',visually_reviewed=True) for p in sorted((ROOT/'Previews').glob('*.png'))],
    reference_image=dict(file=reference_file,sha256=m['reference_image_sha256'],visually_inspected=True,read_only=True),
    preservation=preserved,verification=dict(file='verification.json',sha256=sha(ROOT/'verification.json')),
    refiner_summary=dict(unique_triangles_before=before,unique_triangles_after=after,ucx_before=hulls,ucx_after=hulls,
        controlled_bevels_m=bevels,bevels_rejected_to_preserve_contract=rejected,interface_changes_required=False,
        external_entrances=1,open_internal_connections=2,render_floor_connected_components=1),
    uv_policy='One UV0: 2m metric tiling, cylindrical projection of inner/outer core walls with a periodic seam per surface; planar caps/jambs and remaining assets. Intentional overlaps; no atlas/lightmap acceptance.')
write('manifest.json',m)
rows='\n'.join('| `'+n+'` | '+str(v['before']['triangles'])+' → '+str(v['after']['triangles'])+' | '+str(len(next(e for e in m['exports'] if e['asset_name']==n)['collision_names']))+' | '+('%.1f mm'%(1000*v['controlled_bevel_m']) if v['controlled_bevel_m'] else '–')+' |' for n,v in changes.items())
review=f'''# Refiner-Übergabe B – Baumkörper und Wurzelhof

Status **review_ready**, nicht accepted. Kit `{m['kit_id']}`, Modul `{m['module_id']}`, Creator-Revision **2**, Interface **0.2** unverändert; eigene Refiner-Revision 2.

Eingangscommit **`{m['input_commit']}`**, gezielte Übernahme nach vollständigem Abschluss von A: **`{head}`**. Eingangsquelle SHA-256 **`{m['input_source_sha256']}`**. 41 Lieferhashes und 34 vollständige LFS-Objekte gegen den Commit geprüft. Die abgeschlossene A-Lieferung ist einschließlich aller {len(a_files)} versiegelten Dateien und ihrer Prüfsummenliste unverändert.

## Erhaltene Zusammenstellung

Die eigene editierbare [CourtyardStudy01_Refined.blend](CourtyardStudy01_Refined.blend) begann als byteidentische Eingangskopie. Älterer Baumkörper, zwei Wohnflügel, sämtliche **{len(m['placement_instances'])} Instanztransforms**, Pivots, lokale Maße und Slots sind erhalten. Keine neue Lore-, Kultur-, Architektur- oder Nutzungsfestlegung. Die Bildreferenz ist visuelle Richtung, kein maßhaltiger Bauplan.

- **Genau ein äußerer Haupteingang** am zentralen Baumkörper; genau ein äußeres Türblatt in der Szene.
- Kleine Fenster an beiden Wohnflügeln, geschlossene Brüstungen an den ehemaligen Außentürstellen.
- **Zwei offene Innenverbindungen** durch die jeweils zwei beteiligten Wandlagen.
- **Ein zusammenhängender Renderboden auf Z0**, drei unveränderte einfache Boden-UCX mit absichtlicher Überdeckung am gleichen Niveau.
- Flügelzentren weiterhin `(-5.5,3.70,0)` / `(5.5,3.70,0)` m, Drehungen −12° / +12°; zentraler Ursprung `(0,3,0)` m.

## Technische Verfeinerung

Topologie, geschlossene Komponenten, positive Volumen und Normalen geprüft. Koplanare Bereinigung reduziert den gemeinsamen Renderboden **204 → 164 Dreiecke**, ohne seinen zusammenhängenden Aufbau oder das Z0-Niveau zu ändern. Strukturöffnungen und Kollisionsgeometrie bleiben erhalten. Normale fester Teile sind gewichtet gebacken; organische Rinden-/Wurzelkörper verwenden gleichmäßige Glättung mit harten Kappen und Kanten ab 45°. Laub/Kräuter bleiben weich geglättet, ohne störende Flächengewichtung.

Vier kleine zweistufige Rundungen: Türblatt 3 mm, vorhandener Wurzel-Türbogen 2 mm, Fensterladen 3 mm und Bank 4 mm. Zwei andere Versuche wurden durch die Vertrags-/Topologieprüfung zurückgenommen. Keine zusätzlichen Ornamente. Struktur-Bounds bleiben innerhalb 0,000001 m zum Eingang; die ausdrücklich beauftragte Innenkorrektur zweier Dekorgruppen ist unten getrennt ausgewiesen.

### Innenkorrektur in Refiner-Revision 2

Die in Revision 1 sichtbaren abgeschnittenen Enden von `OldButtressRoots` und `LinkingRootArches` im zentralen Raum wurden geometrisch entfernt. Jeder vorhandene geschlossene Wurzelkörper wurde einzeln gegen eine 40-seitige Freihaltezone geschnitten: Radius 2,24 m, Z −0,10 bis 4,30 m, konzentrisch zur bestehenden Innenwand mit Radius 2,20 m. Die neuen Abschlussflächen liegen innerhalb der bestehenden Wandstärke. Keine zusätzliche Blende und keine versteckte Render-Ersatzgeometrie.

Alle unveränderten Instanzmatrizen, Pivots, Strukturteile, Slots und 158 UCX bleiben exakt erhalten. Die entfernte Spitze von `LinkingRootArches` verkleinert ausschließlich dessen dekorative lokale Bounds: **Z-Min +0,0199177265 m**, **Y-Max −0,0365405083 m**. Das ist keine Änderung eines Anschlusses oder der äußeren Haussilhouette. Andere Bounds dieser Gruppe sowie sämtliche Bounds von `OldButtressRoots` bleiben erhalten. [Prüfbeleg](Evidence/interior_root_cleanup.json) dokumentiert Vorher/Nachher, positive geschlossene Volumen, nicht entartete UVs und echte Oberflächenproben außerhalb Radius 2,60 m. Die beiden betroffenen FBXs wurden aus der gespeicherten Quelle erneuert. Strukturöffnungen werden nicht mit einem Dekorteil geschlossen.

UV0 ist nicht entartet. Innen-/Außenwand des runden Baumkörpers erhalten eine metrische zylindrische Abwicklung mit je einer periodischen Naht; Kappen und radiale Laibungen bleiben planar. Die übrigen Teile nutzen konsistente metrische Projektionen mit dem bestehenden 2-m-Kachelmaß. Absichtliche Kachelüberschneidungen sind dokumentiert; kein Produktionsatlas oder finaler Lightmap-Kanal.

**Einzigartige Render-Dreiecke: {before} → {after}**. Einfache UCX-Körper: **{hulls} → {hulls}**, Geometriefingerprints exakt erhalten. Bibliothekswerte, keine Siedlungs-/Draw-Call-/Laufzeitmessung.

| Asset | Dreiecke vorher → nachher | UCX | Rundung |
| --- | ---: | ---: | ---: |
{rows}

## Tatsächliche Prüfbelege

- [Eingangsprüfung](Evidence/intake_verification.json): SHA256SUMS, LFS-OIDs/Dateigrößen und Creator-Bytes gegen Eingangscommit.
- [Vorher/Nachher](Evidence/refinement.json): Maße, UVs, geschlossene Komponenten und Volumen; exakte Instanzmatrizen und UCX-Fingerprints erhalten.
- [Quell-/FBX-Prüfung](verification.json) und [unabhängige Messung](Evidence/independent_verification.json): eigene gespeicherte Quelle in frischem Prozess erneut geöffnet; alle **27 FBX** zurückimportiert, Einheiten, Bounds, Identitätstransforms/Pivots, Slotfolge, UVs, endliche Einheitsnormalen und konvexe UCX geprüft. Alle Prüfungen bestanden.
- [Erneute Prüfung von A](Evidence/study_a_revalidation.json): versiegelte A-Quelle erneut geöffnet, alle 21 FBX samt UCX rückimportiert; keine A-Datei verändert. Quelle, Pivots, Instanzen, Slots, Topologie, Normalen, UVs, Bounds und konvexe Kollision bestanden.
- Der ursprüngliche Prüfer bestätigt genau ein äußeres Türblatt, eine verbundene Bodenkomponente, neun freie Render-/UCX-Strahlen je Zugang, 96 Bodenproben je Innenweg und Darstellung sowie geschlossene ehemalige Außentüren. Zusätzlich **{check['central_room_enclosure']['rays']} radiale Renderstrahlen** auf 1,0/2,2 m Höhe schließen unbeabsichtigte zentrale Außenöffnungen außerhalb des Haupteingangs aus.
- [Dichtere Innenweg-/Fenster-/Bodenprüfung](Evidence/openings_and_floor.json): je Verbindung **144 freie Strahlen pro Darstellung** im 1,2 m breiten Prüfbereich bis 2,2 m Höhe durch reale Rendergeometrie einschließlich Dekor und durch UCX; **704 Bodenproben pro Verbindung und Darstellung** entlang/beiderseits des Übergangs. Maximale Z0-Abweichung etwa **0,000000060 m**. Sieben kleine Öffnungen an den drei eindeutigen Flügelwandtypen geprüft; Brüstungen und Stürze geschlossen.
- [Erhaltung](Evidence/preservation_after.json): **{len(baseline['files'])} bereits vorhandene Dateien byteidentisch**, einschließlich vollständiger Studie A, altem Musterhaus, Content, Konfiguration und gemeinsamen Tools. Creator B ebenfalls unverändert.

Dies sind reale DCC- und stichprobenartige Geometrieprüfungen, **keine kontinuierliche Spielerkapsel- oder Unreal-Abnahme**. Die nominellen Öffnungsmaße sind keine Aussage über jede Kamera-/Kapseltrajektorie.

## Echte Ansichten

[Außenübersicht](Previews/01_eye_overview.png) · [Flügelansicht](Previews/02_house.png) · [Aufsicht](Previews/03_plan.png) · [Innenverbindung](Previews/04_interior.png) · **[Schnittaufsicht](Previews/05_connected_plan.png)**.

Echte Cycles-Render, 24 Samples, AgX, dieselbe neutrale Tagesbeleuchtung wie im Eingang. Innen nutzt eine temporäre neutrale Prüfaufhellung; das ist kein geplantes Gebäudelicht. Die Schnittaufsicht blendet Dach-/Baum-/Dekormassen aus und schneidet die tatsächlichen Wände temporär bei Z1,80 m. Diese Prüfdarstellung wird **nicht in der Quelle gespeichert**; das editierbare Modell bleibt vollständig. Keine AI-Abbildung oder abweichende Render-only-Architektur.

## Übergabe und Grenzen

27 eigene FBX unter [Exports/](Exports/). Kalibriertes Profil unverändert: **FBX_SCALE_NONE**, global_scale 1, Metric Unit Scale 1, Forward -Y / Up Z, `UE_cm=(100*B.x,-100*B.y,100*B.z)`. Keine zusätzliche Spiegelung oder negative Objektskalierung. Materialslots bleiben in identischer Reihenfolge. Blender 5.2.2 LTS.

Die Blender-Prüfmaterialien und ihr prozedurales Bump sind keine fertigen Unreal-Materialien. Kleine Glasflächen, Vegetation, überlappende Dekorkomponenten, fehlende Dekorkollision, finale Texturen/Lightmaps und LODs bleiben Prototypgrenzen. Die 158 kleinen Strukturhüllen wurden bewusst nicht eigenständig umgebaut; Optimierung und vollständige Kapsel-/Kameraprüfung sind spätere Aufgaben.

Die bisher deutlich in den zentralen Raum ragenden Endkappen der beiden Wurzelgruppen sind in der neuen Innenansicht entfernt. Die einfache strukturelle Wand-/Bogenverbindung und die übrigen überlappenden Studiengruppen bleiben gestalterisch vorläufig; keine fertige Innenausstattung oder ausmodellierte Produktionsarchitektur behauptet.

**Nicht durchgeführt:** Unreal-Import/Reimport, Interchange, Karten-/Blueprint-/Materialänderungen, PIE, Packaging/Cooking, Multiplayer, Siedlungsperformance und finale Art-/Produktionsabnahme. Keine Schnittstellenänderung erforderlich. Der anschließende Nutzerauftrag erlaubt einen gezielten Commit beider geprüfter Refiner-Lieferungen; fremde Änderungen und Unreal-Dateien sind davon ausgeschlossen. Kein Push beauftragt.

Reproduktion: `refine_study.py -- --mode prepare` (bei existierender, hashgeprüfter Lieferung nur nach ausdrücklichem Auftrag mit `--revise`), danach `resolve_interior_roots.py`, `refine_study.py -- --mode verify`, `check_clearances.py` und `refine_study.py -- --mode render` in frischem Blender. `reexport_roots.py` erneuert bei Bedarf ausschließlich die beiden Dekorexporte aus der gespeicherten Quelle. Fehlgeschlagene explorative Schnitte, UV-Projektionen und eine leere FBX-Auswahl wurden korrigiert; maßgeblich sind die anschließend vollständig bestandenen Prüfungen. Der Creator-Prüfer wird nur gelesen und auf diesen eigenen Refiner-Pfad gebunden. [Manifest](manifest.json) und [SHA256SUMS](SHA256SUMS) enthalten Herkunft, Werte und Dateihashes.
'''
(ROOT/'REVIEW.md').write_text(review,encoding='utf-8',newline='\n')
(ROOT/'.gitattributes').write_text('# Stable delivery bytes.\n*.py text eol=lf\n*.md text eol=lf\n*.json -text\nSHA256SUMS text eol=lf\n.gitattributes text eol=lf\n',encoding='utf-8',newline='\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts and not p.name.endswith('.blend1'))
(ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
print('REFINER_B_DELIVERY_SEALED',len(files),before,after,hulls,'A_FROZEN',len(a_files))
