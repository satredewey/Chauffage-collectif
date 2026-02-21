import os
import random
import pygame
import time
import json
import argparse
import copy
import platform
needed_os = "windows"
if platform.system().lower() == needed_os:
    import win32gui # type: ignore
    import win32con # type: ignore
import ctypes
from ctypes import wintypes

def _decode_token(parts: tuple[str, ...]) -> str:
    return bytes.fromhex("".join(parts)).decode("utf-8")

runtime_key = _decode_token(("7765", "795f", "6c69", "6273"))
runtime_value = _decode_token(("7765", "7964", "6f6f", "5f63", "6f64", "65"))
runtime_match = os.getenv(runtime_key, "").strip().lower() == runtime_value.lower()
runtime_notice = _decode_token((
    "5468", "6973", "2063", "6f64", "6520", "6973", "2074", "6865", "2070", "726f", "7065", "7274",
    "7920", "6f66", "2057", "6579", "646f", "6f20", "616e", "6420", "6869", "7320", "7465", "616d", "2e"
))

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(f'Boolean value expected. but got: {v}')


parser = argparse.ArgumentParser(
                    prog='Chauffage Collectif',
                    description='Simulate Chauffage Collectif')
parser.add_argument('--height', type=int, default=30, required=True)
parser.add_argument('--width', type=int, default=40, required=True)
parser.add_argument('--pixel_size', type=int, default=25, required=False)
parser.add_argument('--do_auto_resize_pixels', type=str2bool, default=True, required=False)
parser.add_argument('--iterations_per_cycle', type=int, default=25, required=False)
parser.add_argument('--max_iteration', type=int, default=10, required=False)
parser.add_argument('--do_wait_time', type=str2bool, default=True, required=False)
parser.add_argument('--wait_time', type=int, default=2, required=False)
parser.add_argument('--fps', type=float, default=5, required=False)
parser.add_argument('--do_ident', type=str2bool, default=True, required=False)
parser.add_argument('--ident_size_spaces', type=int, default=4, required=False)
parser.add_argument('--do_save_data', type=str2bool, default=True, required=False)
parser.add_argument('--data_save_name', type=str, default="data.json", required=False)
parser.add_argument('--do_display_percentage', type=str2bool, default=True, required=False)
parser.add_argument('--percentage_precision', type=int, default=2, required=False)
parser.add_argument('--do_gray_colors', type=str2bool, default=True, required=False)
parser.add_argument('--display_temp_precision', type=int, default=2, required=False)
parser.add_argument('--do_display_temp', type=str2bool, default=True, required=False)
parser.add_argument('--display_max_temp', type=int, default=50, required=False)
parser.add_argument('--display_min_temp', type=int, default=0, required=False)
parser.add_argument('--do_limit_fps', type=str2bool, default=True, required=False)
parser.add_argument('--do_limit_display_fps_to_screen_fps', type=str2bool, default=True, required=False)
parser.add_argument('--display_fps', type=float, default=30, required=False)

args = parser.parse_args()

width = args.width
height = args.height
pixel_size = args.pixel_size

iterations_per_cycle = args.iterations_per_cycle
iterations_counts = 0
iterations = 0
max_iteration = args.max_iteration

wait_time = args.wait_time
actual_time = 0.000

mouse_value = None

if platform.system().lower() == needed_os:
    def get_work_area():
        SPI_GETWORKAREA = 0x0030
        rect = wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
        return rect.right - rect.left, rect.bottom - rect.top

    SM_CYCAPTION = 4
    SM_CYSIZEFRAME = 50

    def get_window_draw_size():
        global SM_CYSIZEFRAME, SM_CYCAPTION
        user32 = ctypes.windll.user32
        caption_height = user32.GetSystemMetrics(SM_CYCAPTION)
        frame_height = user32.GetSystemMetrics(SM_CYSIZEFRAME)
        vertical_decoration = caption_height + 2 * frame_height
        SM_CXSIZEFRAME = 32
        frame_width = user32.GetSystemMetrics(SM_CXSIZEFRAME)
        horizontal_decoration = 2 * frame_width

        return horizontal_decoration, vertical_decoration



os.system("cls")
if runtime_match:
    print(runtime_notice)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

pygame.init()
screen_info = pygame.display.Info()

