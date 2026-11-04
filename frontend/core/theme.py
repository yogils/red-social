from nicegui import ui, app
import asyncio
from core.api import api_get

def apply_theme():
    ui.add_head_html('''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0f2f5;
        }
        .dark body {
            background-color: #000000;
        }
        
        .bg-unal {
            background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)), url('/static/fondo_unal.jpeg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
    </style>
    ''')

async def load_badges(notif_badge, chat_badge):
    if 'user_id' not in app.storage.user:
        return
    current_user_id = app.storage.user['user_id']
    
    res_notif = await api_get(f"/notifications/unread/{current_user_id}")
    if res_notif.status_code == 200:
        count = res_notif.json().get('count', 0)
        if count > 0:
            notif_badge.set_text(f'{count}')
            notif_badge.classes(remove='hidden')
        else:
            notif_badge.set_text('')
            notif_badge.classes(add='hidden')

    res_chat = await api_get(f"/users/messages/unread/{current_user_id}")
    if res_chat.status_code == 200:
        count = res_chat.json().get('count', 0)
        if count > 0:
            chat_badge.set_text(f'{count}')
            chat_badge.classes(remove='hidden')
        else:
            chat_badge.set_text('')
            chat_badge.classes(add='hidden')

def app_header(title: str):
    with ui.header().classes('bg-white dark:bg-black text-gray-900 dark:text-white items-center px-4 py-2 border-b border-gray-200 dark:border-gray-800 shadow-sm'):
        ui.label(title).classes('text-xl font-bold tracking-tight')
        ui.space()
        
        with ui.row().classes('items-center gap-4'):
            with ui.column().classes('items-center cursor-pointer hover:text-primary transition-colors').on('click', lambda: ui.navigate.to('/feed')):
                ui.icon('home', size='md')
                ui.label('Inicio').classes('text-xs font-medium')

            with ui.column().classes('items-center cursor-pointer hover:text-primary transition-colors').on('click', lambda: ui.navigate.to('/friends')):
                ui.icon('people', size='md')
                ui.label('Amigos').classes('text-xs font-medium')

            with ui.column().classes('items-center cursor-pointer hover:text-primary transition-colors').on('click', lambda: ui.navigate.to('/myprofile')):
                ui.icon('person', size='md')
                ui.label('Perfil').classes('text-xs font-medium')

            with ui.column().classes('items-center cursor-pointer hover:text-primary relative transition-colors').on('click', lambda: ui.navigate.to('/chat')):
                ui.icon('chat', size='md')
                chat_badge = ui.badge('').classes('absolute -top-1 right-2 bg-red-500 text-white hidden')
                ui.label('Chat').classes('text-xs font-medium')

            with ui.column().classes('items-center cursor-pointer hover:text-primary relative transition-colors').on('click', lambda: ui.navigate.to('/notifications')):
                ui.icon('notifications', size='md')
                notif_badge = ui.badge('').classes('absolute -top-1 right-2 bg-red-500 text-white hidden')
                ui.label('Avisos').classes('text-xs font-medium')

            dark = ui.dark_mode()
            ui.button(icon='dark_mode', on_click=dark.toggle).props('flat round color=black dark:color=white size=md')
            
            ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat round color=black dark:color=white size=md')

        ui.timer(3.0, lambda: asyncio.create_task(load_badges(notif_badge, chat_badge)))