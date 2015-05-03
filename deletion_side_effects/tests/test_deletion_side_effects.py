from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase
from mock import Mock

from deletion_side_effects.deletion_side_effects import (
    BaseDeletionSideEffects, register_deletion_side_effects,
    _DELETION_SIDE_EFFECTS, gather_deletion_side_effects
)


class TestGatherDeletionSideEffects(SimpleTestCase):
    def setUp(self):
        _DELETION_SIDE_EFFECTS.clear()

    def test_no_side_effects(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects()(MyDeletionSideEffects)

        ct = ContentType(id=1)
        side_effects = gather_deletion_side_effects(ContentType, [ct])
        self.assertEquals(side_effects, [])

    def test_one_side_effect(self):
        side_effect_obj = Mock(value='hi')

        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return [side_effect_obj], []

            def get_side_effect_message(self, side_effect_objs):
                return '{0} objs deleted, first value {1}'.format(len(side_effect_objs), side_effect_objs[0].value)

        register_deletion_side_effects()(MyDeletionSideEffects)

        ct = ContentType(id=1)
        side_effects = gather_deletion_side_effects(ContentType, [ct])
        self.assertEquals(side_effects, [{
            'msg': '1 objs deleted, first value hi',
            'side_effect_objs': [side_effect_obj],
        }])


class TestRegisterDelectionSideEffects(SimpleTestCase):
    def setUp(self):
        _DELETION_SIDE_EFFECTS.clear()

    def test_register_delection_side_effects_single(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects()(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_delection_side_effects_duplicates(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects()(MyDeletionSideEffects)
        register_deletion_side_effects()(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_delection_side_effects_multiple(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        class MyOtherDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects()(MyDeletionSideEffects)
        register_deletion_side_effects()(MyOtherDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects, MyOtherDeletionSideEffects])
        })

    def test_register_delection_invalid_side_effects_single(self):
        with self.assertRaises(ValueError):
            register_deletion_side_effects()(object)
