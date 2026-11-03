from nicegui import ui, app

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

def app_header(title: str):
    with ui.header().classes('bg-white dark:bg-black text-gray-900 dark:text-white items-center px-4 py-3 border-b border-gray-200 dark:border-gray-800 shadow-sm'):
        ui.label(title).classes('text-xl font-bold tracking-tight')
        ui.space()
        
        with ui.row().classes('items-center gap-2'):
            ui.button(icon='home', on_click=lambda: ui.navigate.to('/feed')).props('flat round color=black dark:color=white size=lg')
            ui.button(icon='people', on_click=lambda: ui.navigate.to('/friends')).props('flat round color=black dark:color=white size=lg')
            ui.button(icon='chat', on_click=lambda: ui.navigate.to('/chat')).props('flat round color=black dark:color=white size=lg')
            ui.button(icon='notifications', on_click=lambda: ui.navigate.to('/notifications')).props('flat round color=black dark:color=white size=lg')
            
            dark = ui.dark_mode()
            ui.button(icon='dark_mode', on_click=dark.toggle).props('flat round color=black dark:color=white size=lg')
            
            ui.button(icon='logout', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat round color=black dark:color=white size=lg')