import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import json
import os

# =========================
# CONFIGURAÇÃO E CORES
# =========================

COLOR_MAP = {
    'U': (1, 1, 1),      # Branco
    'D': (1, 1, 0),      # Amarelo
    'F': (0, 1, 0),      # Verde
    'B': (0, 0, 1),      # Azul
    'L': (1, 0.5, 0),    # Laranja
    'R': (1, 0, 0),      # Vermelho
    '.': (0.1, 0.1, 0.1) 
}

RGB_TO_CHAR = {v: k for k, v in COLOR_MAP.items()}

class Cubie:
    def __init__(self, position):
        self.pos = list(position)
        self.colors = {}

    def draw(self):
        x, y, z = self.pos
        glPushMatrix()
        glTranslatef(x, y, z)
        size = 0.95
        faces = [
            ('U', [(0.5,0.5,0.5), (-0.5,0.5,0.5), (-0.5,0.5,-0.5), (0.5,0.5,-0.5)]),
            ('D', [(0.5,-0.5,-0.5), (-0.5,-0.5,-0.5), (-0.5,-0.5,0.5), (0.5,-0.5,0.5)]),
            ('F', [(0.5,0.5,0.5), (0.5,-0.5,0.5), (-0.5,-0.5,0.5), (-0.5,0.5,0.5)]),
            ('B', [(-0.5,0.5,-0.5), (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5)]),
            ('L', [(-0.5,0.5,0.5), (-0.5,-0.5,0.5), (-0.5,-0.5,-0.5), (-0.5,0.5,-0.5)]),
            ('R', [(0.5,0.5,-0.5), (0.5,-0.5,-0.5), (0.5,-0.5,0.5), (0.5,0.5,0.5)]),
        ]
        glBegin(GL_QUADS)
        for face_id, verts in faces:
            color = self.colors.get(face_id, COLOR_MAP['.'])
            glColor3fv(color)
            for v in verts:
                glVertex3f(v[0]*size, v[1]*size, v[2]*size)
        glEnd()
        glPopMatrix()

# =========================
# LÓGICA DE SINCRONIZAÇÃO
# =========================

