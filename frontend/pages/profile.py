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

    with ui.column().classes('w-full max-w-2xl mx-auto p-4 mt-4'):
        res = await api_get(f"/users/profiles/{current_user_id}")
        profile_data = res.json() if res.status_code == 200 else {}

        with ui.card().classes('w-full p-6 shadow-lg rounded-xl'):
            ui.label('Editar mi Perfil').classes('text-h5 font-bold mb-4')
            
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                if profile_data.get('profile_picture_url'):
                    ui.image(f"http://localhost:8000{profile_data['profile_picture_url']}").classes('w-24 h-24 rounded-full object-cover')
                else:
                    ui.avatar(app.storage.user.get('email', 'U')[0].upper(), color='primary', text_color='white', size='xl')

                async def handle_pfp(e):
                    file_bytes = await e.file.read()
                    res_up = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                    if res_up.status_code == 200:
                        img_url = res_up.json()['image_url']
                        await api_post(f"/users/profiles/{current_user_id}/picture?image_url={img_url}")
                        ui.navigate.to('/myprofile')

                ui.upload(on_upload=handle_pfp, label='Cambiar Foto', auto_upload=True).props('accept=".jpg,.png,.jpeg" flat')
            
            career_input = ui.input('Carrera', value=profile_data.get('career', '')).classes('w-full').props('outlined')
            bio_input = ui.textarea('Biografía corta', value=profile_data.get('bio', '')).classes('w-full').props('outlined')

            async def save_profile():
                await api_post(f"/users/profiles/{current_user_id}/update", json={
                    "career": career_input.value,
                    "bio": bio_input.value
                })
                ui.notify('Perfil actualizado', color='positive')
                ui.navigate.to('/myprofile')

            ui.button('Guardar Cambios', on_click=save_profile).props('color=primary rounded').classes('w-full mt-4')

        ui.label(f"Mi cuenta: {app.storage.user.get('email')}").classes('text-center mt-4 text-gray-500')


@ui.page('/profile/{user_id}')
async def user_profile(user_id: int):
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')

    app_header('Perfil de Usuario')

    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        res_profile = await api_get(f"/users/profiles/{user_id}")
        pfp_url = None
        career = None
        bio = None
        
        if res_profile.status_code == 200:
            data = res_profile.json()
            pfp_url = data.get('profile_picture_url')
            career = data.get('career')
            bio = data.get('bio')
        
        with ui.card().classes('w-full p-6 items-center text-center mb-6 mt-4 shadow-lg rounded-xl'):
            if pfp_url:
                ui.image(f"http://localhost:8000{pfp_url}").classes('w-32 h-32 rounded-full object-cover mx-auto')
            else:
                ui.avatar(f"U{user_id}", color='primary', text_color='white', size='xl').classes('mx-auto')
            
            ui.label(f"Usuario {user_id}").classes('text-h4 font-bold mt-4')
            
            if career:
                ui.label(career).classes('text-h6 text-primary')
            
            if bio:
                ui.label(bio).classes('text-gray-600 mt-2 italic')

        if user_id != current_user_id:
            ui.button('Enviar Mensaje', on_click=lambda: ui.navigate.to(f'/chat?user_id={user_id}')).props('color=primary outline rounded').classes('w-full mb-6')
        
        ui.separator()
        ui.label('Publicaciones').classes('text-h5 font-bold mt-4')

        posts_container = ui.column().classes('w-full')
        
        async def load_user_posts():
            posts_container.clear()
            res = await api_get("/users/posts", params={"user_id": current_user_id})
            if res.status_code == 200:
                posts = [p for p in res.json() if p['author_id'] == user_id]
                with posts_container:
                    if not posts:
                        ui.label('Este usuario no tiene publicaciones').classes('text-gray-500 text-center w-full mt-4')
                    for post in posts:
                        with ui.card().classes('w-full mt-4 shadow-md rounded-xl p-0 overflow-hidden'):
                            if post.get('image_url'):
                                ui.image(f"http://localhost:8000{post['image_url']}").classes('w-full max-h-96 object-cover')
                            with ui.column().classes('p-4 w-full'):
                                ui.label(post['content']).classes('whitespace-pre-wrap text-base')
                                ui.label(post['created_at'][:16].replace('T', ' ')).classes('text-xs text-gray-400 mt-2')

        await load_user_posts()