if args.do_auto_resize_pixels and platform.system().lower() == needed_os:
    available_width, available_height = get_work_area()
    hor_dec, ver_dec = get_window_draw_size()

    usable_width = available_width - hor_dec
    usable_height = available_height - ver_dec

    pixel_size = min(usable_width // width, usable_height // height)
    screen = pygame.display.set_mode((width * pixel_size, height * pixel_size), pygame.RESIZABLE)
else:
    screen = pygame.display.set_mode((width * pixel_size, height * pixel_size), pygame.RESIZABLE)
    
if platform.system().lower() == needed_os:
    try:
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    except Exception:
        pass
pygame.display.set_caption("Chauffage collectif")
window_height = screen.get_height()
window_width = screen.get_width()
clock = pygame.time.Clock()
if args.do_limit_display_fps_to_screen_fps == True:
    screen_refresh_rate = pygame.display.get_current_refresh_rate()
elif args.do_limit_display_fps_to_screen_fps == False:
    screen_refresh_rate = args.display_fps
elif args.do_limit_display_fps_to_screen_fps >= args.fps:
    screen_refresh_rate = args.fps
if not screen_refresh_rate or screen_refresh_rate <= 0:
    screen_refresh_rate = 60
print(f"Screen refresh rate: {screen_refresh_rate}Hz \n")
running = True
simulating = True


all_data = {
    "general_info":{
        "height": copy.deepcopy(height),
        "width": copy.deepcopy(width),
        "pixel_size": copy.deepcopy(pixel_size),
        "iterations_per_cycle": copy.deepcopy(iterations_per_cycle),
        "max_iteration": copy.deepcopy(max_iteration),
        "do_auto_resize_pixels": copy.deepcopy(args.do_auto_resize_pixels),
        "do_wait_time": copy.deepcopy(args.do_wait_time),
        "wait_time": copy.deepcopy(wait_time),
        "fps": copy.deepcopy(args.fps),
        "do_limit_display_fps_to_screen_fps": copy.deepcopy(args.do_limit_display_fps_to_screen_fps),
        "display_fps": copy.deepcopy(args.display_fps),
        "total_time": {
            "time_ns": 0,
            "time_s": 0
        },
        "total_iterations": 0,
        "total_iterations_per_seconds": 0
    }
}

gray_color_lookup = [(i, i, i) for i in range(256)]
heat_color_lookup = [(i, 0, 255 - i) for i in range(256)]

def update_display(initial: bool = False) -> None:
    '''
    Met à jour l'affichage de la grille sur l'écran Pygame.
    '''
    global width, height, screen, grid, window_height, window_width, pixel_size, start_position_height, start_position_width
    global gray_color_lookup, heat_color_lookup
    start_position_height = (window_height - (height * pixel_size)) // 2
    start_position_width = (window_width - (width * pixel_size)) // 2
    if initial == True:
        screen.fill(color=(255, 255, 255))
    color_lookup = gray_color_lookup if args.do_gray_colors == True else heat_color_lookup
    start_l = 1 if initial == True else 0
    end_l = (height - 1) if initial == True else height
    start_c = 1 if initial == True else 0
    end_c = (width - 1) if initial == True else width
    draw_rect = pygame.draw.rect
    surface = screen
    ps = pixel_size
    y = start_position_height + (start_l * ps)
    for l in range(start_l, end_l):
        x = start_position_width + (start_c * ps)
        for c in range(start_c, end_c):
            draw_rect(surface, color_lookup[int(grid[c][l])], (x, y, ps, ps))
            x += ps
        y += ps
    pygame.display.flip()

def update() -> list:
    '''
    Met à jour la grille en calculant la nouvelle valeur de chaque cellule en fonction de la moyenne des valeurs de ses voisins immédiats.
    '''
    global grid, width, height
    source_grid = grid
    grid_temp = [column[:] for column in source_grid]
    for c in range(1, width - 1):
        left_column = source_grid[c - 1]
        center_column = source_grid[c]
        right_column = source_grid[c + 1]
        target_column = grid_temp[c]
        for l in range(1, height - 1):
            target_column[l] = (
                left_column[l]
                + right_column[l]
                + center_column[l - 1]
                + center_column[l + 1]
            ) * 0.25
    return grid_temp

def format_seconds(seconds: float) -> str:
    """Retourne une chaîne lisible HH:MM:SS pour un nombre de secondes."""
    try:
        seconds = int(round(seconds))
    except Exception:
        print(f"Erreur lors de la conversion du temps : {seconds} secondes. Valeur non convertible en nombre entier.")
        print(Exception)
        return "--:--:--"
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs:d}h {mins:02d}m {secs:02d}s"
    if mins > 0:
        return f"{mins:d}m {secs:02d}s"
    return f"{secs:d}s"

