from collections import defaultdict


# The global variable that holds all side effects that have been registered
_DELETION_SIDE_EFFECTS = defaultdict(set)


def register_deletion_side_effects(*deletion_side_effects_handlers):
    """
    Registers deletion side effect handler classes. The class must inherit BaseDeletionSideEffects
    and define a deleted_obj_class variable.
    """
    for deletion_side_effects_handler in deletion_side_effects_handlers:
        if not issubclass(deletion_side_effects_handler, BaseDeletionSideEffects):
            raise ValueError('Deletion side effects handler must inherit BaseDeletionSideEffects')
        elif deletion_side_effects_handler.deleted_obj_class is None:
            raise ValueError('Deletion side effects handler must define a deleted_obj_class variable')

        _DELETION_SIDE_EFFECTS[deletion_side_effects_handler.deleted_obj_class].add(deletion_side_effects_handler)


def _recursive_gather_deletion_side_effects(deleted_obj_class, deleted_objs, all_side_effects, all_deleted_objs):
    # The objects being passed in are deleted, so add them to the set of all deleted objects
    all_deleted_objs |= set(deleted_objs)

    # Pass the deleted objects through the registered side effect classes for the deleted object class
    all_cascade_deleted_objs = defaultdict(set)
    for side_effects_class in _DELETION_SIDE_EFFECTS[deleted_obj_class]:
        side_effect_objs, cascade_deleted_objs = side_effects_class().get_side_effects(deleted_objs)

        # Add the side effects from this round of recursion to the set of all side effects for that side effect
        # class so far
        if side_effect_objs:
            all_side_effects[side_effects_class] |= set(side_effect_objs)

        # Add to the set of all cascade deleted objects this round. This is keyed on object type
        for cascade_deleted_obj in [o for o in cascade_deleted_objs if o not in all_deleted_objs]:
            all_cascade_deleted_objs[cascade_deleted_obj.__class__].add(cascade_deleted_obj)

    for deleted_class, deleted_objs in all_cascade_deleted_objs.items():
        # Gather cascading deletion side effects
        _recursive_gather_deletion_side_effects(
            deleted_class, deleted_objs, all_side_effects, all_deleted_objs)

    return all_side_effects


def gather_deletion_side_effects(obj_class, objs):
    """
    Given an object, gather the side effects of deleting it. The return value is a list of dictionaries, each
    of which contain the following keys:

    1. msg - This key contains a human-readable message of the side effect.
    2. side_effect_objs: This key contains a list of ever object related to this side effect and the message.
    """
    # Recursively gather all side effects
    gathered_side_effects = _recursive_gather_deletion_side_effects(obj_class, objs, defaultdict(set), set())

    # Render the side effect messages and reorganize the output
    return [
        {
            'msg': side_effect().get_side_effect_message(list(side_effect_objs)),
            'side_effect_objs': list(side_effect_objs),
        }
        for side_effect, side_effect_objs in gathered_side_effects.items()
    ]


class BaseDeletionSideEffects(object):
    """
    Provides the interface for a user to make a deletion side effects class. The user must define
    the following:

    1. A `deleted_obj_class` variable. This variable denotes the class of the object being deleted.

    2. A 'get_side_effects` method. This method is passed a list of objects of `deleted_obj_class`\
    type that are candidates for deletion. The method returns a tuple of objects that are affected by deletion\
    of the objects for deletion (i.e the side effect objects) and a list of objects that will be cascade deleted\
    if the candidate objects are deleted.

    3. A `get_side_effect_message` method. This method is passed all of the side effect objects from\
    gathering side effects with the class. The method is responsible for returning a human-readable string of\
    he side effects.

    """
    deleted_obj_class = None

    def get_side_effects(self, deleted_objects):
        """
        Returns a tuple. The first part of the tuple is list of objects that
        have side effects associated with them. The second part of the tuple is a list of other objects
        that will be deleted as a result of the passed objects being deleted. Side effects of other deleted
        models will be populated when gather_deletion_side_effects is called.
        """
        raise NotImplementedError

    def get_side_effect_message(self, side_effect_objects):
        """
        Given a list of objects that have this side effect associated with them, return a human
        readable message about the side effect.
        """
        raise NotImplementedError
