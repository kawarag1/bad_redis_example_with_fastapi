from app.database.models.user import User
from app.database.repos.abc.abstract_repository import AbstractRepository


class UserRepository(AbstractRepository):
    model = User