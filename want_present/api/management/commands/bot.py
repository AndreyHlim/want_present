import logging
import os
from datetime import datetime as dt

import requests
from api.telegram_calendar import telegramcalendar
from constants import TELEGRAM_TEXT
from dotenv import load_dotenv
from holidays.models import Holiday
from telegram import Bot, ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater
)
from telegram.utils.request import Request
from users.models import Profile

from django.core.management.base import BaseCommand

load_dotenv()


STEP1, STEP2 = range(2)


# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()


def log_errors(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            error_message = f'Произошла ошибка: {error}'
            print(error_message)
            raise error
    return inner


@log_errors
def say_hi(update, context):
    chat = update.effective_chat
    username = chat.first_name

    user = Profile.objects.filter(id_telegram=chat.id)
    if not user.exists():
        context.bot.send_message(
            chat_id=chat.id,
            text=f'Приятно познакомиться, {username}!.',
        )
        requests.post(
            'http://127.0.0.1:8000/api/users/',
            headers={'content-type': 'application/json'},
            json={
                'id_telegram': chat.id,
                'username': username,
            }
        )
        # ToDo: надо как-то по-другому запросить пароль у пользователя
        # или лучше автоматически его придумать и написать в чат
        user = Profile.objects.get(id_telegram=chat.id)
        user.set_password(os.getenv('USER_PASSWORD'))
        user.save()


def forward(update, context):
    chat = update.effective_chat

    if update.message.forward_from.is_bot:
        text = TELEGRAM_TEXT['ID_BOT']
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user = Profile.objects.filter(id_telegram=update.message.forward_from.id)
    if not user.exists():
        text = TELEGRAM_TEXT['ID_NOT'].format(
            update.message.forward_from.first_name,
        )
    else:
        user = Profile.objects.get(id_telegram=update.message.forward_from.id)
        text = 'Попробуйте что-нибудь подобрать'
        response = requests.get(
            url=(
                'http://127.0.0.1:8000/api/users/'
                f'{user.id_telegram}/holidays/'
            ),
            headers={
                'Authorization': 'Token {}'.format(os.getenv('SUPERBOT_TOKEN'))
            },
        ).json()
        if len(response) == 0:
            text = 'Пользователь пока не сохранил свои праздники'
        else:
            context.bot.send_message(
                chat_id=chat.id,
                text=holiday_card(response, user.username),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    context.bot.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


def start_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TELEGRAM_TEXT['START'],
    )


def help_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TELEGRAM_TEXT['HELP'].format(update.effective_chat.first_name),
    )


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TELEGRAM_TEXT['END_DAY'],
    )
    return ConversationHandler.END


def day_start(update, _):
    update.message.reply_text(
        'Итак, приступим. Как желаете назвать праздник?',
    )
    return STEP1


def step1(update, context):
    context.user_data['name'] = update.message.text
    logger.info(
        "Праздник пользователя id={0}: {1}".format(
            update.effective_chat.id, update.message.text
        )
    )
    update.message.reply_text(
        "Укажите ближайшую дату этого праздника: ",
        reply_markup=telegramcalendar.create_calendar()
    )
    return STEP2


def step2(update, context):
    logger.info(
        'Дата празднования: {0}'.format(
            context.user_data['date'],
        )
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            'Итак, мы сохранили такой праздник: \n\n'
            'Название праздника: {0}\n'
            'Ближайшая дата празднования: {1}'
        ).format(
            context.user_data['name'], context.user_data['date']
        ),
    )
    # update.message.reply_text(
    #     reply_markup=ReplyKeyboardMarkup(
    #         [['Всё верно', 'Нет, исправлю']], one_time_keyboard=True
    #     )
    # )

    context.user_data['user'] = Profile.objects.get(
        id_telegram=update.effective_chat.id,
    )

    Holiday.objects.create(
        user=context.user_data['user'],
        date=context.user_data['date'],
        name=context.user_data['name'],
    )
    return ConversationHandler.END


def inline_handler(update, context):
    selected, date = telegramcalendar.process_calendar_selection(
        context.bot, update
    )
    if selected:
        context.user_data['date'] = date.strftime("%Y-%m-%d")
        step2(update, context)


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=8,
            read_timeout=16,
            con_pool_size=8,
        )
        bot = Bot(
            request=request,
            token=os.getenv('TELEGTAM_TOKEN_BOT'),
        )
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('new_holiday', day_start)],
            states={
                STEP1: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, step1)],
                STEP2: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, step2)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        updater.dispatcher.add_handler(CommandHandler('start', start_bot))
        updater.dispatcher.add_handler(CommandHandler('help', help_bot))
        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(CallbackQueryHandler(inline_handler))
        updater.dispatcher.add_handler(
            MessageHandler(Filters.forwarded, forward)
        )
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling(1)
        updater.idle()


def holiday_card(response, user) -> str:
    return '\n'.join((
        '___________________________________________\n'
        '{4} Дата празднования: {0}\n'
        'Событие: {1}\n'
        'Пользователь {2} хочет принять в дар:\n'
        '{3}'
    ).format(
        dt.strptime(holiday['date'], '%Y-%m-%d').strftime('%d.%m.%Y'),
        holiday['name'],
        user,
        '{0}'.format(
            ' '.join(
                (
                    f'\n    {1+holiday["gifts"].index(gift)}) '
                    f'<a href="{gift["hyperlink"]}">{gift["short_name"]}</a>\n'
                    f'    Комментарий: {gift["comment"]}\n'
                ) for gift in holiday['gifts']
            )
        ),
        TELEGRAM_TEXT[1+response.index(holiday)],
    ) if holiday['gifts'] else (
        '___________________________________________\n'
        'На событие {0} (празднуемое {1}) '
        'пользователь {2} пока ничего не захотел.'
    ).format(
        holiday["name"],
        dt.strptime(holiday["date"], '%Y-%m-%d').strftime('%d.%m.%Y'),
        user,
    ) for holiday in response)
