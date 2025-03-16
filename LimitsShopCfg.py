#meta developer: @sleep_modules
from .. import loader, utils
from asyncio import sleep
from telethon.tl.functions.messages import GetHistoryRequest
import re
import logging

@loader.tds
class LimitsShopCfg(loader.Module):
    """Настройки магазина лимитов"""
    strings_en = {
        'name': 'LimitsShopCfg',
        'main_text': '<emoji document_id=5870478797593120516>💵</emoji> <b>Config to Limits Shop</b>',
        'status': '<emoji document_id=5870982283724328568>⚙</emoji> <b>Status:</b>',
        'limits_status_yes': '<emoji document_id=5870633910337015697>✅</emoji> <b>Send limits</b>',
        'limits_status_no': '<emoji document_id=5870657884844462243>❌</emoji> <b>No send limits</b>',
        'queue': '<emoji document_id=5870772616305839506>👥</emoji> <b>Queue, format: nickname -> quantity limits</b>',
        'lvl_limit': '<emoji document_id=5870730156259152122>😀</emoji> <b>Level limit:</b>',
        'my_nick': '<emoji document_id=5870994129244131212>👤</emoji> <b>My nickname:</b>',
        'status_changed': '<b>Status changed to:</b> <code>{}</code>',
        'queue_added': '<b>Queue added:</b> <code>{}</code>',
        'queue_message': '<b>Current Queue:</b>\n<code>{}</code>',
        'no_queue': '<b>No queue</b>',
        'level_limit_set': '<b>Level limit set to:</b> <code>{}</code>',
        'nickname_set': '<b>Nickname set to:</b> <code>{}</code>'
    }

    strings_ru = {
        'name': 'LimitsShopCfg',
        'main_text': '<emoji document_id=5870478797593120516>💵</emoji> <b>Настройки магазина лимитов</b>',
        'status': '<emoji document_id=5870982283724328568>⚙</emoji> <b>Статус:</b>',
        'limits_status_yes': '<emoji document_id=5870633910337015697>✅</emoji> <b>Отправляю лимиты</b>',
        'limits_status_no': '<emoji document_id=5870657884844462243>❌</emoji> <b>Не отправляю лимиты</b>',
        'queue': '<emoji document_id=5870772616305839506>👥</emoji> <b>Очередь, Формат: никнейм -> количество лимитов</b>',
        'lvl_limit': '<emoji document_id=5870730156259152122>😀</emoji> <b>Ограничение уровня:</b>',
        'my_nick': '<emoji document_id=5870994129244131212>👤</emoji> <b>Мой ник:</b>',
        'status_changed': '<b>Статус изменён на:</b> <code>{}</code>',
        'queue_added': '<b>Очередь добавлена:</b> <code>{}</code>',
        'queue_message': '<b>Текущая очередь:</b>\n<code>{}</code>',
        'no_queue': '<b>Нет очереди</b>',
        'level_limit_set': '<b>Уровень лимита установлен на:</b> <code>{}</code>',
        'nickname_set': '<b>Никнейм установлен на:</b> <code>{}</code>'
    }

    async def client_ready(self, client, db):
        if self.get('current_status') is None:
            self.set('current_status', 'limits_status_yes')
            logging.info("LimitsShopCfg: Initialized current_status to limits_status_yes")
        if self.get('level_limit') is None:
            self.set('level_limit', 0)
            logging.info("LimitsShopCfg: Initialized level_limit to 0")
        if self.get('nickname') is None:
            self.set('nickname', 'NoNick')
            logging.info("LimitsShopCfg: Initialized nickname to NoNick")

        if self.get('queue') is None:
            self.set('queue', [])
            logging.info("LimitsShopCfg: Initialized queue to []")

    @loader.command()
    async def aque(self, message):
        """{ник} {кол-во лимитов} - добавить в очередь"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Использование: <code>.aque {ник} {кол-во лимитов}</code></b>")
            return

        parts = args.split()
        if len(parts) < 2:
            await message.edit("<b>Неправильный формат, используй:</b> <code>.aque {ник} {кол-во лимитов}</code>")
            return

        text = parts[0]
        numbers = parts[1]
        new_queue_item = f"{text} {numbers}"

        queue = self.get('queue', [])
        queue.append(new_queue_item)
        self.set('queue', queue)

        await message.edit(self.strings['queue_added'].format(new_queue_item))

    @loader.command()
    async def dque(self, message):
        """{ник} - удалить из очереди"""
        text_to_remove = utils.get_args_raw(message)
        if not text_to_remove:
            await message.edit("<b>Использование:</b> <code>.dque {ник}</code>")
            return

        queue = self.get('queue', [])
        new_queue = [item for item in queue if text_to_remove not in item]
        self.set('queue', new_queue)

        await message.edit("<b>Пользователь удален из очереди</b>")

    @loader.command()
    async def setstat(self, message):
        """- изменить статус отправки лимитов"""
        current_status = self.get('current_status')
        new_status = "limits_status_no" if current_status == "limits_status_yes" else "limits_status_yes"
        self.set('current_status', new_status)
        await message.edit(self.strings['status_changed'].format(self.strings[new_status]))

    @loader.command()
    async def setll(self, message):
        """{уровень} - установить лимит уровня"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Использование:</b> <code>.setll {уровень}</code>")
            return
        
        try:
            level_limit = int(args)
            self.set('level_limit', level_limit)
            await message.edit(self.strings['level_limit_set'].format(level_limit))
        except ValueError:
            await message.edit("<b>Неправильный формат уровня</b>")

    @loader.command()
    async def setnick(self, message):
        """{ник} - установить свой никнейм"""
        nickname = utils.get_args_raw(message)
        if not nickname:
            await message.edit("<b>Использование:</b> <code>.setnick {никнейм}</code>")
            return

        if len(nickname.split()) > 1:
            await message.edit("<b>Никнейм должен быть одним словом</b>")
            return

        self.set('nickname', nickname)
        await message.edit(self.strings['nickname_set'].format(nickname))

    @loader.command()
    async def lcfg(self, message):
        """- показать текущие настройки магазина лимитов"""
        current_status = self.get('current_status')
        status_text = self.strings[current_status]

        queue = self.get('queue', [])
        queue_text = "\n".join(queue) if queue else self.strings['no_queue']
        level_limit = self.get('level_limit')
        nickname = self.get('nickname')

        await message.edit(
            f"{self.strings['main_text']}\n\n{self.strings['status']} {status_text}\n\n{self.strings['queue']}\n{queue_text}\n\n{self.strings['lvl_limit']} {level_limit}\n\n{self.strings['my_nick']} {nickname}"
        )
