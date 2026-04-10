import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import json
import os
import time
import serial
import serial.tools.list_ports
from kociemba_solver import solve_from_file
import tkinter as tk  # <-- ADICIONADO PARA A TELA DE CONFIGURAÇÃO

# =========================
# CONFIGURAÇÕES TÉCNICAS
# =========================

BASE_DIR = os.path.dirname(__file__)

logo_path = os.path.join(BASE_DIR, "logo_pro.jpg")
cube_state_path = os.path.join(BASE_DIR, "cube_state.json")

RES = (1400, 750)
COLOR_MAP = {
    'U': (1, 1, 1), 'D': (1, 1, 0), 'F': (0, 1, 0),
    'B': (0, 0, 1), 'L': (1, 0.5, 0), 'R': (1, 0, 0), 
    '.': (0.2, 0.2, 0.2)
}
RGB_TO_CHAR = {v: k for k, v in COLOR_MAP.items()}

MOVE_TABLE = {
    "U1": "A", "U3": "B", "U2": "C", "R1": "D", "R3": "E", "R2": "F",
    "F1": "G", "F3": "H", "F2": "I", "D1": "J", "D3": "K", "D2": "L",
    "L1": "M", "L3": "N", "L2": "O", "B3": "Q", "B1": "P", "B2": "R",
    "L1": "M", "L3": "N", "L2": "O", "B1": "P", "B3": "Q", "B2": "R"

}

# =========================
# CONTROLADOR DO ROBÔ
# =========================

