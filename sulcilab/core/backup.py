import enum 


class BackupTriggering(enum.Enum):
    SCHEDULED = "scheduled"
    SYSTEM = "system"
    USER = "user"