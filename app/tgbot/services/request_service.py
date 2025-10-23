from datetime import datetime

from aiogram import types
from aiogram.filters import CommandObject
from sqlalchemy.orm import Session

from database import Request, User
from exceptions import RequestAlreadyExistsError


class RequestService:
    @staticmethod
    def create_request(session: Session, user: User) -> Request:
        existing = session.query(Request).filter(Request.email == user.username).first()
        if existing:
            raise RequestAlreadyExistsError(existing)
        req = Request(telegram_id=user.telegram_id, email=user.username, status="pending", created_at=datetime.utcnow())
        session.add(req)
        session.commit()
        return req

    @staticmethod
    def get_request_by_user_id(session: Session, telegram_id: int) -> Request | None:
        return session.query(Request).filter(Request.telegram_id == telegram_id).first()

    @staticmethod
    def get_requests_by_status(session: Session, status: str) -> list[Request]:
        return session.query(Request).filter(Request.status == status).all()

    @staticmethod
    def get_request_by_id(session: Session, req_id: int) -> Request | None:
        return session.query(Request).filter(Request.id == req_id).first()

    @staticmethod
    async def change_request_status(session: Session, message: types.Message, command: CommandObject, status: str) -> Request | None:
        args = command.args
        if not args or len(args.split()) > 1:
            await message.answer("❌ Укажи id заявки. Пример: /approve 5")
            return None
        try:
            req_id = int(args.strip())
        except ValueError:
            await message.answer("❌ id должен быть числом")
            return None
        req = RequestService.get_request_by_id(session, req_id)
        if not req:
            await message.answer(f"Заявка с id {req_id} не найдена")
            return None
        req.status = status
        return req
