import arcade, random
import arcade.gui

TITULO = "Laberinto de Escape"

SPRITE_IMAGEN_VALOR = 13

SPRITE_JUGADOR_ESCALADO = 3
SPRITE_TILES_ESCALADO = 4
SPRITE_MONEDAS_ESCALADO = 4

SPRITE_SIZE = int(SPRITE_IMAGEN_VALOR * SPRITE_TILES_ESCALADO)

VENTANA_GRID_ANCHO = 22
VENTANA_GRID_ALTO = 14

VENTANA_ANCHO = SPRITE_SIZE * VENTANA_GRID_ANCHO
VENTANA_ALTO = SPRITE_SIZE * VENTANA_GRID_ALTO

JUGADOR_VELOCIDAD = 7

TIEMPO_LIMITE = 180

PUNTAJE = 1100
VIDAS = 10
MASCOTAS = 0
NIVEL = 1


class VistaInicio(arcade.View):
    """Clase que maneja el menú de inicio"""

    def __init__(self):

        super().__init__()

        self.fondo = None
        self.tiempo_titulo = 3.0
        self.muestra_instrucciones = False

        global NIVEL
        NIVEL = 1

        # Cargar el sonido para el menú de inicio
        self.menu_musica = arcade.Sound(r"./snd/inicio.ogg")
        self.menu_musica.play(volume=0.5)  # Reproducir la música con un volumen del 50%
        
        
        # --------- Botones ---------------------
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Crea el boton para ver instrucciones
        self.v_box = arcade.gui.UIBoxLayout(vertical= False)
        ui_flatbutton = arcade.gui.UIFlatButton(text="Instrucciones", width=200)
        self.v_box.add(ui_flatbutton.with_space_around(right=20))

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            vista_intrucciones = VistaIntrucciones()
            self.window.show_view(vista_intrucciones)

        # Crea el boton para iniciar el juego
        ui_flatbutton_v2 = arcade.gui.UIFlatButton(text="Iniciar juego", width=200)
        self.v_box.add(ui_flatbutton_v2.with_space_around(left=20))

        @ui_flatbutton_v2.event("on_click")
        def on_click_flatbutton(event):
            vista_laberinto = VistaLaberinto()
            self.window.show_view(vista_laberinto)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x= 0,
                align_y= 40,
                child=self.v_box)
        )
        
    def on_show_view(self):
        """Se ejecuta al cambiar a esta vista"""
        self.fondo = arcade.load_texture(r"./img/gui/1_inicio.png")

    def on_draw(self):
        """Dibuja el menú"""
        self.clear()
        arcade.draw_texture_rectangle(VENTANA_ANCHO // 2, VENTANA_ALTO // 2, VENTANA_ANCHO, VENTANA_ALTO, self.fondo)
        self.manager.draw()


class VistaIntrucciones(arcade.View):
    """Clase que maneja las intrucciones de inicio"""

    def __init__(self):
        super().__init__()
        # Cargar el sonido para el menú de inicio
        self.menu_musica = arcade.Sound(r"./snd/inicio.ogg")
        self.menu_musica.play(volume=0.5)  # Reproducir la música con un volumen del 50%

        # --------- Botones ---------------------
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Crea el boton para ver instrucciones
        self.v_box = arcade.gui.UIBoxLayout(align= "left")
        ui_flatbutton = arcade.gui.UIFlatButton(text="Volver al Inicio", width=200)
        self.v_box.add(ui_flatbutton)

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            vista_inicio = VistaInicio()
            self.window.show_view(vista_inicio)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                align_x= -400,
                align_y= 200,
                child=self.v_box)
        )

    def on_show_view(self):
        """Muestra la imagen de instrucciones"""
        self.fondo = arcade.load_texture(r"./img/gui/2_intrucciones.png")

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rectangle(
            VENTANA_ANCHO / 2,
            VENTANA_ALTO / 2,
            VENTANA_ANCHO,
            VENTANA_ALTO,
            self.fondo,
        )
        self.manager.draw()


