import os
import json
import sys
import codecs
import requests
import config
import data_base
import re
import logging
import  asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import sql
from data_base import SQLl

from bs4 import BeautifulSoup as BS

class GetID(StatesGroup):
    id = State()

class GetSer(StatesGroup):
    ser = State()
    number = State()


passport_file_name = "test.json"
url_db = config.url
logging.basicConfig(filename="DocumentCheckBotLog.log", level=logging.INFO)
logger = logging.getLogger(__name__)
storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot,storage=storage)
db = SQLl('passports.db')

@dp.message_handler(commands = ['start','help'])
async def help(message: types.Message):
    #список команд
    await message.answer("Привет. Давай проверим проверим что я умею.")


@dp.message_handler(commands = ['menu'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('Поиск по ID')
    itembtn2 = types.KeyboardButton('Поиск по серии и номеру паспорта')
    itembtn3 = types.KeyboardButton('О разработчике')
    itembtn4 = types.KeyboardButton('Справка')
    markup.add(itembtn1, itembtn2, itembtn3,itembtn4)
    await message.answer("Выберите действие, которое хотите совершить или напишите команду.", reply_markup=markup)

## Информация о разработчике
@dp.message_handler(commands = ['dev'])
@dp.message_handler(Text(equals="О разработчике"))
async def devinf(message: types.Message):
    markup = types.ReplyKeyboardRemove(selective=False)
    await message.answer('Разработчик бота студент 535Б группы: Морозов Д.С.\nОбратная связь: https://t.me/r3ason_why\nДата создания: 23.05.2021.', reply_markup=markup)

@dp.message_handler(commands = ['info'])
@dp.message_handler(Text(equals="Справка"))
async def get_info(message: types.Message):
    markup = types.ReplyKeyboardRemove(selective=False)
    await message.answer("Этот бот позволяет вам проверить получить информацию о документе по ID или серии и номеру."
                         "\nДоступные команды:"
                         "\n/menu - выбор функций\n/id - поиск по id\n/series - поиск по серии и номеру документа\n/dev - информация о разработчике\n/uplist - узнать историю обновлений\n/unsubscribe - отписаться от уведомлений", reply_markup=markup)

@dp.message_handler(commands = ['id'])
@dp.message_handler(Text(equals="Поиск по ID"))
async def input_id(message: types.Message):
    markup = types.ReplyKeyboardRemove(selective=False)
    await message.answer('Введите ID: ', reply_markup=markup)
    await GetID.id.set()




@dp.message_handler(commands = ['series'])
@dp.message_handler(Text(equals="Поиск по серии и номеру паспорта"))
async def input_series(message: types.Message):
    markup = types.ReplyKeyboardRemove(selective=False)
    await message.answer('Введите серию: ', reply_markup=markup)
    await GetSer.ser.set()


@dp.message_handler(state=GetSer.ser)
async def input_number(message: types.Message, state: FSMContext):
    await state.update_data(ser=message.text)
    await message.answer("Введите номер паспорта : ")
    await GetSer.number.set()

# Метод для поиска по серии и номеру
@dp.message_handler(state=GetSer.number)
async def search_by_series(message: types.Message, state: FSMContext):
    number = str(message.text)
    check_db_update()
    data = await state.get_data()
    series = data.get("ser")
    del data
    await state.finish()
    #проверка введенных данных
    if(is_int(number) and len(series) == 2 and series.isupper()):
        res = get_pass(series,number)
        sub_id = res[1]
        if(sub_id != "0"):
            logging.info("Search passport by series for id" + str(message.chat.id))
            await message.answer(str(sub_id))
            await subscribe(message, str(sub_id))
            await unsubscribe(message, str(sub_id))
            await add_sub_but(message)
        else:
            await start(message)
    else:
        await message.answer("Вы неверно ввели номер и/или серию.")
        await start(message)





# Метод для поиска по id
@dp.message_handler(state=GetID.id)
async def search_by_id(message: types.Message, state: FSMContext):
    id = message.text
    await state.finish()
    #проверка введенных данных
    if(is_int(id)):
        check_db_update()
        res = get_pass_by_id(int(id))
        await message.answer(res[0])
        sub_id = res[1]
        if(sub_id != "0"):
            logging.info('Search passport by id for id' + str(message.from_user.id))
            await subscribe(message,str(sub_id))
            await unsubscribe(message,str(sub_id))
            await add_sub_but(message)
        else:
            await start(message)
    else:
        await message.answer("Вы неверно ввели id.")
        await start(message)


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

@dp.callback_query_handler(text="add_sub")
async def sub(call: types.CallbackQuery):
    await get_notifications(call)
    await call.message.answer("Вы успешно подписались на рассылку!\n")

async def add_sub_but(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Подписаться",callback_data="add_sub"))
    await message.answer("Хотите ли получать уведомления при обновлении статуса данного документа ?", reply_markup=keyboard)


# Метод для отправки уведомлений
async def notification(wait_for):
    if(os.path.exists("passports.db")):
        while True:
                await asyncio.sleep(wait_for)
                response = requests.get(config.url)
                soup = BS(response.content, 'html.parser')
                items = soup.findAll('div', class_='resource-list__item-container-title')
                for item in items:
                    if (item == items[1]):
                        passport_url = item.find('a').get('href')
                        break
                passport_url = "https://data.gov.ua" + str(passport_url)
                response = requests.get(passport_url)
                soup = BS(response.content, 'html.parser')
                items = soup.findAll('p', class_='dataset-details')
                update_date = items[0].get_text()
                if (check_last_update(update_date)):
                    break
                write_new_date(update_date)
                items = soup.findAll('div')
                for item in items:
                    if (item.find('a', class_='resource-url-analytics')):
                        passport_url = item.find('a', class_='resource-url-analytics').get('href')
                        break
                os.remove(passport_file_name)
                load_new_file(passport_url)
                subscriptions = db.get_subscriptions()
                for ntf in subscriptions:
                    if(ntf[2]):
                        logging.info('Notification to user id' + str(ntf[1]))
                        res = get_pass_by_id(ntf[3])
                        await bot.send_message(ntf[1],res[0])

# Метод для проверки обновления бд
def check_db_update():
    response = requests.get(config.url)
    soup = BS(response.content,'html.parser')
    items = soup.findAll('div', class_='resource-list__item-container-title')
    for item in items:
        if (item == items[1]):
            passport_url = item.find('a').get('href')
            break
    passport_url = "https://data.gov.ua" + str(passport_url)
    response = requests.get(passport_url)
    soup = BS(response.content, 'html.parser')
    items = soup.findAll('p', class_='dataset-details')
    update_date = items[0].get_text()
    check_last_update(update_date)
    if (not check_last_update(update_date)):
        write_new_date(update_date)
        items = soup.findAll('div')
        for item in items:
            if (item.find('a', class_='resource-url-analytics')):
                passport_url = item.find('a', class_='resource-url-analytics').get('href')
                break
        if (os.path.isfile(passport_file_name)):
            os.remove(passport_file_name)
        load_new_file(passport_url)


# метод для скачивания нового файла
def load_new_file(url):
    response = requests.get(url)
    f = open(passport_file_name, "wb")  # открываем файл для записи, в режиме wb
    f.write(response.content)  # записываем содержимое в файл; как видите - content запроса
    f.close()

# Метод для проверки последнего обновления
def check_last_update(update_date):
    with open("last_update.txt", 'r',encoding='latin-1') as file:
        result = file.readline()
        if(str(update_date) == result):
            return True
        else:
            return False
# Метод для записи новой даты
def write_new_date(date):
    with open("last_update.txt", 'w') as file:
        file.write(str(date))
        file.close()

# Метод для поиска паспорта по id
def get_pass_by_id (id):
    with open('test.json', 'r',encoding='utf_8_sig') as f:
        data = json.load(f)
        f.close()
        output = "0"
        res= ""
        for passport in data:
            if(int(id) == int(passport['ID'])):
                output = str(id)
                res = "ID: " + passport['ID'] + "\nПодразделение зарегистрировашее информацию: " + passport[
                    'OVD'] + "\nСерия: " + passport[
                          'D_SERIES'] + "\nНомер: " + passport['D_NUMBER'] + "\nТип документа: " + passport[
                          'D_TYPE'] + "\nСтатус: " + passport['D_STATUS'] + "\nДата пропажи: " + passport[
                          'THEFT_DATA'] + "\nДата добавления: " + passport['INSERT_DATE']
                break
        if(output == "0"):
            res = "Паспорта с таким id нет в базе"
            return [res, output]
        else:
            return [res, output]

# Метод для поиска паспорта по серии и номеру
def get_pass(series,number):
    with open('test.json', 'r',encoding='utf_8_sig') as f:
        data = json.load(f)
        f.close()
        output = "0"
        res = ""
        for passport in data:
            if(series == passport['D_SERIES'] and int(number) == int(passport['D_NUMBER']) ):
                output = passport['ID']
                res = "ID: " + passport['ID'] + "\nПодразделение зарегистрировашее информацию: " + passport['OVD'] + "\nСерия: " + passport[
                    'D_SERIES'] + "\nНомер: " + passport['D_NUMBER'] + "\nТип документа: " + passport[
                          'D_TYPE'] + "\nСтатус: " + passport['D_STATUS'] + "\nДата пропажи: " + passport[
                          'THEFT_DATA'] + "\nДата добавления: " + passport['INSERT_DATE']
                break
        if (output == "0"):
            res = "Паспорта с таким id нет в базе"
            return [res, output]
        else:
            return [res, output]


#update list
@dp.message_handler(commands = ['uplist'])
async def updt_list(message: types.Message):
    with open('uplist.txt', 'r',encoding='utf_8_sig') as f:
        data = f.read()
        f.close()
        await message.answer(data)


# Команда активации подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message,pass_id):
    logging.info('Subscribe for user id' + str(message.from_user.id))
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id,str(pass_id) )
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.add_id(message.from_user.id, pass_id,True)

async def get_notifications(call: types.CallbackQuery):
    logging.info('Subscribe for user id' + str(call.message.chat.id))
    db.update_subscription(call.message.chat.id, True)



@dp.message_handler(commands=['unsubscribe'])
async def unsub(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id,"0", False)
        await message.answer("Вы не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        logging.info('Unsubscribe for user id' + str(message.from_user.id))
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы отписаны от рассылки.")

# Команда отписки
async def unsubscribe(message: types.Message,pass_id):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id,pass_id, False)
        await message.answer("Вы не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        logging.info('Unsubscribe for user id' + str(message.from_user.id))
        db.update_subscription(message.from_user.id,False)
        await message.answer("Вы отписаны от рассылки.")



def main():
    loop = asyncio.get_event_loop()
    loop.create_task(notification(120))
    executor.start_polling(dispatcher=dp)


if __name__ == '__main__':
    if (not os.path.isfile(passport_file_name)):
        write_new_date("1")
        check_db_update()
    main()

