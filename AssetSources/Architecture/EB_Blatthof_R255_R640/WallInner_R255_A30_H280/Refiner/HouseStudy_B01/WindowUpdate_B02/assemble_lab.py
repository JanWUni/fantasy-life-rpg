"""Add two window-updated houses to free southern ground; preserve all prior Lab actors."""
import json
import math
AS='editor_toolset.toolsets.asset.AssetTools'
OB='editor_toolset.toolsets.object.ObjectTools'
AC='editor_toolset.toolsets.actor.ActorTools'
SC='editor_toolset.toolsets.scene.SceneTools'
BASE='/Game/Art/Architecture/ElvenHouseB01'
ROOT='E:/Business/fantasy-rpg-refiner/AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Refiner/HouseStudy_B01/'
MAP='/Game/Prototype/Maps/Lvl_AssetLab'


def tool(group,operation,**args):
    result=execute_tool(group+'.'+operation,json.dumps(args))
    return result['returnValue'] if 'returnValue' in result else None


def ref(path):return {'refPath':path+'.'+path.rsplit('/',1)[-1]}
def vec(x,y,z):return dict(x=x,y=y,z=z)
def props(obj,**values):
    tool(OB,'list_properties',instance=obj)
    assert tool(OB,'set_properties',instance=obj,values=json.dumps(values))


def run():
    assert tool(SC,'get_current_level')==MAP
    assert not tool('EditorToolset.EditorAppToolset','IsPIERunning')
    with open(ROOT+'Integration/assembly.json','r',encoding='utf-8') as f:assemblies=json.load(f)
    existing={tool(AC,'get_label',actor=a):a for a in tool(SC,'find_actors',name='',tag='',collision_channels=[])}
    placed={}
    def place(name,asset,loc,yaw=0,scale=(1,1,1),folder=''):
        label='Lab_EH_B02_'+name
        xform=dict(location=vec(*loc),rotation=dict(pitch=0,yaw=yaw,roll=0),scale=vec(*scale))
        if label in existing:
            actor=existing[label];tool(AC,'set_actor_transform',actor=actor,xform=xform)
        else:
            actor=tool(SC,'add_to_scene_from_asset',asset_path=asset,name=label,xform=xform,snap_to_ground=False)
        tool(SC,'set_actor_folder',actor=actor,folder_path='Lab/Architecture/ElvenHouseB02/'+folder)
        placed[label]=actor
        return actor
    def box(name,loc,scale,folder):
        actor=place(name,'/Engine/BasicShapes/Cube',loc,scale=scale,folder=folder)
        for c in tool(AC,'get_components',actor=actor,component_type={'refPath':'/Script/Engine.StaticMeshComponent'}):
            props(c,overrideMaterials=[ref('/Game/Art/Materials/ElvenHouseB01/M_EH_Stone')])
        return actor
    counts={}
    for scene,x0,length in [('House_10x12',-2400,1200),('House_10x16_Variation',0,1600)]:
        windows=0
        for index,item in enumerate(assemblies[scene]):
            name=scene+'_'+str(index)
            if item['module']:
                loc=[item['location_cm'][0]+x0,item['location_cm'][1]-1900,item['location_cm'][2]+31]
                yaw=item['yaw_deg'];module=item['module']
                if module=='SM_EH_Wall_Window_200x24x320':
                    asset=BASE+'/Windows/Meshes/SM_EH_Wall_WindowOpening_200x24x320'
                elif module=='SM_EH_DoorLeaf_132_Study':asset=BASE+'/Blueprints/BP_EH_ReviewDoor'
                else:asset=BASE+'/Meshes/'+module
                place(name,asset,loc,yaw,folder=scene)
                if module=='SM_EH_Wall_Window_200x24x320':
                    r=math.radians(yaw)
                    mount=[loc[0]+100*math.cos(r)-5.5*math.sin(r),loc[1]+100*math.sin(r)+5.5*math.cos(r),loc[2]+95]
                    place(name+'_Window',BASE+'/Windows/BP_EH_Window_Arch_100x173',mount,yaw,folder=scene+'/Windows')
                    windows+=1
            else:
                lower,upper=item['bounds_blender_m']
                number=int(item['label'].rsplit('_',1)[-1].split('.')[0]);height=[11,22,31][number]
                box(name+'_Step',[50*(lower[0]+upper[0])+x0,-50*(lower[1]+upper[1])-1900,height/2],
                    [upper[0]-lower[0],upper[1]-lower[1],height/100],scene)
        box(scene+'_Foundation',(x0+500,-1900-length/2,5.5),(10,length/100,.11),scene)
        counts[scene]=dict(origin_cm=[x0,-1900,31],windows=windows,footprint_cm=[1000,length])
    assert tool(AS,'save_assets',asset_paths=[MAP])
    return dict(map=MAP,actors=placed,houses=counts,existing_actor_count=len(existing),
        existing_actors_not_modified=True,lighting='Existing Lab daylight, unchanged; no house fill lights added')
