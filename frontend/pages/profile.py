import asyncio
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/myprofile')
async def my_profile():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')
    user_email = app.storage.user.get('email', 'U')

    app_header('Mi Perfil')

    with ui.column().classes('w-full max-w-6xl mx-auto pb-10 bg-gray-100 dark:bg-black'):
        
        res = await api_get(f"/users/profiles/{current_user_id}")
        profile_data = res.json() if res.status_code == 200 else {}
        
        cover_url = profile_data.get('cover_picture_url')
        if cover_url:
            ui.image(f"http://localhost:8000{cover_url}").classes('w-full h-64 md:h-80 object-cover')
        else:
            with ui.row().classes('w-full h-64 md:h-80 bg-gradient-to-r from-green-700 to-green-900 items-center justify-center'):
                ui.label('Universidad Nacional de Colombia').classes('text-white text-2xl font-bold opacity-50')

        with ui.row().classes('w-full px-4 md:px-12 relative -mt-16 md:-mt-20 items-end gap-6'):
            if profile_data.get('profile_picture_url'):
                ui.image(f"http://localhost:8000{profile_data['profile_picture_url']}").classes('w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-white dark:border-gray-800 shadow-lg bg-white')
            else:
                ui.avatar(profile_data.get('full_name', 'U')[0].upper(), color='primary', text_color='white', size='xl').classes('w-32 h-32 md:w-40 md:h-40 text-6xl border-4 border-white dark:border-gray-800 shadow-lg')

            with ui.column().classes('mb-4 gap-1 flex-grow'):
                ui.label(profile_data.get('full_name', 'Usuario')).classes('text-3xl font-bold text-gray-900 dark:text-white')
                ui.label(f"{profile_data.get('career', 'Estudiante UNAL')}").classes('text-md font-medium text-green-700 dark:text-green-500')

        with ui.row().classes('w-full px-4 md:px-12 mt-2 gap-2'):
            async def handle_cover(e):
                file_bytes = await e.file.read()
                res_up = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                if res_up.status_code == 200:
                    img_url = res_up.json()['image_url']
                    await api_post(f"/users/profiles/{current_user_id}/cover?image_url={img_url}")
                    ui.navigate.to('/myprofile')
            
            ui.button('Editar Portada', icon='photo_camera', on_click=lambda: cover_uploader.run_method('pickFiles')).props('unelevated rounded color=gray-200 text-color=black')
            cover_uploader = ui.upload(on_upload=handle_cover, auto_upload=True).classes('hidden')
            
            async def handle_pfp(e):
                file_bytes = await e.file.read()
                res_up = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                if res_up.status_code == 200:
                    img_url = res_up.json()['image_url']
                    await api_post(f"/users/profiles/{current_user_id}/picture?image_url={img_url}")
                    ui.navigate.to('/myprofile')

            ui.button('Editar Foto', icon='person', on_click=lambda: pfp_uploader.run_method('pickFiles')).props('unelevated rounded color=gray-200 text-color=black')
            pfp_uploader = ui.upload(on_upload=handle_pfp, auto_upload=True).classes('hidden')

        active_tab = {'value': 'todo'}
        content_container = ui.column().classes('w-full px-4 md:px-12 mt-6')

        async def render_content():
            content_container.clear()
            with content_container:
                if active_tab['value'] == 'todo':
                    with ui.row().classes('w-full gap-6'):
                        with ui.column().classes('w-full md:w-1/3 gap-4'):
                            with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4'):
                                info_container = ui.column().classes('w-full')
                                
                                async def render_info(edit_mode=False):
                                    info_container.clear()
                                    with info_container:
                                        if edit_mode:
                                            career_input = ui.input('Carrera', value=profile_data.get('career', '')).props('outlined dense').classes('w-full mb-2')
                                            bio_input = ui.textarea('Biografía corta', value=profile_data.get('bio', '')).props('outlined dense rows=2').classes('w-full mb-2')
                                            
                                            async def save_profile():
                                                await api_post(f"/users/profiles/{current_user_id}/update", json={
                                                    "career": career_input.value,
                                                    "bio": bio_input.value
                                                })
                                                ui.notify('Perfil actualizado correctamente', color='positive')
                                                profile_data['career'] = career_input.value
                                                profile_data['bio'] = bio_input.value
                                                await render_info(False)
                                            
                                            ui.button('Guardar', on_click=save_profile).props('unelevated rounded color=primary size=sm').classes('w-full')
                                            ui.button('Cancelar', on_click=lambda: render_info(False)).props('flat color=gray size=sm').classes('w-full mt-1')
                                        else:
                                            with ui.row().classes('w-full justify-between items-center'):
                                                ui.label('Información').classes('text-lg font-bold text-gray-900 dark:text-white')
                                                ui.button(icon='edit', on_click=lambda: render_info(True)).props('flat round color=gray-500 size=sm')
                                            
                                            ui.label(f"Carrera: {profile_data.get('career', 'No especificada')}").classes('text-sm text-gray-600 dark:text-gray-300 mt-2')
                                            if profile_data.get('bio'):
                                                ui.separator().classes('my-2')
                                                ui.label(f"Bio: {profile_data.get('bio')}").classes('text-sm text-gray-600 dark:text-gray-300')
                                
                                await render_info(False)

                        with ui.column().classes('w-full md:w-2/3 gap-4'):
                            with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4'):
                                with ui.row().classes('w-full items-center gap-3'):
                                    ui.avatar(user_email[0].upper(), color='primary', text_color='white', size='md')
                                    new_post_text = ui.input(placeholder="¿Qué estás pensando?").classes('flex-grow').props('borderless dense')
                                
                                uploaded_image = {'url': None}
                                async def handle_upload(e):
                                    file_bytes = await e.file.read()
                                    res = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                                    if res.status_code == 200:
                                        uploaded_image['url'] = res.json()['image_url']
                                        ui.notify('Imagen lista para publicar', color='positive')

                                async def publish():
                                    if not new_post_text.value and not uploaded_image['url']:
                                        return
                                    res = await api_post("/users/posts", json={
                                        "author_id": current_user_id, "author_name": user_email,
                                        "content": new_post_text.value or "", "image_url": uploaded_image['url']
                                    })
                                    if res.status_code == 200:
                                        ui.navigate.to('/myprofile')

                                with ui.row().classes('w-full justify-between items-center mt-3 pt-3 border-t border-gray-100 dark:border-gray-700'):
                                    with ui.row().classes('gap-2 cursor-pointer').on('click', lambda: uploader.run_method('pickFiles')):
                                        ui.icon('photo_camera', size='sm').classes('text-green-500')
                                        ui.label('Foto/video').classes('text-xs text-gray-500')
                                    uploader = ui.upload(on_upload=handle_upload, auto_upload=True).props('accept=".jpg,.png,.jpeg"').classes('hidden')
                                    
                                    with ui.row().classes('gap-2 cursor-pointer'):
                                        ui.icon('movie', size='sm').classes('text-blue-500')
                                        ui.label('Reel').classes('text-xs text-gray-500')
                                        
                                    ui.button('Publicar', on_click=publish).props('unelevated rounded color=primary size=sm')

                            ui.label('Mis Publicaciones').classes('text-lg font-bold text-gray-900 dark:text-white mt-2')
                            res_posts = await api_get("/users/posts", params={"user_id": current_user_id})
                            user_posts = []
                            if res_posts.status_code == 200:
                                user_posts = [p for p in res_posts.json() if p['author_id'] == current_user_id]
                            
                            if not user_posts:
                                ui.label('Aún no tienes publicaciones.').classes('text-gray-500 text-center w-full mt-8')
                            for post in user_posts:
                                with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-0 overflow-hidden mb-4'):
                                    if post['content']:
                                        ui.label(post['content']).classes('p-4 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap')
                                    if post.get('image_url'):
                                        ui.image(f"http://localhost:8000{post['image_url']}").classes('w-full object-cover')

                elif active_tab['value'] == 'info':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Información Personal').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        ui.label(f"Nombre completo: {profile_data.get('full_name', 'No especificado')}").classes('text-md text-gray-700 dark:text-gray-300 mb-2')
                        ui.label(f"Carrera: {profile_data.get('career', 'No especificada')}").classes('text-md text-gray-700 dark:text-gray-300 mb-2')
                        ui.label(f"Biografía: {profile_data.get('bio', 'Sin biografía')}").classes('text-md text-gray-700 dark:text-gray-300')

                elif active_tab['value'] == 'friends':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Mis Amigos').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        res_amigos = await api_get(f"/friends/list/{current_user_id}")
                        if res_amigos.status_code == 200:
                            amigos = res_amigos.json()
                            if not amigos:
                                ui.label('No tienes amigos aún.').classes('text-gray-500')
                            for amigo in amigos:
                                with ui.row().classes('items-center gap-3 p-2 border-b border-gray-100 dark:border-gray-700'):
                                    ui.avatar(amigo['full_name'][0].upper(), color='primary', text_color='white')
                                    ui.label(amigo['full_name']).classes('text-md text-gray-800 dark:text-gray-200')

                elif active_tab['value'] == 'photos':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Mis Fotos').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        res_posts = await api_get("/users/posts", params={"user_id": current_user_id})
                        if res_posts.status_code == 200:
                            photos = [p for p in res_posts.json() if p['author_id'] == current_user_id and p.get('image_url')]
                            if not photos:
                                ui.label('No has subido fotos aún.').classes('text-gray-500')
                            with ui.row().classes('gap-4 flex-wrap'):
                                for p in photos:
                                    ui.image(f"http://localhost:8000{p['image_url']}").classes('w-48 h-48 object-cover rounded-lg shadow-md')

                elif active_tab['value'] == 'reels':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Mis Reels').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        ui.label('Aún no has subido ningún Reel.').classes('text-gray-500')

        async def change_tab(tab_name):
            active_tab['value'] = tab_name
            tabs_dict = {'todo': tab_todo, 'info': tab_info, 'friends': tab_friends, 'photos': tab_photos, 'reels': tab_reels}
            for key, tab_el in tabs_dict.items():
                if key == tab_name:
                    tab_el.classes(add='text-blue-600 border-b-2 border-blue-600', remove='text-gray-500')
                else:
                    tab_el.classes(add='text-gray-500', remove='text-blue-600 border-b-2 border-blue-600')
            await render_content()

        with ui.row().classes('w-full px-4 md:px-12 mt-6 border-b border-gray-300 dark:border-gray-700 gap-6'):
            tab_todo = ui.label('Todo').classes('text-md font-bold text-blue-600 border-b-2 border-blue-600 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('todo')))
            tab_info = ui.label('Información').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('info')))
            tab_friends = ui.label('Amigos').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('friends')))
            tab_photos = ui.label('Fotos').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('photos')))
            tab_reels = ui.label('Reels').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('reels')))

        await render_content()


