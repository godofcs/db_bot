from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
import datetime
import re
from time import sleep
from database import db_session
from database.bonus import Bonus
from database.bookings import Booking
from database.clients import Client
from database.tours import Tour
from database.tour_operators import TourOperator
from database import requests
import aio_pika
import json
import asyncio


class Gen(StatesGroup):
    register = State()
    tour_operator_name = State()
    tour_operator_description = State()
    tour_operator_telephone = State()
    tour_operator_email = State()
    tour_operator_password = State()
    tour_operator_email_auth = State()
    tour_operator_password_auth = State()
    client_name = State()
    client_type = State()
    client_telephone = State()
    client_email = State()
    client_password = State()
    client_email_auth = State()
    client_password_auth = State()
    tour_name = State()
    tour_season_price = State()
    tour_date = State()
    tour_description = State()
    tour_place = State()
    tour_duration = State()
    tour_limit = State()
    just_chill = State()
    auth_client = State()
    auth_tour_operator = State()
    tour_operator_see_all_my_tour = State()
    tour_operator_delete_tour = State()
    tour_operator_edit_tour = State()
    tour_operator_edit_tour_set_parameter = State()
    tour_operator_edit_tour_wait_parameter = State()
    edit_tour_operator_profile = State()
    get_new_parameter_for_tour_operator_profile = State()
    tour_operator_conduct_tour_date = State()
    tour_operator_conduct_tour = State()
    tour_operator_switch_bonus_count = State()
    client_see_all_tour = State()
    client_register_to_tour = State()
    client_switch_kol = State()
    edit_client_profile = State()
    get_new_parameter_for_client_profile = State()
    client_switch_booking = State()
    client_edit_booking = State()


dp = Dispatcher()
global_rmq_config = ""
token = "6738381880:AAELUsct4kWkM-VXi7evcpr7ToqiJ_qSC5s"
users_data = {}
tour_on_page = 2