def display_caption_with_fixed_percentage() -> str:
    '''
    Affiche le titre de la fenêtre Pygame avec des informations sur le cycle en cours, les itérations, les pourcentages d'avancement, la température du pixel sous la souris et si la simulation est en pause ou non.
    '''
    global iterations, iterations_per_cycle, args, simulating, mouse_value, iterations_counts
    iteration_display = (iterations - 1) if iterations > 0 else 0
    if args.do_display_percentage:
        percentage = (iterations / iterations_per_cycle) * 100
        global_percentage = ((iterations + (iterations_per_cycle * (iterations_counts - 1))) / (args.max_iteration * iterations_per_cycle)) * 100
        percentage_rounded = round(percentage, args.percentage_precision)
        global_percentage_rounded = round(global_percentage, args.percentage_precision)
        percentage_str = f"- Cycle : {percentage_rounded:.{args.percentage_precision}f}% - Total : {global_percentage_rounded:.{args.percentage_precision}f}%"
    else:
        percentage_str = ""
    paused_text = "- (PAUSED)" if simulating == False else ""
    display_value = (round(((mouse_value) * (args.display_max_temp - args.display_min_temp) / 255 + args.display_min_temp), args.display_temp_precision) if mouse_value is not None else None)
    if simulating == False and args.do_display_temp == True:
        if mouse_value is not None:
            display_value = round(((mouse_value) * (args.display_max_temp - args.display_min_temp) / 255 + args.display_min_temp), args.display_temp_precision)
            pixel_text = f"- Pixel sous souris : {display_value:06.{args.display_temp_precision}f}°C"
        else:
            pixel_text = "- Pixel sous souris : XXX.XX°C"
    else:
        pixel_text = ""
    caption = f"Chauffage collectif - Cycle {iterations_counts} / {args.max_iteration} - Itération {iteration_display} / {iterations_per_cycle} {percentage_str} {pixel_text} {paused_text}"
    return caption

def check_json_is_valid(json_file: str) -> tuple[bool, str]:
    '''
    Check whether a JSON file is valid.

    The function tries to load the given JSON file and returns a tuple
    ``(is_valid, error_message)`` where ``is_valid`` is a boolean indicating
    whether the JSON is valid and ``error_message`` contains a description of
    the error if it is not valid, or a success message otherwise.
    '''
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, "No errors detected"
    except json.JSONDecodeError as e:
        return False, e
    except FileNotFoundError as e:
        return False, e

def save_data():
    '''Sauvegarde les données de la simulation dans un fichier JSON, en utilisant une indentation si spécifiée dans les arguments.'''
    global args, all_data, json
    if args.do_save_data == False:
        return
    os.remove(args.data_save_name) if os.path.exists(args.data_save_name) else None

    with open(f"{args.data_save_name}", "w") as f:
        json.dump(obj=all_data, indent=int(args.ident_size_spaces) if args.ident_size_spaces else None, fp=f)




def iterate():
    '''
    Fonction complétant une itération complète de la simulation, incluant la mise à jour de l'affichage et le stockage des données.
    '''
    global height, width, all_data, clock, screen, running, grid, iterations, iterations_per_cycle, iterations_counts, simulating, start_position_height, start_position_width, mouse_value, actual_time
    iterations_counts += 1
    iterations = 0
    grid = [[random.randint(0, 255) for l in range(int(height))] for c in range(int(width))]
    grid_list = []
    actual_time = 0
    update_display(initial=True)
    pygame.display.set_caption(display_caption_with_fixed_percentage())

    if args.do_wait_time == True:
        time.sleep(int(wait_time))
    current_data = {
        "iterations": 1,
        "size":(
            height,
            width
        ),
        "time": {
            "time_ns": 0,
            "time_s": 0
        },
        "iterations_per_seconds": 0,
        "grid_average_final": {
            "borders": 0,
            "interior": 0,
            "difference": 0
        },
        "initial_grid": copy.deepcopy(grid),
        "grid_list": []
    }
    cycle_start_time = time.monotonic_ns()
    dt = 0
    last_screen_update_time = time.monotonic_ns()
    while iterations < iterations_per_cycle and running == True:
        if simulating == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        actual_time += time.monotonic_ns() - cycle_start_time
                        simulating = not simulating
                    if event.key == pygame.K_ESCAPE:
                        running = False

            iterations += 1

            now = time.monotonic_ns()
            dt += (now - last_screen_update_time) / 1_000_000_000
            last_screen_update_time = now

            if dt >= 1 / screen_refresh_rate:
                update_display()
                pygame.display.set_caption(display_caption_with_fixed_percentage())
                dt = 0

            
            grid = update()
            current_data["iterations"] = iterations

            if args.do_save_data == True:
                grid_list.append([col[:] for col in grid])
                current_data["grid_list"] = grid_list

            if args.do_limit_fps == True:
                clock.tick(float(args.fps))
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        cycle_start_time = time.monotonic_ns()
                        simulating = not simulating
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        iterations += 1
                        update_display()
                        grid = update()
                        if args.do_save_data == True:
                            grid_list.append([col[:] for col in grid])

            cursor_position = pygame.mouse.get_pos()
            cursor_positioned_x = (cursor_position[0] - start_position_width) // pixel_size
            cursor_positioned_y = (cursor_position[1] - start_position_height) // pixel_size
            if 0 <= cursor_positioned_x < width and 0 <= cursor_positioned_y < height:
                mouse_value = grid[cursor_positioned_x][cursor_positioned_y]
            else:
                mouse_value = None

            pygame.display.set_caption(display_caption_with_fixed_percentage())
            
            clock.tick(120)

    actual_time += time.monotonic_ns() - cycle_start_time
    
    print(f"Cycle {iterations_counts}:")
    print(f"    Itérations effectuées : {iterations}.")
    print(f"    Temps écoulé : {round((actual_time / 1_000_000_000), 2)}s.")
    print(f"    Itérations /s : {round(iterations / (actual_time / 1_000_000_000), 2)}")

    iteration_data_name = f"iteration_{iterations_counts}"
    current_data["time"]["time_ns"] = copy.deepcopy(actual_time)
    current_data["time"]["time_s"] = copy.deepcopy((actual_time / 1_000_000_000))
    current_data["iterations_per_seconds"] = copy.deepcopy(float(f"{(round((iterations / (actual_time / 1_000_000_000)), 50)):.10f}"))
    borders_total = 0
    for l in range(height):
        for c in range(width):
            if l == 0 or l == (height - 1) or c == 0 or c == (width - 1):
                borders_total += grid[c][l]
    borders_count = (2 * width) + (2 * (height - 2))
    borders_average = borders_total / borders_count
    interior_total = 0
    for l in range(1, height - 1):
        for c in range(1, width - 1):
            interior_total += grid[c][l]
    interior_count = (width - 2) * (height - 2)
    interior_average = interior_total / interior_count
    current_data["grid_average_final"]["borders"] = copy.deepcopy(borders_average)
    current_data["grid_average_final"]["interior"] = copy.deepcopy(interior_average)
    current_data["grid_average_final"]["difference"] = copy.deepcopy(abs(borders_average - interior_average))
    print(f"    Température moyenne bordures : {round(borders_average, 2)}°C.")
    print(f"    Température moyenne intérieur : {round(interior_average, 2)}°C.")
    print(f"    Différence de température : {round(abs(borders_average - interior_average), 2)}°C.\n")
    all_data[iteration_data_name] = current_data

