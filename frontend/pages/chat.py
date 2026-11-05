import asyncio
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme, update_badges_func

@ui.page('/chat')
async def chat_page():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')
    chat_theme = app.storage.user.get('chat_theme', 'Clásico')

    app_header('Chat UNAL')

    if chat_theme == 'Oscuro':
        card_bg = 'bg-gray-900 text-white'
        header_bg = 'bg-gray-800 text-white'
        input_bg = 'bg-gray-800'
    elif chat_theme == 'Minimalista':
        card_bg = 'bg-white border border-gray-200'
        header_bg = 'bg-gray-100 text-black'
        input_bg = 'bg-gray-50'
    elif chat_theme == 'Colorido':
        card_bg = 'bg-blue-50'
        header_bg = 'bg-purple-600 text-white'
        input_bg = 'bg-white'
    else:
        card_bg = 'bg-white'
        header_bg = 'bg-primary text-white'
        input_bg = 'bg-white'

    open_chats = {}
    floating_chats_container = ui.row().classes('fixed bottom-0 right-4 gap-4 items-end z-50')

    def open_chat_window(friend_id, friend_name):
        if friend_id in open_chats:
            if open_chats[friend_id]['minimized']:
                toggle_minimize(friend_id)
            return
        
        with floating_chats_container:
            with ui.card().classes(f'w-80 h-[500px] shadow-2xl rounded-t-lg p-0 flex flex-col overflow-hidden {card_bg}') as chat_card:
                open_chats[friend_id] = {
                    'card': chat_card, 
                    'minimized': False, 
                    'last_msg_id': 0,
                    'friend_name': friend_name,
                    'messages_container': None
                }
                
                with ui.row().classes(f'{header_bg} p-2 w-full justify-between items-center flex-shrink-0'):
                    ui.button(friend_name, on_click=lambda: ui.navigate.to(f'/profile/{friend_id}')).props('flat no-caps color=white size=sm').classes('font-bold text-sm truncate')
                    with ui.row().classes('gap-1'):
                        ui.button(icon='remove', on_click=lambda: toggle_minimize(friend_id)).props('flat round color=white size=sm')
                        ui.button(icon='close', on_click=lambda: close_chat(friend_id)).props('flat round color=white size=sm')
                
                messages_container = ui.column().classes('flex-grow overflow-y-auto p-2 w-full')
                open_chats[friend_id]['messages_container'] = messages_container
                
                with ui.row().classes(f'w-full p-2 border-t items-center gap-1 flex-shrink-0 {input_bg}'):
                    uploader = ui.upload(on_upload=lambda e: handle_upload(e, friend_id), auto_upload=True).props('accept="image/*,video/*"').classes('hidden')
                    ui.button(icon='attach_file', on_click=lambda: uploader.run_method('pickFiles')).props('flat round color=primary size=sm')
                    
                    new_msg = ui.input(placeholder='Escribe...').props('borderless dense').classes('flex-grow')
                    
                    async def send():
                        if new_msg.value:
                            await api_post("/users/messages", json={"sender_id": current_user_id, "receiver_id": friend_id, "content": new_msg.value})
                            new_msg.value = ''
                            await load_messages(force=True)
                    
                    new_msg.on('keydown.enter', lambda: asyncio.create_task(send()))
                    ui.button(icon='send', on_click=lambda: asyncio.create_task(send())).props('flat round color=primary size=sm')
                    
                    ui.button(icon='mic', on_click=lambda: ui.notify('Nota de voz en desarrollo', color='info')).props('flat round color=primary size=sm')
                
                async def handle_upload(e, f_id):
                    file_bytes = await e.file.read()
                    res = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                    if res.status_code == 200:
                        data = res.json()
                        await api_post("/users/messages", json={
                            "sender_id": current_user_id,
                            "receiver_id": f_id,
                            "file_url": data['file_url'],
                            "file_type": data['file_type']
                        })
                        await load_messages(force=True)

                async def load_messages(force=False):
                    if friend_id not in open_chats or open_chats[friend_id]['minimized']:
                        return
                    
                    res = await api_get(f"/users/messages/{current_user_id}", params={"other_id": friend_id})
                    if res.status_code == 200:
                        msgs = res.json()
                        if msgs and (msgs[-1]['id'] != open_chats[friend_id]['last_msg_id'] or force):
                            open_chats[friend_id]['last_msg_id'] = msgs[-1]['id']
                            messages_container.clear()
                            with messages_container:
                                for msg in msgs:
                                    is_me = msg['sender_id'] == current_user_id
                                    if msg.get('file_url'):
                                        if msg['file_type'] == 'image':
                                            ui.image(f"http://localhost:8000{msg['file_url']}").classes('w-full rounded-lg mb-1')
                                        elif msg['file_type'] == 'video':
                                            ui.video(f"http://localhost:8000{msg['file_url']}").classes('w-full rounded-lg mb-1')
                                        elif msg['file_type'] == 'audio':
                                            ui.audio(f"http://localhost:8000{msg['file_url']}").classes('w-full mb-1')
                                    
                                    if msg.get('content'):
                                        ui.chat_message(msg['content'], name='Yo' if is_me else friend_name, sent=is_me)
                                
                                ui.run_javascript(f'const el = document.getElementById("c{messages_container.id}"); if(el) el.scrollTop = el.scrollHeight;')
                            
                            await api_post(f"/users/messages/read/{current_user_id}?sender_id={friend_id}")
                            if update_badges_func:
                                update_badges_func()
                
                ui.timer(2.0, load_messages)
                asyncio.create_task(load_messages(force=True))

    def close_chat(friend_id):
        if friend_id in open_chats:
            floating_chats_container.remove(open_chats[friend_id]['card'])
            del open_chats[friend_id]

    def toggle_minimize(friend_id):
        if friend_id in open_chats:
            data = open_chats[friend_id]
            card = data['card']
            msg_container = data['messages_container']
            
            if data['minimized']:
                card.classes(remove='h-16', add='h-[500px]')
                msg_container.classes(remove='hidden')
                data['minimized'] = False
                asyncio.create_task(reload_messages(friend_id))
            else:
                card.classes(remove='h-[500px]', add='h-16')
                msg_container.classes(add='hidden')
                data['minimized'] = True

    async def reload_messages(friend_id):
        if friend_id in open_chats and not open_chats[friend_id]['minimized']:
            msg_container = open_chats[friend_id]['messages_container']
            res = await api_get(f"/users/messages/{current_user_id}", params={"other_id": friend_id})
            if res.status_code == 200:
                msgs = res.json()
                open_chats[friend_id]['last_msg_id'] = msgs[-1]['id'] if msgs else 0
                msg_container.clear()
                with msg_container:
                    for msg in msgs:
                        is_me = msg['sender_id'] == current_user_id
                        if msg.get('file_url'):
                            if msg['file_type'] == 'image':
                                ui.image(f"http://localhost:8000{msg['file_url']}").classes('w-full rounded-lg mb-1')
                            elif msg['file_type'] == 'video':
                                ui.video(f"http://localhost:8000{msg['file_url']}").classes('w-full rounded-lg mb-1')
                            elif msg['file_type'] == 'audio':
                                ui.audio(f"http://localhost:8000{msg['file_url']}").classes('w-full mb-1')
                        if msg.get('content'):
                            ui.chat_message(msg['content'], name='Yo' if is_me else open_chats[friend_id]['friend_name'], sent=is_me)
                ui.run_javascript(f'const el = document.getElementById("c{msg_container.id}"); if(el) el.scrollTop = el.scrollHeight;')

    with ui.column().classes('w-full max-w-xl mx-auto p-4'):
        ui.label('Selecciona un amigo para chatear').classes('text-lg font-bold mb-4 text-gray-900 dark:text-white')
        friends_container = ui.column().classes('w-full')
        
        async def load_friends():
            res = await api_get(f"/friends/list/{current_user_id}")
            if res.status_code == 200:
                with friends_container:
                    for f in res.json():
                        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 flex-row items-center justify-between cursor-pointer hover:bg-gray-50').on('click', lambda u=f: open_chat_window(u['id'], u['full_name'])):
                            with ui.row().classes('items-center gap-3'):
                                ui.avatar(f['full_name'][0].upper(), color='primary', text_color='white')
                                with ui.column().classes('gap-0'):
                                    ui.label(f['full_name']).classes('font-medium text-gray-800 dark:text-gray-200')
                                    ui.label(f['email']).classes('text-xs text-gray-500')
                            ui.icon('chat', color='primary')

        await load_friends()