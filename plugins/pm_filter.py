# iFilmsBotz

import asyncio
import re
import ast
import math

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, SUPPORT, UPDATES, MYSUP, URL_SHORTENR_WEBSITE, URL_SHORTNER_WEBSITE_API
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)
    
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pv_filter(client,message):
    await auto_filter(client, message)
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖲ᴇᴀʀᴄʜ 𝖸ᴏᴜʀ 𝖮ᴡɴ 𝖥ɪʟᴇ, 𝖣ᴏɴ'ᴛ 𝖢ʟɪᴄᴋ 𝖮ᴛʜᴇʀ𝗌 𝖱ᴇ𝗌ᴜʟᴛ𝗌 😬", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖸ᴏᴜ Aʀᴇ U𝗌ɪɴɢ Oɴᴇ Oғ Mʏ Oʟᴅ Mᴇ𝗌𝗌ᴀɢᴇ𝗌, Sᴇɴᴅ Tʜᴇ Rᴇǫᴜᴇ𝗌ᴛ Aɢᴀɪɴ ⚠️", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📂 [{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("🗑", callback_data="delit"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖸ᴏᴜ Aʀᴇ U𝗌ɪɴɢ Oɴᴇ Oғ Mʏ Oʟᴅ Mᴇ𝗌𝗌ᴀɢᴇ𝗌, Sᴇɴᴅ Tʜᴇ Rᴇǫᴜᴇ𝗌ᴛ Aɢᴀɪɴ ⚠️", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(f"⚠️ Hey, {query.from_user.first_name}! You Are Clicking On An Old Button Which Is Expired ⚠️", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(f'⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖳ʜɪ𝗌 𝖬ᴏᴠɪᴇ/𝖲ᴇʀɪᴇ𝗌 𝖭ᴏᴛ Aᴅᴅᴇᴅ Iɴ @iFilms_Studios Dᴀᴛᴀʙᴀ𝗌ᴇ ⚠️')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer(f"🤒 Hey, {query.from_user.first_name}! You Need To Be Group Owner Or An Auth User To Do That! 🤒", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(f"⚠️ Hey, {query.from_user.first_name}! That's Not For You!! ⚠️", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode="md")
        return
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        buttons = [
            [
                InlineKeyboardButton('ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ]
            ]

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"Hey, {query.from_user.first_name}! I Like Your Smartness, But Don't Be Oversmart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(f'Hello, {query.from_user.first_name}! No Such File Exist. Send Request Again')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        buttons = [
            [
                InlineKeyboardButton('ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ]
            ]
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
            ],[
            InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ?', url=f'http://t.me/iFilms_Studios/352')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help":
        buttons =  [[
            InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ?', url=f'http://t.me/iFilms_Studios/352')
            ],[
            InlineKeyboardButton('ᴏᴡɴᴇʀ', callback_data='ownr'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ', callback_data='adm'),
            InlineKeyboardButton('ᴜsᴇʀs', callback_data='usr')
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('sᴛᴀᴛᴜs', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
           
    elif query.data == "ownr":
        buttons= [[
            InlineKeyboardButton('ᴍᴀɪɴ', callback_data='admin'),
            InlineKeyboardButton('ʟɪɴᴋ', callback_data='genlink'),
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛ', callback_data='coct')
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ʜᴇʟᴘ', url=f'https://t.me/{SUPPORT}'),
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇꜱ', url=f'https://t.me/{UPDATES}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.OWNR_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "adm":
        buttons= [[
            InlineKeyboardButton('ғɪʟᴛᴇʀs', callback_data='manuelfilter'),
            InlineKeyboardButton('ᴘᴀsᴛᴇ', callback_data='paste'),
            InlineKeyboardButton('zᴏᴍʙɪᴇs', callback_data='zombies')
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ʜᴇʟᴘ', url=f'https://t.me/{SUPPORT}'),
            InlineKeyboardButton('ɪɴғᴏ', callback_data='usersinfo')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADM_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "usr":
        buttons= [[
            InlineKeyboardButton('sᴇᴀʀᴄʜ', callback_data='extra'),
            InlineKeyboardButton('ʏᴏᴜᴛᴜʙᴇ', callback_data='music'),
            InlineKeyboardButton('ᴛ-ɢʀʜ', callback_data='tgraph')
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('sᴘᴇᴇᴄʜ', callback_data='tts'),
            InlineKeyboardButton('ɢᴀᴍᴇs', callback_data='games')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USR_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons= [[
            InlineKeyboardButton('ʀᴇᴘᴏʀᴛ ʙᴜɢꜱ & ꜰᴇᴇᴅʙᴀᴄᴋ', url=f'https://t.me/{SUPPORT}')
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇꜱ', url=f'https://t.me/{UPDATES}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='ownr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='ownr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "genlink":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='ownr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GENLINK_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='adm'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='usr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "usersinfo":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='adm'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USERSINFO_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "games":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='usr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GAMES_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "paste":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='adm'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.PASTE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tgraph":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='usr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TGRAPH_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "zombies":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='adm'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ZOMBIES_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('ɢᴇᴛ ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs', url='https://cloud.google.com/translate/docs/languages'),
            ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='usr'),
            InlineKeyboardButton('ᴄʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.TTS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "music":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='usr'),
            InlineKeyboardButton('cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MUSIC_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⧖', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching iFilms DataBase")
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⧖', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
      )
    elif query.data == "delit":
        chat_type = query.message.chat.type
        if chat_type == 'private':
            await query.message.delete()
            await query.answer('Deleted!😎')
        elif query.from_user.id == query.message.reply_to_message.from_user.id:
            msg = query.message.reply_to_message
            await msg.delete()
            await query.message.delete()
            await query.answer('Deleted!😎')
        else:
            await query.answer('Not yours!', show_alert = True)
            
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"] and msg.chat.id not in filters.chat(chats=MYSUP):
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📂 [{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    elif msg.chat.id in filters.chat(chats=MYSUP): return await message.reply_text(f'Dear, {message.from_user.mention}\n{total_results} results are already available for your requested {search} in (@iFilms_Movie_Bot).</a>', disable_web_page_preview=True)
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", 
                    url=await get_shortlink(f"https://t.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton("🗑", callback_data="delit"),
             InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )

    btn.insert(0, [
        InlineKeyboardButton('ʜᴏᴡ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ ᴏʀ ɢᴇᴛ ꜰɪʟᴇꜱ?', url=f'http://t.me/iFilms_Studios/352')
    ])
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ꜱᴇᴀʀᴄʜ ʀᴇꜱᴜʟᴛ ꜰᴏʀ ʏᴏᴜʀ 🇶ᴜᴇʀʏ ☟</b>\n\n<code>[彡 ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀꜰᴛᴇʀ 15 ᴍɪɴ 彡]</code>"  
    if imdb and imdb.get('poster'):
        try:
            fmsg = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            fmsg = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            fmsg = await message.reply_text(cap, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))
    else:
        fund = await msg.reply_photo(photo="https://graph.org/file/1571cf70ff4f00c71c45f.jpg", caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(900)
        await fund.delete()
        await msg.delete()
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        if msg.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP] or msg.chat.id in filters.chat(chats=MYGRP):
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f'https://www.google.com/search?q={msg.text.replace(" ", "+")}'),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f'https://www.imdb.com/find?q={msg.text.replace(" ", "+")}')
           ],
           [
             InlineKeyboardButton("ʜᴇʟᴘ!", url=f"https://t.me/{SUPPORT}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if movielist:
        if msg.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f'https://www.google.com/search?q={msg.text.replace(" ", "+")}'),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f'https://www.imdb.com/find?q={msg.text.replace(" ", "+")}')
           ],
           [
             InlineKeyboardButton("ʜᴇʟᴘ!", url=f"https://t.me/{SUPPORT}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return

    if not movielist:
        if msg.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP] or msg.chat.id in filters.chat(chats=MYGRP):
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f'https://www.google.com/search?q={msg.text.replace(" ", "+")}'),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f'https://www.imdb.com/find?q={msg.text.replace(" ", "+")}')
           ],
           [
             InlineKeyboardButton("ʜᴇʟᴘ!", url=f"https://t.me/{SUPPORT}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
