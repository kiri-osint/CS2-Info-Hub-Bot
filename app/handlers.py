# app/handlers.py
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest 
from datetime import datetime 

# --- Наши импорты ---
from . import keyboards as kb
from . import data_manager as dm
from . import steam_api               
from . import keyboard_builders       
from . import valve_stats_api         
from . import official_steam_api  
from . import inventory_api       

router = Router()

class SkinSearch(StatesGroup):
    waiting_for_name = State() 
    showing_results = State() 

class ProfileSearch(StatesGroup):
    waiting_for_steamid = State()

class InventorySearch(StatesGroup):
    waiting_for_steamid = State()
    showing_inventory = State() 

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("👋 Welcome! Here you can find CS2 item prices.", reply_markup=kb.main)

@router.message(Command('profile_steam'))
async def command_profile_steam_handler(message: Message) -> None:
    await message.answer("Steam Profile Link", reply_markup=kb.steam)

@router.message(F.text == "Server Stats")
async def server_stats_handler(message: Message):
    loading_msg = await message.answer("<i>Fetching server stats...</i>", parse_mode="HTML")
    
    stats = await valve_stats_api.get_online_stats()
    
    if stats:
        text = (
            "<b>Steam Server Stats</b>\n\n"
            f"🟢 <b>Players Online:</b> {stats['online']}\n"
            f"🎮 <b>Players In-Game:</b> {stats['in_game']}"
        )
        await loading_msg.edit_text(text, parse_mode="HTML")
    else:
        await loading_msg.edit_text("⚠️ Could not retrieve stats. The Valve stats page might be down or its layout changed.", parse_mode="HTML")


@router.message(F.text == "Steam Profile Search")
async def profile_search_start(message: Message, state: FSMContext):
    await state.set_state(ProfileSearch.waiting_for_steamid)
    await message.answer(
        "Please enter the user's **SteamID64**.\n\n"
        "*You can find it on sites like `steamid.io` by user's profile link.*",
        parse_mode="Markdown",
        reply_markup=None 
    )

