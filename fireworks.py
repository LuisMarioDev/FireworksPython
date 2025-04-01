import pygame
from random import randint, uniform, choice
import math

vector2 = pygame.math.Vector2  # Usamos el tipo de datos Vector2 de Pygame para manejar coordenadas 2D
trails = []  # Lista para almacenar las estelas de las partículas
fade_p = []  # Lista para almacenar partículas en proceso de desvanecimiento


# Parámetros generales
GRAVITY_FIREWORK = vector2(0, 0.3)  # Gravedad para el fuego artificial
GRAVITY_PARTICLE = vector2(0, 0.07)  # Gravedad para las partículas
DISPLAY_WIDTH = DISPLAY_HEIGHT = 1000  # Tamaño de la ventana
BACKGROUND_COLOR = (10, 10, 40)  # Color de fondo de la pantalla
STAR_COLOR = (255, 255, 255)
NUM_STARS = 100

# Parámetros para los fuegos artificiales
FIREWORK_SPEED_MIN = 15
FIREWORK_SPEED_MAX = 25
FIREWORK_SIZE = 6

# Parámetros para las partículas
PARTICLE_LIFESPAN = 100
X_SPREAD = 0.8
Y_SPREAD = 0.8
PARTICLE_SIZE = 4
MIN_PARTICLES = 100
MAX_PARTICLES = 300
X_WIGGLE_SCALE = 15  # A mayor valor, menos "movimiento" aleatorio
Y_WIGGLE_SCALE = 10
EXPLOSION_RADIUS_MIN = 15
EXPLOSION_RADIUS_MAX = 35
COLORFUL = True  # Si True, las partículas tendrán colores aleatorios

# Parámetros para las estelas
TRAIL_LIFESPAN = PARTICLE_LIFESPAN / 2  # Duración de las estelas
TRAIL_FREQUENCY = 8  # Mayor valor -> menos estelas
TRAILS = True  # Si True, se muestran estelas

class Firework:
    def __init__(self):
        # Inicializamos el color del fuego artificial y las partículas
        self.colour = tuple(randint(0, 255) for _ in range(3))
        self.colours = tuple(tuple(randint(0, 255) for _ in range(3)) for _ in range(3))  # Colores de las partículas
        self.firework = Particle(randint(0, DISPLAY_WIDTH), DISPLAY_HEIGHT, True, self.colour)  # Crea la partícula del fuego artificial
        self.exploded = False  # Indica si el fuego artificial ha explotado
        self.particles = []  # Lista de partículas que serán creadas al explotar

    def update(self, win: pygame.Surface) -> None:
        # Método que se llama en cada cuadro de la animación
        if not self.exploded:
            self.firework.apply_force(GRAVITY_FIREWORK)  # Aplica la gravedad al fuego artificial
            self.firework.move()  # Mueve el fuego artificial
            self.show(win)  # Dibuja el fuego artificial en la ventana
            if self.firework.vel.y >= 0:  # Si la velocidad en el eje Y es positiva (cuando empieza a caer)
                self.exploded = True  # El fuego artificial explota
                self.explode()  # Crea las partículas de la explosión

        else:
            for particle in self.particles:  # Actualiza las partículas
                particle.update()
                particle.show(win)

    def explode(self):
        # Crea las partículas al momento de la explosión
        amount = randint(MIN_PARTICLES, MAX_PARTICLES)  # Número aleatorio de partículas
        if COLORFUL:
            # Si COLORFUL es True, las partículas tendrán colores aleatorios
            self.particles = [Particle(self.firework.pos.x, self.firework.pos.y, False, choice(self.colours)) for _ in range(amount)]
        else:
            # Si COLORFUL es False, todas las partículas tendrán el mismo color que el fuego artificial
            self.particles = [Particle(self.firework.pos.x, self.firework.pos.y, False, self.colour) for _ in range(amount)]

    def show(self, win: pygame.Surface) -> None:
        # Dibuja el fuego artificial en la ventana
        x = int(self.firework.pos.x)
        y = int(self.firework.pos.y)
        pygame.draw.circle(win, self.colour, (x, y), self.firework.size)

    def remove(self) -> bool:
        # Elimina el fuego artificial si ya ha explotado y no quedan partículas
        if not self.exploded:
            return False

        for p in self.particles:
            if p.remove:
                self.particles.remove(p)

        return len(self.particles) == 0


