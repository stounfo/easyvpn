import datetime
import logging
import json
import time

from xtlsapi import XrayClient
from config import INBOUND_TAG, XRAY_CONFIG_PATH
from database import get_session, Queue


def is_uuid_in_config(uuid: str) -> bool:
    with open(XRAY_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    for inbound in config.get("inbounds", []):
        if inbound.get("tag", None) == INBOUND_TAG:
            clients = inbound.get("settings", {}).get("clients", [])
            return any(map(lambda client: client["id"] == uuid, clients))
        else:
            print("Something wrong with config.json")
            return True


def add_client_to_config(uuid: str, email: str):
    with open(XRAY_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    for inbound in config.get("inbounds", []):
        if inbound.get("tag", None) == INBOUND_TAG:
            clients = inbound.get("settings", {}).get("clients", [])
            clients.append({
                "id": uuid,
                "email": email,
                "flow": "xtls-rprx-vision"
            })
            inbound["settings"]["clients"] = clients
            # записываем обратно в файл
            with open(XRAY_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            break

    else:
        print(f"Inbound with tag '{INBOUND_TAG}' not found in config")


def process_tasks():
    while True:
        xray_client = XrayClient('127.0.0.1', 10085)
        with get_session() as session:
            active_process: Queue | None = session.query(Queue).filter(Queue.status == 'created').first()
            if not active_process:
                print(f"Queue is empty")
                time.sleep(60)
                continue
            payload = json.loads(active_process.payload)
            uuid = payload.get("uuid")
            email = payload.get("email")

            if is_uuid_in_config(uuid):
                print("uuid already exist")
                continue

            user = xray_client.add_client(INBOUND_TAG, uuid, email, flow="xtls-rprx-vision")
            active_process.status = "completed"
            active_process.completed = datetime.datetime.utcnow()
            session.commit()
            add_client_to_config(uuid, email)
            print(f"Xray client was added: {payload}")
            time.sleep(60)


if __name__ == "__main__":
    process_tasks()
