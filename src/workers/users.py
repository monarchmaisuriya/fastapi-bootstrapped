from helpers.logger import Logger
from models.users import UserManage, UserManageAction
from repositories.users import UserRespository

logger = Logger(__name__)


async def on_user_created(email: str):
    user_respository: UserRespository = UserRespository()
    await user_respository.manage(
        UserManageAction.START_EMAIL_VERIFICATION, UserManage(email=email)
    )