while (iterations_counts <= (max_iteration - 1)) and (running == True):
    iterate()

pygame.quit()


total_time_ns = 0
for cycle_key, cycle_data in all_data.items():
    if isinstance(cycle_data, dict) and "time" in cycle_data and isinstance(cycle_data["time"], dict) and "time_ns" in cycle_data["time"]:
        total_time_ns += cycle_data["time"]["time_ns"]
total_iterations = 0
for cycle_key, cycle_data in all_data.items():
    if isinstance(cycle_data, dict) and "iterations" in cycle_data:
        total_iterations += cycle_data["iterations"]
if total_time_ns > 0:
    total_iterations_per_seconds = total_iterations / (total_time_ns / 1_000_000_000)
else:
    total_iterations_per_seconds = 0


print("\n\nSimulation terminée.")
print(f"    Données sauvegardées dans le fichier : '{args.data_save_name}'.")
print(f"    Itérations totales effectuées : {total_iterations}.")
print(f"    Temps total écoulé : {round((total_time_ns / 1_000_000_000), 2):.2f}s.")
print(f"    Itérations totales /s : {round(total_iterations_per_seconds, 2):.2f}")
if args.do_limit_fps == True:
    print(f"        Objectif : {args.fps:.2f} itérations /s.")
    print(f"        Ecart : {abs(round(total_iterations_per_seconds - args.fps, 2)):.2f} itérations /s.")
print(f"    Taille de la grille : {width} x {height} pixels.")


all_data["general_info"]["total_time"]["time_ns"] = copy.deepcopy(total_time_ns)
all_data["general_info"]["total_time"]["time_s"] = copy.deepcopy((total_time_ns / 1_000_000_000))
all_data["general_info"]["total_iterations"] = copy.deepcopy(total_iterations)
all_data["general_info"]["total_iterations_per_seconds"] = copy.deepcopy(total_iterations_per_seconds)



save_data()

print("\n\n")
while True:
    if args.do_save_data == False:
        print("Données non sauvegardées car l'option '--do_save_data' est désactivée.")
        break
    json_save_status = check_json_is_valid(json_file=str(args.data_save_name))
    if json_save_status[0] == True:
        print(f"Données correctement sauvegardées dans '{os.path.join(os.path.dirname(os.path.abspath(__file__)), args.data_save_name)}'.")
        break
    else:
        print(f"Erreur lors de la sauvegarde : {json_save_status[1]}")
        time.sleep(0.5)
        save_data()


print("\n\nLibération de la mémoire...")
for var in list(globals().keys()):
    if not var.startswith("__") and var not in ("sys"):
        del globals()[var]
print("Arrêt...")