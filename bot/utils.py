from telegram import Update
from telegram.ext import ContextTypes



def permission(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user.to_dict()
        usernames = ['ruslan_tilyaev', 'ibrgyz']
        if user.get('username') and user.get('username') in usernames:
            return await func(update, context)
    return wrapped
