from nicegui import ui, app
from core.api import api_post, api_get
from core.theme import apply_theme

def show_register():
    with ui.card().classes('w-full max-w-md p-8 rounded-2xl shadow-xl bg-white dark:bg-gray-900'):
        with ui.row().classes('w-full justify-center mb-4'):
            ui.image('/static/logo_unal.png').classes('w-40 h-auto object-contain')

        ui.label("Únete a la Red UNAL").classes('text-2xl font-bold text-center mb-1 text-gray-900 dark:text-white')
        ui.label("Crea tu cuenta institucional").classes('text-center text-sm text-gray-500 mb-6')
        
        email = ui.input("Correo institucional").props('outlined rounded dense').classes('w-full mb-4').on('keydown.enter', lambda: handle_register())
        full_name = ui.input("Nombre completo").props('outlined rounded dense').classes('w-full mb-4')
        password = ui.input("Contraseña", password=True, password_toggle_button=True).props('outlined rounded dense').classes('w-full mb-6')
        
        async def handle_register():
            res = await api_post("/auth/register", json={
                "email": email.value, "full_name": full_name.value, "password": password.value
            })
            if res.status_code == 200:
                ui.notify("¡Registro exitoso!", color="positive")
                ui.navigate.to('/')
            else:
                ui.notify(f"Error: {res.json().get('detail', 'Error')}", color="negative")

        ui.button("Registrarme", on_click=handle_register).props('unelevated rounded color=primary').classes('w-full py-2 text-base font-semibold')
        
        ui.label("¿Ya tienes cuenta?").classes('text-center text-sm text-gray-500 mt-6')
        ui.link("Inicia sesión", '/').classes('text-center text-sm text-blue-600 font-bold no-underline block')

def show_login():
    with ui.card().classes('w-full max-w-md p-8 rounded-2xl shadow-xl bg-white dark:bg-gray-900'):
        with ui.row().classes('w-full justify-center mb-4'):
            ui.image('/static/logo_unal.png').classes('w-40 h-auto object-contain')
        
        ui.label("Red Social UNAL").classes('text-2xl font-bold text-center mb-1 text-gray-900 dark:text-white')
        ui.label("Conecta con tu comunidad universitaria").classes('text-center text-sm text-gray-500 mb-6')
        
        email = ui.input("Correo institucional").props('outlined rounded dense').classes('w-full mb-4')
        password = ui.input("Contraseña", password=True, password_toggle_button=True).props('outlined rounded dense').classes('w-full mb-6')
        
        async def handle_login():
            res = await api_post("/auth/login", data={"username": email.value, "password": password.value})
            if res.status_code == 200:
                data = res.json()
                app.storage.user['token'] = data["access_token"]
                app.storage.user['email'] = email.value
                
                verify_res = await api_get("/auth/verify")
                if verify_res.status_code == 200:
                    app.storage.user['user_id'] = verify_res.json()["user_id"]
                
                ui.notify("Bienvenido de nuevo", color="positive")
                ui.navigate.to('/feed')
            else:
                ui.notify("Credenciales incorrectas", color="negative")

        password.on('keydown.enter', lambda: handle_login())

        ui.button("Iniciar Sesión", on_click=handle_login).props('unelevated rounded color=primary').classes('w-full py-2 text-base font-semibold')
        
        ui.label("¿No tienes cuenta?").classes('text-center text-sm text-gray-500 mt-6')
        ui.link("Crea una cuenta nueva", '/register').classes('text-center text-sm text-blue-600 font-bold no-underline block')

@ui.page('/')
def index():
    apply_theme() 
    if app.storage.user.get('token'):
        ui.navigate.to('/feed')
        return
    
    with ui.column().classes('w-full min-h-screen items-center justify-center bg-unal p-4'):
        show_login()

@ui.page('/register')
def register_page():
    apply_theme()
    with ui.column().classes('w-full min-h-screen items-center justify-center bg-unal p-4'):
        show_register()