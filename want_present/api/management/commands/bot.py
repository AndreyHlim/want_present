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

    context.bot.send_message(
        chat_id=chat.id,
        text='я простой Bot. Такой команды я ещё не выучил.'
    )

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
                    update.message.forward_from.first_name
                )
            else:
                text = 'Надо прочитать список желаний пользователя'

            context.bot.send_message(
                chat_id=chat.id, text=text,
            )


def start_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо, что включили меня',
    )


def help_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=TELEGRAM_TEXT['HELP'].format(update.effective_chat.first_name),
    )


def day_bot(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='эм..',
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

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        updater.dispatcher.add_handler(CommandHandler('start', start_bot))
        updater.dispatcher.add_handler(CommandHandler('help', help_bot))
        updater.dispatcher.add_handler(CommandHandler('new_holiday', day_bot))
        # updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        updater.start_polling()
        updater.idle()
