import asyncio
import httpx
from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/feed')
async def feed_page():
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')
    user_email = app.storage.user.get('email', 'U')

    app_header('Red Social UNAL')

    with ui.column().classes('w-full max-w-xl mx-auto p-4 pb-20'):
        
        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6'):
            with ui.row().classes('w-full items-center gap-3'):
                ui.avatar(user_email[0].upper(), color='primary', text_color='white', size='md')
                new_post_text = ui.input(placeholder="¿Qué está pasando en la UNAL?").classes('flex-grow').props('borderless dense')
            
            preview_container = ui.column().classes('w-full mt-2 hidden')
            
            uploaded_image = {'url': None}
            
            async def handle_upload(e):
                file_bytes = await e.file.read()
                res = await api_post("/users/upload", files={'file': (e.file.name, file_bytes, e.file.content_type)})
                if res.status_code == 200:
                    uploaded_image['url'] = res.json()['image_url']
                    preview_container.clear()
                    preview_container.classes(remove='hidden')
                    with preview_container:
                        ui.image(f"http://localhost:8000{uploaded_image['url']}").classes('w-full max-h-64 object-cover rounded-lg border border-gray-200')
                    ui.notify('Imagen lista para publicar', color='positive')

            with ui.row().classes('w-full justify-between items-center mt-4 pt-3 border-t border-gray-100 dark:border-gray-700'):
                
                with ui.row().classes('items-center gap-2 cursor-pointer').on('click', lambda: uploader.run_method('pickFiles')):
                    ui.icon('photo_camera', size='md').classes('text-green-500')
                    ui.label('Foto').classes('text-sm font-medium text-gray-600 dark:text-gray-300')
                uploader = ui.upload(on_upload=handle_upload, auto_upload=True).props('accept=".jpg,.png,.jpeg"').classes('hidden')
                
                async def publish():
                    if not new_post_text.value and not uploaded_image['url']:
                        ui.notify('Escribe algo o sube una imagen', color='warning')
                        return
                    res = await api_post("/users/posts", json={
                        "author_id": current_user_id, "author_name": user_email,
                        "content": new_post_text.value or "", "image_url": uploaded_image['url']
                    })
                    if res.status_code == 200:
                        ui.navigate.to('/feed')

                ui.button('Publicar', on_click=publish).props('unelevated rounded color=primary text-weight-bold px-6')

        with ui.row().classes('w-full items-center justify-between mb-4 px-2'):
            ui.label('Publicaciones').classes('text-lg font-bold text-gray-900 dark:text-white')
            filter_switch = ui.switch('Solo amigos').props('color=primary')
        
        posts_container = ui.column().classes('w-full')
        
        async def load_posts():
            posts_container.clear()
            only_friends = filter_switch.value
            res = await api_get("/users/posts", params={"user_id": current_user_id, "only_friends": only_friends})
            if res.status_code == 200:
                posts = res.json()
                with posts_container:
                    if not posts:
                        ui.label('No hay publicaciones para mostrar.').classes('text-gray-500 text-center w-full mt-8')
                    for post in posts:
                        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-0 overflow-hidden mb-4'):
                            
                            with ui.row().classes('items-center p-4 w-full'):
                                res_p = await api_get(f"/users/profiles/{post['author_id']}")
                                if res_p.status_code == 200 and res_p.json().get('profile_picture_url'):
                                    ui.image(f"http://localhost:8000{res_p.json()['profile_picture_url']}").classes('w-10 h-10 rounded-full object-cover mr-3')
                                else:
                                    ui.avatar(post['author_name'][0].upper(), color='primary', text_color='white', size='md').classes('mr-3')
                                
                                with ui.column().classes('gap-0 flex-grow'):
                                    ui.link(post['author_name'], f"/profile/{post['author_id']}").classes('font-bold text-sm text-gray-900 dark:text-white no-underline hover:underline')
                                    ui.label(post['created_at'][:16].replace('T', ' ')).classes('text-xs text-gray-500')
                                
                                if post['author_id'] == current_user_id:
                                    async def delete_post(p_id=post['id']):
                                        async with httpx.AsyncClient() as client:
                                            await client.delete(
                                                f"http://gateway:8000/users/posts/{p_id}?user_id={current_user_id}",
                                                headers={"Authorization": f"Bearer {app.storage.user['token']}"}
                                            )
                                        ui.notify('Publicación eliminada', color='warning')
                                        await load_posts()
                                    
                                    ui.button(icon='delete', on_click=delete_post).props('flat round color=red size=sm no-caps')
                            
                            if post['content']:
                                ui.label(post['content']).classes('px-4 pb-3 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap')
                            
                            if post.get('image_url'):
                                ui.image(f"http://localhost:8000{post['image_url']}").classes('w-full object-cover')
                                
                            with ui.row().classes('w-full px-2 py-1 border-t border-gray-100 dark:border-gray-700 items-center justify-between'):
                                
                                with ui.row().classes('w-full'):
                                    like_color = 'red' if post['user_reaction'] == 'like' else 'gray-500'
                                    ui.button(f"{post['likes_count']}", icon='thumb_up', on_click=lambda p=post: handle_reaction(p['id'], 'like')).props(f'flat round color={like_color} size=sm no-caps')
                                    
                                    dislike_color = 'blue' if post['user_reaction'] == 'dislike' else 'gray-500'
                                    ui.button(f"{post['dislikes_count']}", icon='thumb_down', on_click=lambda p=post: handle_reaction(p['id'], 'dislike')).props(f'flat round color={dislike_color} size=sm no-caps')

                                    async def go_to_post(p_id=post['id']):
                                        ui.navigate.to(f'/post/{p_id}')

                                    ui.button(f"{post.get('comments_count', 0)}", icon='comment', on_click=go_to_post).props('flat round color=gray-500 size=sm no-caps')

                                async def copy_link(p_id=post['id']):
                                    ui.clipboard.write(f"http://localhost:3000/feed#post-{p_id}")
                                    ui.notify('¡Enlace copiado!', color='positive')
                                
                                ui.button('Compartir', icon='share', on_click=copy_link).props('flat round color=gray-500 size=sm no-caps')

        async def handle_reaction(post_id, r_type):
            await api_post(f"/users/posts/{post_id}/react?user_id={current_user_id}", json={"reaction_type": r_type})
            await load_posts()

        filter_switch.on_value_change(lambda e: asyncio.create_task(load_posts()))
        await load_posts()