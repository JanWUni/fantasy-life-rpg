from pathlib import Path
import json,unreal
R=Path(__file__).resolve().parent;repo=R.parents[6]
assert Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).resolve()==repo
base=json.loads((R/'Evidence/baseline.json').read_text());edit=json.loads((R/'Evidence/white_unreal.json').read_text());target=edit['updated_actor']
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();by={a.get_path_name():a for a in actors}
assert set(by)=={a['path'] for a in base['actors']}
def xyz(v):return [v.x,v.y,v.z]
proof={}
for b in base['actors']:
    a=by[b['path']];rot=a.get_actor_rotation();assert xyz(a.get_actor_location())==b['location'] and [rot.pitch,rot.yaw,rot.roll]==b['rotation'] and xyz(a.get_actor_scale3d())==b['scale'] and str(a.get_folder_path())==b['folder']
    cs=a.get_components_by_class(unreal.StaticMeshComponent)
    assert len(cs)==len(b['components'])
    for c,old in zip(cs,b['components']):
        assert c.get_path_name()==old['path'] and (c.static_mesh.get_path_name() if c.static_mesh else None)==old['mesh']
        overrides=[m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]
        if b['path']!=target:assert overrides==old['overrides'],b['label']
        else:
            assert len(overrides)==c.get_num_materials()
            assert all('/HighElfWallStudy03/' in m or '/HighElfWallStudy02/' in m for m in overrides)
            proof[c.get_name()]=dict(mesh=old['mesh'],materials=overrides,collision=str(c.get_collision_profile_name()))
assert len(proof)==6
label=by[edit['updated_label']].get_components_by_class(unreal.TextRenderComponent)[0];assert str(label.get_editor_property('text'))=='WEISS / MIT DETAILS'
(R/'Evidence/unreal_verification.json').write_text(json.dumps(dict(status='passed',actors_checked=len(base['actors']),only_target_material_overrides_changed=True,components=proof),indent=2))
unreal.log('HE03_VERIFY_PASSED')
