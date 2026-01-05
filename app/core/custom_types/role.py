from enum import Enum

class UserRole(str, Enum):
    MEMBER = "member"
    MANAGER = "manager"
    ADMIN = "admin"
