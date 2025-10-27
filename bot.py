import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db_queries import get_expeditions_by_region, get_unique_expeditions, get_coordinates_for_region

# 🔹 Настройки
API_TOKEN = "8307651561:AAGjxStMaM5w6eccOvBpU0TRqCel_4Ys2NE"

# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# 🔹 Создаем клавиатуру с океанами
def get_oceans_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🌊 Атлантический"), 
                KeyboardButton(text="🐠 Индийский")
            ],
            [
                KeyboardButton(text="🧊 Северный Ледовитый"), 
                KeyboardButton(text="🌴 Тихий")
            ],
            [
                KeyboardButton(text="📊 Все экспедиции"),
                KeyboardButton(text="🗺️ Все на карте")
            ],
            [
                KeyboardButton(text="❌ Скрыть меню")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите океан..."
    )
    return keyboard

# 🔹 /start - с красивой клавиатурой
@dp.message(CommandStart())
async def start(message: types.Message):
    text = (
        "🌊 *Добро пожаловать в Ocean Research System!*\n\n"
        "Я помогу вам изучить морские экспедиции по разным океанам.\n\n"
        "👇 *Выберите океан для просмотра экспедиций:*"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_oceans_keyboard())

# 🔹 Показать все экспедиции со статистикой 
async def show_all_expeditions(message: types.Message):
    expeditions = get_unique_expeditions()

    if not expeditions:
        await message.answer("❌ Нет данных об экспедициях.")
        return

    # Собираем статистику
    regions = set(exp["Район"] for exp in expeditions)
    active_expeditions = [e for e in expeditions if e["Дата_окончания"] is None]
    completed_expeditions = [e for e in expeditions if e["Дата_окончания"] is not None]
    
    # Собираем все координаты
    all_coords = []
    region_stats = {}
    
    for region in regions:
        region_exp = [e for e in expeditions if e["Район"] == region]
        region_coords = get_coordinates_for_region(region)
        
        if region_coords:
            all_coords.extend(region_coords)
            
        region_stats[region] = {
            'count': len(region_exp),
            'active': len([e for e in region_exp if e["Дата_окончания"] is None]),
            'points': len(region_coords) if region_coords else 0
        }

    # Формируем сообщение со статистикой
    text = "📊 *Общая статистика экспедиций*\n\n"
    
    # Основная статистика
    text += "📈 *Основные показатели:*\n"
    text += f"• 🚢 Всего экспедиций: *{len(expeditions)}*\n"
    text += f"• 🟢 Активных: *{len(active_expeditions)}*\n"
    text += f"• ✅ Завершенных: *{len(completed_expeditions)}*\n"
    text += f"• 🌍 Исследуемых регионов: *{len(regions)}*\n"
    text += f"• 📍 Точек наблюдения: *{len(all_coords)}*\n\n"

    # Статистика по океанам
    text += "🌊 *Статистика по океанам:*\n"
    ocean_emojis = {
        "Атлантический океан": "🌊",
        "Индийский океан": "🐠",
        "Северный Ледовитый океан": "🧊",
        "Тихий океан": "🌴",
    }

    for region, stats in region_stats.items():
        emoji = ocean_emojis.get(region, "🌊")
        active_percent = (stats['active'] / stats['count']) * 100 if stats['count'] > 0 else 0
        
        text += f"\n{emoji} *{region}:*\n"
        text += f"   📋 Экспедиций: {stats['count']}\n"
        text += f"   🟢 Активных: {stats['active']} ({active_percent:.1f}%)\n"
        text += f"   📍 Точек на карте: {stats['points']}\n"

    # Вместо обзорной карты предлагаем детальную
    if all_coords:
        text += f"\n🗺️ *Для просмотра на карте используйте кнопку* \"🗺️ Все на карте\""

    # Клавиатура с дополнительными действиями
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🟢 Активные"),
                KeyboardButton(text="✅ Завершенные")
            ],
            [
                KeyboardButton(text="🗺️ Все на карте"),  # ИСПРАВЛЕНО
                KeyboardButton(text="📅 По датам")
            ],
            [
                KeyboardButton(text="🌊 Атлантический"),
                KeyboardButton(text="🐠 Индийский")
            ],
            [
                KeyboardButton(text="🧊 Северный Ледовитый"), 
                KeyboardButton(text="🌴 Тихий")
            ],
            [
                KeyboardButton(text="❌ Скрыть меню")
            ]
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, disable_web_page_preview=False)

