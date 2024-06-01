from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class CensoreProfanity(loader.Module):
    """A module to remove profanity from your messages"""

    strings = {"name": "CensoreProfanity"}

    async def client_ready(self, client, db):
        try:
            from censore import Censor

        except ImportError:
            await self._hikka.install_pip_package("censore")
            from censore import Censor

        self.censor = Censor(languages=["all"])
        self.censor_text = self.censor.censor_text

    @loader.watcher(no_commands=True, out=True, only_messages=True, editable=True)
    async def watch_outgoing(self, message: Message):
        """Watch and edit outgoing text messages"""
        await message.edit(self.censor_text(message.raw_text))
