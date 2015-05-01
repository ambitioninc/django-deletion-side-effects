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
