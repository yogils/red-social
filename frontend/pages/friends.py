import httpx
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/friends')
async def friends_page():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Amigos UNAL')

    with ui.column().classes('w-full max-w-xl mx-auto p-4 pb-20'):
        
        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6'):
            ui.label('Encuentra compañeros').classes('text-lg font-bold mb-2 text-gray-900 dark:text-white')
            with ui.row().classes('w-full items-center gap-2'):
                search_input = ui.input(placeholder='Buscar por nombre o correo...').classes('flex-grow').props('outlined dense')
                
                async def do_search():
                    res = await api_get("/friends/search", params={"query": search_input.value, "current_user_id": current_user_id})
                    if res.status_code == 200:
                        results_container.clear()
                        with results_container:
                            for user in res.json():
                                with ui.row().classes('w-full items-center justify-between border-b border-gray-100 dark:border-gray-700 py-2'):
                                    with ui.column().classes('gap-0'):
                                        ui.label(user['full_name']).classes('font-medium text-gray-800 dark:text-gray-200')
                                        ui.label(user['email']).classes('text-xs text-gray-500')
                                    if user['status'] == 'none':
                                        async def send_req(receiver_id=user['id']):
                                            await api_post(f"/friends/request?sender_id={current_user_id}&receiver_id={receiver_id}")
                                            ui.notify('Solicitud enviada', color='positive')
                                            await do_search()
                                            await load_suggestions()
                                        ui.button('Agregar', on_click=send_req).props('flat color=primary size=sm')

                ui.button('Buscar', on_click=do_search).props('unelevated rounded color=primary')
            
            results_container = ui.column().classes('w-full mt-2')

        ui.label('Personas que quizás conozcas').classes('text-lg font-bold text-gray-900 dark:text-white mb-2 px-2')
        suggestions_container = ui.column().classes('w-full mb-6')
        
        async def load_suggestions():
            suggestions_container.clear()
            res = await api_get(f"/friends/suggestions/{current_user_id}")
            if res.status_code == 200:
                sugs = res.json()
                with suggestions_container:
                    if not sugs:
                        ui.label('No hay sugerencias por ahora').classes('text-gray-500 text-sm px-2')
                    for s in sugs:
                        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 flex-row items-center justify-between'):
                            with ui.row().classes('items-center gap-3'):
                                ui.avatar(s['full_name'][0].upper(), color='primary', text_color='white')
                                with ui.column().classes('gap-0'):
                                    ui.label(s['full_name']).classes('font-medium text-gray-800 dark:text-gray-200')
                                    ui.label(f"{s['mutual_friends']} amigos en común").classes('text-xs text-gray-500')
                            
                            async def send_req(receiver_id=s['id']):
                                await api_post(f"/friends/request?sender_id={current_user_id}&receiver_id={receiver_id}")
                                ui.notify('Solicitud enviada', color='positive')
                                await load_suggestions()
                            ui.button('Agregar', on_click=send_req).props('flat color=primary size=sm')
        
        await load_suggestions()

        ui.label('Solicitudes pendientes').classes('text-lg font-bold text-gray-900 dark:text-white mb-2 px-2')
        requests_container = ui.column().classes('w-full mb-6')
        
        async def load_requests():
            requests_container.clear()
            res = await api_get(f"/friends/requests/{current_user_id}")
            if res.status_code == 200:
                reqs = res.json()
                with requests_container:
                    if not reqs:
                        ui.label('No tienes solicitudes pendientes').classes('text-gray-500 text-sm px-2')
                    for r in reqs:
                        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 flex-row items-center justify-between'):
                            with ui.row().classes('items-center gap-3'):
                                ui.avatar(r['sender_name'][0].upper(), color='primary', text_color='white')
                                with ui.column().classes('gap-0'):
                                    ui.label(r['sender_name']).classes('font-medium text-gray-800 dark:text-gray-200')
                                    ui.label(r['sender_email']).classes('text-xs text-gray-500')
                            
                            async def accept(req_id=r['request_id']):
                                await api_post(f"/friends/accept/{req_id}")
                                ui.notify('Amistad aceptada', color='positive')
                                await load_requests()
                                await load_friends()
                                await load_suggestions()
                            ui.button('Aceptar', on_click=accept).props('unelevated rounded color=primary size=sm')

        await load_requests()

        ui.label('Mis Amigos').classes('text-lg font-bold text-gray-900 dark:text-white mb-2 px-2')
        friends_container = ui.column().classes('w-full')
        
        async def load_friends():
            friends_container.clear()
            res = await api_get(f"/friends/list/{current_user_id}")
            if res.status_code == 200:
                friends = res.json()
                with friends_container:
                    if not friends:
                        ui.label('Aún no tienes amigos agregados').classes('text-gray-500 text-sm px-2')
                    
                    grouped = {}
                    for f in friends:
                        fac = f.get('faculty') or 'Sin facultad'
                        if fac not in grouped:
                            grouped[fac] = []
                        grouped[fac].append(f)
                    
                    for fac, fac_friends in grouped.items():
                        ui.label(fac).classes('text-md font-bold text-primary mt-4 mb-2 px-2')
                        for f in fac_friends:
                            with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-3 flex-row items-center justify-between'):
                                with ui.row().classes('items-center gap-3'):
                                    ui.avatar(f['full_name'][0].upper(), color='primary', text_color='white')
                                    with ui.column().classes('gap-0'):
                                        ui.button(f['full_name'], on_click=lambda u=f: ui.navigate.to(f"/profile/{u['id']}")).props('flat no-caps color=primary').classes('font-medium text-left')
                                        ui.label(f['email']).classes('text-xs text-gray-500')
                                
                                with ui.row().classes('gap-2'):
                                    ui.button('Chatear', icon='chat', on_click=lambda u=f: ui.navigate.to('/chat')).props('flat rounded color=primary size=sm')
                                    
                                    async def remove_friend(friend_id=f['id']):
                                        async with httpx.AsyncClient() as client:
                                            await client.delete(f"http://gateway:8000/friends/remove/{friend_id}", params={"user_id": current_user_id}, headers={"Authorization": f"Bearer {app.storage.user['token']}"})
                                        ui.notify('Amigo eliminado', color='warning')
                                        await load_friends()
                                    
                                    ui.button(icon='person_remove', on_click=remove_friend).props('flat round color=red size=sm')

        await load_friends()