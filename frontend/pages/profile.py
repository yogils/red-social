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

    app_header('Mi Perfil')

    with ui.column().classes('w-full max-w-5xl mx-auto p-0 pb-10'):
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

        with ui.row().classes('w-full px-4 md:px-12 mt-6 gap-6'):
            with ui.column().classes('w-full md:w-1/3 gap-4'):
                with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4'):
                    ui.label('Información').classes('text-lg font-bold mb-2 text-gray-900 dark:text-white')
                    ui.label(f"Carrera: {profile_data.get('career', 'No especificada')}").classes('text-sm text-gray-600 dark:text-gray-300')
                    if profile_data.get('bio'):
                        ui.separator().classes('my-2')
                        ui.label(f"Bio: {profile_data.get('bio')}").classes('text-sm text-gray-600 dark:text-gray-300')
                        
                    career_input = ui.input('Carrera', value=profile_data.get('career', '')).props('outlined dense').classes('w-full mt-2')
                    bio_input = ui.textarea('Biografía corta', value=profile_data.get('bio', '')).props('outlined dense rows=2').classes('w-full')

                    async def save_profile():
                        await api_post(f"/users/profiles/{current_user_id}/update", json={
                            "career": career_input.value,
                            "bio": bio_input.value
                        })
                        ui.notify('Perfil actualizado correctamente', color='positive')
                        ui.navigate.to('/myprofile')

                    ui.button('Guardar Datos', on_click=save_profile).props('unelevated rounded color=primary').classes('w-full mt-2')

            with ui.column().classes('w-full md:w-2/3 gap-4'):
                ui.label('Mis Publicaciones').classes('text-lg font-bold text-gray-900 dark:text-white')
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


@ui.page('/profile/{user_id}')
async def user_profile(user_id: int):
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Perfil de Usuario')

    with ui.column().classes('w-full max-w-5xl mx-auto p-0 pb-10'):
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

        with ui.row().classes('w-full px-4 md:px-12 mt-6 gap-6'):
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