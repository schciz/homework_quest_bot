import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, PicklePersistence, filters


BOT_TOKEN = ''


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def init(application):
    if not application.bot_data:
        application.bot_data['user_id'] =  set()
        application.bot_data['user_name'] = dict()
        application.bot_data['current_scene'] = dict()
        application.bot_data['inventory'] = dict()
        application.bot_data['points'] = dict()


async def start(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Привет! Напиши имя пользователя чтобы зарегистрироваться.')
    else:
        current_scene = context.bot_data['current_scene'][user_id]

        if current_scene == 'Барак':
            await barak(update, context)
        if current_scene == 'Плац':
            await plac(update, context)
        if current_scene == 'Казарма охраны':
            await kazarma_ohrani(update, context)
        if current_scene == 'Забор с колючей проволокой':
            await zabor_s_kolyuchey_provolokoy(update, context)
        if current_scene == 'Ворота':
            await vorota(update, context)
        if current_scene == 'Успех':
            await uspeh(update, context)
        if current_scene == 'Провал':
            await proval(update, context)


async def registration(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        user_name = update.message.text.strip()

        context.bot_data['user_id'].add(user_id)
        context.bot_data['user_name'][user_id] = user_name
        context.bot_data['current_scene'][user_id] = 'Барак'
        context.bot_data['inventory'][user_id] = list()
        context.bot_data['points'][user_id] = 0

        await update.message.reply_text(f'Ты успешно зарегистрировался как "{user_name}"! Напиши /start для начала игры.')
    else:
        user_name = context.bot_data['user_name'][user_id]
        await update.message.reply_text(f'Ты уже зарегистрирован как "{user_name}"!')


async def help(update, context):
    text = (
        'Это Telegram-бот, который представляет собой интерактивный текстовый квест. '
        'Игрок должен пройти регистрацию и двигаться по сюжету, делая выбор в ключевых точках повествования. '
        'Прогресс пользователя сохраняется между сеансами общения с ботом.\n\n'
        'Игрок - советский солдат, который пытается сбежать из немецкого лагеря для военнопленных. '
        'Сюжет линейный с одним ключевым выбором, влияющим на концовку.\n\n'
        'Доступные команды:\n'
        '/start — Начать взаимодействие с ботом.\n'
        '/help — Вывести список всех доступных команд и краткое описание игры.\n'
        '/reset — Полностью сбросить прогресс и начинать квест заново.\n'
        '/status — Показать текущее состояние игрока.'
    )
    await update.message.reply_text(text)


async def reset(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        context.bot_data['user_id'].remove(user_id)
        del context.bot_data['user_name'][user_id]
        del context.bot_data['current_scene'][user_id]
        del context.bot_data['inventory'][user_id]
        del context.bot_data['points'][user_id]
        await update.message.reply_text('Данные успешно сброшены.')


async def status(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        user_name = context.bot_data['user_name'][user_id]
        current_scene = context.bot_data['current_scene'][user_id]
        inventory = context.bot_data['inventory'][user_id]
        points = context.bot_data['points'][user_id]

        inventory = sorted(inventory)
        if not inventory:
            inventory = 'Пока нету :('
        else:
            inventory = ', '.join(inventory)

        text = (
            'Текущие характеристики\n\n'
            f'Имя: {user_name}\n'
            f'Локация: {current_scene}\n'
            f'Достижения: {inventory}\n'
            f'Очки: {points}'
        )
        await update.message.reply_text(text)


async def barak(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        context.bot_data['current_scene'][user_id] = 'Барак'

        text = (
            '<b>Описание</b>: Вы просыпаетесь в холодном бараке. Ночь. '
            'Сквозь щели в стенах видны лучи прожекторов. '
            'Вас мучает жажда, но силы нужно беречь для побега. '
            'Рядом с вашей койкой лежит ржавый гвоздь.\n\n'

            '<b>Вопрос</b>: Что будете делать?'
        )

        keyboard = [
            ['Подойти к двери и посмотреть в щель.', 'Взять гвоздь и остаться на месте.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def plac(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        context.bot_data['current_scene'][user_id] = 'Плац'

        text = (
            '<b>Описание</b>: Вы видите, что часовой у ворот заснул, положив винтовку на колени. '
            'До него около 50 метров открытого пространства. '
            'Ваши действия стянутты и почти бесшумны.\n\n'

            '<b>Вопрос</b>: Как попытаться пройти?'
        )

        keyboard = [
            ['Попробовать подкрасться к часовому.', 'Проползти к забору, держась в тени.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def kazarma_ohrani(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        context.bot_data['current_scene'][user_id] = 'Казарма охраны'

        text = (
            '<b>Описание</b>: Вы решаете не рисковать и осматриваете барак. '
            'В углу вы находите потертый китель немецкого унтер-офицера. '
            'Это может быть хорошей маскировкой.\n\n'

            '<b>Вопрос</b>: Надеть китель?'
        )

        keyboard = [
            ['Надеть китель и выйти на улицу.', 'Оставить китель и вернуться к своей койке.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def zabor_s_kolyuchey_provolokoy(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        text = (
            '<b>Описание</b>: Вы благополучно доползли до забора. '
            'Проволока старая, кое-где провисает. '
            'С помощью гвоздя вам удается ослабить ее в одном месте и создать лаз.\n\n'

            'Вы проползаете под проволокой и исчезаете в ночном лесу. ПОБЕДА! Свобода!'
        )

        keyboard = [
            ['Сыграть снова.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

        item = 'Ржавый гвоздь'
        inventory = context.bot_data['inventory'][user_id]
        if item not in inventory:
            context.bot_data['inventory'][user_id].append(item)
            await update.message.reply_text(f'Получено достижение <b>{item}</b>!', parse_mode='HTML')

        target_scene = 'Забор с колючей проволокой'
        current_scene = context.bot_data['current_scene'][user_id]
        if current_scene != target_scene:
            context.bot_data['current_scene'][user_id] = target_scene

            points = 10
            context.bot_data['points'][user_id] += points
            await update.message.reply_text(f'Получено <b>{points}</b> очков!', parse_mode='HTML')


async def vorota(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        context.bot_data['current_scene'][user_id] = 'Ворота'

        text = (
            '<b>Описание</b>: В кителе вы выходите на плац и, стараясь идти уверенно, направляетесь к воротам. '
            'Часовой у ворот просыпается и смотрит на вас с подозрением.\n\n'

            '<b>Вопрос</b>: Что делать?'
        )

        keyboard = [
            ['Сказать по-немецки: "Пароль?"', 'Продолжать молча идти.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


async def uspeh(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        text = (
            '<b>Описание</b>: Часовой, ошеломленный вашей наглостью, бормочет пароль. '
            'Вы киваете и, не спеша, проходите через ворота. '
            'Через несколько минут вы уже в безопасности. \n\n'

            'ПОБЕДА! Вы сбежали благодаря смекалке!'
        )

        keyboard = [
            ['Сыграть снова.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

        item = 'Немецкий китель'
        inventory = context.bot_data['inventory'][user_id]
        if item not in inventory:
            context.bot_data['inventory'][user_id].append(item)
            await update.message.reply_text(f'Получено достижение <b>{item}</b>!', parse_mode='HTML')

        target_scene = 'Успех'
        current_scene = context.bot_data['current_scene'][user_id]
        if current_scene != target_scene:
            context.bot_data['current_scene'][user_id] = target_scene

            points = 15
            context.bot_data['points'][user_id] += points
            await update.message.reply_text(f'Получено <b>{points}</b> очков!', parse_mode='HTML')


async def proval(update, context):
    user_id = update.message.from_user.id
    if user_id not in context.bot_data['user_id']:
        await update.message.reply_text('Сначала зарегистрируйся через /start!')
    else:
        text = (
            '<b>Описание</b>: Часовой поднимает тревогу. '
            'Прожектор освещает вас, слышны выстрелы. '
            'Попытка побега неудачна.\n\n'
            'Вас отправляют в карцер. КОНЕЦ.'
        )

        keyboard = [
            ['Сыграть снова.'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

        target_scene = 'Провал'
        current_scene = context.bot_data['current_scene'][user_id]
        if current_scene != target_scene:
            context.bot_data['current_scene'][user_id] = target_scene

            points = 5
            context.bot_data['points'][user_id] -= points
            await update.message.reply_text(f'Потеряно <b>{points}</b> очков!', parse_mode='HTML')


if __name__ == '__main__':
    persistence = PicklePersistence(filepath='user_data.bin')
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .persistence(persistence=persistence)
        .post_init(init)
        .build()
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^[a-zA-Zа-яА-ЯёЁ0-9]+$'),
            registration
        )
    )

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    reset_handler = CommandHandler('reset', reset)
    application.add_handler(reset_handler)

    status_handler = CommandHandler('status', status)
    application.add_handler(status_handler)

    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^(Оставить китель и вернуться к своей койке|Сыграть снова)\.$'), 
            barak
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^Подойти к двери и посмотреть в щель\.$'), 
            plac
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^Взять гвоздь и остаться на месте\.$'), 
            kazarma_ohrani
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^Проползти к забору, держась в тени\.$'), 
            zabor_s_kolyuchey_provolokoy
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^Надеть китель и выйти на улицу\.$'), 
            vorota
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^Сказать по-немецки: "Пароль\?"$'), 
            uspeh
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r'^(Попробовать подкрасться к часовому|Продолжать молча идти)\.$'), 
            proval
        )
    )

    application.run_polling()
