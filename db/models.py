from tortoise import fields
from tortoise.models import Model


class NamePhoto(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    list_photo = fields.JSONField(default=list)

    class Meta:
        table = 'namephoto'


class BotMessage(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(index=True)
    message_id = fields.IntField(index=True)
    delete_at = fields.DatetimeField(index=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'bot_messages'
        unique_together = (('chat_id', 'message_id'),)
