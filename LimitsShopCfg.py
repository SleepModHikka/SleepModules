
#meta developer: @sleep_modules
from .. import loader, utils
from asyncio import sleep
from telethon.tl.functions.messages import GetHistoryRequest
import re
import logging
from ..inline.types import InlineCall

@loader.tds
class LimitsShopCfg(loader.Module):
    """Настройки магазина лимитов"""
    strings_en = {
        'name': 'LimitsShopCfg',
        'main_text': '<emoji document_id=5870478797593120516>💵</emoji> <b>Config to Limits Shop</b>',
        'status': '<emoji document_id=5870982283724328568>⚙</emoji> <b>Status:</b>',
        'limits_status_yes': '<emoji document_id=5870633910337015697>✅</emoji> <b>Send limits</b>',
        'limits_status_no': '<emoji document_id=5870657884844462243>❌</emoji> <b>Don\'t send limits</b>',
        'queue': '<emoji document_id=5870772616305839506>👥</emoji> <b>Queue, format: nickname -> quantity limits</b>',
        'lvl_limit': '<emoji document_id=5870730156259152122>😀</emoji> <b>Level limit:</b>',
        'my_nick': '<emoji document_id=5870994129244131212>👤</emoji> <b>My nickname:</b>',
        'status_changed': '<b>Status changed to:</b> <code>{}</code>',
        'queue_added': '<b>Queue added:</b> <code>{}</code>',
        'queue_message': '<b>Current Queue:</b>\n<code>{}</code>',
        'no_queue': '<b>No queue</b>',
        'level_limit_set': '<b>Level limit set to:</b> <code>{}</code>',
        'nickname_set': '<b>Nickname set to:</b> <code>{}</code>',
        'status_button_yes': '✅ Send Limits',
        'status_button_no': '❌ Don\'t Send Limits',
        'level_limit_button': '😀 Set Level Limit',
        'nickname_button': '👤 Set Nickname',
        'queue_button': '👥 Manage Queue',
        'close_button': '🔻 Close',
        'invalid_usage': '<b>Invalid usage. See <code>.help setin</code></b>',
        'level_limit_invalid': '<b>Invalid level format</b>',
        'nickname_invalid': '<b>Nickname must be a single word</b>',
        'queue_add_invalid': '<b>Usage: <code>setin addque {nick} {limit}</code></b>',
        'queue_del_invalid': '<b>Usage: <code>setin delque {nick}</code></b>',
        'queue_deleted': '<b>User deleted from queue</b>',
        'status_changed_msg': '<b>Limits sending status changed</b>'
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
        'nickname_set': '<b>Никнейм установлен на:</b> <code>{}</code>',
        'status_button_yes': '✅ Отправлять лимиты',
        'status_button_no': '❌ Не отправлять лимиты',
        'level_limit_button': '😀 Установить лимит уровня',
        'nickname_button': '👤 Установить никнейм',
        'queue_button': '👥 Управление очередью',
        'close_button': '🔻 Закрыть',
        'invalid_usage': '<b>Неверное использование. Смотрите <code>.help setin</code></b>',
        'level_limit_invalid': '<b>Неверный формат уровня</b>',
        'nickname_invalid': '<b>Никнейм должен быть одним словом</b>',
        'queue_add_invalid': '<b>Использование: <code>setin addque {ник} {лимит}</code></b>',
        'queue_del_invalid': '<b>Использование: <code>setin delque {ник}</code></b>',
        'queue_deleted': '<b>Пользователь удален из очереди</b>',
        'status_changed_msg': '<b>Статус отправки лимитов изменен</b>'
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

    @loader.command(ru_doc="[lvl|nick|addque|delque|status] [значение] - Настройка параметров")
    async def setin(self, message):
        """[lvl|nick|addque|delque|status] [value] - Configure settings"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit(self.strings['invalid_usage'])
            return

        parts = args.split()
        action = parts[0].lower()

        if action == "lvl":
            if len(parts) != 2:
                await message.edit(self.strings['invalid_usage'])
                return
            try:
                level_limit = int(parts[1])
                self.set('level_limit', level_limit)
                await message.edit(self.strings['level_limit_set'].format(level_limit))
            except ValueError:
                await message.edit(self.strings['level_limit_invalid'])
        elif action == "nick":
            if len(parts) != 2:
                await message.edit(self.strings['invalid_usage'])
                return

            nickname = parts[1]
            if len(nickname.split()) > 1:
                await message.edit(self.strings['nickname_invalid'])
                return

            self.set('nickname', nickname)
            await message.edit(self.strings['nickname_set'].format(nickname))
        elif action == "addque":
            if len(parts) != 3:
                await message.edit(self.strings['queue_add_invalid'])
                return

            text = parts[1]
            numbers = parts[2]
            new_queue_item = f"{text} {numbers}"

            queue = self.get('queue', [])
            queue.append(new_queue_item)
            self.set('queue', queue)

            await message.edit(self.strings['queue_added'].format(new_queue_item))

        elif action == "delque":
            if len(parts) != 2:
                await message.edit(self.strings['queue_del_invalid'])
                return

            text_to_remove = parts[1]
            queue = self.get('queue', [])
            new_queue = [item for item in queue if text_to_remove not in item]
            self.set('queue', new_queue)

            await message.edit(self.strings['queue_deleted'])
        
        elif action == "status":
            current_status = self.get('current_status')
            new_status = "limits_status_no" if current_status == "limits_status_yes" else "limits_status_yes"
            self.set('current_status', new_status)
            await message.edit(self.strings['status_changed_msg'])

        else:
            await message.edit(self.strings['invalid_usage'])

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

    @loader.command()
    async def ilcfg(self, message):
        """- открыть меню настроек через инлайн-кнопки"""
        current_status = self.get('current_status')
        status_text = self.strings[current_status]

        queue = self.get('queue', [])
        queue_text = "\n".join(queue) if queue else self.strings['no_queue']
        level_limit = self.get('level_limit')
        nickname = self.get('nickname')
        
        text = f"{self.strings['main_text']}\n\n{self.strings['status']} {status_text}\n\n{self.strings['queue']}\n{queue_text}\n\n{self.strings['lvl_limit']} {level_limit}\n\n{self.strings['my_nick']} {nickname}"

        await self.inline.form(
            text=text,
            message=message,
            reply_markup=[
                [
                    {
                        'text': self.strings['status_button_yes'] if self.get('current_status') == 'limits_status_no' else self.strings['status_button_no'],
                        'callback': self.set_status_callback
                    },
                ],
                [
                    {
                        'text': self.strings['level_limit_button'],
                        'callback': self.set_level_limit_callback
                    },
                ],
                [
                    {
                        'text': self.strings['nickname_button'],
                        'callback': self.set_nickname_callback
                    },
                ],
                [
                    {
                        'text': self.strings['queue_button'],
                        'callback': self.manage_queue_callback
                    },
                ],
                [
                    {
                        'text': self.strings['close_button'],
                        'action': 'close'
                    },
                ]
            ]
        )

    async def set_status_callback(self, call: InlineCall):
        """- обработчик нажатия на кнопку изменения статуса"""
        current_status = self.get('current_status')
        new_status = "limits_status_no" if current_status == "limits_status_yes" else "limits_status_yes"
        self.set('current_status', new_status)

        current_status = self.get('current_status')
        status_text = self.strings[current_status]

        queue = self.get('queue', [])
        queue_text = "\n".join(queue) if queue else self.strings['no_queue']
        level_limit = self.get('level_limit')
        nickname = self.get('nickname')
        
        text = f"{self.strings['main_text']}\n\n{self.strings['status']} {status_text}\n\n{self.strings['queue']}\n{queue_text}\n\n{self.strings['lvl_limit']} {level_limit}\n\n{self.strings['my_nick']} {nickname}"

        await call.edit(
            text=text,
            reply_markup=[
                [
                    {
                        'text': self.strings['status_button_yes'] if self.get('current_status') == 'limits_status_no' else self.strings['status_button_no'],
                        'callback': self.set_status_callback
                    },
                ],
                [
                    {
                        'text': self.strings['level_limit_button'],
                        'callback': self.set_level_limit_callback
                    },
                ],
                [
                    {
                        'text': self.strings['nickname_button'],
                        'callback': self.set_nickname_callback
                    },
                ],
                [
                    {
                        'text': self.strings['queue_button'],
                        'callback': self.manage_queue_callback
                    },
                ],
                [
                    {
                        'text': self.strings['close_button'],
                        'action': 'close'
                    },
                ]
            ]
        )
        await call.answer(self.strings['status_changed_msg'])

    async def set_level_limit_callback(self, call: InlineCall):
        """- обработчик нажатия на кнопку изменения лимита уровня"""
        await call.answer("Используйте команду .setin lvl {уровень}", show_alert=True)

    async def set_nickname_callback(self, call: InlineCall):
        """- обработчик нажатия на кнопку изменения никнейма"""
        await call.answer("Используйте команду .setin nick {никнейм}", show_alert=True)

    async def manage_queue_callback(self, call: InlineCall):
        """- обработчик нажатия на кнопку управления очередью"""
        await call.answer("Используйте команды\n .setin addque {ник} {кол-во лимитов} - добавить в очередь\n .setin delque {ник} - удалить из очереди", show_alert=True)
