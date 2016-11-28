from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django_dynamic_fixture import G
from mock import Mock

from deletion_side_effects.deletion_side_effects import (
    BaseDeletionSideEffects, register_deletion_side_effects,
    _DELETION_SIDE_EFFECTS, gather_deletion_side_effects
)


class TestGatherDeletionSideEffects(TransactionTestCase):
    def setUp(self):
        _DELETION_SIDE_EFFECTS.clear()

    def test_no_side_effects(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return ([], [])

        register_deletion_side_effects(MyDeletionSideEffects)

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

        register_deletion_side_effects(MyDeletionSideEffects)

        ct = ContentType(id=1)
        side_effects = gather_deletion_side_effects(ContentType, [ct])
        self.assertEquals(side_effects, [{
            'msg': '1 objs deleted, first value hi',
            'side_effect_objs': [side_effect_obj],
        }])

    def test_cascaded_side_effects(self):
        ctype = G(ContentType)
        user = G(User)

        class CTypeDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return [ctype], [user]

            def get_side_effect_message(self, side_effect_objs):
                return '{0} ctypes deleted'.format(len(side_effect_objs))

        class UserDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return [user], []

            def get_side_effect_message(self, side_effect_objs):
                return '{0} users deleted'.format(len(side_effect_objs))

        register_deletion_side_effects(CTypeDeletionSideEffects)
        register_deletion_side_effects(UserDeletionSideEffects)

        ct = ContentType(id=1)
        side_effects = gather_deletion_side_effects(ContentType, [ct])
        side_effects = sorted(side_effects, key=lambda k: k['msg'])

        self.assertEquals(side_effects, [{
            'msg': '1 ctypes deleted',
            'side_effect_objs': [ctype],
        }, {
            'msg': '1 users deleted',
            'side_effect_objs': [user],
        }])

    def test_cascaded_multiple_side_effects(self):
        ctypes = [G(ContentType), G(ContentType)]
        users = [G(User), G(User)]

        class CTypeDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return ctypes, users

            def get_side_effect_message(self, side_effect_objs):
                return '{0} ctypes deleted'.format(len(side_effect_objs))

        class UserDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

            def get_side_effects(self, deleted_objs):
                return users, []

            def get_side_effect_message(self, side_effect_objs):
                return '{0} users deleted'.format(len(side_effect_objs))

        register_deletion_side_effects(CTypeDeletionSideEffects)
        register_deletion_side_effects(UserDeletionSideEffects)

        ct = ContentType(id=1)
        side_effects = gather_deletion_side_effects(ContentType, [ct])
        side_effects = sorted(side_effects, key=lambda k: k['msg'])

        self.assertEquals(side_effects[0]['msg'], '2 ctypes deleted')
        self.assertEquals(set(side_effects[0]['side_effect_objs']), set(ctypes))
        self.assertEquals(side_effects[1]['msg'], '2 users deleted')
        self.assertEquals(set(side_effects[1]['side_effect_objs']), set(users))


class TestRegisterDeletionSideEffects(TransactionTestCase):
    def setUp(self):
        _DELETION_SIDE_EFFECTS.clear()

    def test_register_deletion_side_effects_single(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_deletion_side_effects_duplicates(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects(MyDeletionSideEffects)
        register_deletion_side_effects(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_deletion_side_effects_multiple(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        class MyOtherDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = ContentType

        register_deletion_side_effects(MyDeletionSideEffects)
        register_deletion_side_effects(MyOtherDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects, MyOtherDeletionSideEffects])
        })

    def test_register_deletion_invalid_side_effects_no_obj_class(self):
        class MyDeletionSideEffects(BaseDeletionSideEffects):
            deleted_obj_class = None

        with self.assertRaises(ValueError):
            register_deletion_side_effects(MyDeletionSideEffects)

    def test_register_deletion_invalid_side_effects_wrong_inheritance(self):
        with self.assertRaises(ValueError):
            register_deletion_side_effects(object)
