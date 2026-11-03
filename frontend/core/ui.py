from nicegui import ui, app

def app_header(title: str):
    with ui.header().classes('bg-primary text-white items-center'):
        ui.label(title).classes('text-h6 font-bold')
        ui.space()
        ui.link('Feed', '/feed').classes('text-white mr-4 no-underline hover:underline')
        ui.link('Amigos', '/friends').classes('text-white mr-4 no-underline hover:underline')
        ui.link('Chat', '/chat').classes('text-white mr-4 no-underline hover:underline')
        ui.link('Notificaciones', '/notifications').classes('text-white mr-4 no-underline hover:underline')
        ui.link('Mi Perfil', '/myprofile').classes('text-white mr-4 no-underline hover:underline')
        
        # Botón de Modo Oscuro
        dark = ui.dark_mode()
        ui.button(icon='dark_mode', on_click=dark.toggle).props('flat color=white round')
        
        ui.button('Cerrar Sesión', on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/'))).props('flat color=white')