@ui.page('/profile/{user_id}')
async def user_profile(user_id: int):
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Perfil de Usuario')

    with ui.column().classes('w-full max-w-6xl mx-auto pb-10 bg-gray-100 dark:bg-black'):
        res_profile = await api_get(f"/users/profiles/{user_id}")
        pfp_url = None
        career = None
        bio = None
        cover_url = None
        full_name = f"Usuario {user_id}"
        
        if res_profile.status_code == 200:
            data = res_profile.json()
            pfp_url = data.get('profile_picture_url')
            career = data.get('career')
            bio = data.get('bio')
            cover_url = data.get('cover_picture_url')
            full_name = data.get('full_name', full_name)

        if cover_url:
            ui.image(f"http://localhost:8000{cover_url}").classes('w-full h-64 md:h-80 object-cover')
        else:
            with ui.row().classes('w-full h-64 md:h-80 bg-gradient-to-r from-green-700 to-green-900 items-center justify-center'):
                ui.label('Universidad Nacional de Colombia').classes('text-white text-2xl font-bold opacity-50')

        with ui.row().classes('w-full px-4 md:px-12 relative -mt-16 md:-mt-20 items-end gap-6'):
            if pfp_url:
                ui.image(f"http://localhost:8000{pfp_url}").classes('w-32 h-32 md:w-40 md:h-40 rounded-full object-cover border-4 border-white dark:border-gray-800 shadow-lg bg-white')
            else:
                ui.avatar(full_name[0].upper(), color='primary', text_color='white', size='xl').classes('w-32 h-32 md:w-40 md:h-40 text-6xl border-4 border-white dark:border-gray-800 shadow-lg')

            with ui.column().classes('mb-4 gap-1 flex-grow'):
                ui.label(full_name).classes('text-3xl font-bold text-gray-900 dark:text-white')
                ui.label(f"{career or 'Estudiante UNAL'}").classes('text-md font-medium text-green-700 dark:text-green-500')

        with ui.row().classes('w-full px-4 md:px-12 mt-2 gap-2'):
            if user_id != current_user_id:
                ui.button('Enviar mensaje', icon='chat', on_click=lambda: ui.navigate.to(f'/chat?user_id={user_id}')).props('unelevated rounded color=primary')

        active_tab = {'value': 'todo'}
        content_container = ui.column().classes('w-full px-4 md:px-12 mt-6')

        async def render_content():
            content_container.clear()
            with content_container:
                if active_tab['value'] == 'todo':
                    with ui.row().classes('w-full gap-6'):
                        with ui.column().classes('w-full md:w-1/3 gap-4'):
                            with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4'):
                                ui.label('Información').classes('text-lg font-bold mb-2 text-gray-900 dark:text-white')
                                ui.label(f"Carrera: {career or 'No especificada'}").classes('text-sm text-gray-600 dark:text-gray-300')
                                if bio:
                                    ui.separator().classes('my-2')
                                    ui.label(f"Bio: {bio}").classes('text-sm text-gray-600 dark:text-gray-300')

                        with ui.column().classes('w-full md:w-2/3 gap-4'):
                            ui.label('Publicaciones').classes('text-lg font-bold text-gray-900 dark:text-white')
                            res_posts = await api_get("/users/posts", params={"user_id": current_user_id})
                            user_posts = []
                            if res_posts.status_code == 200:
                                user_posts = [p for p in res_posts.json() if p['author_id'] == user_id]
                            
                            if not user_posts:
                                ui.label('Este usuario no tiene publicaciones.').classes('text-gray-500 text-center w-full mt-8')
                            for post in user_posts:
                                with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-0 overflow-hidden mb-4'):
                                    if post['content']:
                                        ui.label(post['content']).classes('p-4 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap')
                                    if post.get('image_url'):
                                        ui.image(f"http://localhost:8000{post['image_url']}").classes('w-full object-cover')

                elif active_tab['value'] == 'info':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Información Personal').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        ui.label(f"Nombre completo: {full_name}").classes('text-md text-gray-700 dark:text-gray-300 mb-2')
                        ui.label(f"Carrera: {career or 'No especificada'}").classes('text-md text-gray-700 dark:text-gray-300 mb-2')
                        ui.label(f"Biografía: {bio or 'Sin biografía'}").classes('text-md text-gray-700 dark:text-gray-300')

                elif active_tab['value'] == 'friends':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Amigos').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        res_amigos = await api_get(f"/friends/list/{user_id}")
                        if res_amigos.status_code == 200:
                            amigos = res_amigos.json()
                            if not amigos:
                                ui.label('No tiene amigos aún.').classes('text-gray-500')
                            for amigo in amigos:
                                with ui.row().classes('items-center gap-3 p-2 border-b border-gray-100 dark:border-gray-700'):
                                    ui.avatar(amigo['full_name'][0].upper(), color='primary', text_color='white')
                                    ui.label(amigo['full_name']).classes('text-md text-gray-800 dark:text-gray-200')

                elif active_tab['value'] == 'photos':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Fotos').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        res_posts = await api_get("/users/posts", params={"user_id": current_user_id})
                        if res_posts.status_code == 200:
                            photos = [p for p in res_posts.json() if p['author_id'] == user_id and p.get('image_url')]
                            if not photos:
                                ui.label('No ha subido fotos aún.').classes('text-gray-500')
                            with ui.row().classes('gap-4 flex-wrap'):
                                for p in photos:
                                    ui.image(f"http://localhost:8000{p['image_url']}").classes('w-48 h-48 object-cover rounded-lg shadow-md')

                elif active_tab['value'] == 'reels':
                    with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6'):
                        ui.label('Reels').classes('text-xl font-bold mb-4 text-gray-900 dark:text-white')
                        ui.label('Este usuario no ha subido Reels.').classes('text-gray-500')

        async def change_tab(tab_name):
            active_tab['value'] = tab_name
            tabs_dict = {'todo': tab_todo, 'info': tab_info, 'friends': tab_friends, 'photos': tab_photos, 'reels': tab_reels}
            for key, tab_el in tabs_dict.items():
                if key == tab_name:
                    tab_el.classes(add='text-blue-600 border-b-2 border-blue-600', remove='text-gray-500')
                else:
                    tab_el.classes(add='text-gray-500', remove='text-blue-600 border-b-2 border-blue-600')
            await render_content()

        with ui.row().classes('w-full px-4 md:px-12 mt-6 border-b border-gray-300 dark:border-gray-700 gap-6'):
            tab_todo = ui.label('Todo').classes('text-md font-bold text-blue-600 border-b-2 border-blue-600 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('todo')))
            tab_info = ui.label('Información').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('info')))
            tab_friends = ui.label('Amigos').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('friends')))
            tab_photos = ui.label('Fotos').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('photos')))
            tab_reels = ui.label('Reels').classes('text-md font-bold text-gray-500 hover:text-gray-800 pb-2 cursor-pointer').on('click', lambda: asyncio.create_task(change_tab('reels')))

        await render_content()