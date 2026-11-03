import asyncio
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/chat')
async def chat_page(user_id: int = None):
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Chat UNAL')

    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        if user_id is None:
            ui.label('Selecciona un amigo para chatear').classes('text-h5 mt-4')
            friends_list = ui.column().classes('w-full')
            
            async def load_friends():
                res = await api_get(f"/friends/list/{current_user_id}")
                if res.status_code == 200:
                    with friends_list:
                        for f in res.json():
                            with ui.card().classes('w-full cursor-pointer hover:bg-gray-100').on('click', lambda u=f: ui.navigate.to(f'/chat?user_id={u["id"]}')):
                                ui.label(f['email'])
            
            await load_friends()
            return

        ui.button('← Volver a Amigos', on_click=lambda: ui.navigate.to('/chat')).props('flat')
        ui.label(f'Chat con Usuario {user_id}').classes('text-h6 mb-4')

        chat_container = ui.column().classes('w-full h-96 overflow-y-auto border p-4 bg-gray-50')
        new_msg = ui.input('Escribe un mensaje...').classes('w-full')

        last_msg_id = {'id': 0}

        async def load_msgs(auto_scroll=False):
            res = await api_get(f"/users/messages/{current_user_id}", params={"other_id": user_id})
            if res.status_code == 200:
                msgs = res.json()
                if msgs and msgs[-1]['id'] != last_msg_id['id']:
                    last_msg_id['id'] = msgs[-1]['id']
                    chat_container.clear()
                    with chat_container:
                        for msg in msgs:
                            is_me = msg['sender_id'] == current_user_id
                            ui.chat_message(msg['content'], name='Yo' if is_me else 'Ellos', sent=is_me)
                    
                    if auto_scroll:
                        ui.run_javascript('const el = document.getElementById("c" + ' + str(chat_container.id) + '); if(el) el.scrollTop = el.scrollHeight;')

        async def send_msg():
            if new_msg.value:
                await api_post("/users/messages", json={"sender_id": current_user_id, "receiver_id": user_id, "content": new_msg.value})
                new_msg.value = ''
                await load_msgs(auto_scroll=True)

        await api_post(f"/users/messages/read/{current_user_id}?sender_id={user_id}")
        await load_msgs()

        ui.timer(2.0, lambda: asyncio.create_task(load_msgs(auto_scroll=True)))

        new_msg.on('keydown.enter', lambda: asyncio.create_task(send_msg()))
        ui.button('Enviar', on_click=lambda: asyncio.create_task(send_msg())).props('color=primary').classes('w-full mt-2')