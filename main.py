from database import db_session, requests
from telegram import telegram
import datetime
import asyncio
import json


if __name__ == '__main__':
    db_session.global_init()
    asyncio.run(telegram.start_polling())

