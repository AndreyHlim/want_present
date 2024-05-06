from django.core.management.base import BaseCommand
from telegram.utils.request import Request
from telegram import Bot
import os
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from users.models import Profile
from constants import TELEGRAM_TEXT


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
    context.bot.send_message(chat_id=chat.id, text='Привет, я Bot!')

    Profile.objects.get_or_create(
        id_telegram=chat.id,
        defaults={
            'username': chat.first_name,
        }
    )
    if update.message.forward_from:
        if update.message.forward_from.is_bot:
            text = TELEGRAM_TEXT['ID_IS_BOT']
        else:
            user = Profile.objects.filter(
                id_telegram=update.message.forward_from.id,
            )
            if not user.exists():
                text = TELEGRAM_TEXT['ID_NOT_FOUND'].format(
                    update.message.forward_from.first_name
                )
            else:
                text = 'Надо прочитать список желаний пользователя'

            context.bot.send_message(
                chat_id=chat.id, text=text,
            )


def wake_up(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id, text='Спасибо, что включили меня',
    )


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=os.getenv('TELEGTAM_TOKEN_BOT'),
            base_url=os.getenv('PROXY_URL')
        )
        print(bot.get_me())

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling()
        updater.idle()
