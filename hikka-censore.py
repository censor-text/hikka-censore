from hikkatl.types import Message
from .. import loader, utils
# requires: censore
from censore import Censor

@loader.tds
class CensoreProfanity(loader.Module):
    """A module to remove profanity from your messages"""

    strings = {
        "name": "CensoreProfanity",
        "disabled": "❌ <b>Censorship is disabled</b>",
        "enabled": "✅ <b>Censorship is enabled</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.name = self.strings["name"]

        self.censor = Censor(languages=["all"])
        self.censor_text = self.censor.censor_text

        self.db.set(self.name, "enabled", True)

    async def censoncmd(self, message: Message):
        """Enable censorship"""
        self.db.set(self.name, "enabled", True)
        await message.edit(self.strings["enabled"])

    async def censoffcmd(self, message: Message):
        """Disable censorship"""
        self.db.set(self.name, "enabled", False)
        await message.edit(self.strings["enabled"])


    @loader.watcher()
    async def watch_outgoing(self, message: Message):
        """Watch and edit outgoing text messages"""

        is_enabled = self.db.get(self.name, "enabled", True)

        if is_enabled:
            await message.edit(self.censor_text(message.raw_text))
