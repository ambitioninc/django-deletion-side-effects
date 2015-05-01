from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase

from deletion_side_effects.deletion_side_effects import (
    BaseDeletionSideEffects, register_deletion_side_effects,
    _DELETION_SIDE_EFFECTS
)


class MyDeletionSideEffects(BaseDeletionSideEffects):
    pass


class MyOtherDeletionSideEffects(BaseDeletionSideEffects):
    pass


class TestRegisterDelectionSideEffects(SimpleTestCase):
    def setUp(self):
        _DELETION_SIDE_EFFECTS.clear()

    def test_register_delection_side_effects_single(self):
        register_deletion_side_effects(ContentType)(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_delection_side_effects_duplicates(self):
        register_deletion_side_effects(ContentType)(MyDeletionSideEffects)
        register_deletion_side_effects(ContentType)(MyDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects])
        })

    def test_register_delection_side_effects_multiple(self):
        register_deletion_side_effects(ContentType)(MyDeletionSideEffects)
        register_deletion_side_effects(ContentType)(MyOtherDeletionSideEffects)
        self.assertEquals(_DELETION_SIDE_EFFECTS, {
            ContentType: set([MyDeletionSideEffects, MyOtherDeletionSideEffects])
        })

    def test_register_delection_invalid_side_effects_single(self):
        with self.assertRaises(ValueError):
            register_deletion_side_effects(ContentType)(object)
