from nicegui import ui, app
from core.theme import app_header, apply_theme
import asyncio

@ui.page('/settings')
async def settings_page():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return

    app_header('Ajustes de la Plataforma')

    active_section = {'value': 'apariencia'}

    with ui.row().classes('w-full max-w-6xl mx-auto p-4 mt-4 gap-6'):
        
        with ui.column().classes('w-full md:w-1/4 gap-2'):
            ui.label('Configuración').classes('text-2xl font-bold mb-4')
            
            with ui.column().classes('w-full gap-1'):
                btn_apariencia = ui.button('Apariencia', icon='palette').props('flat no-caps align=left').classes('w-full text-left')
                btn_cuenta = ui.button('Cuenta', icon='person').props('flat no-caps align=left').classes('w-full text-left')
                btn_notificaciones = ui.button('Notificaciones', icon='notifications').props('flat no-caps align=left').classes('w-full text-left')
                btn_privacidad = ui.button('Privacidad', icon='lock').props('flat no-caps align=left').classes('w-full text-left')

        with ui.column().classes('w-full md:w-3/4'):
            content_container = ui.column().classes('w-full')
            
            async def render_content():
                content_container.clear()
                with content_container:
                    if active_section['value'] == 'apariencia':
                        with ui.card().classes('w-full rounded-2xl shadow-sm border border-gray-200 p-6'):
                            ui.label('Apariencia').classes('text-xl font-bold mb-1')
                            ui.label('Personaliza todos los colores de tu red social.').classes('text-sm text-gray-500 mb-6')
                            
                            with ui.row().classes('w-full gap-4 mb-6'):
                                with ui.card().classes('flex-grow p-4 bg-gray-50 rounded-lg border border-gray-200'):
                                    ui.label('Vista Previa').classes('text-xs font-bold text-gray-500 mb-2')
                                    ui.label('Texto de ejemplo').classes('text-lg mb-2')
                                    ui.button('Botón de ejemplo').props('unelevated rounded color=primary')
                            
                            ui.separator().classes('my-4')
                            
                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Color Principal').classes('text-md font-bold')
                                    ui.label('Botones y enlaces.').classes('text-xs text-gray-500')
                                primary_input = ui.color_input(label='', value=app.storage.user.get('primary_color', '#4F46E5')).props('outlined dense').classes('w-48')
                            
                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Color de Fondo').classes('text-md font-bold')
                                    ui.label('Fondo de la página.').classes('text-xs text-gray-500')
                                bg_input = ui.color_input(label='', value=app.storage.user.get('bg_color', '#f0f2f5')).props('outlined dense').classes('w-48')

                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Color de Tarjetas').classes('text-md font-bold')
                                    ui.label('Fondo de las tarjetas y header.').classes('text-xs text-gray-500')
                                card_input = ui.color_input(label='', value=app.storage.user.get('card_color', '#ffffff')).props('outlined dense').classes('w-48')

                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Color de Texto').classes('text-md font-bold')
                                    ui.label('Color principal del texto.').classes('text-xs text-gray-500')
                                text_input = ui.color_input(label='', value=app.storage.user.get('text_color', '#1f2937')).props('outlined dense').classes('w-48')
                            
                            with ui.row().classes('w-full items-center justify-between mb-4'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Tipo de Letra').classes('text-md font-bold')
                                    ui.label('Fuente de toda la plataforma.').classes('text-xs text-gray-500')
                                font_select = ui.select(
                                    ['Inter', 'Roboto', 'Poppins', 'Montserrat', 'Open Sans', 'Arial'], 
                                    label='', 
                                    value=app.storage.user.get('font_family', 'Inter')
                                ).props('outlined dense').classes('w-48')

                            with ui.row().classes('w-full items-center justify-between mb-6'):
                                with ui.column().classes('gap-1'):
                                    ui.label('Tema del Chat').classes('text-md font-bold')
                                    ui.label('Estilo visual de la ventana de chat.').classes('text-xs text-gray-500')
                                chat_theme_select = ui.select(
                                    ['Clásico', 'Oscuro', 'Minimalista', 'Colorido'], 
                                    label='', 
                                    value=app.storage.user.get('chat_theme', 'Clásico')
                                ).props('outlined dense').classes('w-48')

                            async def apply_changes():
                                app.storage.user['primary_color'] = primary_input.value
                                app.storage.user['bg_color'] = bg_input.value
                                app.storage.user['card_color'] = card_input.value
                                app.storage.user['text_color'] = text_input.value
                                app.storage.user['font_family'] = font_select.value
                                app.storage.user['chat_theme'] = chat_theme_select.value
                                ui.notify('Ajustes guardados correctamente', color='positive')
                                ui.navigate.to('/settings')

                            ui.button('Guardar Cambios', on_click=apply_changes).props('unelevated rounded color=primary size=lg').classes('w-full mt-4')

                            ui.separator().classes('my-4')

                            async def reset_settings():
                                app.storage.user.pop('primary_color', None)
                                app.storage.user.pop('bg_color', None)
                                app.storage.user.pop('card_color', None)
                                app.storage.user.pop('text_color', None)
                                app.storage.user.pop('font_family', None)
                                app.storage.user.pop('chat_theme', None)
                                ui.notify('Ajustes restablecidos', color='info')
                                ui.navigate.to('/settings')

                            ui.button('Restablecer valores por defecto', on_click=reset_settings).props('flat color=red size=sm').classes('w-full')

                    elif active_section['value'] == 'cuenta':
                        with ui.card().classes('w-full rounded-2xl shadow-sm border border-gray-200 p-6'):
                            ui.label('Cuenta').classes('text-xl font-bold mb-1')
                            ui.label('Gestiona tu información personal y seguridad.').classes('text-sm text-gray-500 mb-6')
                            
                            ui.label('Correo electrónico').classes('text-sm font-bold')
                            ui.label(app.storage.user.get('email')).classes('text-md mb-4')
                            
                            ui.separator().classes('my-4')
                            
                            ui.label('Cambiar contraseña').classes('text-sm font-bold mb-2')
                            ui.input('Contraseña actual', password=True).props('outlined dense').classes('w-full mb-2')
                            ui.input('Nueva contraseña', password=True).props('outlined dense').classes('w-full mb-2')
                            ui.button('Actualizar Contraseña').props('unelevated rounded color=primary size=sm')

                    elif active_section['value'] == 'notificaciones':
                        with ui.card().classes('w-full rounded-2xl shadow-sm border border-gray-200 p-6'):
                            ui.label('Notificaciones').classes('text-xl font-bold mb-1')
                            ui.label('Elige qué notificaciones quieres recibir.').classes('text-sm text-gray-500 mb-6')
                            
                            ui.switch('Notificaciones de solicitudes de amistad').props('color=primary')
                            ui.switch('Notificaciones de mensajes nuevos').props('color=primary')
                            ui.switch('Notificaciones de comentarios').props('color=primary')

                    elif active_section['value'] == 'privacidad':
                        with ui.card().classes('w-full rounded-2xl shadow-sm border border-gray-200 p-6'):
                            ui.label('Privacidad').classes('text-xl font-bold mb-1')
                            ui.label('Controla quién puede ver tu información.').classes('text-sm text-gray-500 mb-6')
                            
                            ui.select(['Todos', 'Solo amigos', 'Nadie'], label='¿Quién puede ver mi perfil?', value='Todos').props('outlined dense').classes('w-full mb-4')
                            ui.select(['Todos', 'Solo amigos', 'Nadie'], label='¿Quién puede enviarme mensajes?', value='Todos').props('outlined dense').classes('w-full')

            async def change_section(section_name):
                active_section['value'] = section_name
                buttons = {
                    'apariencia': btn_apariencia,
                    'cuenta': btn_cuenta,
                    'notificaciones': btn_notificaciones,
                    'privacidad': btn_privacidad
                }
                for key, btn in buttons.items():
                    if key == section_name:
                        btn.props('color=primary text-color=white')
                    else:
                        btn.props('color=grey-8 text-color=grey-8')
                await render_content()

            btn_apariencia.on('click', lambda: asyncio.create_task(change_section('apariencia')))
            btn_cuenta.on('click', lambda: asyncio.create_task(change_section('cuenta')))
            btn_notificaciones.on('click', lambda: asyncio.create_task(change_section('notificaciones')))
            btn_privacidad.on('click', lambda: asyncio.create_task(change_section('privacidad')))

            await change_section('apariencia')