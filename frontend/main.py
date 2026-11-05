from nicegui import ui, app
from pages import auth, feed, friends, chat, profile, notifications, post_detail, settings

app.add_static_files('/static', 'static')

ui.run(title="Red UNAL", storage_secret="super-secret-unal-key", port=3000, reload=False, show=False)