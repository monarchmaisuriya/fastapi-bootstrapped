from sqlmodel import SQLModel


class UserAuthenticate(SQLModel):
    email: str
    password: str


class UserManage(SQLModel):
    email: str
    password: str
