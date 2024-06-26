# censore-hikka

# meta developer: @okineadev
# requires: censore

from hikkatl.types import Message, PeerUser
from .. import loader, utils
from censore import Censor


@loader.tds
class CensoreProfanity(loader.Module):
    """A module to remove profanity from your messages"""

    strings = {
        "name": "CensoreProfanity",
        "disabled": "<emoji document_id=5210952531676504517>❌</emoji> <b>Censorship is disabled</b>",
        "enabled": "<b>Censorship is enabled</b>",
    }

    strings_ru = {
        "name": "CensoreProfanity",
        "disabled": "<emoji document_id=5210952531676504517>❌</emoji> <b>Цензура выключена</b>",
        "enabled": "<b>Цензура включена</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enabled",
                True,
                "Determines whether censorship is enabled",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "censoring_char",
                "#",
                "Symbol for word censorship",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "partial_censorship",
                False,
                "Determine whether to partially censor obscene language",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self.name = self.strings["name"]

        self.censor = Censor(languages=["all"])
        self.censor_text = self.censor.censor_text

        self.config["enabled"] = True

    @loader.command(ru_doc="Включить цензуру")
    async def censon(self, message: Message):
        """Enable censorship"""
        self.config["enabled"] = True
        await message.edit(
            (
                "<emoji document_id=5206607081334906820>✔️</emoji>"
                if message.sender.premium
                or (
                    # In saved messages
                    isinstance(message.peer_id, PeerUser)
                    and message.from_id == message.to_id.user_id
                )
                else "✅"
            )
            + " "
            + self.strings("enabled")
        )

    @loader.command(ru_doc="Выключить цензуру")
    async def censoff(self, message: Message):
        """Disable censorship"""
        self.config["enabled"] = False
        await message.edit(self.strings("disabled"))

    @loader.watcher(only_messages=True, out=True, no_commands=True)
    async def watch_outgoing(self, message: Message):
        """Watch and edit outgoing text messages"""

        is_enabled = self.config.get("enabled", True)

        if is_enabled:
            censored_text = self.censor_text(
                message.raw_text,
                censoring_char=self.config["censoring_char"],
                partial_censor=self.config["partial_censorship"],
            )

            if message.raw_text != censored_text:
                await message.edit(censored_text)
