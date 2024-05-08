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
from dotenv import load_dotenv


load_dotenv()


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
    logger.info(
        "Праздник пользователя id={0}: {1}".format(
            update.effective_chat.id, update.message.text
        )
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Хорошо. Какого числа ждёте праздника?',
    )
    return STEP2


def step2(update, context):
    logger.info(
        "День празднования пользователя {0}: {1}".format(
            update.effective_chat.id,
            update.message.text
        )
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Великолепно! А какой месяц?',
    )
    return STEP3


def step3(update, context):
    logger.info(
        "Месяц празднования пользователя {0}: {1}".format(
            update.effective_chat.id,
            update.message.text
        )
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Сохранили праздник!',
    )
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
                STEP1: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, step1)],
                STEP2: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, step2)],
                STEP3: [CommandHandler('cancel', cancel),
                        MessageHandler(Filters.text, step3)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        updater.dispatcher.add_handler(CommandHandler('start', start_bot))
        updater.dispatcher.add_handler(CommandHandler('help', help_bot))
        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling(10)
        updater.idle()
