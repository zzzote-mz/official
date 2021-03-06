# Module to blacklist users and prevent them from using commands by @TheRealPhoenix
import html

from typing import List

from telegram import Bot, Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, OWNER_ID, DEV_USERS, SUDO_USERS, WHITELIST_USERS, SUPPORT_USERS
from tg_bot.modules.helper_funcs.chat_status import dev_plus
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text, extract_user
from tg_bot.modules.log_channel import gloggable
import tg_bot.modules.sql.blacklistusers_sql as sql

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + SUDO_USERS + WHITELIST_USERS + SUPPORT_USERS
BLABLEUSERS = [OWNER_ID] + DEV_USERS


@run_async
@dev_plus
@gloggable
def bl_user(bot: Bot, update: Update, args: List[str]) -> str:

    message = update.effective_message
    user = update.effective_user

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        message.reply_text("How am I supposed to do my work if I am ignoring myself?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        message.reply_text("No!\nNoticing Disasters is my job.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            raise

    sql.blacklist_user(user_id, reason)
    message.reply_text("I shall ignore the existence of this user!")
    log_message = "#BLACKLIST" \
                  "\n<b>Admin:</b> {}" \
                  "\n<b>User:</b> {}".format(mention_html(user.id, user.first_name),
                                            mention_html(target_user.id, target_user.first_name))
    if reason:
        log_message += "\n<b>Reason:</b> {}".format(reason)
    
    return log_message
    

@run_async
@dev_plus
@gloggable
def unbl_user(bot: Bot, update: Update, args: List[str]) -> str:

    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return ""

    if user_id == bot.id:
        message.reply_text("I always notice myself.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        else:
            raise

    if sql.is_user_blacklisted(user_id):

        sql.unblacklist_user(user_id)
        message.reply_text("*notices user*")
        log_message = "#UNBLACKLIST" \
                      "\n<b>Admin:</b> {}" \
                      "\n<b>User:</b> {}".format(mention_html(user.id, user.first_name),
                                                mention_html(target_user.id, target_user.first_name))

        return log_message

    else:
        message.reply_text("I am not ignoring them at all though!")
        return ""


@run_async
@dev_plus
def bl_users(bot: Bot, update: Update):

    reply = "<b>Blacklisted Users</b>\n"

    for each_user in sql.BLACKLIST_USERS:
        
        name = html.escape(bot.get_chat(each_user))
        reason = sql.get_reason(each_user)

        if reason:
            reply += f"??? <a href='tg://user?id={each_user}'>{name}</a> :- {reason}\n"
        else:
            reply += f"??? <a href='tg://user?id={each_user}'>{name}</a>\n"

    if reply == "<b>Blacklisted Users</b>\n":
        reply += "Noone is being ignored as of yet."

    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)
        
        
def __user_info__(user_id):

    is_blacklisted = sql.is_user_blacklisted(user_id)
    
    text = "Blacklisted: <b>{}</b>"

    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nReason: <code>{reason}</code>"
    else:
        text = text.format("No")
    
    return text

    
BL_HANDLER = CommandHandler("ignore", bl_user, pass_args=True)
UNBL_HANDLER = CommandHandler("notice", unbl_user, pass_args=True)
BLUSERS_HANDLER = CommandHandler("ignoredlist", bl_users)

dispatcher.add_handler(BL_HANDLER)
dispatcher.add_handler(UNBL_HANDLER)
dispatcher.add_handler(BLUSERS_HANDLER)

__mod_name__ = "Blacklisting Users"
__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]
