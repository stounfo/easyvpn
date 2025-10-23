import json
from uuid import uuid4

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, CommandObject

from config import API_TOKEN
from database import Request, Queue
from database.base_meta import get_session
from exceptions import RequestAlreadyExistsError
from services import RequestService, UserService

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    with get_session() as session:
        UserService.ensure_user(session, message.from_user.id, message.from_user.full_name, message.from_user.username)
        await message.answer("Привет! Введи /token для создания заявки на получение токена")


@dp.message(Command("token"))
async def create_token(message: types.Message):
    with get_session() as session:
        try:
            user = UserService.ensure_user(session, message.from_user.id, message.from_user.full_name,
                                           message.from_user.username)
            req = RequestService.create_request(session, user)
            await message.answer(f"Заявка с id {req.id} создана. Жди одобрения админа.", parse_mode="Markdown")
        except RequestAlreadyExistsError as e:
            req: Request = e.request
            answer_text = f"Ты уже создавал заявку `id={req.id}`. "
            match req.status:
                case 'pending':
                    answer_text += "Заявка на рассмотрении"
                case 'rejected':
                    answer_text += "Заявка отклонена. Обратись к администратору для уточнения причины"
                case 'approved':
                    pass  # TODO
                case _:
                    raise ValueError("Unknown type of Request.status")
            await message.answer(answer_text, parse_mode="Markdown")


@dp.message(Command("list"))
async def list_requests(message: types.Message):
    with get_session() as session:
        try:
            admin = UserService.get_admin(session, message.from_user.id)
            reqs = RequestService.get_requests_by_status(session, 'pending')
            users = list(map(lambda req: req.user, reqs))
            answer_text = "\n----------------------------\n".join(map(lambda t: t[0] + "\n---\n" + t[1], zip(map(str, reqs), map(str, users))))
            if answer_text:
                await message.answer(answer_text)
            else:
                await message.answer("Нет заявок")
        except PermissionError:
            await message.answer("Нет прав администратора.")


@dp.message(Command("approve"))
async def approve(message: types.Message, command: CommandObject):
    with get_session() as session:
        req = await RequestService.change_request_status(session, message, command, "approved")
        if req:
            req.uuid = str(uuid4())
            username = req.user.username
            queue = Queue(payload=json.dumps({"uuid": req.uuid, "email": username}))
            session.add(queue)
            session.commit()
            await message.answer(f"Заявка апрувнута {req}")


@dp.message(Command("reject"))
async def reject(message: types.Message, command: CommandObject):
    with get_session() as session:
        req = await RequestService.change_request_status(session, message, command, "rejected")
        if req:
            await message.answer(f"Заявка отклонена {req}")


@dp.message()
async def default_message_handler(message: types.Message):
    await message.answer("Непонятно. Начните заного используя /start")


async def main():
    await dp.start_polling(bot)
