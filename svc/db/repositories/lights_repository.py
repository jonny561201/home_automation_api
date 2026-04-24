from sqlalchemy import select, delete

from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import Scenes, SceneDetails
from svc.models.scenes import LightScenes, LightScene, LightDetail


class LightsRepository(DatabaseBase):

    def get_scenes_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(Scenes).filter_by(user_id=user_id)
        scenes = self.session.execute(stmt).unique().scalars().all()
        if scenes is None:
            return LightScenes(scenes=[])
        light_scenes = [LightScene(id=scene.id, name=scene.name, lights=self.__create_light_scenes(scene.details)) for scene in scenes]
        return LightScenes(scenes=light_scenes)

    def create_scene(self, user_id, request):
        self._validate_property(user_id)
        new_scene = Scenes(name=request['name'], user_id=user_id)
        self.session.add(new_scene)
        self.session.flush()
        for detail in request['details']:
            new_detail = SceneDetails(
                scene_id=new_scene.id,
                light_group=detail.get('groupId'),
                light_id=detail.get('lightId'),
                light_brightness=detail.get('brightness')
            )
            self.session.add(new_detail)

    def delete_scene_by_user(self, user_id, scene_id):
        self._validate_property(user_id)
        self._validate_property(scene_id)
        self.session.execute(delete(SceneDetails).where(SceneDetails.scene_id == scene_id))
        self.session.execute(delete(Scenes).where(Scenes.user_id == user_id, Scenes.id == scene_id))

    @staticmethod
    def __create_light_scenes(light_details):
        return [LightDetail(groupId=detail.light_group, groupName=detail.light_group_name, brightness=detail.light_brightness) for detail in light_details]
