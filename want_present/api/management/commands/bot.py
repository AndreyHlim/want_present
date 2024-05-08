from django.core.management.base import BaseCommand
from telegram.utils.request import Request
from telegram import Bot, ParseMode
import os
import logging
from telegram.ext import (
    Updater, Filters, MessageHandler, CommandHandler, ConversationHandler
)
from users.models import Profile
from constants import TELEGRAM_TEXT


STEP1, STEP2, STEP3 = range(3)


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

    Profile.objects.get_or_create(
        id_telegram=chat.id,
        defaults={
            'username': chat.first_name,
        }
    )

    if update.message.forward_from:
        if update.message.forward_from.is_bot:
            text = TELEGRAM_TEXT['ID_BOT']
        else:
            user = Profile.objects.filter(
                id_telegram=update.message.forward_from.id,
            )
            if not user.exists():
                text = TELEGRAM_TEXT['ID_NOT'].format(
                    update.message.forward_from.first_name,
                )
            else:
                text = 'Надо прочитать список желаний пользователя'
    else:
        text = TELEGRAM_TEXT['UNKNOW']

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


# def day_bot(update, context):
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text='эм..  тут должен быть диалог с сохранением праздника',
#     )


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TELEGRAM_TEXT['END_DAY'],
    )
    return ConversationHandler.END


def day_start(update, _):
    # Список кнопок для ответа
    # reply_keyboard = [['Boy', 'Girl', 'Other']]
    # Создаем простую клавиатуру для ответа
    # markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    # Начинаем разговор с вопроса
    update.message.reply_text(
        'Итак, приступим. Как желаете назвать праздник?',
        # reply_markup=markup_key,
    )
    # переходим к этапу `STEP1`, это значит, что ответ
    # отправленного сообщения в виде кнопок будет список
    # обработчиков, определенных в виде значения ключа `STEP1`
    return STEP1


def step1(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал пол пользователя
    logger.info("Пол %s: %s", user.first_name, update.message.text)
    # Следующее сообщение с удалением клавиатуры `ReplyKeyboardRemove`
    update.message.reply_text(
        'Хорошо. Какого числа ждёте праздника?',
        # reply_markup=ReplyKeyboardRemove(),
    )
    # переходим к этапу `PHOTO`
    return STEP2


# Обрабатываем фотографию пользователя
def step2(update, _):
    # определяем пользователя
    user = update.message.from_user
    # захватываем фото
    # photo_file = update.message.photo[-1].get_file()
    # скачиваем фото
    # photo_file.download(f'{user.first_name}_photo.jpg')
    # Пишем в журнал сведения о фото
    logger.info("Фотография %s: %s", user.first_name,
                f'{user.first_name}_photo.jpg')
    # Отвечаем на сообщение с фото
    update.message.reply_text(
        'Великолепно! А какой месяц?'
    )
    # переходим к этапу `LOCATION`
    return STEP3


# Обрабатываем местоположение пользователя
def step3(update, _):
    # определяем пользователя
    user = update.message.from_user
    # захватываем местоположение пользователя
    # user_location = update.message.location
    # Пишем в журнал сведения о местоположении
    logger.info(
        "Местоположение %s.", user.first_name)
    # Отвечаем на сообщение с местоположением
    update.message.reply_text(
        'ну вроде сохранили?...'
    )
    # переходим к этапу `BIO`
    return ConversationHandler.END


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
            # base_url=os.getenv('PROXY_URL'),
        )
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('new_holiday', day_start)],
            states={
                # GENDER
                STEP1: [MessageHandler(Filters.text, step1),
                        CommandHandler('cancel', cancel)],
                # PHOTO
                STEP2: [MessageHandler(Filters.text, step2),
                        CommandHandler('cancel', cancel)],
                # LOCATION
                STEP3: [
                    MessageHandler(Filters.text, step3),
                    CommandHandler('cancel', cancel)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        updater.dispatcher.add_handler(CommandHandler('start', start_bot))
        updater.dispatcher.add_handler(CommandHandler('help', help_bot))
        updater.dispatcher.add_handler(conv_handler)
        # updater.dispatcher.add_handler(CommandHandler('new_holiday', day_bot)
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling(10)
        updater.idle()