class Particle(object):
    def __init__(self, x, y, firework, colour):
        self.firework = firework  # Si es un fuego artificial o una partícula de explosión
        self.pos = vector2(x, y)  # Posición de la partícula
        self.origin = vector2(x, y)  # Origen de la partícula
        self.acc = vector2(0, 0)  # Aceleración de la partícula
        self.remove = False  # Si la partícula debe ser eliminada
        self.explosion_radius = randint(EXPLOSION_RADIUS_MIN, EXPLOSION_RADIUS_MAX)  # Radio de la explosión
        self.life = 0  # Tiempo de vida de la partícula
        self.colour = colour  # Color de la partícula
        self.trail_frequency = TRAIL_FREQUENCY + randint(-3, 3)  # Frecuencia de las estelas

        if self.firework:
            # Si es el fuego artificial, la partícula se mueve hacia arriba
            self.vel = vector2(0, -randint(FIREWORK_SPEED_MIN, FIREWORK_SPEED_MAX))
            self.size = FIREWORK_SIZE
        else:
            # Si es una partícula de explosión, su movimiento es aleatorio
            self.vel = vector2(uniform(-1, 1), uniform(-1, 1))
            self.vel.x *= randint(7, self.explosion_radius + 2)
            self.vel.y *= randint(7, self.explosion_radius + 2)
            self.size = randint(PARTICLE_SIZE - 1, PARTICLE_SIZE + 1)
            self.move()  # Mueve la partícula
            self.outside_spawn_radius()  # Elimina la partícula si está fuera del radio de explosión

    def update(self) -> None:
        # Actualiza la partícula cada cuadro
        self.life += 1
        if self.life % self.trail_frequency == 0:  # Si el tiempo de vida es múltiplo de la frecuencia, crea una estela
            trails.append(Trail(self.pos.x, self.pos.y, False, self.colour, self.size))
        # Agrega un movimiento aleatorio a la partícula
        self.apply_force(vector2(uniform(-1, 1) / X_WIGGLE_SCALE, GRAVITY_PARTICLE.y + uniform(-1, 1) / Y_WIGGLE_SCALE))
        self.move()

    def apply_force(self, force: pygame.math.Vector2) -> None:
        # Aplica una fuerza a la partícula (como la gravedad o el movimiento aleatorio)
        self.acc += force

    def outside_spawn_radius(self) -> bool:
        # Si la partícula está fuera del radio de explosión, se elimina
        distance = math.sqrt((self.pos.x - self.origin.x) ** 2 + (self.pos.y - self.origin.y) ** 2)
        return distance > self.explosion_radius

    def move(self) -> None:
        # Mueve la partícula en función de su velocidad y aceleración
        if not self.firework:
            # Si no es un fuego artificial, aplica la dispersión en X y Y
            self.vel.x *= X_SPREAD
            self.vel.y *= Y_SPREAD

        self.vel += self.acc  # Aplica la aceleración
        self.pos += self.vel  # Mueve la partícula
        self.acc *= 0  # Resetea la aceleración

        self.decay()  # Decae la partícula (suaviza su desaparición)

    def show(self, win: pygame.Surface) -> None:
        # Dibuja la partícula en la ventana
        x = int(self.pos.x)
        y = int(self.pos.y)
        pygame.draw.circle(win, self.colour, (x, y), self.size)

    def decay(self) -> None:
        # La partícula se va desvaneciendo con el tiempo
        if self.life > PARTICLE_LIFESPAN:
            if randint(0, 15) == 0:  # Algunas partículas se eliminan aleatoriamente
                self.remove = True
        if not self.remove and self.life > PARTICLE_LIFESPAN * 1.5:
            self.remove = True  # Si la partícula es demasiado vieja, se elimina


class Trail(Particle):
    def __init__(self, x, y, is_firework, colour, parent_size):
        # Las estelas son partículas con una vida más corta y un tamaño decreciente
        Particle.__init__(self, x, y, is_firework, colour)
        self.size = parent_size - 1

    def decay(self) -> bool:
        # La estela se desvanece cambiando su color y tamaño
        self.life += 1
        if self.life % 100 == 0:
            self.size -= 1

        self.size = max(0, self.size)  # Evita que el tamaño sea negativo
        self.colour = (min(self.colour[0] + 5, 255), min(self.colour[1] + 5, 255), min(self.colour[2] + 5, 255))

        if self.life > TRAIL_LIFESPAN:
            ran = randint(0, 15)
            if ran == 0:
                return True  # Si la estela es demasiado vieja, se elimina
        if not self.remove and self.life > TRAIL_LIFESPAN * 1.5:
            return True
        
        return False


def update(win: pygame.Surface, fireworks: list, trails: list) -> None:
    # Actualiza la pantalla con los fuegos artificiales y las estelas
    if TRAILS:
        for t in trails:
            t.show(win)
            if t.decay():
                trails.remove(t)

    for fw in fireworks:
        fw.update(win)
        if fw.remove():
            fireworks.remove(fw)

    pygame.display.update()

# Generar posiciones de estrellas una sola vez (estáticas)
stars = [(randint(0, DISPLAY_WIDTH), randint(0, DISPLAY_HEIGHT)) for _ in range(NUM_STARS)]

def draw_stars(win):
    """Dibuja estrellas en el fondo"""
    for star in stars:
        pygame.draw.circle(win, STAR_COLOR, star, 1)  # Pequeñas estrellas blancas

def main():
    pygame.init()
    pygame.display.set_caption("Fireworks in Pygame")  # Título de la ventana
    win = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))  # Crea la ventana
    clock = pygame.time.Clock()

    fireworks = [Firework() for i in range(1)]  # Crea el primer fuego artificial
    running = True

    while running:
        clock.tick(60)  # Controla la tasa de actualización a 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    fireworks.append(Firework())  # Si presiona "1", se crea un nuevo fuego artificial
                elif event.key == pygame.K_2:
                    for i in range(10):
                        fireworks.append(Firework())  # Si presiona "2", se crean 10 fuegos artificiales

        win.fill(BACKGROUND_COLOR)  # Rellena la pantalla con el color de fondo
        draw_stars(win)

        if randint(0, 70) == 1:  # Con una probabilidad de 1 en 70, crea un nuevo fuego artificial
            fireworks.append(Firework())
        
        update(win, fireworks, trails)  # Actualiza y muestra los fuegos artificiales

    pygame.quit()  # Cierra Pygame
    quit()


main()  # Llama a la función principal