def get_keyboard_from_reg():
    buttons = [
        [
            types.InlineKeyboardButton(text="Туроператор", callback_data="reg_oper"),
            types.InlineKeyboardButton(text="Клиент", callback_data="reg_client")
        ],
        # TODO в команде help написать, что при прерывании регистрации данные не сохраняются
        [types.InlineKeyboardButton(text="Прервать регистрацию", callback_data="reg_finish"), ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_auth():
    buttons = [
        [
            types.InlineKeyboardButton(text="Туроператор", callback_data="auth_oper"),
            types.InlineKeyboardButton(text="Клиент", callback_data="auth_client")
        ],
        # TODO в команде help написать, что при прерывании регистрации данные не сохраняются
        [types.InlineKeyboardButton(text="Прервать авторизацию", callback_data="auth_finish"), ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_search_type():
    buttons = [
        [
            types.InlineKeyboardButton(text="Юрлицо", callback_data="typ_ur"),
            types.InlineKeyboardButton(text="Физлицо", callback_data="typ_fiz")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_see_all_my_tour(all_tour, page):
    cur_tour = []
    i = 0
    for tour in all_tour[page * tour_on_page:min(page * tour_on_page + tour_on_page, len(all_tour))]:
        print(tour.name, page * tour_on_page + i)
        cur_tour += [[types.InlineKeyboardButton(text=tour.name, callback_data=f"tour_{page * tour_on_page + i}")]]
        i += 1
    # TODO добавить проверку того, что туров нет
    buttons = [
        *cur_tour,
        [
            types.InlineKeyboardButton(text="<", callback_data="tour_prev"),
            types.InlineKeyboardButton(text="Закрыть", callback_data="tour_close"),
            types.InlineKeyboardButton(text=">", callback_data="tour_next")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_edit_tour():
    buttons = [
        [
            types.InlineKeyboardButton(text="Название", callback_data="tour_name"),
        ],
        [
            types.InlineKeyboardButton(text="Описание", callback_data="tour_description"),
            types.InlineKeyboardButton(text="Сезонные цены", callback_data="tour_season_price"),
        ],
        [
            types.InlineKeyboardButton(text="Даты", callback_data="tour_dates"),
            types.InlineKeyboardButton(text="Продолжительность", callback_data="tour_duration"),
        ],
        [
            types.InlineKeyboardButton(text="Места", callback_data="tour_place"),
            types.InlineKeyboardButton(text="Количество мест", callback_data="tour_limit"),
        ],
        [
            types.InlineKeyboardButton(text="Закрыть", callback_data="tour_close")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_edit_tour_operator_profile():
    buttons = [
        [
            types.InlineKeyboardButton(text="Название", callback_data="oper_name"),
            types.InlineKeyboardButton(text="Описание", callback_data="oper_description"),
        ],
        [
            types.InlineKeyboardButton(text="Телефон", callback_data="oper_telephone"),
            types.InlineKeyboardButton(text="email", callback_data="oper_email"),
        ],
        [
            types.InlineKeyboardButton(text="Пароль", callback_data="oper_password"),
        ],
        [
            types.InlineKeyboardButton(text="Закрыть", callback_data="oper_close")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_register_to_tour(tour):
    res = []
    for date in tour.dates:
        res += [[types.InlineKeyboardButton(text=date.strftime("%d.%m.%Y"), callback_data=f"regtour_{date.strftime('%d.%m.%Y')}")]]
    #print(res)
    buttons = [
        *res,
        [
            types.InlineKeyboardButton(text="Закрыть", callback_data="regtour_close")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_edit_client_profile():
    buttons = [
        [
            types.InlineKeyboardButton(text="Имя", callback_data="client_name"),
            types.InlineKeyboardButton(text="Тип", callback_data="client_type"),
        ],
        [
            types.InlineKeyboardButton(text="Телефон", callback_data="client_telephone"),
            types.InlineKeyboardButton(text="email", callback_data="client_email"),
        ],
        [
            types.InlineKeyboardButton(text="Пароль", callback_data="client_password"),
        ],
        [
            types.InlineKeyboardButton(text="Закрыть", callback_data="client_close")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_my_bookings(bookings, page):
    cur_booking = []
    i = 0
    for booking in bookings[page * tour_on_page:min(page * tour_on_page + tour_on_page, len(bookings))]:
        cur_booking += [[types.InlineKeyboardButton(text=f"{booking[0]}:\nДата:{booking[1].date.strftime('%d.%m.%Y')}\nКоличество:{booking[1].count}", callback_data=f"booking_{page * tour_on_page + i}")]]
        i += 1
    # TODO добавить проверку того, что брони нет
    buttons = [
        *cur_booking,
        [
            types.InlineKeyboardButton(text="<", callback_data="booking_prev"),
            types.InlineKeyboardButton(text="Закрыть", callback_data="booking_close"),
            types.InlineKeyboardButton(text=">", callback_data="booking_next")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_from_delete_booking():
    buttons = [
        [
            types.InlineKeyboardButton(text="Закрыть", callback_data="booking_close"),
            types.InlineKeyboardButton(text="Удалить бронь", callback_data="booking_delete")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if await state.get_state() == Gen.auth_tour_operator:
        await message.answer("Если хотите создать новый тур используйте команду: /create_new_tour")
        await message.answer("Если хотите посмотреть все туры которые у вас есть используйте команду: /see_all_my_tour")
        await message.answer("Если хотите удалить старый тур используйте команду: /delete_tour")
        await message.answer("Если хотите редактировать старый тур используйте команду: /edit_tour")
        await message.answer("Если хотите редактировать свой профиль используйте команду: /edit_profile")
        await message.answer("Если хотите провести тур используйте команду: /start_tour")
        await message.answer("Если хотите выйти из аккаунта используйте команду: /quite")
        return
    if await state.get_state() == Gen.auth_client:
        # TODO сдеалть пользователя
        await message.answer("Если вы хотите посмотреть список всех туров используйте команду: /see_all_tour") #com
        await message.answer("Если хотите редактировать свой профиль используйте команду: /edit_profile") #com
        await message.answer("Если хотите посмотреть все свои бонусы используйте команду: /see_all_my_bonus") #com
        await message.answer("Если хотите посмотреть все ваши брони используйте команду: /see_all_my_booking")
        await message.answer("Если хотите выйти из аккаунта используйте команду: /quite") #com
        return
    await message.answer("Привет, я телеграм бот, который помогает взаимодействовать клиентам и тур операторам.")
    await message.answer("Авторизуйтесь с помощью команды: /auth\nИли зарегестрируйтесь с помощью команды /reg")
    users_data[message.from_user.id] = {"registration": {},
                                        "authorization": {},
                                        # "type": "", "name": "", "description": "", "typ": "", "telephone": "", "email": ""
                                        "tour": {}}
    await state.set_state(Gen.just_chill)


@dp.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    #TODO добавить все команды и расписать команды для каждого типа пользователей
    await message.answer("""
Команды:
Общие команды:
/start - запустить бота
/help - прочитать справочную информацию о боте
/auth - авторизоваться
/reg - зарегистрироваться
/quite - выйти из аккаунта
Команды для туроператора:
/create_new_tour - создание нового тура
/see_all_my_tour - посмотреть все ваши туры
/delete_tour - удалить тур
/edit_tour - редактировать тур
/start_tour - провести тур
/edit_profile - редактировать профиль
Команды для пользователя:
/see_all_tour - посмотреть все туры и зарегистрироваться на один из них
/see_all_my_bonus - посмотреть все ваши бонусы
/see_all_my_booking - посмотреть все ваши забронированные туры
/edit_profile - редактировать профиль
""")


@dp.message(Command("see_all_my_booking"), Gen.auth_client)
async def cmd_see_all_my_booking(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_bookings"] = requests.get_all_my_bookings(users_data[message.from_user.id]["client_id"])
    users_data[message.from_user.id]["booking_page"] = 0
    if users_data[message.from_user.id]["all_bookings"] == []:
        await message.answer("У вас нет брони")
        return
    await message.answer(f"Вот {users_data[message.from_user.id]['booking_page'] + 1}-я страница с вашими бронями:", reply_markup=get_keyboard_from_my_bookings(users_data[message.from_user.id]["all_bookings"], users_data[message.from_user.id]["booking_page"]))
    await state.set_state(Gen.client_switch_booking)


@dp.callback_query(F.data.startswith("booking_"), Gen.client_switch_booking)
async def work_with_all_tour_pages_for_edit(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "prev":
        await switch_prev_page_booking(callback)
    elif type == "next":
        await switch_next_page_booking(callback)
    elif type == "close":
        await callback.message.edit_text("Не будем ничего исправлять? Эх, а я уже подключился к бд.")
        await state.set_state(Gen.auth_client)
    elif type.isdigit():
        users_data[callback.from_user.id]["ind"] = int(type)
        await edit_booking_page(callback, state)


async def switch_next_page_booking(callback: types.CallbackQuery):
    if len(users_data[callback.from_user.id]["all_bookings"]) > (users_data[callback.from_user.id]["booking_page"] + 1) * tour_on_page:
        users_data[callback.from_user.id]["booking_page"] += 1
        await callback.message.edit_text(f"Вот {users_data[callback.from_user.id]['booking_page'] + 1}-я страница с вашими бронями.",
                             reply_markup=get_keyboard_from_my_bookings(
                                 users_data[callback.from_user.id]["all_bookings"],
                                 users_data[callback.from_user.id]["booking_page"]))


async def switch_prev_page_booking(callback: types.CallbackQuery):
    if users_data[callback.from_user.id]["booking_page"] != 0:
        users_data[callback.from_user.id]["booking_page"] -= 1
        await callback.message.edit_text(f"Вот {users_data[callback.from_user.id]['booking_page'] + 1}-я страница с вашими бронями.",
                                reply_markup=get_keyboard_from_my_bookings(
                                    users_data[callback.from_user.id]["all_bookings"],
                                    users_data[callback.from_user.id]["booking_page"]))


async def edit_booking_page(callback: types.CallbackQuery, state: FSMContext):
    ind = users_data[callback.from_user.id]["ind"]
    booking = users_data[callback.from_user.id]["all_bookings"][ind]
    await callback.message.edit_text(f"""Вот ваша бронь:
{booking[0]}:
Дата: {booking[1].date}
Количество мест: {booking[1].count}
""", reply_markup=get_keyboard_from_delete_booking())
    await state.set_state(Gen.client_edit_booking)


@dp.callback_query(F.data.startswith("booking_"), Gen.client_edit_booking)
async def edit_booking(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "close":
        await callback.message.edit_text("Посмотрели и ладно.")
        await state.set_state(Gen.auth_client)
        return
    elif type == "delete":
        ind = users_data[callback.from_user.id]["ind"]
        booking = users_data[callback.from_user.id]["all_bookings"][ind]
        requests.delete_booking_by_id(booking[1])
        await callback.message.edit_text("Бронь удалена.")
        await state.set_state(Gen.auth_client)


@dp.message(Command("see_all_my_bonus"), Gen.auth_client)
async def cmd_see_all_my_bonus(message: types.Message, state: FSMContext):
    res = requests.get_all_my_bonus(users_data[message.from_user.id]["client_id"])
    if len(res) == 0:
        await message.answer(f"У вас нет бонусов")
        return
    for i in range(len(res)):
        res[i] = ": ".join(res[i])
    res = '\n'.join(res)
    await message.answer(f"Вот все ваши бонусы:\n{res}")


@dp.message(Command("edit_profile"), Gen.auth_client)
async def cmd_edit_client_profile(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["client_info"] = requests.get_client_by_id(users_data[message.from_user.id]["client_id"])
    await state.set_state(Gen.edit_client_profile)
    await edit_client_page(message, state)


async def edit_client_page(message: types.Message, state: FSMContext):
    client = users_data[message.from_user.id]["client_info"]
    await message.answer(f"""Вот вся информация:
id: {client.id}
name: {client.name}
description: {client.type}
telephone: {client.telephone}
email: {client.email}
password: {client.password}
""",    reply_markup=get_keyboard_from_edit_client_profile())


async def edit_client_page_call(callback: types.CallbackQuery, state: FSMContext):
    client = users_data[callback.from_user.id]["client_info"]
    await callback.message.edit_text(f"""Вот вся информация:
id: {client.id}
name: {client.name}
description: {client.type}
telephone: {client.telephone}
email: {client.email}
password: {client.password}
""",    reply_markup=get_keyboard_from_edit_client_profile())


@dp.callback_query(F.data.startswith("client_"), Gen.edit_client_profile)
async def work_with_tour_operator_edit(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "close":
        requests.update_client(users_data[callback.from_user.id]["client_info"])
        await callback.message.edit_text("Всё поменяли, работаем дальше, изменения в бд сами внесутся как-нибудь")
        await state.set_state(Gen.auth_client)
    else:
        users_data[callback.from_user.id]["parameter_type"] = type
        if type == "type":
            await callback.message.edit_text(f"Выберите новое значение поля {type}:", reply_markup=get_keyboard_from_search_type())
            await state.set_state(Gen.get_new_parameter_for_client_profile)
            return
        await callback.message.edit_text(f"Введите новое значение поля {type}:")
        await state.set_state(Gen.get_new_parameter_for_client_profile)


@dp.callback_query(F.data.startswith("typ_"), Gen.get_new_parameter_for_client_profile)
async def get_new_parameter_for_client_profile_call(callback: types.CallbackQuery, state: FSMContext):
    users_data[callback.from_user.id]["client_info"].set_parameter("type", callback.data.split("_")[1])
    await state.set_state(Gen.edit_client_profile)
    await edit_client_page_call(callback, state)


@dp.message(F.text, Gen.get_new_parameter_for_client_profile)
async def get_new_parameter_for_client_profile(message: types.Message, state: FSMContext):
    res = message.text
    type = users_data[message.from_user.id]["parameter_type"]
    if type == "telephone":
        res = check_telephone_number(res)
        if not res:
            await message.answer("Введён неправильный номер телефона.\nВведите корректный номер телефона в формате +7(888)888-88-88")
            return
    elif type == "email":
        res = check_email(res)
        if not res:
            await message.answer("Введён неправильный email.\nВведите корректный email")
            return
    users_data[message.from_user.id]["client_info"].set_parameter(type, res)
    await state.set_state(Gen.edit_client_profile)
    await edit_client_page(message, state)


@dp.message(Command("see_all_tour"), Gen.auth_client)
async def cmd_see_all_tour(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_tours"] = requests.get_all_tour()
    users_data[message.from_user.id]["tour_page"] = 0
    if users_data[message.from_user.id]["all_tours"] == []:
        await message.answer("Пока туров нет")
        return
    await message.answer(f"Вот {users_data[message.from_user.id]['tour_page'] + 1}-я страница с турами.",
                         reply_markup=get_keyboard_from_see_all_my_tour(users_data[message.from_user.id]["all_tours"],
                                                                        users_data[message.from_user.id]["tour_page"]))
    await state.set_state(Gen.client_see_all_tour)


@dp.callback_query(F.data.startswith("tour_"), Gen.client_see_all_tour)
async def work_with_all_tour(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    print(type)
    if type == "prev":
        await switch_prev_page(callback)
    elif type == "next":
        await switch_next_page(callback)
    elif type == "close":
        await callback.message.edit_text("Насмотрелись")
        await state.set_state(Gen.auth_client)
    elif type.isdigit():
        users_data[callback.from_user.id]["tour_ind"] = int(type)
        await switch_to_tour_page_from_register(callback, state)


async def switch_to_tour_page_from_register(callback: types.CallbackQuery, state: FSMContext):
    ind = users_data[callback.from_user.id]["tour_ind"]
    tour = users_data[callback.from_user.id]["all_tours"][ind]
    await callback.message.edit_text(
        f"""Вот вся информация, о требуемом туре:
id: {tour.id}
Название: {tour.name}
Сезонные цены: {print_season_price(tour.season_price)}
Даты: {print_dates(tour.dates)}
Описание: {tour.description}
Места: {print_places(tour.place)}
Продолжительность: {tour.duration}
Количество мест: {tour.limit}
Выберете дату в которую хотите забронировать.""", reply_markup=get_keyboard_from_register_to_tour(tour))
    await state.set_state(Gen.client_register_to_tour)


@dp.callback_query(F.data.startswith("regtour_"), Gen.client_register_to_tour)
async def register_to_tour(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "close":
        await state.set_state(Gen.auth_client)
    else:
        date = check_date(type)[0]
        #ind = users_data[callback.from_user.id]["tour_ind"]
        #tour = users_data[callback.from_user.id]["all_tours"][ind]
        users_data[callback.from_user.id]["date"] = date
        #ans = requests.register_client_to_tour(users_data[callback.from_user.id]["client_id"], tour.id, date)
        await callback.message.edit_text("Сколько мест хотите забронировать?")
        await state.set_state(Gen.client_switch_kol)


@dp.message(F.text.isdigit(), Gen.client_switch_kol)
async def switch_kol(message: types.Message, state: FSMContext):
    kol = int(message.text)
    ind = users_data[message.from_user.id]["tour_ind"]
    tour = users_data[message.from_user.id]["all_tours"][ind]
    date = users_data[message.from_user.id]["date"]
    if requests.register_client_to_tour(users_data[message.from_user.id]["client_id"], tour.id, date, kol):
        await message.answer("Вы зарегестрированы")
    else:
        await message.answer("Не достаточно мест.")
    await state.set_state(Gen.auth_client)


@dp.message(Command("start_tour"), Gen.auth_tour_operator)
async def cmd_start_tour(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_tours"] = requests.get_all_my_tour(users_data[message.from_user.id]["tour_operator_id"])
    users_data[message.from_user.id]["tour_page"] = 0
    if users_data[message.from_user.id]["all_tours"] == []:
        await message.answer("У вас нет туров")
        return
    await message.answer(
        f"Вот {users_data[message.from_user.id]['tour_page'] + 1}-я страница с вашими турами. Выберете тур, который хотите провести.",
        reply_markup=get_keyboard_from_see_all_my_tour(users_data[message.from_user.id]["all_tours"],
                                                       users_data[message.from_user.id]["tour_page"]))
    await state.set_state(Gen.tour_operator_conduct_tour)


@dp.callback_query(F.data.startswith("tour_"), Gen.tour_operator_conduct_tour)
async def select_tour_from_conduct(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    print(type)
    if type == "prev":
        await switch_prev_page(callback)
    elif type == "next":
        await switch_next_page(callback)
    elif type == "close":
        await callback.message.edit_text("Насмотрелись")
        await state.set_state(Gen.auth_tour_operator)
    elif type.isdigit():
        users_data[callback.from_user.id]["tour_ind"] = int(type)
        await switch_to_tour_page_from_conduct(callback, state)


async def switch_to_tour_page_from_conduct(callback: types.CallbackQuery, state: FSMContext):
    ind = users_data[callback.from_user.id]["tour_ind"]
    tour = users_data[callback.from_user.id]["all_tours"][ind]
    await callback.message.edit_text(
        f"""Вот вся информация, о требуемом туре:
id: {tour.id}
Название: {tour.name}
Сезонные цены: {print_season_price(tour.season_price)}
Даты: {print_dates(tour.dates)}
Описание: {tour.description}
Места: {print_places(tour.place)}
Продолжительность: {tour.duration}
Количество мест: {tour.limit}
Выберете дату в которую вы хотите провести тур.""", reply_markup=get_keyboard_from_register_to_tour(tour))
    await state.set_state(Gen.tour_operator_conduct_tour_date)


@dp.callback_query(F.data.startswith("regtour_"), Gen.tour_operator_conduct_tour_date)
async def register_to_tour(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "close":
        await state.set_state(Gen.auth_tour_operator)
    else:
        date = check_date(type)[0]
        users_data[callback.from_user.id]["date"] = date
        await callback.message.edit_text("Какой бонус хотите начислить, всем, кто записался на тур?\n(Введите количество бонусов, которое будет зачисляться за каждое купленное место)")
        await state.set_state(Gen.tour_operator_switch_bonus_count)


@dp.message(F.text.isdigit(), Gen.tour_operator_switch_bonus_count)
async def conduct_tour(message: types.Message, state: FSMContext):
    count = int(message.text)
    ind = users_data[message.from_user.id]["tour_ind"]
    tour = users_data[message.from_user.id]["all_tours"][ind]
    date = users_data[message.from_user.id]["date"]
    requests.give_bonus_to_tour(users_data[message.from_user.id]["tour_operator_id"], tour.id, date, count)
    requests.delete_bookings_tour(tour.id, date)
    await message.answer("Тур проведён, бонусы разосланы")
    await state.set_state(Gen.auth_tour_operator)

@dp.message(Command("edit_profile"), Gen.auth_tour_operator)
async def cmd_edit_tour_operator_profile(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["tour_operator_info"] = requests.get_tour_operator_by_id(users_data[message.from_user.id]["tour_operator_id"])
    await state.set_state(Gen.edit_tour_operator_profile)
    await edit_tour_operator_page(message, state)


async def edit_tour_operator_page(message: types.Message, state: FSMContext):
    tour_operator = users_data[message.from_user.id]["tour_operator_info"]
    await message.answer(f"""Вот вся информация:
id: {tour_operator.id}
name: {tour_operator.name}
description: {tour_operator.description}
telephone: {tour_operator.telephone}
email: {tour_operator.email}
password: {tour_operator.password}
""",    reply_markup=get_keyboard_from_edit_tour_operator_profile())


@dp.callback_query(F.data.startswith("oper_"), Gen.edit_tour_operator_profile)
async def work_with_tour_operator_edit(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "close":
        requests.update_tour_operator(users_data[callback.from_user.id]["tour_operator_info"])
        await callback.message.edit_text("Всё поменяли, работаем дальше, изменения в бд сами внесутся как-нибудь")
        await state.set_state(Gen.auth_tour_operator)
    else:
        users_data[callback.from_user.id]["parameter_type"] = type
        await callback.message.edit_text(f"Введите новое значение поля {type}:")
        await state.set_state(Gen.get_new_parameter_for_tour_operator_profile)


@dp.message(F.text, Gen.get_new_parameter_for_tour_operator_profile)
async def get_new_parameter_for_tour_operator_profile(message: types.Message, state: FSMContext):
    res = message.text
    type = users_data[message.from_user.id]["parameter_type"]
    if type == "telephone":
        res = check_telephone_number(res)
        if not res:
            await message.answer("Введён неправильный номер телефона.\nВведите корректный номер телефона в формате +7(888)888-88-88")
            return
    elif type == "email":
        res = check_email(res)
        if not res:
            await message.answer("Введён неправильный email.\nВведите корректный email")
            return
    users_data[message.from_user.id]["tour_operator_info"].set_parameter(type, res)
    await state.set_state(Gen.edit_tour_operator_profile)
    await edit_tour_operator_page(message, state)


@dp.message(Command("edit_tour"), Gen.auth_tour_operator)
async def cmd_edit_tour(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_tours"] = requests.get_all_my_tour(users_data[message.from_user.id]["tour_operator_id"])
    users_data[message.from_user.id]["tour_page"] = 0
    if users_data[message.from_user.id]["all_tours"] == []:
        await message.answer("У вас нет туров")
        return
    await message.answer(f"Вот {users_data[message.from_user.id]['tour_page'] + 1}-я страница с вашими турами. Выберете тур, который хотите изменить.",
                         reply_markup=get_keyboard_from_see_all_my_tour(users_data[message.from_user.id]["all_tours"],
                                                                        users_data[message.from_user.id]["tour_page"]))
    await state.set_state(Gen.tour_operator_edit_tour)


@dp.callback_query(F.data.startswith("tour_"), Gen.tour_operator_edit_tour)
async def work_with_all_tour_pages_for_edit(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "prev":
        await switch_prev_page(callback)
    elif type == "next":
        await switch_next_page(callback)
    elif type == "close":
        await callback.message.edit_text("Не будем ничего исправлять? Эх, а я уже подключился к бд.")
        await state.set_state(Gen.auth_tour_operator)
    elif type.isdigit():
        users_data[callback.from_user.id]["tour_number"] = int(type)
        await edit_tour_page(callback, state)


async def edit_tour_page(callback: types.CallbackQuery, state: FSMContext):
    ind = users_data[callback.from_user.id]["tour_number"]
    tour = users_data[callback.from_user.id]["all_tours"][ind]
    await callback.message.edit_text(
        f"""Вот вся информация, о требуемом туре:
id: {tour.id}
Название: {tour.name}
Сезонные цены: {print_season_price(tour.season_price)}
Даты: {print_dates(tour.dates)}
Описание: {tour.description}
Места: {print_places(tour.place)}
Продолжительность: {tour.duration}
Количество мест: {tour.limit}
Выберите параметр, который хотите поменять:
""", reply_markup=get_keyboard_from_edit_tour())
    await state.set_state(Gen.tour_operator_edit_tour_set_parameter)


async def edit_tour_page_mes(message: types.Message, state: FSMContext):
    ind = users_data[message.from_user.id]["tour_number"]
    print(ind)
    tour = users_data[message.from_user.id]["all_tours"][ind]
    print(users_data[message.from_user.id]["all_tours"])
    await message.answer(
        f"""Вот вся информация, о требуемом туре:
id: {tour.id}
Название: {tour.name}
Сезонные цены: {print_season_price(tour.season_price)}
Даты: {print_dates(tour.dates)}
Описание: {tour.description}
Места: {print_places(tour.place)}
Продолжительность: {tour.duration}
Количество мест: {tour.limit}
Выберите параметр, который хотите поменять:
""", reply_markup=get_keyboard_from_edit_tour())
    await state.set_state(Gen.tour_operator_edit_tour_set_parameter)


@dp.callback_query(F.data.startswith("tour_"), Gen.tour_operator_edit_tour_set_parameter)
async def set_tour_parametrs(callback: types.CallbackQuery, state: FSMContext):
    type = "_".join(callback.data.split("_")[1:])
    if type == "close":
        await callback.message.edit_text("Всё, поменяли? Работаем дальше, обновление бд отдам на аутсорс.")
        ind = users_data[callback.from_user.id]["tour_number"]
        tour = users_data[callback.from_user.id]["all_tours"][ind]
        requests.update_tour(tour)
        await state.set_state(Gen.auth_tour_operator)
    else:
        await callback.message.edit_text(f"Введите новое значение для поля: {type} (помните, что значения такого поля как например dates нужно вводить в определённом формате):")
        await state.set_state(Gen.tour_operator_edit_tour_wait_parameter)
        users_data[callback.from_user.id]["parameter_type"] = type


@dp.message(F.text, Gen.tour_operator_edit_tour_wait_parameter)
async def wait_tour_parameter(message: types.Message, state: FSMContext):
    type = users_data[message.from_user.id]["parameter_type"]
    res = message.text
    print(type)
    if type == "season_price":
        res = check_season_price(res)
    elif type == "dates":
        res = check_date(res)
        if not res:
            await message.answer(
                "Введена некорректная дата.\nВведите даты, в которые будет стартовать этот тур в формате ДД.ММ.ГГГГ через пробел:")
            return
    elif type == "place":
        res = check_tour_place(res)
    ind = users_data[message.from_user.id]["tour_number"]
    print(res)
    users_data[message.from_user.id]["all_tours"][ind].set_parameter(type, res)
    await state.set_state(Gen.tour_operator_edit_tour)
    await edit_tour_page_mes(message, state)


@dp.message(Command("delete_tour"), Gen.auth_tour_operator)
async def cmd_delete_tour(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_tours"] = requests.get_all_my_tour(users_data[message.from_user.id]["tour_operator_id"])
    users_data[message.from_user.id]["tour_page"] = 0
    if users_data[message.from_user.id]["all_tours"] == []:
        await message.answer("У вас нет туров")
        return
    await message.answer(f"Вот {users_data[message.from_user.id]['tour_page'] + 1}-я страница с вашими турами. Выберете тур, который хотите удалить",
                         reply_markup=get_keyboard_from_see_all_my_tour(users_data[message.from_user.id]["all_tours"],
                                                                        users_data[message.from_user.id]["tour_page"]))
    await state.set_state(Gen.tour_operator_delete_tour)


@dp.callback_query(F.data.startswith("tour_"), Gen.tour_operator_delete_tour)
async def work_with_all_tour_pages_for_delete(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    if type == "prev":
        await switch_prev_page(callback)
    elif type == "next":
        await switch_next_page(callback)
    elif type == "close":
        await callback.message.edit_text("Решили ничего не удалять, ну и правильно.")
        await state.set_state(Gen.auth_tour_operator)
    elif type.isdigit():
        requests.delete_tour(users_data[callback.from_user.id]["all_tours"][int(type)])
        # TODO написать проверку того, что тур удалён
        await callback.message.edit_text("Тур удалён.")
        await state.set_state(Gen.auth_tour_operator)


@dp.message(Command("see_all_my_tour"), Gen.auth_tour_operator)
async def cmd_see_all_my_tour(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["all_tours"] = requests.get_all_my_tour(users_data[message.from_user.id]["tour_operator_id"])
    users_data[message.from_user.id]["tour_page"] = 0
    if users_data[message.from_user.id]["all_tours"] == []:
        await message.answer("У вас нет туров")
        return
    await message.answer(f"Вот {users_data[message.from_user.id]['tour_page'] + 1}-я страница с вашими турами.",
                         reply_markup=get_keyboard_from_see_all_my_tour(users_data[message.from_user.id]["all_tours"], users_data[message.from_user.id]["tour_page"]))
    await state.set_state(Gen.tour_operator_see_all_my_tour)


async def switch_next_page(callback: types.CallbackQuery):
    if len(users_data[callback.from_user.id]["all_tours"]) > (users_data[callback.from_user.id]["tour_page"] + 1) * tour_on_page:
        users_data[callback.from_user.id]["tour_page"] += 1
        await callback.message.edit_text(f"Вот {users_data[callback.from_user.id]['tour_page'] + 1}-я страница с вашими турами.",
                             reply_markup=get_keyboard_from_see_all_my_tour(
                                 users_data[callback.from_user.id]["all_tours"],
                                 users_data[callback.from_user.id]["tour_page"]))


async def switch_prev_page(callback: types.CallbackQuery):
    if users_data[callback.from_user.id]["tour_page"] != 0:
        users_data[callback.from_user.id]["tour_page"] -= 1
        await callback.message.edit_text(f"Вот {users_data[callback.from_user.id]['tour_page'] + 1}-я страница с вашими турами.",
                                reply_markup=get_keyboard_from_see_all_my_tour(
                                    users_data[callback.from_user.id]["all_tours"],
                                    users_data[callback.from_user.id]["tour_page"]))


async def switch_to_tour_page(callback: types.CallbackQuery, ind, state: FSMContext):
    tour = users_data[callback.from_user.id]["all_tours"][ind]
    await callback.message.edit_text(
        f"""Вот вся информация, о требуемом туре:
id: {tour.id}
Название: {tour.name}
Сезонные цены: {print_season_price(tour.season_price)}
Даты: {print_dates(tour.dates)}
Описание: {tour.description}
Места: {print_places(tour.place)}
Продолжительность: {tour.duration}
Количество мест: {tour.limit}
""")
    await state.set_state(Gen.auth_tour_operator)


def print_places(places):
    places = json.loads(places)
    s = "\n"
    for i in places.keys():
        s = s + i + ": " + ', '.join(places[i]) + "\n"
    s = s[:-1]
    return s


def print_dates(dates):
    s = "\n"
    for date in dates:
        s = s + date.strftime('%d.%m.%Y') + "\n"
    s = s[:-1]
    return s


def print_season_price(season_price):
    season_price = json.loads(season_price)
    s = "\n"
    for i in season_price.keys():
        s = s + i + ": " + str(season_price[i]) + "\n"
    s = s[:-1]
    return s


#TODO подумать над добавлением состояния просмотра страницы
@dp.callback_query(F.data.startswith("tour_"), Gen.tour_operator_see_all_my_tour)
async def work_with_all_tour_pages(callback: types.CallbackQuery, state: FSMContext):
    type = callback.data.split("_")[1]
    print(type)
    if type == "prev":
        await switch_prev_page(callback)
    elif type == "next":
        await switch_next_page(callback)
    elif type == "close":
        await callback.message.edit_text("Насмотрелись")
        await state.set_state(Gen.auth_tour_operator)
    elif type.isdigit():
        await switch_to_tour_page(callback, int(type), state)



# norm
@dp.message(Command("create_new_tour"), Gen.auth_tour_operator)
async def cmd_create_new_tour(message: types.Message, state: FSMContext):
    await message.answer("Введите название тура:")
    await state.set_state(Gen.tour_name)


# norm
@dp.message(F.text, Gen.tour_name)
async def set_tour_name(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["tour"]["name"] = message.text
    await message.answer("Введите даты, в которые будет стартовать этот тур в формате ДД.ММ.ГГГГ через пробел:")
    await state.set_state(Gen.tour_date)


def check_date(dates):
    try:
        dates_array = dates.split()
        for i in range(len(dates_array)):
            val = datetime.datetime.strptime(dates_array[i], "%d.%m.%Y").date()
            dates_array[i] = val
        return dates_array
    except ValueError:
        return False


# norm
@dp.message(F.text, Gen.tour_date)
async def set_tour_date(message: types.Message, state: FSMContext):
    ans = check_date(message.text)
    if ans:
        users_data[message.from_user.id]["tour"]["dates"] = ans
        await message.answer("Введите продолжительность тура с указанием едениц измерения (часы, дни, месяцы)")
        await state.set_state(Gen.tour_duration)
    else:
        await message.answer("Введена некорректная дата.\nВведите даты, в которые будет стартовать этот тур в формате ДД.ММ.ГГГГ через пробел:")


# norm
@dp.message(F.text, Gen.tour_duration)
async def set_tour_duration(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["tour"]["duration"] = message.text
    await message.answer("Введите описание тура:")
    await state.set_state(Gen.tour_description)


# norm
@dp.message(F.text, Gen.tour_description)
async def set_tour_description(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["tour"]["description"] = message.text
    await message.answer("Введите места, которые будут посещены в туре:")
    await message.answer(
        "Места следует вводить в таком формате:\nСтрана1: город1, город2\nСтрана2: город1, город2\nКаждую новую страну необходимо вводить на новой строке, каждый новый город необходимо вводить через запятую.")
    await state.set_state(Gen.tour_place)


def check_tour_place(data):
    place = {}
    for big in data.split("\n"):
        s = big.split(":")
        place[s[0]] = [i.strip() for i in s[1].split(",")]
    return place

# norm
@dp.message(F.text, Gen.tour_place)
async def set_tour_place(message: types.Message, state: FSMContext):
    place = check_tour_place(message.text)
    print(place)
    users_data[message.from_user.id]["tour"]["place"] = json.dumps(place, ensure_ascii=False)
    await message.answer("Введите сезонные цены:")
    await message.answer(
        "Сезонные цены следует вводить в таком формате:\nМесяц1: цена\nМесяц2: цена\n Каждый новый месяц необходимо вводить на новой строке")
    await state.set_state(Gen.tour_season_price)


def check_season_price(data):
    price = {}
    for big in data.split("\n"):
        s = big.split(":")
        price[int(s[0])] = int(s[1].strip())
    return price

# norm
@dp.message(F.text, Gen.tour_season_price)
async def set_tour_season_price(message: types.Message, state: FSMContext):
    price = check_season_price(message.text)
    print(price)
    users_data[message.from_user.id]["tour"]["season_price"] = json.dumps(price, ensure_ascii=False)
    await message.answer("Введите количество мест в туре:")
    await state.set_state(Gen.tour_limit)


# qwerty123
# norm
@dp.message(F.text, Gen.tour_limit)
async def set_tour_limit(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите количество мест в туре (только число):")
        return
    users_data[message.from_user.id]["tour"]["limit"] = int(message.text)
    requests.create_new_tour(users_data[message.from_user.id]["tour"]["name"],
                             users_data[message.from_user.id]["tour"]["season_price"],
                             users_data[message.from_user.id]["tour"]["dates"],
                             users_data[message.from_user.id]["tour"]["description"],
                             users_data[message.from_user.id]["tour"]["place"],
                             users_data[message.from_user.id]["tour"]["duration"],
                             users_data[message.from_user.id]["tour"]["limit"],
                             users_data[message.from_user.id]["tour_operator_id"])
    users_data[message.from_user.id]["tour"] = {}
    # TODO добавить проверку того, что тур создан
    await message.answer("Тур создан!")
    await state.set_state(Gen.auth_tour_operator)


# norm
# TODO подумать над добавлением состояния just_chill как фильтра для команд auth, reg и остальных
@dp.message(Command("auth"))
async def cmd_authorization(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип пользователя, под которым вы хотите авторизоваться:",
                         reply_markup=get_keyboard_from_auth())
    await state.set_state(Gen.register)


# norm
@dp.callback_query(F.data.startswith("auth_"), Gen.register)
async def set_type_authorization(callback: types.CallbackQuery, state: FSMContext):
    types = callback.data.split("_")[1]
    if types == "oper":
        users_data[callback.from_user.id]["authorization"]["type"] = "operator"
        await callback.message.edit_text(f"Введите почту туроператора:")
        await state.set_state(Gen.tour_operator_email_auth)
    elif types == "client":
        users_data[callback.from_user.id]["authorization"]["type"] = "client"
        await callback.message.edit_text(f"Введите почту:")
        await state.set_state(Gen.client_email_auth)
    elif types == "finish":
        await callback.message.edit_text(f"Авторизация прервана")
        await state.set_state(Gen.just_chill)


# norm
@dp.message(F.text, Gen.tour_operator_email_auth)
async def auth_tour_operator_email(message: types.Message, state: FSMContext):
    res = check_email(message.text)
    if res:
        if requests.find_tour_operator_by_email(res) is None:
            await message.answer("Пользователя с такой почтой не существует.\nВведите другой email")
            return
        users_data[message.from_user.id]["authorization"]["email"] = res
        await message.answer(f"Введите пароль:")
        await state.set_state(Gen.tour_operator_password_auth)
    else:
        await message.answer(f"Введён некорректный email.\nВведите корректный email")


# norm
@dp.message(F.text, Gen.tour_operator_password_auth)
async def auth_tour_operator_password(message: types.Message, state: FSMContext):
    ans = requests.auth_tour_operator(users_data[message.from_user.id]["authorization"]["email"], message.text)
    if ans[0]:
        users_data[message.from_user.id]["tour_operator_id"] = ans[1]
        await message.answer("Вы авторизованы.")
        await state.set_state(Gen.auth_tour_operator)
        await cmd_start(message, state)
    else:
        await message.answer("Неправильный пароль, введите другой пароль:")


# norm
@dp.message(F.text, Gen.client_email_auth)
async def auth_client_email(message: types.Message, state: FSMContext):
    res = check_email(message.text)
    if res:
        print(res)
        if requests.find_client_by_email(res) is None:
            await message.answer("Пользователя с такой почтой не существует.\nВведите другой email")
            return
        users_data[message.from_user.id]["authorization"]["email"] = res
        await message.answer(f"Введите пароль:")
        await state.set_state(Gen.client_password_auth)
    else:
        await message.answer(f"Введён неправильный email.\nВведите корректный email")


# norm
@dp.message(F.text, Gen.client_password_auth)
async def auth_client_password(message: types.Message, state: FSMContext):
    ans = requests.auth_client(users_data[message.from_user.id]["authorization"]["email"], message.text)
    if ans[0]:
        users_data[message.from_user.id]["client_id"] = ans[1]
        await message.answer("Вы авторизованы.")
        await state.set_state(Gen.auth_client)
        await cmd_start(message, state)
    else:
        await message.answer("Неправильный пароль, введите другой пароль:")


# norm
@dp.message(Command("quite"))
async def cmd_quite(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["client_id"] = -1
    users_data[message.from_user.id]["tour_operator_id"] = -1
    users_data[message.from_user.id]["all_tours"] = []
    await state.set_state(Gen.just_chill)


# norm
@dp.message(Command("reg"))
async def cmd_registration(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип пользователя, под которым вы хотите зарегестрироваться:",
                         reply_markup=get_keyboard_from_reg())
    await state.set_state(Gen.register)


# norm
@dp.callback_query(F.data.startswith("reg_"), Gen.register)
async def continue_registration(callback: types.CallbackQuery, state: FSMContext):
    types = callback.data.split("_")[1]
    if types == "oper":
        users_data[callback.from_user.id]["registration"]["type"] = "operator"
        await callback.message.edit_text(f"Будем регестрироваться, как туроператор.\nВведите название туроператора:")
        await state.set_state(Gen.tour_operator_name)
    elif types == "client":
        users_data[callback.from_user.id]["registration"]["type"] = "client"
        await callback.message.edit_text(f"Будем регестрироваться, как клиент.\nВведите имя:")
        await state.set_state(Gen.client_name)
    elif types == "finish":
        await callback.message.edit_text(f"Регистрация прервана")
        await state.set_state(Gen.just_chill)


# norm
@dp.message(F.text, Gen.tour_operator_name)
async def set_tour_operator_name(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["registration"]["name"] = message.text
    await message.answer(f"Отлично, {message.text}, продолжим регистрацию.\nВведите описание туроператора:")
    await state.set_state(Gen.tour_operator_description)


# norm
@dp.message(F.text, Gen.tour_operator_description)
async def set_tour_operator_description(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["registration"]["description"] = message.text
    await message.answer(
        f"Отлично, {users_data[message.from_user.id]['registration']['name']}, продолжим регистрацию.\nВведите телефонный номер туроператора в формате +7(888)888-88-88:")
    await state.set_state(Gen.tour_operator_telephone)


def check_telephone_number(number):
    number = ''.join(number.split())
    result = re.search("^[+]?[0-9]+[(]?[0-9]{3}[)]?[-\s]?[0-9]{3}[-\s]?[0-9]{2,3}[-\s]?[0-9]{2,3}$", number)
    # print(result.string)
    if result:
        return result.string
    return False


# norm
@dp.message(F.text, Gen.tour_operator_telephone)
async def set_tour_operator_telephone(message: types.Message, state: FSMContext):
    res = check_telephone_number(message.text)
    if res:
        print(message.text)
        users_data[message.from_user.id]["registration"]["telephone"] = res
        print(users_data[message.from_user.id])
        await message.answer(
            f"Отлично, {users_data[message.from_user.id]['registration']['name']}, продолжим регистрацию.\nВведите email:")
        await state.set_state(Gen.tour_operator_email)
    else:
        await message.answer(
            f"Введён неправильный номер телефона.\nВведите корректный номер телефона в формате +7(888)888-88-88")


def check_email(email):
    result = re.search("^[a-zA-Z0-9.]+[@][a-zA-Z0-9]+[.][a-zA-Z0-9]+$", email)
    if result:
        return result.string
    return False


# norm
@dp.message(F.text, Gen.tour_operator_email)
async def set_tour_operator_email(message: types.Message, state: FSMContext):
    res = check_email(message.text)
    if res:
        if not (requests.find_tour_operator_by_email(res) is None):
            await message.answer("Пользователь с такой почтой уже существует.\nВведите другой email")
            return
        users_data[message.from_user.id]["registration"]["email"] = res
        await message.answer(
            f"Отлично, {users_data[message.from_user.id]['registration']['name']}, регистрация почти закончена.\nВведите пароль:")
        await state.set_state(Gen.tour_operator_password)
    else:
        await message.answer(f"Введён неправильный email.\nВведите корректный email")


# norm
@dp.message(F.text, Gen.tour_operator_password)
async def create_tour_operator(message: types.Message, state: FSMContext):
    requests.create_new_tour_operator(users_data[message.from_user.id]["registration"]["name"],
                                      users_data[message.from_user.id]["registration"]["description"],
                                      users_data[message.from_user.id]["registration"]["telephone"],
                                      users_data[message.from_user.id]["registration"]["email"],
                                      message.text)
    await message.answer("Новый пользователь типа туроператор создан.")
    # TODO подумать над проверкой того, что пользователь создан
    await state.set_state(Gen.just_chill)
    await cmd_start(message, state)


# norm
@dp.message(F.text, Gen.client_name)
async def set_client_name(message: types.Message, state: FSMContext):
    users_data[message.from_user.id]["registration"]["name"] = message.text
    await message.answer(f"Отлично, {message.text}, продолжим регистрацию.\nВыберете тип пользователя:",
                         reply_markup=get_keyboard_from_search_type())
    await state.set_state(Gen.client_type)

#norm
@dp.callback_query(F.data.startswith("typ_"), Gen.client_type)
async def set_client_type(callback: types.CallbackQuery, state: FSMContext):
    types = callback.data.split("_")[1]
    users_data[callback.from_user.id]["registration"]["typ"] = types
    if types == "ur":
        await callback.message.edit_text(
            f"Отлично, {users_data[callback.from_user.id]['registration']['name']}, будем регестрироваться, как юрлицо.\nВведите телефонный номер туроператора в формате +7(888)888-88-88:")
    else:
        await callback.message.edit_text(
            f"Отлично, {users_data[callback.from_user.id]['registration']['name']}, будем регестрироваться, как физлицо.\nВведите телефонный номер туроператора в формате +7(888)888-88-88:")
    await state.set_state(Gen.client_telephone)

#norm
@dp.message(F.text, Gen.client_telephone)
async def set_client_telephone(message: types.Message, state: FSMContext):
    res = check_telephone_number(message.text)
    if res:
        print(message.text)
        users_data[message.from_user.id]["registration"]["telephone"] = res
        print(users_data[message.from_user.id])
        await message.answer(
            f"Отлично, {users_data[message.from_user.id]['registration']['name']}, продолжим регистрацию.\nВведите email:")
        await state.set_state(Gen.client_email)
    else:
        await message.answer(
            f"Введён неправильный номер телефона.\nВведите корректный номер телефона в формате +7(888)888-88-88")

#norm
@dp.message(F.text, Gen.client_email)
async def set_client_email(message: types.Message, state: FSMContext):
    res = check_email(message.text)
    if res:
        if not (requests.find_client_by_email(res) is None):
            await message.answer("Пользователь с такой почтой уже существует.\nВведите другой email")
            return
        users_data[message.from_user.id]["registration"]["email"] = res
        await message.answer(
            f"Отлично, {users_data[message.from_user.id]['registration']['name']}, регистрация почти закончена.\nВведите пароль:")
        await state.set_state(Gen.client_password)
    else:
        await message.answer(f"Введён неправильный email.\nВведите корректный email")

#norm
@dp.message(F.text, Gen.client_password)
async def create_client(message: types.Message, state: FSMContext):
    requests.create_new_client(users_data[message.from_user.id]["registration"]["name"],
                               users_data[message.from_user.id]["registration"]["typ"],
                               users_data[message.from_user.id]["registration"]["telephone"],
                               users_data[message.from_user.id]["registration"]["email"],
                               message.text)
    await message.answer("Новый пользователь создан.")
    #TODO подумать над добавлением проверки того, что новый клиент создан
    await state.set_state(Gen.just_chill)
    await cmd_start(message, state)


async def start_polling():
    bot = Bot(token)
    await bot.delete_webhook(drop_pending_updates=True)
    print("log: 200")
    await dp.start_polling(bot)
