import httpx
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/notifications')
async def notifications_page():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Notificaciones')

    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        notifs_container = ui.column().classes('w-full')
        
        async def load_notifs():
            notifs_container.clear()
            res = await api_get(f"/notifications/{current_user_id}")
            if res.status_code == 200:
                with notifs_container:
                    notifs = res.json()
                    if not notifs:
                        ui.label('No tienes notificaciones por ahora.').classes('text-gray-500 text-center w-full mt-8')
                    for n in notifs:
                        color = 'bg-white dark:bg-gray-800' if n['is_read'] else 'bg-blue-50 dark:bg-blue-900'
                        with ui.card().classes(f'w-full {color} mt-2 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4'):
                            with ui.row().classes('items-center gap-2 w-full justify-between'):
                                with ui.row().classes('items-center gap-2'):
                                    if n['type'] == 'friend_request':
                                        ui.icon('person_add', color='primary').classes('text-xl')
                                    elif n['type'] == 'friend_accept':
                                        ui.icon('check_circle', color='green').classes('text-xl')
                                    elif n['type'] == 'new_comment':
                                        ui.icon('comment', color='purple').classes('text-xl')
                                    else:
                                        ui.icon('notifications', color='gray').classes('text-xl')
                                    
                                    ui.label(n['message']).classes('font-bold text-gray-800 dark:text-gray-200')
                                
                                if n['type'] == 'friend_request' and n.get('related_id'):
                                    ui.button('Ver Perfil', icon='person', on_click=lambda u=n['related_id']: ui.navigate.to(f'/profile/{u}')).props('flat color=primary size=sm')
                            
                            if n['type'] == 'friend_request' and n.get('related_id'):
                                async def accept(req_sender_id=n['related_id'], notif_id=n['id']):
                                    res_req = await api_get(f"/friends/requests/{current_user_id}")
                                    if res_req.status_code == 200:
                                        for req in res_req.json():
                                            if req['sender_id'] == req_sender_id:
                                                await api_post(f"/friends/accept/{req['request_id']}")
                                                async with httpx.AsyncClient() as client:
                                                    await client.delete(
                                                        f"http://gateway:8000/notifications/{notif_id}", 
                                                        headers={"Authorization": f"Bearer {app.storage.user['token']}"}
                                                    )
                                                ui.notify('Amistad aceptada', color='positive')
                                                await load_notifs()
                                                return
                                
                                ui.button('Aceptar solicitud', on_click=accept).props('flat color=positive mt-2 rounded font-bold')
                            
                            ui.label(n['created_at'][:16].replace('T', ' ')).classes('text-xs text-gray-500 mt-2')

        await api_post(f"/notifications/{current_user_id}/read")
        
        res_all = await api_get(f"/notifications/{current_user_id}")
        if res_all.status_code == 200:
            for n in res_all.json():
                if n['type'] == 'friend_accept' and n['is_read']:
                    async with httpx.AsyncClient() as client:
                        await client.delete(
                            f"http://gateway:8000/notifications/{n['id']}", 
                            headers={"Authorization": f"Bearer {app.storage.user['token']}"}
                        )

        await load_notifs()