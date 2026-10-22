"""Build delivery metadata and verify write scope. Never changes Git state."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[4]
REL=ROOT.relative_to(REPO).as_posix()
NAME='SM_EB_WallInner_R255_A30_H280'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path,value):
    assert path.resolve().is_relative_to(ROOT)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def git(*args):
    return subprocess.check_output(['git','--no-optional-locks',*args],cwd=REPO).decode()

def main():
    intake=read(ROOT/'Evidence/input_verification.json')
    refinement=read(ROOT/'Evidence/refinement.json')
    verification=read(ROOT/'verification.json')
    creator=read(ROOT/'Evidence/Input/manifest.json')
    baseline=read(ROOT/'Evidence/preservation_before.json')
    assert verification['status']=='passed'
    assert all(sha(ROOT/p)==h for p,h in verification['output_sha256'].items())
    assert all(sha(ROOT/'Evidence/Input'/p)==h for p,h in intake['files'].items())
    assert git('branch','--show-current').strip()=='assets/refiner'
    assert git('rev-parse','HEAD').strip()==baseline['head']
    changed=[p for p,h in baseline['files'].items() if not (REPO/p).is_file() or sha(REPO/p)!=h]
    assert not changed,changed
    statuses=[x for x in git('status','--porcelain=v1','-z','--untracked-files=all').split('\0') if x]
    assert all(x.startswith('?? '+REL+'/') for x in statuses),statuses
    preservation={'status':'passed','tracked_files_checked':len(baseline['files']),
        'tracked_files_changed':changed,'head_before_and_after':baseline['head'],'branch':'assets/refiner',
        'new_files_only_under':REL+'/', 'git_index_unchanged':True,
        'input_snapshot_hashes_reverified':True,'source_and_export_hashes_reverified':True,
        'method':'SHA-256 of every tracked file before intake and after Blender work; final porcelain status has only untracked files under the authorized Refiner directory',
        'unreal_started':False,'creator_checkout_or_cherry_pick_performed':False}
    write(ROOT/'Evidence/preservation_after.json',preservation)
    manifest=copy.deepcopy(creator)
    manifest.update({'role':'Asset Refiner','revision':1,'status':'review_ready',
        'allowed_write_directory':REL,'base_commit':baseline['head'],
        'input_revision':{'commit':intake['commit'],'path':intake['creator_path'],'creator_revision':intake['creator_revision'],
                          'creator_base_commit':intake['creator_base_commit'],'sha256':intake['files']},
        'sources':{'blend':NAME+'.blend','fbx':'Exports/'+NAME+'.fbx','refinement_script':'refine_wall.py'},
        'changes':['UV0 remapped to uniform physical density with six non-overlapping padded charts',
                   'Existing chart boundaries marked as authoring seams; Refiner provenance metadata added'],
        'geometry_normals_transforms_unchanged':True,'interface_change_required':False,
        'before':refinement['before'],'after':refinement['after'],
        'bounds_ue_cm':verification['source']['bounds_ue_cm'],
        'review':'REVIEW.md','previews':['Previews/two_modules.png','Previews/two_modules_outer.png',
                                     'Previews/uv_before.png','Previews/uv_after.png'],
        'evidence':{'intake':'Evidence/input_verification.json','refinement':'Evidence/refinement.json',
                    'verification':'verification.json','preservation':'Evidence/preservation_after.json'},
        'sha256':{p:sha(ROOT/p) for p in [NAME+'.blend','Exports/'+NAME+'.fbx','refine_wall.py','prepare_delivery.py','finish_delivery.py']},
        'verification':{'file':'verification.json','sha256':sha(ROOT/'verification.json')},
        'integration_approval':None})
    manifest['uv'].update({'layout':refinement['packing']['layout'],'overlap':'none above 1e-9 UV-area numerical tolerance',
        'density_max_min_ratio':refinement['after']['uv']['density_max_min_ratio'],
        'max_triangle_anisotropy':refinement['after']['uv']['max_triangle_anisotropy'],
        'minimum_chart_bbox_gap_uv':refinement['after']['uv']['minimum_chart_bbox_gap_uv'],
        'occupied_uv_area':refinement['after']['uv']['occupied_uv_area'],
        'seam_edges_marked':refinement['packing']['seam_edges_marked'],
        'packing':refinement['packing']})
    manifest['collision']['difference_from_creator']='none: same ten source-owned convex prisms; exact positions, normals and topology retained'
    manifest['export']['validation']='passed: Refiner source reopened, FBX Blender roundtrip and per-corner UV preservation; no Unreal import'
    # Interface metadata is copied without recomputation or coordinate rounding.
    for key in ('kit_id','module_id','interface_version','profile','pivot','object_transform_blender',
                'joins_ue_cm_degrees','joins_blender_m_degrees','tolerances','material_slots'):
        assert manifest[key]==creator[key],key
    write(ROOT/'manifest.json',manifest)
    b,a=refinement['before'],refinement['after']
    uvb,uva=b['uv'],a['uv']
    report=f'''# Refiner-Review: Innenwand R255 / A30 / H280

Stand: 22. Oktober 2026. **Status: `review_ready`**, Refiner-Revision 1. Keine Integrationsfreigabe (`accepted`).

## Auftrag, Herkunft und Schreibzuständigkeit

- Asset: `{NAME}`; KitId `EB.Blatthof.R255_R640`; ModuleId `WallInner_R255_A30_H280`; InterfaceVersion **1**.
- Eingangsrevision: **`{intake['commit']}`**, Creator-Revision 1.
- Creator-Pfad im Commit: `{intake['creator_path']}`.
- Creator-Basis: `{intake['creator_base_commit']}`. Refiner-Worktree: `E:/Business/fantasy-rpg-refiner`, Branch `assets/refiner`, HEAD unverändert `{baseline['head']}`.
- Ausschließlicher Schreibbereich: `{REL}/`.

Die Lieferung wurde direkt aus dem bezeichneten Git-Commit gelesen; LFS-Payloads wurden anhand ihrer OIDs und Größen aus der lokalen Objektablage verifiziert. Kein Checkout, Cherry-Pick oder Branchwechsel. Alle **acht** Einträge aus Creator-`SHA256SUMS` stimmen, ebenso die Querverweise in Manifest und Prüfbericht. Eine bytegleiche Eingangskopie liegt isoliert unter `Evidence/Input/`; sie ist ein Prüfbeleg, kein alternativer Creator-Arbeitsbereich. Das archivierte `create_wall.py` wurde nicht ausgeführt.

| Eingangsdatei | SHA-256 |
| --- | --- |
| Blender-Quelle | `{intake['files'][NAME+'.blend']}` |
| FBX | `{intake['files']['Exports/'+NAME+'.fbx']}` |
| manifest.json | `{intake['files']['manifest.json']}` |
| verification.json | `{intake['files']['verification.json']}` |

Vollständige Dateiliste einschließlich HANDOFF und SHA256SUMS: [input_verification.json](Evidence/input_verification.json). Die eigene Quelldatei wurde zunächst als bytegleiche Kopie übernommen und anschließend ausschließlich im Refiner-Ordner gespeichert.

## Befund und gezielte Verbesserung

Topologie, Split-Normalen und zehn konvexe Kollisionskörper bestanden die unabhängige Prüfung bereits im Eingang. Deshalb wurden keine Vertices, Flächen, Profile, Normalen oder Kollisionskörper verändert und keine Rundungen/Ornamente ergänzt. Der direkte Vergleich sämtlicher Vertexpositionen, Polygonindizes, Ecknormalen, Glättungsflags und Objektmatrizen vor/nach der Bearbeitung ist exakt gleich.

Die bisher gleich groß belegten sechs UV-Kacheln skalierten unterschiedlich große reale Flächen verschieden stark und verzerrten besonders Ober-/Unterkante. UV0 wurde deshalb metrisch neu abgewickelt: Seiten nach tatsächlicher summierter Segmentsehnenlänge und Höhe, Ober-/Unterseite durch verzerrungsfreie XY-Projektion, Stirnseiten in ihrer radialen Ebene. Alle sechs Charts werden gemeinsam gleichmäßig skaliert und mit Abstand gepackt. {refinement['packing']['seam_edges_marked']} vorhandene Kanten tragen jetzt passende UV-Nahtmarkierungen. Hinzu kommen Herkunftsmetadaten am Renderobjekt; die Schnittstellenmetadaten bleiben erhalten.

| Kennzahl | Creator-Eingang → Refiner |
| --- | --- |
| Render-Vertices / editierbare Quads | 44 / 42 → 44 / 42 |
| Dreiecke nach Triangulierung / im FBX | 84 → 84 |
| Materialslots / Texturen | 1 / 0 → 1 / 0 |
| UV-Kanäle / Inseln | 1 / 6 → 1 / 6 |
| Verhältnis höchste/niedrigste lineare UV-Dichte | {uvb['density_max_min_ratio']:.8f} → {uva['density_max_min_ratio']:.8f} |
| Maximale Dreiecks-Anisotropie (1 = unverzerrt) | {uvb['max_triangle_anisotropy']:.8f} → {uva['max_triangle_anisotropy']:.8f} |
| Belegte UV-Fläche | {100*uvb['occupied_uv_area']:.3f}% → {100*uva['occupied_uv_area']:.3f}% |
| Kleinster Abstand der Insel-Boundingboxen | {uvb['minimum_chart_bbox_gap_uv']:.8f} → {uva['minimum_chart_bbox_gap_uv']:.8f} UV |
| UCX-Körper / UCX-Dreiecke | 10 / 120 → 10 / 120 |
| Gelieferte LODs / beabsichtigtes Nanite | 1 / aus → 1 / aus |

Die geringere UV-Belegung ist die bewusste Folge der einheitlichen Dichte und verzerrungsfreien Charts. Der Abstand entspricht bei einer lediglich beispielhaften 1024²-Textur ungefähr {1024*uva['minimum_chart_bbox_gap_uv']:.2f} Pixeln; es wurde keine Texturgröße oder spätere Mip-/Produktionsvorgabe festgelegt. UV0 ist kein geprüfter Lightmap-Kanal. Render-Vertexzahl und UV1 in Unreal bleiben unbekannt.

## Unveränderter Maß-, Pivot- und Anschlussvertrag

- Radien **245–265 cm**, Referenzradius **255 cm**, 30°, Höhe **280 cm**, Unterkante Z0, zehn 3°-Segmente; geschlossene Vollwand ohne Öffnungen.
- R255-Startpivot am Ursprung, X tangential, Unreal Y zum Kreismittelpunkt, Z oben. Kreismittelpunkt lokal UE `(0,255,0)` cm. Alle Render-/UCX-Objekte Position/Rotation Null, Skalierung Eins, positive Determinante.
- `Join_A`: Position `(0,0,0)`, auswärts Yaw 180°.
- `Join_B`: Position `(127.49999999999999,34.16352203496813,0)` cm, auswärts Yaw 30°. Diese Werte sind aus dem Eingangsmanifest übernommen, nicht neu gerundet.
- Zweite Blender-Instanz: `(1.275,-0.3416352203496813,0)` m, Z-Rotation −30°. Grenzwerte 0,1 cm / 0,1°. Endprofile einschließlich der vorhandenen geschlossenen Stirnflächen erhalten.
- Slot 0 **Ivory** → `/Game/Art/Materials/ElvenBlatthof/MI_Blatthof_Ivory`; ein UV-Kanal UV0; zehn unveränderte `UCX_{NAME}_00` bis `_09`, beabsichtigter UE-Modus `UseSimpleAsComplex`.
- Lokale UE-Bounds aus der erneut geöffneten Quelle: Min `{verification['source']['bounds_ue_cm'][0]}`, Max `{verification['source']['bounds_ue_cm'][1]}` cm.

Kein Schnittstellenänderungsbedarf festgestellt. Kein Boden-/Dachteil mitgeliefert; die bestehenden Dachfüllungen wurden weder bearbeitet noch gemeinsam geprüft.

## Tatsächlich ausgeführte Prüfungen und Ansichten

Blender **{verification['blender']}**, Build `{verification['build']}`; eingebautes FBX-Add-on `io_scene_fbx`, keine externen Texturen/Bibliotheken. Der Prüfcode verwendet analytische Profilpunkte und eigene Topologie-/UV-Prüfungen, ohne den Creator- oder Bestandsgenerator auszuführen.

| Prüfung | Ergebnis / Beleg |
| --- | --- |
| Eingangsdateien und eigene Kopie | Alle Hashes bestanden; `Evidence/input_verification.json` |
| Topologie und Volumen | Quelle und Rückimport geschlossen, konsistent nach außen orientiert, keine degenerierten Flächen/ko­inzidenten Vertices; `verification.json` |
| Profil, Endpunkte und Naht | Maximale analytische Profilabweichung Quelle {verification['source']['analytic_profile_max_error_cm']:.10f} cm; Rückimport {verification['fbx_roundtrip']['analytic_profile_max_error_cm']:.10f} cm |
| Zwei passende Instanzen | Nahtabweichung Quelle {verification['source']['two_instance_seam_error_cm']:.10f} cm; Rückimport {verification['fbx_roundtrip']['two_instance_seam_error_cm']:.10f} cm |
| Normalen | Jede radiale Ecknormale, jede harte Planfläche und transformierte Nahtnormale geprüft; keine Änderung am Eingang |
| UV0 | Sechs Inseln, endlich/nicht degeneriert, Bereich 0…1; alle Dreieckspaare auf Überdeckungsfläche > 1e-9 UV² geprüft: keine; Dichte/Verzerrung gemessen |
| Einfache Kollision | Zehn geschlossene konvexe 3°-Prismen, Segmentpunkte analytisch passend, positive Volumina; Volumensumme entspricht Renderkörper; unverändert |
| Gespeicherte eigene Quelle | In separatem Blender-Prozess neu geöffnet; sämtliche Nachherwerte stimmen exakt mit dem Bearbeitungslauf überein |
| Eigenes FBX | In leere Blender-Szene zurückimportiert: 84 Renderdreiecke, zehn UCX, Ivory/UV0/Profil/Normalen erhalten; maximaler UV-Eckfehler {verification['roundtrip_max_corner_uv_error']:.10f}; Binärversion {verification['fbx_binary_version']} |
| Erhaltungsnachweis | {len(baseline['files'])} vorher versionierte Dateien SHA-256-identisch; alle neuen Dateien ausschließlich im erlaubten Refiner-Bereich; `Evidence/preservation_after.json` |

Sichtprüfung der finalen Blender-Ansichten: [zwei Module innen](Previews/two_modules.png), [außen und Endprofil](Previews/two_modules_outer.png), [UV0 vorher](Previews/uv_before.png), [UV0 nachher](Previews/uv_after.png). Die Wandansichten zeigen durchgehende Kontur ohne sichtbare offene Naht in diesen Blickwinkeln. Die zweite Instanz hat nur für die Sichtbarkeit der Teilung eine andere Objektfarbe; Slotvertrag und Quelldatei enthalten keine zusätzliche Variante. Die UV-Ansichten zeigen die tatsächlichen Charts unter gleichem Maßstab. Kameras und zweite Instanz wurden nur transient erzeugt und nie in die editierbare Quelle gespeichert.

Ausführungsbelege: `Evidence/refine.log`, `verify.log`, `previews.log`; Messdaten: `Evidence/refinement.json` und [verification.json](verification.json). Der erste Sandbox-Start von Blender lieferte keine Ausgabe; die erfolgreichen Läufe erfolgten nach automatischer Freigabe außerhalb der Sandbox. Ein erster Bearbeitungsprüflauf brach vor dem Speichern an einem zu strikten Metadatenvergleich ab (`refine_attempt_01.log`). Die Prüfung verwendet jetzt gemessene numerische Abweichung statt Container-/Float-Gleichheit; volle Manifestpräzision bleibt erhalten. Erste Vorschau-Ränder wurden nach Sichtkontrolle erweitert; `previews_attempt_01.log` dokumentiert den vorigen Lauf. Diese Fehlversuche sind keine ungelösten Assetfehler. Keine Warnungsunterdrückung oder Blender-Benutzerkonfiguration gespeichert.

## Exportprofil und offene nächste Zuständigkeit

Eigenes Ergebnis: [{NAME}.blend]({NAME}.blend), [FBX](Exports/{NAME}.fbx), [manifest.json](manifest.json). Der Export stammt aus der eigenen Kopie; das Creator-FBX wurde nicht als Ergebnis wiederverwendet.

Metric, Unit Scale 1, Meter; `global_scale=1`, `apply_unit_scale=True`, **`FBX_SCALE_NONE`**, Forward −Y, Up Z, `use_space_transform=True`, `bake_space_transform=False`. Abbildung **`UE_cm=(100*B.x,-100*B.y,100*B.z)`**, keine zusätzliche Spiegelung oder negative Objektskalierung. Nur ausgewählte MESH-Objekte: ein Render-Mesh plus zehn UCX, kontrollierte FIXED-Triangulierung, FACE-Smoothing und Tangenten; keine Kameras/Lichter/Animation/Texturen exportiert.

**Nicht durchgeführt:** Unreal-Import/Reimport, Prüfung gespeicherter UE-Einstellungen, UE-Kollision/UV1/Material-Override, Kapsel/PIE/Kamera, Montage mit Boden/Dach, Performance, Packaging, Multiplayer. Der Blender-Rückimport ersetzt keine Unreal-Abnahme. Integration ist ein gesonderter Auftrag mit Zielpfad und benannter Zuständigkeit; ausschließlich der kalibrierte **FbxFactory/FbxStaticMeshImportData-Legacy-Pfad** ist vorgesehen. Interchange bleibt nicht validiert. Die tatsächlich gespeicherten Importwerte und zehn UCX ohne Zusatzkörper später nachweisen; keine pauschale Löschung bestehender Kollision. Kein Austausch des gleichnamigen Bestandsassets freigegeben.

Creator-Dateien, Content, Materialien, Blueprints, Levels, gemeinsame Generatoren und Projektkonfiguration blieben unberührt. Keine Unreal-Karte geöffnet/gespeichert, keine Commits oder Staging-Aktionen. Die Rolle Integration hat keine Freigabe erteilt; Status bleibt höchstens **review_ready**.
'''
    (ROOT/'REVIEW.md').write_text(report,encoding='utf-8',newline='\n')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
    # Nested input SHA256SUMS remains covered via the intake record; include it here too.
    files=sorted(set(files+[ROOT/'Evidence/Input/SHA256SUMS']))
    (ROOT/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
    print('DELIVERY_REVIEW_READY',len(files),'files hashed;',len(baseline['files']),'tracked files unchanged')

if __name__=='__main__':
    main()