@router.message(ProfileSearch.waiting_for_steamid)
async def process_profile_search(message: Message, state: FSMContext):
    await state.clear()
    steam_id = message.text.strip()
    
    if not (steam_id.isdigit() and len(steam_id) == 17):
        await message.answer("That doesn't look like a valid SteamID64. It must be 17 digits long.", reply_markup=kb.main)
        return

    loading_msg = await message.answer(f"<i>Searching for profile {steam_id}...</i>", parse_mode="HTML")
    
    summary = await official_steam_api.get_player_summary(steam_id)
    
    if not summary:
        await loading_msg.edit_text(
            "⚠️ Could not find this profile. It might be private or the SteamID is incorrect.",
            reply_markup=None 
        )
        await message.answer("Main Menu:", reply_markup=kb.main)
        return

    status_map = {
        0: "🔴 Offline", 1: "🟢 Online", 2: "🟡 Busy",
        3: "🟡 Away", 4: "🟡 Snooze", 5: "🔵 Looking to trade",
        6: "🔵 Looking to play"
    }
    status = status_map.get(summary.get("personastate", 0), "❓ Unknown")
    
    if summary.get("communityvisibilitystate", 1) != 3:
        status = "🔒 Private Profile"

    game_name = summary.get("gameextrainfo")
    if game_name:
        status = f"🎮 Playing: {game_name}"
        
    real_name = summary.get('realname')
    real_name_str = f"👤 <b>Real Name:</b> {real_name}\n" if real_name else ""
    
    join_date_str = ""
    time_created = summary.get('timecreated')
    if time_created:
        join_date = datetime.fromtimestamp(time_created).strftime("%b %d, %Y")
        join_date_str = f"📅 <b>Joined Steam:</b> {join_date}\n"

    text = (
        f"<b>{summary.get('personaname', 'Unknown Name')}</b>\n"
        f"{status}\n\n"
        f"{real_name_str}"
        f"{join_date_str}"
        f"🔗 <b>Profile URL:</b> {summary.get('profileurl', 'N/A')}\n"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Close", callback_data="close_profile_hub"))
    
    try:
        await loading_msg.delete() 
        await message.answer_photo(
            photo=summary.get('avatarfull', ''), 
            caption=text,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Failed to send profile photo: {e}")
        await message.answer(text, parse_mode="HTML", reply_markup=builder.as_markup())
    
    await message.answer("Main Menu:", reply_markup=kb.main)

@router.callback_query(F.data == "close_profile_hub")
async def close_profile_hub_handler(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass 
    await callback.answer("Closed.")


@router.message(F.text == "View Inventory")
async def inventory_search_start(message: Message, state: FSMContext):
    await state.set_state(InventorySearch.waiting_for_steamid)
    await message.answer(
        "Please enter the user's **SteamID64** to view their inventory.",
        parse_mode="Markdown",
        reply_markup=None 
    )

@router.message(InventorySearch.waiting_for_steamid)
async def process_inventory_search(message: Message, state: FSMContext):
    steam_id = message.text.strip()
    
    if not (steam_id.isdigit() and len(steam_id) == 17):
        await state.clear()
        await message.answer("That doesn't look like a valid SteamID64. It must be 17 digits long.", reply_markup=kb.main)
        return

    loading_msg = await message.answer(f"<i>Fetching inventory for {steam_id}... (this may take a moment)</i>", parse_mode="HTML")
    
    inventory_or_error = await inventory_api.get_user_inventory(steam_id)
    
    if isinstance(inventory_or_error, str):
        await state.clear()
        await loading_msg.edit_text(f"⚠️ {inventory_or_error}", reply_markup=None)
        await message.answer("Main Menu:", reply_markup=kb.main)
        return

    await loading_msg.delete() 
    
    await state.set_state(InventorySearch.showing_inventory)
    await state.update_data(inventory=inventory_or_error, page=0, steam_id=steam_id)

    keyboard = keyboard_builders.create_inventory_keyboard(inventory_or_error, page=0)
    await message.answer(f"Inventory for {steam_id} ({len(inventory_or_error)} items):", reply_markup=keyboard)


@router.callback_query(InventorySearch.showing_inventory, F.data.startswith("inv_page:"))
async def inventory_page_handler(callback: CallbackQuery, state: FSMContext):
    new_page = int(callback.data.split(":")[1])
    data = await state.get_data()
    inventory = data.get("inventory")
    
    if not inventory:
        await callback.answer("Error: Inventory data lost. Please start over.", show_alert=True)
        return

    await state.update_data(page=new_page)
    keyboard = keyboard_builders.create_inventory_keyboard(inventory, page=new_page)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except TelegramBadRequest:
        pass 
    await callback.answer()

@router.callback_query(InventorySearch.showing_inventory, F.data.startswith("inv_idx:"))
async def inventory_item_price_handler(callback: CallbackQuery, state: FSMContext):
    item_index = int(callback.data.split(":")[1])
    data = await state.get_data()
    inventory = data.get("inventory")
    
    if not inventory or item_index >= len(inventory):
        await callback.answer("Error: Inventory data lost or item index out of bounds.", show_alert=True)
        return

    market_hash_name = inventory[item_index]
    await callback.answer(f"Searching price for {market_hash_name}...")
    
    price_data = await steam_api.get_item_price(market_hash_name)
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="« Back to Inventory", callback_data="back_to_inv"))
    
    text_to_send = ""
    if price_data:
        lowest_price = price_data.get('lowest_price', 'N/A')
        median_price = price_data.get('median_price', 'N/A')
        volume = price_data.get('volume', 'N/A')
        
        text_to_send = (
            f"<b>{market_hash_name}</b>\n\n"
            f"📉 <b>Lowest Price:</b> {lowest_price}\n"
            f"📊 <b>Median Price:</b> {median_price}\n"
            f"📦 <b>Volume (24h):</b> {volume} sold"
        )
    else:
        text_to_send = f"⚠️ Could not retrieve price for '{market_hash_name}'."

    try:
        await callback.message.edit_text(
            text_to_send,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        pass

@router.callback_query(InventorySearch.showing_inventory, F.data == "back_to_inv")
async def back_to_inventory_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    inventory = data.get("inventory")
    page = data.get("page", 0)
    steam_id = data.get("steam_id", "Unknown")
    
    if not inventory:
        await callback.answer("Error: Inventory data lost.", show_alert=True)
        return

    await callback.answer("Loading inventory...")
    
    keyboard = keyboard_builders.create_inventory_keyboard(inventory, page=page)
    
    try:
        await callback.message.edit_text(
            f"Inventory for {steam_id} ({len(inventory)} items):",
            reply_markup=keyboard
        )
    except TelegramBadRequest:
        pass

@router.callback_query(InventorySearch.showing_inventory, F.data == "close_inv")
async def inventory_close_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.answer("Inventory closed.")
    await callback.message.answer("Main Menu:", reply_markup=kb.main)

@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    await callback.answer()

# ---"Skin Price Search" (FSM) ---

@router.message(F.text == "Skin Price Search")
async def gun(message: Message, state: FSMContext) -> None:
    await state.set_state(SkinSearch.waiting_for_name)
    await message.answer("Please type a skin name to search (e.g., 'Redline' or 'AWP Asiimov'):",
                         reply_markup=None) 

@router.message(SkinSearch.waiting_for_name)
async def process_skin_search(message: Message, state: FSMContext):
    query = message.text
    results = dm.find_items_by_name(query)
    
    if not results:
        await state.clear() 
        await message.answer("⚠️ Nothing found. Please try again.", reply_markup=kb.main)
        return

    await state.set_state(SkinSearch.showing_results) 
    await state.update_data(query=query) 
    
    keyboard = keyboard_builders.create_skin_search_keyboard(results)
    
    await message.answer(
        f"Here's what I found for '{query}' (up to 15 shown):",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("priceid:"))
async def send_skin_price(callback: CallbackQuery, state: FSMContext):
    
    item_id = callback.data.split(":")[1]
    item_details = dm.item_database.get(item_id)
    
    if not item_details:
        await callback.answer("Error: Item not found in database.", show_alert=True)
        return

    market_hash_name = item_details['name']
    await callback.answer(f"Searching price for {market_hash_name}...")

    price_data = await steam_api.get_item_price(market_hash_name)
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="« Back to Results", callback_data="back_to_results"))
    
    text_to_send = ""
    if price_data:
        lowest_price = price_data.get('lowest_price', 'N/A')
        median_price = price_data.get('median_price', 'N/A')
        volume = price_data.get('volume', 'N/A')
        
        text_to_send = (
            f"<b>{market_hash_name}</b>\n\n"
            f"📉 <b>Lowest Price:</b> {lowest_price}\n"
            f"📊 <b>Median Price:</b> {median_price}\n"
            f"📦 <b>Volume (24h):</b> {volume} sold"
        )
    else:
        text_to_send = (f"⚠️ Could not retrieve price for '{market_hash_name}'. "
                        f"It might not be marketable or the Steam API is down.")

    try:
        await callback.message.edit_text(
            text_to_send,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        pass 

@router.callback_query(SkinSearch.showing_results, F.data == "back_to_results")
async def back_to_results_handler(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    query = state_data.get("query")
    
    if not query:
        await callback.answer("Error: Search query lost...", show_alert=True)
        await state.clear()
        try:
            await callback.message.edit_text("Session expired.", reply_markup=None)
        except TelegramBadRequest:
            pass
        return
    
    await callback.answer(f"Loading results for '{query}'...")
    
    results = dm.find_items_by_name(query)
    keyboard = keyboard_builders.create_skin_search_keyboard(results)
    
    try:
        await callback.message.edit_text(
            f"Here's what I found for '{query}' (up to 15 shown):",
            reply_markup=keyboard
        )
    except TelegramBadRequest:
        pass 


@router.message(F.text == "CS Price")
async def cs_price(message: Message) -> None:
    await message.answer("Counter-Strike 2 prices are fetched via the Steam Market using an unofficial API.", reply_markup=kb.main)