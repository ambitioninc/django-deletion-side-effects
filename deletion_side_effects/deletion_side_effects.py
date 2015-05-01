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


def gather_deletion_side_effects(obj):
    """
    Given an object, gather the side effects of deleting it as a list of messages.
    """
    return chain(*[
        deletion_side_effects(obj) for deletion_side_effects in _DELETION_SIDE_EFFECTS
    ])


class BaseDeletionSideEffects(object):
    """
    Provides the interface for a user to make a delection side effects class.
    """
    def get_side_effects(obj_model, objects):
        """
        Returns a tuple. The first part of the tuple is list of objects in the passed object list that
        have side effects associated with them. The second part of the tuple is a list of other objects
        that will be deleted as a result of the passed objects being deleted.
        """
        return ([], [])

    def get_side_effect_message(obj_model, objects):
        """
        Given a list of objects that have this side effect associated with them, return a human
        readable message about the side effect.
        """
        return ''
