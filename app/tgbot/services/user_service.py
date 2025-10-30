from sqlalchemy.orm import Session

from database import User


class UserService:
    @staticmethod
    def get_user_or_none(session: Session, telegram_id: int) -> User | None:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

    @staticmethod
    def get_admin(session: Session, telegram_id: int) -> User:
        admin = session.query(User).filter((User.telegram_id == telegram_id) & (User.is_admin.is_(True))).first()
        if not admin:
            raise PermissionError
        return admin

    @staticmethod
    def create_user(session: Session, telegram_id: int, full_name: str, username: str, is_admin: bool = False) -> User:
        exist_user = UserService.get_user_or_none(session, telegram_id)
        if exist_user:
            raise ValueError(f"User with tg_id={telegram_id} already exist")
        new_user = User(telegram_id=telegram_id, full_name=full_name, username=username, is_admin=is_admin)
        session.add(new_user)
        session.commit()
        return new_user

    @staticmethod
    def ensure_user(session: Session, telegram_id: int, full_name: str, username: str) -> User:
        user = UserService.get_user_or_none(session, telegram_id)
        if not user:
            user = UserService.create_user(session, telegram_id, full_name, username)
        return user
