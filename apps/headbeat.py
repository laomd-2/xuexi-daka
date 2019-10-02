import wxpy
from core import bot


@bot.register(bot.file_helper, wxpy.TEXT, except_self=False)
def alive_reply(msg):
    return 'alive'
