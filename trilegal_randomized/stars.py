"""
Classes to wrap skycatalogs.TrilegalObjects to enable their sky
positions to be randomized at the CCD level.
"""
from skycatalogs.objects import BaseObject, ObjectCollection
from skycatalogs.objects.trilegal_object import TrilegalObject
from .utils import RandomSkyPositions

__all__ = ["TrilegalRandomizedObject", "TrilegalRandomizedCollection"]


class TrilegalRandomizedObject(BaseObject):

    def __init__(self, trilegal_object, ra, dec, parent_collection, index):
        self.trilegal_object = trilegal_object
        obj_id = trilegal_object.id + "_randomized"
        super().__init__(ra, dec, obj_id, parent_collection._object_type,
                         parent_collection, index)

    def get_gsobject_components(self, gsparams=None, rng=None):
        return self.trilegal_object.get_gsobject_components(
            gsparams=gsparams, rng=rng)

    def get_observer_sed_component(self, component, mjd=None):
        return self.trilegal_object.get_observer_sed_component(
            component, mjd=mjd)


class TrilegalRandomizedCollection(ObjectCollection):
    _object_type = "trilegal_randomized"

    def __init__(self, region, random_seed, object_list, sky_catalog):
        self.sky_pos = RandomSkyPositions.make_generator(
            region, seed=random_seed)
        self.object_list = object_list
        self._sky_catalog = sky_catalog
        self._object_type_unique = self._object_type
        self._object_class = TrilegalRandomizedObject
        self._uniform_object_type = True

    @property
    def native_columns(self):
        return ()

    def __getitem__(self, key):
        trilegal_object = self.object_list[key]
        if not isinstance(trilegal_object, TrilegalObject):
            raise RuntimeError("expected TrilegalObject")
        ra, dec = next(self.sky_pos)
        return TrilegalRandomizedObject(trilegal_object, ra, dec, self, key)

    def __len__(self):
        return len(self.object_list)

    @staticmethod
    def register(sky_catalog, object_type):
        sky_catalog.cat_cxt.register_source_type(
            TrilegalRandomizedCollection._object_type,
            object_class=TrilegalRandomizedObject,
            collection_class=TrilegalRandomizedCollection,
            custom_load=True
        )

    @staticmethod
    def load_collection(region, sky_catalog, mjd=None, **kwds):
        object_type = TrilegalRandomizedCollection._object_type
        config = dict(sky_catalog.raw_config["object_types"][object_type])
        object_list = sky_catalog.get_object_type_by_region(region, "trilegal")
        return TrilegalRandomizedCollection(region,
                                            config['random_seed'],
                                            object_list,
                                            sky_catalog)
