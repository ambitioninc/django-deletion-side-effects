from collections import defaultdict
from itertools import chain


# The global variable that holds all side effects that have been registered
_DELETION_SIDE_EFFECTS = defaultdict(set)


def register_deletion_side_effects(sender):
    """
    Registers the function as a deletion side effect handler. This function
    should return a list of side effects that occur when a provided object is about to
    be deleted.

    @register_deletion_side_effects
    def fantasy_app_deletion(obj):
        # Return a list of side effects for the fantasy app when obj is deleted
        pass
    """
    def _register_deletion_side_effects_wrapper(deletion_side_effects_handler):
        if not issubclass(deletion_side_effects_handler, BaseDeletionSideEffects):
            raise ValueError('Deletion side effects handler must inherit BaseDelectionSideEffects')

        _DELETION_SIDE_EFFECTS[sender].add(deletion_side_effects_handler)
        return deletion_side_effects_handler

    return _register_deletion_side_effects_wrapper


def _recursive_gather_delection_side_effects(obj_class, objs, gathered_side_effects, gathered_deleted_objs):
    gathered_deleted_objs.add(objs)

    side_effect_objs, deleted_objs = zip(chain(*[
        deletion_side_effects(obj_class).get_side_effects(objs)
        for deletion_side_effects in _DELETION_SIDE_EFFECTS[obj_class]
    ]))

    gathered_side_effects[_DELETION_SIDE_EFFECTS[obj_class]].add(*side_effect_objs)

    # Organize all deleted objects into a mapping of their classes. Only populate deleted objects
    # here that have not been deleted before in order to avoid circular deletions.
    mapped_deleted_objs = defaultdict(set)
    for obj in deleted_objs & gathered_deleted_objs:
        mapped_deleted_objs[obj.__class__].add(obj)

    for deleted_class, deleted_objs in mapped_deleted_objs.items():
        _recursive_gather_delection_side_effects(
            deleted_class, deleted_objs, gathered_side_effects, gathered_deleted_objs)

    return gathered_side_effects


def gather_deletion_side_effects(obj_class, objs):
    """
    Given an object, gather the side effects of deleting it.
    """
    # Recursively gather all side effects
    gathered_side_effects = _recursive_gather_delection_side_effects(obj_class, objs, defaultdict(set), set())

    # Render the side effect messages and reorganize the output
    return [
        {
            'msg': side_effect.get_side_effect_message(side_effect_objs),
            'side_effect_objs': side_effect_objs,
        }
        for side_effect, side_effect_objs in gathered_side_effects.items()
    ]


class BaseDeletionSideEffects(object):
    """
    Provides the interface for a user to make a delection side effects class.
    """
    def __init__(self, deleted_obj_class):
        self.deleted_obj_class = deleted_obj_class

    def get_side_effects(self, deleted_objects):
        """
        Returns a tuple. The first part of the tuple is list of objects that
        have side effects associated with them. The second part of the tuple is a list of other objects
        that will be deleted as a result of the passed objects being deleted. Side effects of other deleted
        models will be populated when gather_deletion_side_effects is called.
        """
        return ([], [])

    def get_side_effect_message(self, side_effect_objects):
        """
        Given a list of objects that have this side effect associated with them, return a human
        readable message about the side effect.
        """
        return ''
