

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

ITEMS_PER_PAGE = 8 

def create_skin_search_keyboard(results: list) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру из списка найденных предметов. (Поиск)
    """
    builder = InlineKeyboardBuilder()
    
    for item in results:
        item_name = item['name']
        item_id = item['id']
        builder.add(InlineKeyboardButton(
            text=item_name,
            callback_data=f"priceid:{item_id}"
        ))
    
    builder.adjust(1)
    return builder.as_markup()


def create_inventory_keyboard(inventory: list, page: int = 0) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра инвентаря с пагинацией.
    """
    builder = InlineKeyboardBuilder()
    
    total_pages = (len(inventory) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    page_items = inventory[start_index:end_index]
    
    for i, item_name in enumerate(page_items):
        item_index = start_index + i 
        
        short_name = (item_name[:40] + '...') if len(item_name) > 43 else item_name
        
        builder.add(InlineKeyboardButton(
            text=short_name,
            callback_data=f"inv_idx:{item_index}"
        ))
    
    builder.adjust(2)
    
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(text="« Prev", callback_data=f"inv_page:{page - 1}")
        )
    
    pagination_buttons.append(
        InlineKeyboardButton(text=f"Page {page + 1}/{total_pages}", callback_data="noop") 
    )
        
    if page < total_pages - 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="Next »", callback_data=f"inv_page:{page + 1}")
        )
    
    builder.row(*pagination_buttons)
    
    builder.row(InlineKeyboardButton(text="Close Inventory", callback_data="close_inv"))
    
    return builder.as_markup()