class RobotController:
    def __init__(self):
        self.ser = None
        self.port = "COM4"
        self.speed = 1000
        self.delay = 0
        self.last_solve_time = "--"
        self.is_busy = False 
        self.auto_connect()

    def auto_connect(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if self.port in ports: self.connect(self.port)
        elif ports: self.connect(ports[0])

    def connect(self, port):
        try:
            if self.ser: self.ser.close()
            self.ser = serial.Serial()
            self.ser.port = port
            self.ser.baudrate = 9600
            self.ser.timeout = 0.1
            self.ser.setDTR(False)
            self.ser.open()
            time.sleep(3) 
            self.port = port
            return True
        except:
            self.ser = None
            return False

    def check_for_done(self):
        if not self.ser or not self.is_busy: return
        if self.ser.in_waiting:
            try:
                line = self.ser.readline().decode().strip()
                if line.startswith("DONE"):
                    parts = line.split()
                    if len(parts) > 1: self.last_solve_time = parts[1]
                    self.is_busy = False 
                    pygame.event.clear()
            except: pass

    def send_moves(self, sequence_str, wait_completion=True):
        if not self.ser or not self.ser.is_open: return
        try:
            self.ser.write(b"<START>\n")
            self.ser.write(f"<SPEED:{self.speed}>\n".encode())
            self.ser.write(f"<DELAY:{self.delay}>\n".encode())
            for move in sequence_str:
                self.ser.write((move + "\n").encode())
                time.sleep(0.01)
            self.ser.write(b"<END>\n")
            
            if wait_completion:
                self.is_busy = True
            else:
                self.is_busy = True
        except: self.is_busy = False

# =========================
# LÓGICA DO CUBO 3D
# =========================

class Cubie:
    def __init__(self, position):
        self.pos = list(position)
        self.colors = {}

    def draw(self, anim_params=None):
        glPushMatrix()
        if anim_params:
            ax_idx, angle, layer_val = anim_params
            if round(self.pos[ax_idx]) == layer_val:
                rot_v = [0, 0, 0]; rot_v[ax_idx] = 1
                glRotatef(angle, *rot_v)

        glTranslatef(*self.pos)
        size = 0.96 
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
            for v in verts: glVertex3f(v[0]*size, v[1]*size, v[2]*size)
        glEnd()
        glPopMatrix()

class RubiksCube:
    def __init__(self, robot):
        self.robot = robot
        self.cubies = [Cubie((x, y, z)) for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
        self.queue = []
        self.is_animating = False
        self.anim_angle = 0
        self.anim_speed = 15 
        self.current_move = None
        self.target_visual_angle = 0
        self.load_from_json()

    def move(self, face, times=1, send_serial=True):
        if send_serial:
            char_move = MOVE_TABLE.get(f"{face}{times}")
            if char_move: self.robot.send_moves(char_move, wait_completion=False)
        self.queue.append({'face': face, 'times': times})

    def update_animation(self):
        if not self.is_animating and self.queue:
            self.current_move = self.queue.pop(0)
            self.is_animating = True
            self.anim_angle = 0
            t = self.current_move['times']
            self.target_visual_angle = 180 if t == 2 else (90 if t == 1 else -90)
        
        if self.is_animating:
            step = self.anim_speed
            if self.target_visual_angle < 0:
                self.anim_angle -= step
                if self.anim_angle <= self.target_visual_angle: self.finish_move()
            else:
                self.anim_angle += step
                if self.anim_angle >= self.target_visual_angle: self.finish_move()

    def finish_move(self):
        for _ in range(self.current_move['times']): self.rotate_layer_logical(self.current_move['face'])
        self.is_animating = False
        self.anim_angle = 0
        self.save_to_json()

    def rotate_layer_logical(self, face):
        mapping = {'R': ('x', 1, -1), 'L': ('x', -1, 1), 'U': ('y', 1, -1), 
                   'D': ('y', -1, 1), 'F': ('z', 1, -1), 'B': ('z', -1, 1)}
        axis, layer_val, direction = mapping[face]
        ax_idx = "xyz".index(axis)
        for c in self.cubies:
            if round(c.pos[ax_idx]) == layer_val:
                x, y, z = c.pos
                if axis == 'x': c.pos[1], c.pos[2] = -direction*z, direction*y
                elif axis == 'y': c.pos[0], c.pos[2] = direction*z, -direction*x
                elif axis == 'z': c.pos[0], c.pos[1] = -direction*y, direction*x
                self.rotate_cubie_colors(c, axis, direction)

    def rotate_cubie_colors(self, cubie, axis, direction):
        cycles = {'x': ['U', 'F', 'D', 'B'], 'y': ['F', 'R', 'B', 'L'], 'z': ['U', 'L', 'D', 'R']}
        cycle = cycles[axis]
        if direction == -1: cycle = cycle[::-1]
        old = cubie.colors.copy()
        for i in range(4):
            src, dst = cycle[i], cycle[(i+1)%4]
            if src in old: cubie.colors[dst] = old[src]
            elif dst in cubie.colors: del cubie.colors[dst]

    def draw(self):
        anim_params = None
        if self.is_animating:
            mapping = {'R': ('x', 1, -1), 'L': ('x', -1, 1), 'U': ('y', 1, -1), 
                       'D': ('y', -1, 1), 'F': ('z', 1, -1), 'B': ('z', -1, 1)}
            axis_name, layer_val, direction = mapping[self.current_move['face']]
            ax_idx = "xyz".index(axis_name)
            anim_params = (ax_idx, self.anim_angle * direction, layer_val)
        for c in self.cubies: c.draw(anim_params)

    def get_cubie_at(self, x, y, z):
        for c in self.cubies:
            if [round(p) for p in c.pos] == [round(x), round(y), round(z)]: return c
        return None

    def get_state_string(self):
        def f_c(tp, fk):
            c = self.get_cubie_at(*tp)
            return RGB_TO_CHAR.get(c.colors.get(fk, COLOR_MAP['.']), 'U') if c else 'U'
        res = ""
        for z in [-1,0,1]: 
            for x in [-1,0,1]: res += f_c((x,1,z), 'U')
        for y in [1,0,-1]: 
            for z in [1,0,-1]: res += f_c((1,y,z), 'R')
        for y in [1,0,-1]: 
            for x in [-1,0,1]: res += f_c((x,y,1), 'F')
        for z in [1,0,-1]: 
            for x in [-1,0,1]: res += f_c((x,-1,z), 'D')
        for y in [1,0,-1]: 
            for z in [-1,0,1]: res += f_c((-1,y,z), 'L')
        for y in [1,0,-1]: 
            for x in [1,0,-1]: res += f_c((x,y,-1), 'B')
        return res

    def save_to_json(self):
        state = self.get_state_string()
        with open(cube_state_path, 'w') as f: json.dump({"cube_string": state}, f)

    def load_from_json(self):
        s = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        if os.path.exists(cube_state_path):
            try:
                with open(cube_state_path, 'r') as f:
                    data = json.load(f); s = data.get("cube_string", s)
            except: pass
        if len(s) != 54: return
        idx = 0
        for z in [-1,0,1]: 
            for x in [-1,0,1]: self.get_cubie_at(x,1,z).colors['U'] = COLOR_MAP[s[idx]]; idx+=1
        for y in [1,0,-1]: 
            for z in [1,0,-1]: self.get_cubie_at(1,y,z).colors['R'] = COLOR_MAP[s[idx]]; idx+=1
        for y in [1,0,-1]: 
            for x in [-1,0,1]: self.get_cubie_at(x,y,1).colors['F'] = COLOR_MAP[s[idx]]; idx+=1
        for z in [1,0,-1]: 
            for x in [-1,0,1]: self.get_cubie_at(x,-1,z).colors['D'] = COLOR_MAP[s[idx]]; idx+=1
        for y in [1,0,-1]: 
            for z in [-1,0,1]: self.get_cubie_at(-1,y,z).colors['L'] = COLOR_MAP[s[idx]]; idx+=1
        for y in [1,0,-1]: 
            for x in [1,0,-1]: self.get_cubie_at(x,y,-1).colors['B'] = COLOR_MAP[s[idx]]; idx+=1

# =========================
# INTERFACE E SOLVER
# =========================

def load_logo(path):
    try:
        img = pygame.image.load(path)
        img = pygame.transform.flip(img, False, True)
        img_data = pygame.image.tostring(img, "RGBA", True)
        w, h = img.get_rect().size
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return tex_id, w, h
    except: return None, 0, 0

def run_solver(cube):
    cube.save_to_json()
    res = solve_from_file(cube_state_path)
    if "error" in res: return

    cube.robot.send_moves(res["robot_sequence"], wait_completion=False)
    
    moves = res["solution"].split()
    for m in moves:
        face = m[0]
        t = 3 if "'" in m else (2 if "2" in m else 1)
        cube.move(face, t, send_serial=False) 

def draw_text_hud(x, y, text, size, center_x=None, center_y=None):
    font = pygame.font.SysFont('Consolas', size, bold=True)
    surface = font.render(text, True, (255, 255, 255, 255))
    tw, th = surface.get_size() 
    render_x = x if center_x is None else center_x - (tw / 2)
    render_y = y if center_y is None else center_y - (th / 2)
    data = pygame.image.tostring(surface, "RGBA", True)
    glWindowPos2d(int(render_x), int(render_y))
    glDrawPixels(tw, th, GL_RGBA, GL_UNSIGNED_BYTE, data)

def draw_hud(robot, logo_tex):
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, RES[0], RES[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    if logo_tex[0]:
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, logo_tex[0])
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(20, 20)
        glTexCoord2f(1,0); glVertex2f(200, 20)
        glTexCoord2f(1,1); glVertex2f(200, 180)
        glTexCoord2f(0,1); glVertex2f(20, 180)
        glEnd(); glDisable(GL_TEXTURE_2D)
    
    if robot.is_busy: glColor3f(0.8, 0.2, 0.2) 
    elif not robot.ser: glColor3f(0.4, 0.4, 0.4)
    else: glColor3f(0.29, 0.42, 0.44) 
        
    x_s, x_e = RES[0] - 380, RES[0] - 20
    glBegin(GL_QUADS)
    glVertex2f(x_s, 20); glVertex2f(x_e, 20)
    glVertex2f(x_e, 180); glVertex2f(x_s, 180)
    glEnd()

    status_text = "BUSY..." if robot.is_busy else (f"TIME: {robot.last_solve_time} s" if robot.ser else "OFFLINE")
    draw_text_hud(0, 0, status_text, 42, center_x=(x_s+x_e)/2, center_y=RES[1]-100)
    
    glColor4f(0, 0, 0, 0.6)
    glBegin(GL_QUADS)
    glVertex2f(0, RES[1]-60); glVertex2f(RES[0], RES[1]-60)
    glVertex2f(RES[0], RES[1]); glVertex2f(0, RES[1])
    glEnd()
    
    p_s = robot.port if robot.ser else "DISCONNECTED"
    draw_text_hud(25, 35, f"PORT: {p_s} | SPEED: {robot.speed} | DELAY: {robot.delay}ms", 18)
    draw_text_hud(25, 10, "[S] Config | [X] Resolver | [R,L,U,D,F,B] Moves | [2] Double | [Shift] Inverse | APERTE ESC PARA SAIR",  14)

    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glEnable(GL_DEPTH_TEST)


# =========================
# Eixos de Coordendas
# =========================

def draw_axes_corner(rot_x, rot_y):
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(-3.2, -1, -6.0) 
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)
    glDisable(GL_DEPTH_TEST) 
    glLineWidth(3.0)
    glBegin(GL_LINES)
    s = 0.7
    
    glColor3f(1.0, 1.0, 1.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, s, 0.0) 
    glColor3f(0.0, 1.0, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, s) 
    glColor3f(1.0, 0.5, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(-s, 0.0, 0.0) 
    glColor3f(1.0, 1.0, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, -s, 0.0) 
    glColor3f(1.0, 0.0, 0.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(s, 0.0, 0.0) 
    glColor3f(0.0, 0.0, 1.0); glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, -s) 
    glEnd()
    glLineWidth(1.0)
    
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    
    l_off = s + 0.1 
    labels = [
        ("Y (RIGHT)", (l_off, 0.0, 0.0)), ("X (FRONT)", (0.0, 0.0, l_off)), ("Z (UP)", (0.0, l_off, 0.0)),
        ("-Y (LEFT)", (-l_off, 0.0, 0.0)), ("-Z (DOWN)", (0.0, -l_off, 0.0)), ("-X (BACK)", (0.0, 0.0, -l_off))
    ]
    
    for label, pos in labels:
        try:
            win_x, win_y, win_z = gluProject(pos[0], pos[1], pos[2], modelview, projection, viewport)
            if 0.0 <= win_z <= 1.0:
                draw_text_hud(0, 0, label, 16, center_x=win_x, center_y=win_y)
        except: pass
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()

# =========================
# JANELA DE CONFIGURAÇÃO TKINTER
# =========================

def open_config_window(robot):
    root = tk.Tk()
    root.title("Configurações do Robô")
    root.geometry("300x250")
    
    # Isso é essencial! Força a janela do Tkinter a ficar por cima da tela cheia do Pygame
    root.attributes('-topmost', True) 
    
    # Centraliza a janelinha na tela
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Porta Serial (ex: COM4, /dev/ttyUSB0):", font=("Arial", 10)).pack(pady=(10, 0))
    port_entry = tk.Entry(root, justify="center")
    port_entry.insert(0, robot.port)
    port_entry.pack(pady=5)

    tk.Label(root, text="Velocidade do Robô (Speed):", font=("Arial", 10)).pack(pady=(10, 0))
    speed_entry = tk.Entry(root, justify="center")
    speed_entry.insert(0, str(robot.speed))
    speed_entry.pack(pady=5)

    tk.Label(root, text="Atraso (Delay em ms):", font=("Arial", 10)).pack(pady=(10, 0))
    delay_entry = tk.Entry(root, justify="center")
    delay_entry.insert(0, str(robot.delay))
    delay_entry.pack(pady=5)

    def save_and_close():
        robot.port = port_entry.get().strip()
        try:
            robot.speed = int(speed_entry.get())
            robot.delay = int(delay_entry.get())
        except ValueError:
            pass # Ignora caso o usuário digite texto em vez de número
        
        # Tenta conectar com a nova porta
        robot.connect(robot.port)
        root.destroy()

    tk.Button(root, text="Salvar e Conectar", command=save_and_close, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=15)
    
    # Roda a janela (isso vai pausar o Pygame momentaneamente enquanto a janela estiver aberta)
    root.mainloop()

# =========================
# LOOP PRINCIPAL
# =========================

def main():
    global RES  
    
    pygame.init()
    
    info = pygame.display.Info()
    RES = (info.current_w, info.current_h)
    
    pygame.display.set_mode(RES, DOUBLEBUF | OPENGL | FULLSCREEN)
    pygame.display.set_caption("RobotCube 3D - Unicamp Cube")
    
    robot = RobotController(); cube = RubiksCube(robot)
    logo_data = load_logo(logo_path)
    rot_x, rot_y = 30, -30
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): 
                pygame.quit(); return
            
            if event.type == KEYDOWN and not robot.is_busy:
                
                # --- AQUI ESTÁ O CHAMADO DA CONFIGURAÇÃO (TECLA S) ---
                if event.key == K_s:
                    # Desativa a captura exclusiva de mouse do pygame (se houver) para você poder clicar no Tkinter
                    pygame.event.set_grab(False)
                    open_config_window(robot)
                    continue
                # -----------------------------------------------------

                mods = pygame.key.get_mods()
                t = 3 if (mods & KMOD_SHIFT) else (2 if pygame.key.get_pressed()[K_2] else 1)
                key_map = {K_r:'R', K_l:'L', K_u:'U', K_d:'D', K_f:'F', K_b:'B'}
                if event.key in key_map: cube.move(key_map[event.key], t)
                elif event.key == K_x: run_solver(cube)

        if pygame.mouse.get_pressed()[0]:
            rel = pygame.mouse.get_rel()
            rot_y += rel[0] * 0.4; rot_x += rel[1] * 0.4
        else: pygame.mouse.get_rel()

        cube.update_animation() 
        robot.check_for_done()  

        glClearColor(0.12, 0.12, 0.14, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        
        gluPerspective(45, (RES[0]/RES[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glTranslatef(0, 0, -10.0) 
        
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0); glRotatef(rot_y, 0, 1, 0)
        cube.draw()
        glPopMatrix()
        
        draw_axes_corner(rot_x, rot_y)
        draw_hud(robot, logo_data)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()