# 🔹 Показать детальную карту всех экспедиций
async def show_detailed_map(message: types.Message):
    expeditions = get_unique_expeditions()
    regions = set(exp["Район"] for exp in expeditions)
    
    # Собираем все координаты
    all_coords = []
    region_coords = {}
    
    for region in regions:
        coords = get_coordinates_for_region(region)
        if coords:
            all_coords.extend(coords)
            region_coords[region] = coords
    
    if not all_coords:
        await message.answer("❌ Нет координат для отображения карты.")
        return

    await message.answer(
        f"🗺️ *Все экспедиции на карте*\n\n"  # ИСПРАВЛЕНО название
        f"Отправляю {len(all_coords)} точек с {len(expeditions)} экспедиций...",
        parse_mode=ParseMode.MARKDOWN
    )

    # Отправляем точки по регионам
    for region, coords in region_coords.items():
        if coords:
            # Информация о регионе
            region_expeditions = [e for e in expeditions if e["Район"] == region]
            
            ocean_emojis = {
                "Атлантический океан": "🌊",
                "Индийский океан": "🐠", 
                "Северный Ледовитый океан": "🧊",
                "Тихий океан": "🌴"
            }
            emoji = ocean_emojis.get(region, "🌊")
            
            region_info = f"{emoji} *{region}*\n"
            region_info += f"Экспедиций: {len(region_expeditions)}\n"
            region_info += f"Точек на карте: {len(coords)}\n"
            
            await message.answer(region_info, parse_mode=ParseMode.MARKDOWN)
            
            # Отправляем координаты (ограничиваем 3 точками на регион)
            for i, coord in enumerate(coords[:3]):
                lat, lon = coord["Широта"], coord["Долгота"]
                maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=5"
                
                await message.answer_location(latitude=lat, longitude=lon)
                await message.answer(
                    f"📍 Точка {i+1}\n"
                    f"🗺️ [Открыть на карте]({maps_url})",
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=False
                )
                await asyncio.sleep(0.3)

# 🔹 Показать активные экспедиции
async def show_active_expeditions(message: types.Message):
    expeditions = get_unique_expeditions()
    active_expeditions = [e for e in expeditions if e["Дата_окончания"] is None]
    
    if not active_expeditions:
        await message.answer("🔍 *В данный момент нет активных экспедиций.*", parse_mode=ParseMode.MARKDOWN)
        return

    text = "🟢 *Активные экспедиции в реальном времени:*\n\n"
    
    # Словарь для правильных названий регионов
    region_names = {
        "Атлантический океан": "Атлантическом океане",
        "Индийский океан": "Индийском океане", 
        "Северный Ледовитый океан": "Северном Ледовитом океане",
        "Тихий океан": "Тихом океане"
    }
    
    for exp in active_expeditions:
        # Расчет продолжительности экспедиции
        start_date = exp["Дата_начала"]
        days_active = (datetime.now().date() - start_date).days
        
        coords_list = get_coordinates_for_region(exp["Район"])
        emoji = "🌊" if "Атлантический" in exp["Район"] else "🐠" if "Индийский" in exp["Район"] else "🧊" if "Северный" in exp["Район"] else "🌴"
        
        region_display = region_names.get(exp["Район"], exp["Район"])
        
        text += f"{emoji} *{exp['Название']}*\n"
        text += f"📍 *Регион:* {region_display}\n"
        text += f"📅 *Начало:* {exp['Дата_начала']}\n"
        text += f"⏱️ *Дней в работе:* {days_active}\n"
        
        if coords_list:
            # Ссылка на последнюю точку
            last_coord = coords_list[-1]
            maps_url = f"https://www.google.com/maps?q={last_coord['Широта']},{last_coord['Долгота']}&z=6"
            text += f"🗺️ [Последнее местоположение]({maps_url})\n"
        
        text += "\n"

    await message.answer(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False)

# 🔹 Показать завершенные экспедиции
async def show_completed_expeditions(message: types.Message):
    expeditions = get_unique_expeditions()
    completed_expeditions = [e for e in expeditions if e["Дата_окончания"] is not None]
    
    if not completed_expeditions:
        await message.answer("✅ *Нет завершенных экспедиций.*", parse_mode=ParseMode.MARKDOWN)
        return

    text = "✅ *Завершенные экспедиции:*\n\n"
    
    # Словарь для правильных названий регионов
    region_names = {
        "Атлантический океан": "Атлантическом океане",
        "Индийский океан": "Индийском океане", 
        "Северный Ледовитый океан": "Северном Ледовитом океане",
        "Тихий океан": "Тихом океане"
    }
    
    for exp in completed_expeditions:
        # Расчет продолжительности экспедиции
        start_date = exp["Дата_начала"]
        end_date = exp["Дата_окончания"]
        duration = (end_date - start_date).days
        
        coords_list = get_coordinates_for_region(exp["Район"])
        emoji = "🌊" if "Атлантический" in exp["Район"] else "🐠" if "Индийский" in exp["Район"] else "🧊" if "Северный" in exp["Район"] else "🌴"
        
        region_display = region_names.get(exp["Район"], exp["Район"])
        
        text += f"{emoji} *{exp['Название']}*\n"
        text += f"📍 *Регион:* {region_display}\n"
        text += f"📅 *Период:* {start_date} — {end_date}\n"
        text += f"⏱️ *Продолжительность:* {duration} дней\n"
        
        if coords_list:
            text += f"📍 *Точек исследования:* {len(coords_list)}\n"
        
        text += "\n"

    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

