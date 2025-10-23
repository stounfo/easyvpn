import io
import json
from uuid import uuid4

import qrcode
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import BufferedInputFile

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


def generate_vless_link(uuid: str) -> str:
    return f"vless://{uuid}@165.227.161.51:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=google.com&fp=chrome&pbk=zoTJTUgvIi30WGkqZad6vpAVyHE2xFZN0C4frgFB9DM&sid=39224acf&type=tcp&headerType=none#vless-reality"


def generate_qr_code(data: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, 'PNG')
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


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
            match req.status:
                case 'pending':
                    answer_text = f"Заявка `id={req.id}` на рассмотрении"
                    await message.answer(answer_text, parse_mode="Markdown")
                case 'rejected':
                    answer_text = f"Заявка `id={req.id}` отклонена. Обратись к администратору"
                    await message.answer(answer_text, parse_mode="Markdown")
                case 'approved':
                    vless_link = generate_vless_link(req.uuid)

                    caption = (
                        "✅ *Твой VPN конфиг готов!*\n\n"
                        "Отсканируй QR-код или скопируй конфиг ниже:\n\n"
                        f"`{vless_link}`\n\n"
                        "_Для использования скачай приложение V2Ray или Nekoray_"
                    )

                    qr_image = generate_qr_code(vless_link)

                    await message.answer_photo(
                        photo=BufferedInputFile(qr_image, filename="vpn_config.png"),
                        caption=caption,
                        parse_mode="Markdown"
                    )
                case _:
                    raise ValueError("Unknown type of Request.status")


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
