from enum import StrEnum


class UserPermisionEnum(StrEnum):
    CAN_SEE_USERS = "can_see_users"
    CAN_SELF_DELETE = "can_self_delete"
    CAN_CREATE_CATERGORY = "can_create_category"