class VistaLaberinto(arcade.View):
    """ Main Window """

    def __init__(self):
        """ Crea las variables """

        # Init the parent class
        super().__init__()

        # Contadores
        global PUNTAJE, VIDAS, MASCOTAS, NIVEL

        self.Laberinto = None
        self.escena = None
        
        self.pausa = False

        # Motor físico
        self.motor_fisico = None

        # Jugador
        self.jugador_sprite = None

        # Teclado 
        self.arriba_tecla = False
        self.abajo_tecla = False
        self.izquierda_tecla = False
        self.derecha_tecla = False

        # Camara
        self.camara = None
        self.gui_camara = None

        # Advertencia
        self.advertencia = False

        # Reseteos
        self.reset_puntaje = True
        self.reset_vida = False
        self.reset_mascotas = False

        # mapa finalización
        self.termina = 0

        # Juego pausado
        self.pausa = False

        # Temporizador
        self.tiempo_total = 0.0
        self.tiempo_texto = arcade.Text(
            text="00:00:00",
            start_x=490,
            start_y=VENTANA_ALTO - 50,
            color=arcade.color.LIGHT_SKY_BLUE,
            font_size=18,
            anchor_x="center",
        )
        self.tiempo_transcurrido = 0.0

        # Color de fondo
        arcade.set_background_color(arcade.color.BLACK)

        
        # Carga los sonidos
        self.monedas_sonido = arcade.load_sound(r"./snd/moneda.wav")
        self.enemigo_sonido = arcade.load_sound(r"./snd/enemigo.wav")
        self.trampa_sonido = arcade.load_sound(r"./snd/trampa.wav")
        self.extra_sonido = arcade.load_sound(r"./snd/extra.wav")
        self.objeto_sonido = arcade.load_sound(r"./snd/objetos.wav")

        self.lista_terror = []
        for img in range(1, 14):
            self.lista_terror.append(f"./img/terror/terror_{img}.jpg")
        
        # --------- Botones ---------------------
        # Create and enable the UIManager
        self.boton_advertencia = arcade.gui.UIManager()
        self.boton_advertencia.enable()

        # Boton advertencia
        mensaje = arcade.gui.UIMessageBox(
            width=300,
            height=200,
            message_text=(
                "ADVERTENCIA:"
                "No puedes pasar al siguiente nivel sin tener las 3 mascotas!!!"
            ),
            buttons=["Aceptar"]
        )
        self.boton_advertencia.add(mensaje)

        
        self.manager_v2 = arcade.gui.UIManager()
        self.manager_v2.enable()

        # Crea el boton para reiniciar el juego
        self.v_box = arcade.gui.UIBoxLayout(vertical= False)
        ui_flatbutton = arcade.gui.UIFlatButton(text="Reiniciar", width=150)
        self.v_box.add(ui_flatbutton.with_space_around(right=20))

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            self.pausa = True
            vista_reinicio = VistaReinicio(self)
            self.window.show_view(vista_reinicio)

        self.manager_v2.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x= -490,
                align_y= 320,
                child=self.v_box)
        )
   
    def setup(self):
        """ Configurar todo con el juego """

        global PUNTAJE, VIDAS, MASCOTAS

        self.camara = arcade.Camera(self.window.width, self.window.height)
        self.gui_camara = arcade.Camera(self.window.width, self.window.height)

        PUNTAJE = 1100
        MASCOTAS = 0
        VIDAS = 10

        self.tiempo_total = 0.0

        # Carga el Laberinto mapa
        map_name = (f"./map/mapa{NIVEL}.tmx")

        self.Laberinto = arcade.load_tilemap(map_name, SPRITE_TILES_ESCALADO)
        self.escena = arcade.Scene.from_tilemap(self.Laberinto)

        # Llevar la cuenta de la puntuación, vidas y mascotas
        if self.reset_puntaje:
            PUNTAJE = 1100 # Puntaje inicial
        self.reset_puntaje = True

        if self.reset_vida:
            VIDAS = 10 # Vidas iniciales
        self.reset_vida = True

        if self.reset_mascotas:
            MASCOTAS = 0 # Mascotas inicial
        self.reset_mascotas = False

        # Crea el sprite del jugador
        if not self.jugador_sprite:
            self.jugador_sprite = self.create_player_sprite()

        inicializa_jugador = self.escena["Inicio"]
        inicializa_jugador_xy = inicializa_jugador[0]

        self.jugador_sprite.center_x = inicializa_jugador_xy.center_x
        self.jugador_sprite.center_y = inicializa_jugador_xy.center_y

        # Añade el jugador a la escena
        self.escena.add_sprite("Player", self.jugador_sprite)

        # Crea el 'physics engine'
        self.motor_fisico = arcade.PhysicsEngineSimple(
            self.jugador_sprite, walls=self.escena["Laberinto"]
        )

    def create_player_sprite(self):
        """ Crea el sprite animado del jugador 
            Retorna: El sprite del jugador configurado correctamente """

        # Where are the player images stored?
        texture_path = "./img/sprite/"

        # Set up the appropriate textures
        lados_paths =  [texture_path + "camina_der1.png",
                        texture_path + "camina_der2.png",
                        texture_path + "camina_der3.png"]
        atras_paths =  [texture_path + "atras1.png",
                        texture_path + "atras2.png",
                        texture_path + "atras3.png"]
        frente_paths = [texture_path + "frente_1.png",
                        texture_path + "frente2.png",
                        texture_path + "frente3.png"]
        quieto_path = texture_path + "frente_1.png"

        # Load them all now
        camina_derecha_lista = [arcade.load_texture(texture) for texture in lados_paths]
        camina_izquierda_lista = [arcade.load_texture(texture, mirrored=True) for texture in lados_paths]
        camina_atras_lista = [arcade.load_texture(texture) for texture in atras_paths]
        camina_frente_lista = [arcade.load_texture(texture) for texture in frente_paths]
        quieto_derecha_lista = [arcade.load_texture(quieto_path)]
        quieto_izquierda_lista = [arcade.load_texture(quieto_path, mirrored=True)]
        # Create the sprite
        player = arcade.AnimatedWalkingSprite()

        # Add the proper textures
        player.stand_right_textures = quieto_derecha_lista
        player.stand_left_textures = quieto_izquierda_lista
        player.walk_left_textures = camina_izquierda_lista
        player.walk_right_textures = camina_derecha_lista
        player.walk_up_textures = camina_atras_lista
        player.walk_down_textures = camina_frente_lista

        # Set the player defaults
        player.state = arcade.FACE_DOWN

        # Set the initial texture
        player.texture = player.stand_right_textures[0]

        player.scale = SPRITE_JUGADOR_ESCALADO
        
        return player

    def on_show_view(self):
        self.setup()

    def update_player_speed(self):

        # Calcula la velocidad en base a la tecla presionada
        self.jugador_sprite.change_x = 0
        self.jugador_sprite.change_y = 0

        if self.arriba_tecla and not self.abajo_tecla:
            self.jugador_sprite.change_y = JUGADOR_VELOCIDAD
        elif self.abajo_tecla and not self.arriba_tecla:
            self.jugador_sprite.change_y = -JUGADOR_VELOCIDAD
        if self.izquierda_tecla and not self.derecha_tecla:
            self.jugador_sprite.change_x = -JUGADOR_VELOCIDAD
        elif self.derecha_tecla and not self.izquierda_tecla:
            self.jugador_sprite.change_x = JUGADOR_VELOCIDAD

    def on_key_press(self, key, modifiers):
        """Llamada cuando se presiona una tecla"""

        if key == arcade.key.UP or key == arcade.key.W:
            self.arriba_tecla = True
            self.update_player_speed()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.abajo_tecla = True
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.izquierda_tecla = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.derecha_tecla = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Llamada cuando el usuario suelta una tecla"""

        if key == arcade.key.UP or key == arcade.key.W:
            self.arriba_tecla = False
            self.update_player_speed()
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.abajo_tecla = False
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.izquierda_tecla = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.derecha_tecla = False
            self.update_player_speed()

    def center_camera_to_player(self, speed=0.2):
        ventana_centrada_x = self.camara.scale * (self.jugador_sprite.center_x - (self.camara.viewport_width / 2))
        ventana_centrada_y = self.camara.scale * (self.jugador_sprite.center_y - (self.camara.viewport_height / 2))
        if ventana_centrada_x < 0:
            ventana_centrada_x = 0
        if ventana_centrada_y < 0:
            ventana_centrada_y = 0
        jugador_centrado = (ventana_centrada_x, ventana_centrada_y)    

        self.camara.move_to(jugador_centrado, speed)
    
    def on_update(self, delta_time):
        """ Movimiento y lógica del juego """

        global PUNTAJE, VIDAS, MASCOTAS, NIVEL

        # Acumula el total del tiempo
        self.tiempo_total += delta_time
        # Calcula los minutos
        minutes = int(self.tiempo_total) // 60
        # Calcula los segundos
        seconds = int(self.tiempo_total) % 60
        # Calcula los milisegundos
        seconds_100s = int((self.tiempo_total - seconds) * 100)
        # crear una nueva cadena de texto para el temporizador
        self.tiempo_texto.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"

        # Verificar si se ha agotado el tiempo límite
        self.tiempo_transcurrido = int(self.tiempo_total)
        if self.tiempo_transcurrido >= TIEMPO_LIMITE:
            # Abre la ventana de "Game Over" cuando se agote el tiempo
            NIVEL = 1
            game_over = VistaGameOver()
            self.window.show_view(game_over)
            return
        # Reducir el puntaje gradualmente a lo largo del tiempo
        elif seconds == 59:
            PUNTAJE -= 10

        if PUNTAJE < 11:
            PUNTAJE = 11
            return PUNTAJE
        
        self.escena.update_animation(delta_time)
        self.motor_fisico.update()

        # Actualiza animaciones
        self.escena.update_animation(delta_time, ["Laberinto", "Enemigos", "Extra", "Mascotas", "Final", "Vidas"])

        # Monedas
        moneda_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Monedas"])
        for moneda in moneda_lista:
            # Eliminar monedas
            moneda.remove_from_sprite_lists()
            PUNTAJE += 3
            arcade.play_sound(self.monedas_sonido, volume=5)

        # Coronitas
        coronas_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Extra"])
        for corona in coronas_lista:
            # Eliminar coronas
            corona.remove_from_sprite_lists()
            PUNTAJE += 11
            arcade.play_sound(self.extra_sonido, volume=20)
        
        # Vidas
        vidas_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Vidas"])
        for vida in vidas_lista:
            # Eliminar vida
            vida.remove_from_sprite_lists()
            VIDAS += 1
            arcade.play_sound(self.extra_sonido, volume=20)
        
        # Objetos
        objetos_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena['Mascotas'])
        for objeto in objetos_lista:
            # Eliminar objeto
            objeto.remove_from_sprite_lists()
            # agregar al contador para pasar al siguiente nivel
            MASCOTAS += 1
            arcade.play_sound(self.objeto_sonido, volume=20)

        # Enemigos
        enemigos_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Enemigos"])
        for enemigo in enemigos_lista:
            enemigo.remove_from_sprite_lists()
            VIDAS -= 0.5
            arcade.play_sound(self.enemigo_sonido, volume=20)
            if VIDAS <= 0:
                # abre la ventana de game over si se le acaban las vidas
                NIVEL = 1
                game_over = VistaGameOver()
                self.window.show_view(game_over)
                return
        
        # Trampas
        trampas_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Trampas"])
        for trampa in trampas_lista:
            # Crear una variable para almacenar la imagen aleatoria
            trampa.remove_from_sprite_lists()
            VIDAS -= 2
            PUNTAJE -= 30
            imagen_aleatoria = random.choice(self.lista_terror)

            # Mostrar la imagen aleatoria en toda la pantalla
            arcade.set_background_color(arcade.color.BLACK)
            imagen_terror_sprite = arcade.Sprite(imagen_aleatoria)
            imagen_terror_sprite.set_position(
                self.jugador_sprite.center_x, self.jugador_sprite.center_y)
            self.escena.add_sprite("Imagen aleatoria", imagen_terror_sprite)

            # Ocultar la imagen aleatoria después de 3 segundos
            arcade.schedule(lambda delta_time: imagen_terror_sprite.remove_from_sprite_lists(), 0.5)

        if self.pausa:
            return
        
        # Final
        final_lista = arcade.check_for_collision_with_list(
            self.jugador_sprite, self.escena["Final"])
        for fin in final_lista:
            # Avanza al siguiente nivel
            if MASCOTAS == 3:

                self.reset_puntaje = False
                self.reset_vida = False
                self.reset_mascotas = False

                # Muestra la pantalla intermedia
                vista_intermedia = VistaNivel()
                self.window.show_view(vista_intermedia)
                return
            
            else:
                self.advertencia = True
        
        # Posiciona la cámara
        self.center_camera_to_player()

    def on_draw(self):
        """ Draw everything """
        
        self.clear()
        self.camara.use()
        self.escena.draw()
        
        # Activa la gui camara para on_draw
        self.gui_camara.use()

        # Dibuja un rectangulo arriba de la ventanapara los textos adicionales
        arcade.draw_rectangle_filled(
            self.window.width // 2, self.window.height - 25, self.window.width, 100, arcade.color.BLACK)
        
        score_text = f"Puntaje: {PUNTAJE}"
        arcade.draw_text(
            score_text,
            176,
            self.window.height - 50,
            arcade.csscolor.LIGHT_YELLOW,
            18,)
        
        self.tiempo_texto.draw() # 490

        vida_text = f"Vidas: {VIDAS}"
        if VIDAS < 2:
            arcade.draw_text(
                vida_text,
                616,
                self.window.height - 50,
                arcade.csscolor.ORANGE_RED,
                18,)
        else:
            arcade.draw_text(
                vida_text,
                616,
                self.window.height - 50,
                arcade.csscolor.WHITE,
                18,)

        mascotas_text = f"Mascotas: {MASCOTAS}"
        
        if MASCOTAS == 3:
            arcade.draw_text(
            mascotas_text,
            792,
            self.window.height - 50,
            arcade.csscolor.GREENYELLOW,
            18,)
        elif MASCOTAS < 3:
            arcade.draw_text(
            mascotas_text,
            792,
            self.window.height - 50,
            arcade.csscolor.WHITE,
            18,)
        
        if self.advertencia:
            self.boton_advertencia.draw()
        
        self.manager_v2.draw()


class VistaNivel(arcade.View):

    def __init__(self):
        super().__init__()
        self.intermediate_texture = arcade.load_texture(f"./img/gui/5_vista_nivel{NIVEL}.png")

        # --------- Botones ---------------------
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Crea el boton para volver al inicio
        self.v_box = arcade.gui.UIBoxLayout(vertical= False)
        ui_flatbutton = arcade.gui.UIFlatButton(text="Volver al Inicio", width=200)
        self.v_box.add(ui_flatbutton.with_space_around(right=20))

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            vista_inicio = VistaInicio()
            self.window.show_view(vista_inicio)

        # Crea el boton para continuar
        ui_flatbutton_v2 = arcade.gui.UIFlatButton(text="Continuar", width=200)
        self.v_box.add(ui_flatbutton_v2.with_space_around(left=20))

        @ui_flatbutton_v2.event("on_click")
        def on_click_flatbutton(event):
            # Continuar al siguiente nivel
            global NIVEL
            NIVEL += 1
            vista_juego = VistaLaberinto()

            if NIVEL >= 7:
                vista_inicio = VistaInicio() # abre la ventana de game over ya que no hay más niveles
                self.window.show_view(vista_inicio)
                return
            else:
                vista_juego.setup() # Carga el siguiente nivel

            self.window.show_view(vista_juego)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x= 0,
                align_y= -200,
                child=self.v_box)
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        # Dibuja la pantalla de nivel con opacidad
        arcade.set_viewport(0, VENTANA_ANCHO, 0, VENTANA_ALTO)
        arcade.draw_rectangle_filled(
            VENTANA_ANCHO / 2,
            VENTANA_ALTO / 2,
            VENTANA_ANCHO,
            VENTANA_ALTO,
            arcade.make_transparent_color(arcade.color.WHITE, transparency=150),  # Opacidad
        )
        arcade.draw_texture_rectangle(
            VENTANA_ANCHO // 2, VENTANA_ALTO // 2, VENTANA_ANCHO, VENTANA_ALTO, self.intermediate_texture)
        
        global PUNTAJE
        arcade.draw_rectangle_filled(
            self.window.width // 2, self.window.height // 2 + 60, self.window.width, 100, arcade.color.BLACK)
        arcade.draw_text(
            f"Puntaje: {PUNTAJE}",
            VENTANA_ANCHO // 2,
            VENTANA_ALTO // 2 + 50,
            arcade.color.WHITE_SMOKE,
            font_size=40,
            font_name= ("Impact", "arial"),
            anchor_x="center",
        )
        arcade.draw_text(
            f"Vidas: {VIDAS}",
            VENTANA_ANCHO - VENTANA_ANCHO // 6,
            VENTANA_ALTO // 2 + 50,
            arcade.color.WHITE_SMOKE,
            font_size=40,
            font_name= ("Impact", "arial"),
            anchor_x="center",
        )
        arcade.draw_text(
            f"Nivel: {NIVEL}",
            VENTANA_ANCHO // 6,
            VENTANA_ALTO // 2 + 50,
            arcade.color.WHITE_SMOKE,
            font_size=40,
            font_name= ("Impact", "arial"),
            anchor_x="center",
        )

        self.manager.draw()


class VistaReinicio(arcade.View):
    """Crea el menú de pausa"""

    def __init__(self, game_view):

        super().__init__()
        self.game_view = game_view

        # --------- Botones ---------------------
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Crea el boton para volver al inicio
        self.v_box = arcade.gui.UIBoxLayout(vertical= False)
        ui_flatbutton = arcade.gui.UIFlatButton(text="Volver al Inicio", width=200)
        self.v_box.add(ui_flatbutton.with_space_around(right=20))

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            vista_inicio = VistaInicio()
            self.window.show_view(vista_inicio)

        # Crea el boton para volver a jugar
        ui_flatbutton_v2 = arcade.gui.UIFlatButton(text="Volver a Jugar", width=200)
        self.v_box.add(ui_flatbutton_v2.with_space_around(left=20))

        @ui_flatbutton_v2.event("on_click")
        def on_click_flatbutton(event):
            vista_juego = VistaLaberinto()
            vista_juego.setup()
            self.window.show_view(vista_juego)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x= 0,
                align_y= -300,
                child=self.v_box)
        )

    def on_draw(self):
        """Dibuja la pantalla de reinicio y el juego de fondo con opacidad"""
        self.clear()
        
        # Dibuja el juego de fondo (VistaLaberinto)
        self.game_view.on_draw()
        
        # Dibuja la pantalla de reinicio con opacidad
        arcade.set_viewport(0, VENTANA_ANCHO, 0, VENTANA_ALTO)
        arcade.draw_rectangle_filled(
            VENTANA_ANCHO / 2,
            VENTANA_ALTO / 2,
            VENTANA_ANCHO,
            VENTANA_ALTO,
            arcade.make_transparent_color(arcade.color.WHITE, transparency=150),  # Opacidad
        )

        arcade.draw_text("Juego Reiniciado", 
                         VENTANA_ANCHO / 2, 
                         VENTANA_ALTO / 2,
                         arcade.color.BLACK, 
                         font_size=50, 
                         anchor_x="center",
                         font_name= ("Impact", "arial"))
                         
        self.manager.draw()


class VistaGameOver(arcade.View):
    """Clase que maneja el final del juego"""

    def __init__(self):
        super().__init__()

        # --------- Botones ---------------------
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Crea el boton para volver al inicio
        self.v_box = arcade.gui.UIBoxLayout(vertical= False)
        ui_flatbutton = arcade.gui.UIFlatButton(text="Volver al Inicio", width=200)
        self.v_box.add(ui_flatbutton.with_space_around(right=20))

        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            vista_inicio = VistaInicio()
            self.window.show_view(vista_inicio)

        # Crea el boton para volver a jugar
        ui_flatbutton_v2 = arcade.gui.UIFlatButton(text="Volver a Jugar", width=200)
        self.v_box.add(ui_flatbutton_v2.with_space_around(left=20))

        @ui_flatbutton_v2.event("on_click")
        def on_click_flatbutton(event):
            vista_juego = VistaLaberinto()
            self.window.show_view(vista_juego)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                align_x= 0,
                align_y= -200,
                child=self.v_box)
        )

    def on_show_view(self):
        """Llamada al cambiar a esta vista"""
        self.fondo = arcade.load_texture(r"./img/gui/3_game_over.png")
        self.game_over_sound = arcade.Sound(r"./snd/final.ogg")
        self.game_over_sound.play()

    def on_draw(self):
        """on_draw la visión general del juego"""
        self.clear()
        arcade.draw_texture_rectangle(VENTANA_ANCHO // 2, VENTANA_ALTO // 2, VENTANA_ANCHO, VENTANA_ALTO, self.fondo)
        
        global PUNTAJE, VIDAS, MASCOTAS
        arcade.draw_text(
            f"Puntaje: {PUNTAJE}",
            VENTANA_ANCHO / 2  - VENTANA_ANCHO / 6,
            VENTANA_ALTO / 2 - VENTANA_ALTO / 6,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Vidas: {VIDAS}",
            VENTANA_ANCHO / 2,
            VENTANA_ALTO / 2 - VENTANA_ALTO / 6,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            f"Mascotas: {int(MASCOTAS)}",
            VENTANA_ANCHO / 2  + VENTANA_ANCHO / 6,
            VENTANA_ALTO / 2 - VENTANA_ALTO / 6,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.manager.draw()



def main():
    ventena = arcade.Window(VENTANA_ANCHO, VENTANA_ALTO, TITULO)
    vista_inicio = VistaInicio()
    ventena.show_view(vista_inicio)
    arcade.run()

if __name__ == "__main__":
    main()