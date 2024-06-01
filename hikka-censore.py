from hikkatl.types import Message
from .. import loader, utils
# requires: censore
from censore import Censor

@loader.tds
class CensoreProfanity(loader.Module):
    """A module to remove profanity from your messages"""

    strings = {"name": "CensoreProfanity"}

    async def client_ready(self, client, db):
        self.db = db
        self.me_id = (await client.get_me()).id

        self.censor = Censor(languages=["all"])
        self.censor_text = self.censor.censor_text

    async def censcmd(self, message):
        """.cens <reply>|<text>
        Проверка фильтра обсценной лексики"""
        
        args = utils.get_args_raw(message)
        
        if not message.is_reply and not args:
            return await message.edit("???")
            
        if message.is_reply:
            reply = await message.get_reply_message()
            raw_text = reply.raw_text
            
        else:
            raw_text = args

        censored_text = self.censor_text(raw_text)
        
        if raw_text != censored_text:
            await message.edit(censored_text)
        else:
            await message.edit(censored_text if not message.is_reply else "no")

    async def censlistcmd(self, message):
        """Выводит список айди чатов, в которых работает фильтрация"""
        ids = dict(self.db).get(self.name)
        
        if not ids:
            return await message.edit("empty")
        censlist = [
            f'<code>{x}</code>{"*" if ids[x]==2 else ""}'
            for x in ids
            if isinstance(x, int) and ids[x] > 0
        ]
        
        if not censlist:
            return await message.edit("empty")
            
        answer = " ".join(censlist)
        await message.edit(answer)

    async def censoncmd(self, message):
        """.censon [<id>|<username>|*]
        Запуск фильтрации в том чате, куда отправлена команда
        Можно запустить в любом чате по id или username
        * запускает на все сообщения в текущем чате (по умолчанию на свои)"""
        
        args = utils.get_args_raw(message)
        if args == "*":
            chat = message.chat
            if (
                not isinstance(chat, Channel)
                or not chat.admin_rights
                or not chat.admin_rights.delete_messages
            ):
                return await message.edit("<b>Не могу удалять чужие посты в этом чате</b>")
            flag = 1
            args = args[:-1]
            
        else:
            flag = 1
        if not args:
            id = utils.get_chat_id(message)
        elif args.isnumeric():
            id = int(args)
            
        else:
            try:
                id = (await self.client.get_entity(args)).id
            except Exception:
                return await message.edit("invalid")
                
        self.db.set(self.name, id, flag)
        await message.edit("Включено")

    async def censoffcmd(self, message):
        """.censoff [<id>|<username>|all]
        Остановка фильтрации в том чате, куда отправлена команда
        Можно остановить в любом чате по id или username
        all останавливает фильтрацию во всех чатах"""
        
        args = utils.get_args_raw(message)
        if args == "all":
            del self.db[self.name]
            return await message.edit("off")
            
        if not args:
            id = utils.get_chat_id(message)
            
        elif args.isnumeric():
            id = int(args)
            
        else:
            try:
                id = (await self.client.get_entity(args)).id
            except Exception:
                return await message.edit("invalid")
                
        self.db.set(self.name, id, 0)
        await message.edit("off")

    @loader.watcher(no_commands=True, out=True, only_messages=True, editable=True)
    async def watch_outgoing(self, message: Message):
        """Watch and edit outgoing text messages"""
        
        id = utils.get_chat_id(event)
        flag = self.db.get(self.name, id, 0)
        
        if not flag or (flag == 1 and event.sender_id != self.me_id):
            return

        await message.edit(self.censor_text(message.raw_text))
