import enum


class LLMEventTypes(enum.Enum):
    START = 1
    INITIALIZED = 3
    PROGRESS = 4
    COMPLETE = 5
    ERROR = 6

