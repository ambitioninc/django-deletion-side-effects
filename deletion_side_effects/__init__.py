# flake8: noqa
from .deletion_side_effects import register_deletion_side_effects, gather_deletion_side_effects, BaseDeletionSideEffects
from .version import __version__

default_app_config = 'deletion_side_effects.apps.DeletionSideEffectsConfig'
