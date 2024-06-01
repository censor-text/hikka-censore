from hikkatl.types import Message
from censore import Censor

from .. import loader, utils

censor = Censor(languages=["all"])

@loader.tds
class CensoreProfanity(loader.Module):
    """A module to remove profanity from your messages"""

    strings = {"name": "CensoreProfanity"}

    @loader.watcher()
    async def watch_outgoing(self, message: Message):
        """Watch and edit outgoing text messages"""
        await message.edit(censor.censor_text(message.raw_text))