# 🔹 Показать экспедиции по датам
async def show_expeditions_by_date(message: types.Message):
    expeditions = get_unique_expeditions()
    
    if not expeditions:
        await message.answer("❌ Нет данных об экспедициях.")
        return

    # Сортируем по дате начала
    sorted_expeditions = sorted(expeditions, key=lambda x: x["Дата_начала"], reverse=True)
    
    text = "📅 *Экспедиции по датам (сначала новые):*\n\n"
    
    for exp in sorted_expeditions[:10]:  # Показываем только 10 последних
        status = "🟢 Активная" if exp["Дата_окончания"] is None else "✅ Завершена"
        emoji = "🌊" if "Атлантический" in exp["Район"] else "🐠" if "Индийский" in exp["Район"] else "🧊" if "Северный" in exp["Район"] else "🌴"
        
        text += f"{emoji} *{exp['Название']}*\n"
        text += f"📅 {exp['Дата_начала']} — {exp['Дата_окончания'] or 'по н.в.'}\n"
        text += f"📍 {exp['Район']} • {status}\n\n"

    if len(sorted_expeditions) > 10:
        text += f"... и еще {len(sorted_expeditions) - 10} экспедиций"

    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

# 🔹 Показать экспедиции по конкретному океану с ссылками на карты
async def show_expeditions_by_ocean(message: types.Message, ocean_name: str):
    expeditions = get_expeditions_by_region(ocean_name)
    
    if not expeditions:
        await message.answer(f"❌ В {ocean_name} нет данных об экспедициях.")
        return

    # Получаем координаты для этого океана
    coords_list = get_coordinates_for_region(ocean_name)
    
    # Эмодзи и правильные названия для океанов
    ocean_data = {
        "Атлантический океан": {"emoji": "🌊", "name": "Атлантическом океане"},
        "Индийский океан": {"emoji": "🐠", "name": "Индийском океане"}, 
        "Северный Ледовитый океан": {"emoji": "🧊", "name": "Северном Ледовитом океане"},
        "Тихий океан": {"emoji": "🌴", "name": "Тихом океане"}
    }
    
    ocean_info = ocean_data.get(ocean_name, {"emoji": "🌊", "name": ocean_name})
    emoji = ocean_info["emoji"]
    display_name = ocean_info["name"]
    
    text = f"{emoji} *Экспедиции в {display_name}:*\n\n"
    
    for exp in expeditions:
        text += f"*{exp['Название']}*\n"
        text += f"🗓 *Период:* {exp['Дата_начала']} — {exp['Дата_окончания'] or 'в процессе'}\n"
        
        # Добавляем информацию о координатах
        if coords_list:
            # Создаем ссылку на карту с первыми координатами
            first_coord = coords_list[0]
            lat, lon = first_coord["Широта"], first_coord["Долгота"]
            maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=4"
            
            text += f"📍 *Точек на карте:* {len(coords_list)}\n"
            text += f"🗺️ [Открыть регион на карте]({maps_url})\n"
        else:
            text += "⚠️ *Координаты не указаны*\n"
            
        text += "\n"

    # Добавляем общую карту региона
    if coords_list:
        # Создаем ссылку на общую карту со всеми точками
        if len(coords_list) == 1:
            lat, lon = coords_list[0]["Широта"], coords_list[0]["Долгота"]
            all_maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=4"
        else:
            # Для нескольких точек создаем примерную центральную точку
            avg_lat = sum(coord["Широта"] for coord in coords_list) / len(coords_list)
            avg_lon = sum(coord["Долгота"] for coord in coords_list) / len(coords_list)
            all_maps_url = f"https://www.google.com/maps?q={avg_lat},{avg_lon}&z=3"
        
        text += f"🗺️ *Общая карта региона:* [Открыть]({all_maps_url})"

    # Клавиатура с дополнительными действиями
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"🗺️ {ocean_name} на карте"),
                KeyboardButton(text="📊 Все экспедиции")
            ],
            [
                KeyboardButton(text="🌊 Атлантический"),
                KeyboardButton(text="🐠 Индийский")
            ],
            [
                KeyboardButton(text="🧊 Северный Ледовитый"), 
                KeyboardButton(text="🌴 Тихий")
            ],
            [
                KeyboardButton(text="❌ Скрыть меню")
            ]
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard, disable_web_page_preview=False)