class RubiksCube:
    def __init__(self):
        self.cubies = [Cubie((x, y, z)) for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
        self.filename = "state.json"
        self.last_mtime = 0  # Guarda a última vez que o arquivo foi lido
        self.current_state_str = ""
        self.check_for_updates() # Primeira leitura

    def check_for_updates(self):
        """Verifica se o arquivo JSON mudou no disco e atualiza o cubo."""
        if os.path.exists(self.filename):
            mtime = os.path.getmtime(self.filename)
            if mtime > self.last_mtime:
                self.last_mtime = mtime
                try:
                    with open(self.filename, 'r') as f:
                        data = json.load(f)
                        new_state = data.get("state", "")
                        if new_state != self.current_state_str:
                            self.set_state_from_string(new_state)
                            self.current_state_str = new_state
                            print("Sincronizado com state.json")
                except Exception as e:
                    print(f"Erro ao ler JSON: {e}")

    def save_to_json(self):
        """Gera a string do estado atual e salva no JSON."""
        state_str = self.get_state_string()
        self.current_state_str = state_str
        with open(self.filename, 'w') as f:
            json.dump({"state": state_str}, f)
        # Atualiza o timestamp interno para não ler o próprio arquivo que acabou de salvar
        self.last_mtime = os.path.getmtime(self.filename)

    def get_state_string(self):
        """Lê os cubinhos no espaço 3D e gera a string Kociemba."""
        def find_color(target_pos, face_key):
            for c in self.cubies:
                if [round(p) for p in c.pos] == list(target_pos):
                    return RGB_TO_CHAR.get(c.colors.get(face_key, COLOR_MAP['.']), 'U')
            return 'U'

        res = ""
        
        for z in [-1, 0, 1]:
            for x in [-1, 0, 1]: res += find_color((x, 1, z), 'U')
        for y in [1, 0, -1]:
            for z in [1, 0, -1]: res += find_color((1, y, z), 'R')
        for y in [1, 0, -1]:
            for x in [-1, 0, 1]: res += find_color((x, y, 1), 'F')
        for z in [1, 0, -1]:
            for x in [-1, 0, 1]: res += find_color((x, -1, z), 'D')
        for y in [1, 0, -1]:
            for z in [-1, 0, 1]: res += find_color((-1, y, z), 'L')
        for y in [1, 0, -1]:
            for x in [1, 0, -1]: res += find_color((x, y, -1), 'B')
        return res

    def set_state_from_string(self, s):
        """Aplica a string de 54 caracteres aos cubinhos nas posições atuais."""
        if len(s) != 54: return
        
        # Resetamos as cores mas mantemos os cubinhos onde estão
        for c in self.cubies: c.colors = {}
        
        idx = 0
        # Mapeamento espacial idêntico ao get_state_string
        def set_c(pos, face, char):
            for c in self.cubies:
                if [round(p) for p in c.pos] == list(pos):
                    c.colors[face] = COLOR_MAP[char]
                    break

        for z in [-1, 0, 1]:
            for x in [-1, 0, 1]: set_c((x, 1, z), 'U', s[idx]); idx += 1
        for y in [1, 0, -1]:
            for z in [1, 0, -1]: set_c((1, y, z), 'R', s[idx]); idx += 1
        for y in [1, 0, -1]:
            for x in [-1, 0, 1]: set_c((x, y, 1), 'F', s[idx]); idx += 1
        for z in [1, 0, -1]:
            for x in [-1, 0, 1]: set_c((x, -1, z), 'D', s[idx]); idx += 1
        for y in [1, 0, -1]:
            for z in [-1, 0, 1]: set_c((-1, y, z), 'L', s[idx]); idx += 1
        for y in [1, 0, -1]:
            for x in [1, 0, -1]: set_c((x, y, -1), 'B', s[idx]); idx += 1

    def move(self, face, times=1):
        for _ in range(times):
            self.rotate_layer(face)
        self.save_to_json()

    def rotate_layer(self, face):
        mapping = {'R':('x',1,-1), 'L':('x',-1,1), 'U':('y',1,-1), 'D':('y',-1,1), 'F':('z',1,-1), 'B':('z',-1,1)}
        ax, lv, dr = mapping[face]
        idx = "xyz".index(ax)
        for c in self.cubies:
            if round(c.pos[idx]) == lv:
                x, y, z = c.pos
                if ax == 'x': c.pos[1], c.pos[2] = -dr*z, dr*y
                elif ax == 'y': c.pos[0], c.pos[2] = dr*z, -dr*x
                elif ax == 'z': c.pos[0], c.pos[1] = -dr*y, dr*x
                self.rotate_cubie_colors(c, ax, dr)

    def rotate_cubie_colors(self, cubie, axis, direction):
        cycles = {'x':['U','F','D','B'], 'y':['F','R','B','L'], 'z':['U','L','D','R']}
        cyc = cycles[axis]
        if direction == -1: cyc = cyc[::-1]
        old = cubie.colors.copy()
        for i in range(4):
            src, dst = cyc[i], cyc[(i+1)%4]
            if src in old: cubie.colors[dst] = old[src]
            elif dst in cubie.colors: del cubie.colors[dst]

# =========================
# MAIN
# =========================

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Robot Cube Monitor")
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -10)

    cube = RubiksCube()
    rot_x, rot_y = 30, -30
    clock = pygame.time.Clock()

    while True:
        # 1. VERIFICA MUDANÇAS EXTERNAS NO ARQUIVO
        cube.check_for_updates()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

            if event.type == KEYDOWN:
                mods = pygame.key.get_mods()
                is_shift = mods & KMOD_SHIFT
                keys = pygame.key.get_pressed()
                is_two = keys[K_2] or keys[K_KP2]

                times = 1
                if is_shift: times = 3 
                elif is_two: times = 2

                key_map = {K_r:'R', K_l:'L', K_u:'U', K_d:'D', K_f:'F', K_b:'B'}
                if event.key in key_map:
                    cube.move(key_map[event.key], times)

        if pygame.mouse.get_pressed()[0]:
            rel = pygame.mouse.get_rel()
            rot_y += rel[0] * 0.5
            rot_x += rel[1] * 0.5
        else:
            pygame.mouse.get_rel()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        for c in cube.cubies: c.draw()
        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()