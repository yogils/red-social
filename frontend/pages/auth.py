from nicegui import ui, app
from core.api import api_post, api_get
from core.theme import apply_theme

def show_register():
    card_container = ui.column().classes('w-full max-w-2xl p-8 rounded-2xl shadow-xl bg-white dark:bg-gray-900')
    
    with card_container:
        with ui.row().classes('w-full justify-center mb-4'):
            ui.image('/static/logo_unal.png').classes('w-24 h-auto object-contain')

        ui.label("Únete a la Red UNAL").classes('text-2xl font-bold text-center mb-1 text-gray-900 dark:text-white')
        ui.label("Completa tus datos institucionales").classes('text-center text-sm text-gray-500 mb-6')
        
        ui.label("Datos Personales").classes('text-lg font-bold mt-4 mb-2 text-gray-800 dark:text-gray-200 border-b pb-1 w-full')
        
        with ui.row().classes('w-full gap-2'):
            first_name = ui.input("Nombre").props('outlined dense').classes('flex-grow')
            last_name = ui.input("Primer apellido").props('outlined dense').classes('flex-grow')
        with ui.row().classes('w-full gap-2'):
            second_last_name = ui.input("Segundo apellido (opcional)").props('outlined dense').classes('flex-grow')
            birth_date = ui.input("Fecha de nacimiento (AAAA-MM-DD)").props('outlined dense').classes('flex-grow')
            
        with ui.row().classes('w-full gap-2'):
            document_type = ui.select(['CC', 'TI', 'CE', 'Pasaporte'], label='Tipo de Documento').props('outlined dense').classes('flex-grow')
            document_number = ui.input("Número de Documento").props('outlined dense').classes('flex-grow')
            
        with ui.row().classes('w-full gap-2'):
            city = ui.input("Ciudad de Residencia").props('outlined dense').classes('flex-grow')
            phone = ui.input("Número de Teléfono").props('outlined dense').classes('flex-grow')

        ui.label("Datos de Cuenta").classes('text-lg font-bold mt-6 mb-2 text-gray-800 dark:text-gray-200 border-b pb-1 w-full')
        
        with ui.row().classes('w-full gap-2'):
            username = ui.input("Nombre de Usuario").props('outlined dense').classes('flex-grow')
            email = ui.input("Correo institucional").props('outlined dense').classes('flex-grow')
        
        with ui.row().classes('w-full gap-2'):
            password = ui.input("Contraseña", password=True, password_toggle_button=True).props('outlined dense').classes('flex-grow')
            confirm_password = ui.input("Confirmar Contraseña", password=True, password_toggle_button=True).props('outlined dense').classes('flex-grow')
        
        ui.label("Datos Académicos").classes('text-lg font-bold mt-6 mb-2 text-gray-800 dark:text-gray-200 border-b pb-1 w-full')
        
        with ui.row().classes('w-full gap-2'):
            faculty = ui.select(
                ['Ingeniería', 'Ciencias', 'Medicina', 'Derecho', 'Ciencias Económicas', 'Artes', 'Ciencias Humanas', 'Agrarias', 'Veterinaria', 'Enfermería', 'Odontología', 'Otra'], 
                label='Facultad'
            ).props('outlined dense').classes('flex-grow')
            career = ui.input("Carrera").props('outlined dense').classes('flex-grow')

        ui.label("Autorizaciones").classes('text-lg font-bold mt-6 mb-2 text-gray-800 dark:text-gray-200 border-b pb-1 w-full')
        accept_terms = ui.checkbox("Acepto los términos y condiciones")
        accept_data_policy = ui.checkbox("Acepto la política de tratamiento de datos")
        accept_commercial = ui.checkbox("Acepto recibir comunicaciones comerciales (opcional)")

        async def handle_register():
            if not all([first_name.value, last_name.value, birth_date.value, document_type.value, document_number.value, city.value, username.value, email.value, password.value, faculty.value, career.value]):
                ui.notify("Por favor completa todos los campos obligatorios", color="warning")
                return
            if password.value != confirm_password.value:
                ui.notify("Las contraseñas no coinciden", color="warning")
                return
            if not accept_terms.value or not accept_data_policy.value:
                ui.notify("Debes aceptar los términos y la política de datos", color="warning")
                return

            full_name = f"{first_name.value} {last_name.value} {second_last_name.value or ''}".strip()
            
            res = await api_post("/auth/register", json={
                "email": email.value, 
                "full_name": full_name,
                "first_name": first_name.value,
                "last_name": last_name.value,
                "second_last_name": second_last_name.value,
                "username": username.value,
                "birth_date": birth_date.value,
                "document_type": document_type.value,
                "document_number": document_number.value,
                "city": city.value,
                "phone": phone.value,
                "faculty": faculty.value,
                "career": career.value,
                "bio": "",
                "password": password.value,
                "accept_terms": accept_terms.value,
                "accept_data_policy": accept_data_policy.value,
                "accept_commercial": accept_commercial.value
            })
            
            if res.status_code == 200:
                card_container.clear()
                with card_container:
                    ui.icon('check_circle', size='4rem').classes('mx-auto text-green-500 mb-4')
                    ui.label("¡Registro Exitoso!").classes('text-2xl font-bold text-center text-gray-900 dark:text-white mb-2')
                    ui.label("Tu cuenta ha sido creada correctamente. Ya puedes iniciar sesión con tu correo institucional.").classes('text-center text-gray-600 dark:text-gray-400 mb-6')
                    ui.button("Ir a Iniciar Sesión", on_click=lambda: ui.navigate.to('/')).props('unelevated rounded color=primary').classes('w-full')
            else:
                ui.notify(f"Error: {res.json().get('detail', 'Error')}", color="negative")

        ui.button("Registrarme", on_click=handle_register).props('unelevated rounded color=primary').classes('w-full py-2 text-base font-semibold mt-6')
        
        ui.label("¿Ya tienes cuenta?").classes('text-center text-sm text-gray-500 mt-4')
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