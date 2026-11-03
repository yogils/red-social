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

    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        search_input = ui.input('Buscar por correo o nombre...').classes('w-full')
        results_container = ui.column().classes('w-full mt-2')

        async def do_search():
            res = await api_get("/friends/search", params={"query": search_input.value, "current_user_id": current_user_id})
            if res.status_code == 200:
                results_container.clear()
                with results_container:
                    for user in res.json():
                        with ui.row().classes('w-full items-center justify-between border-b pb-2'):
                            ui.link(user['email'], f"/profile/{user['id']}").classes('no-underline text-black')
                            if user['status'] == 'none':
                                async def send_req(receiver_id=user['id']):
                                    await api_post(f"/friends/request?sender_id={current_user_id}&receiver_id={receiver_id}")
                                    ui.notify('Solicitud enviada', color='positive')
                                    await do_search()
                                ui.button('Agregar', on_click=send_req).props('flat color=primary')

        ui.button('Buscar', on_click=do_search).props('color=primary')
        ui.separator()