# 🔹 Показать конкретный океан на карте с всеми точками
async def show_ocean_on_map(message: types.Message, ocean_name: str):
    expeditions = get_expeditions_by_region(ocean_name)
    coords_list = get_coordinates_for_region(ocean_name)
    
    if not coords_list:
        await message.answer(f"❌ Для {ocean_name} нет координат для отображения на карте.")
        return

    # Правильные названия для океанов
    ocean_data = {
        "Атлантический океан": {"emoji": "🌊", "name": "Атлантическом океане"},
        "Индийский океан": {"emoji": "🐠", "name": "Индийском океане"}, 
        "Северный Ледовитый океан": {"emoji": "🧊", "name": "Северном Ледовитом океане"},
        "Тихий океан": {"emoji": "🌴", "name": "Тихом океане"}
    }
    
    ocean_info = ocean_data.get(ocean_name, {"emoji": "🌊", "name": ocean_name})
    emoji = ocean_info["emoji"]
    display_name = ocean_info["name"]
    
    await message.answer(f"{emoji} *Отправляю точки в {display_name}:*\n{len(coords_list)} точек, {len(expeditions)} экспедиций")

    # Отправляем каждую точку на карте
    for i, coord in enumerate(coords_list, 1):
        lat, lon = coord["Широта"], coord["Долгота"]
        maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=6"
        
        # Создаем сообщение с информацией о точке
        point_info = (
            f"{emoji} *Точка {i} в {display_name}*\n"
            f"📍 Координаты: {lat:.4f}, {lon:.4f}\n"
            f"🗺️ [Открыть на карте]({maps_url})"
        )
        
        await message.answer_location(latitude=lat, longitude=lon)
        await message.answer(point_info, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False)
        await asyncio.sleep(0.3)

    # Общая карта региона
    if len(coords_list) > 1:
        avg_lat = sum(coord["Широта"] for coord in coords_list) / len(coords_list)
        avg_lon = sum(coord["Долгота"] for coord in coords_list) / len(coords_list)
        overview_url = f"https://www.google.com/maps?q={avg_lat},{avg_lon}&z=3"
        
        await message.answer(
            f"🗺️ *Обзорная карта всего региона:* [Открыть]({overview_url})\n"
            f"📍 Охватывает все {len(coords_list)} точек",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )

# 🔹 Обработчик кнопок океанов
@dp.message(lambda message: message.text in [
    "🌊 Атлантический", "🐠 Индийский", "🧊 Северный Ледовитый", "🌴 Тихий",
    "📊 Все экспедиции", "🗺️ Все на карте", "❌ Скрыть меню",  
    "🗺️ Атлантический океан на карте", "🗺️ Индийский океан на карте", 
    "🗺️ Северный Ледовитый океан на карте", "🗺️ Тихий океан на карте",
    "🟢 Активные", "✅ Завершенные", "📅 По датам"  
])
async def handle_ocean_buttons(message: types.Message):
    ocean_map = {
        "🌊 Атлантический": "Атлантический океан",
        "🐠 Индийский": "Индийский океан", 
        "🧊 Северный Ледовитый": "Северный Ледовитый океан",
        "🌴 Тихий": "Тихий океан",
        "🗺️ Атлантический океан на карте": "Атлантический океан",
        "🗺️ Индийский океан на карте": "Индийский океан",
        "🗺️ Северный Ледовитый океан на карте": "Северный Ледовитый океан", 
        "🗺️ Тихий океан на карте": "Тихий океан"
    }
    
    if message.text == "❌ Скрыть меню":
        await message.answer("⌨️ Клавиатура скрыта. Используйте /start чтобы вернуть меню.", reply_markup=ReplyKeyboardRemove())
        return
        
    elif message.text == "📊 Все экспедиции":
        await show_all_expeditions(message)
        return
        
    elif message.text == "🗺️ Все на карте":  
        await show_detailed_map(message)
        return
        
    elif message.text == "🟢 Активные":
        await show_active_expeditions(message)
        return
        
    elif message.text == "✅ Завершенные":
        await show_completed_expeditions(message)
        return
        
    elif message.text == "📅 По датам":
        await show_expeditions_by_date(message)
        return
        
    elif message.text.startswith("🗺️ "):
        ocean_name = ocean_map[message.text]
        await show_ocean_on_map(message, ocean_name)
        return
        
    else:
        ocean_name = ocean_map[message.text]
        await show_expeditions_by_ocean(message, ocean_name)

# 🔹 Обработка текстовых команд (для обратной совместимости)
@dp.message(Command("list"))
async def command_list(message: types.Message):
    await show_all_expeditions(message)

@dp.message(Command("map"))
async def command_map(message: types.Message):
    await show_detailed_map(message) 

@dp.message(Command("remove"))
async def command_remove(message: types.Message):
    await message.answer(
        "⌨️ Клавиатура скрыта. Используйте /start чтобы вернуть меню.",
        reply_markup=ReplyKeyboardRemove()
    )

# 🔹 Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())