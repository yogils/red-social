from nicegui import ui, app
from core.api import api_get, api_post
from core.theme import app_header, apply_theme

@ui.page('/post/{post_id}')
async def post_detail_page(post_id: int):
    apply_theme()
    if 'token' not in app.storage.user:
        ui.navigate.to('/')
        return
    current_user_id = app.storage.user.get('user_id')
    user_email = app.storage.user.get('email', 'U')

    app_header('Publicación')

    with ui.column().classes('w-full max-w-2xl mx-auto p-4'):
        
        res_posts = await api_get("/users/posts", params={"user_id": current_user_id})
        post = None
        if res_posts.status_code == 200:
            for p in res_posts.json():
                if p['id'] == post_id:
                    post = p
                    break
        
        if not post:
            ui.label('Publicación no encontrada.').classes('text-center text-gray-500 mt-10')
            return

        with ui.card().classes('w-full bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-0 overflow-hidden mb-6'):
            with ui.row().classes('items-center p-4 w-full'):
                res_p = await api_get(f"/users/profiles/{post['author_id']}")
                if res_p.status_code == 200 and res_p.json().get('profile_picture_url'):
                    ui.image(f"http://localhost:8000{res_p.json()['profile_picture_url']}").classes('w-10 h-10 rounded-full object-cover mr-3')
                else:
                    ui.avatar(post['author_name'][0].upper(), color='primary', text_color='white', size='md').classes('mr-3')
                
                with ui.column().classes('gap-0'):
                    ui.link(post['author_name'], f"/profile/{post['author_id']}").classes('font-bold text-sm text-gray-900 dark:text-white no-underline hover:underline')
                    ui.label(post['created_at'][:16].replace('T', ' ')).classes('text-xs text-gray-500')
            
            if post['content']:
                ui.label(post['content']).classes('px-4 pb-3 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap')
            
            if post.get('image_url'):
                ui.image(f"http://localhost:8000{post['image_url']}").classes('w-full object-cover')

        ui.label('Comentarios').classes('text-lg font-bold text-gray-900 dark:text-white mb-2 px-2')
        
        comments_container = ui.column().classes('w-full mb-4')
        
        async def load_comments():
            comments_container.clear()
            res = await api_get(f"/users/posts/{post_id}/comments")
            if res.status_code == 200:
                with comments_container:
                    comments = res.json()
                    if not comments:
                        ui.label('No hay comentarios aún. ¡Sé el primero en comentar!').classes('text-gray-500 text-sm px-2')
                    for c in comments:
                        with ui.row().classes('w-full items-start gap-3 p-3 border-b border-gray-100 dark:border-gray-700'):
                            ui.avatar(c['author_name'][0].upper(), color='secondary', text_color='white', size='sm')
                            with ui.column().classes('gap-0'):
                                ui.label(c['author_name']).classes('font-bold text-xs text-gray-800 dark:text-gray-200')
                                ui.label(c['content']).classes('text-sm text-gray-600 dark:text-gray-300')
        
        await load_comments()

        with ui.row().classes('w-full items-center gap-2 px-2'):
            new_comment = ui.input(placeholder='Escribe un comentario...').props('outlined dense').classes('flex-grow')
            
            async def send_comment():
                if new_comment.value.strip():
                    await api_post(f"/users/posts/{post_id}/comments", json={
                        "author_id": current_user_id,
                        "author_name": user_email,
                        "content": new_comment.value
                    })
                    new_comment.value = ''
                    await load_comments()
            
            new_comment.on('keydown.enter', lambda: send_comment())
            ui.button('Enviar', on_click=send_comment).props('unelevated rounded color=primary')