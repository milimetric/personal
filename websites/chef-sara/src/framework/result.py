class Result:
    def __init__(self, type, reason = ''):
        self.type = type
        self.reason = reason

    def __eq__(self, other):
        if isinstance(other, Result):
            return self.type == other.type
        elif isinstance(other, str):
            return self.type == other
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # types of results
    Success = 'success'
    NotNeeded = 'not needed'
    NotPossible = 'not possible'
