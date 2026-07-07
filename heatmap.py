from ursina import Entity, color
from config import GROUND_SIZE

GRID_RESOLUTION = 10   # kitne cells (10x10 grid) — jitna zyada, utna detailed but heavy


def create_heatmap_grid():
    """
    Ground ko chhote cells mein baant kar ek visit-counter grid banata hai.
    Har cell ek Entity hai jiska color coverage ke hisaab se change hoga.
    """
    cell_size = GROUND_SIZE / GRID_RESOLUTION
    cells = []
    visit_counts = {}

    for row in range(GRID_RESOLUTION):
        cell_row = []
        for col in range(GRID_RESOLUTION):
            x = (col - GRID_RESOLUTION / 2 + 0.5) * cell_size
            z = (row - GRID_RESOLUTION / 2 + 0.5) * cell_size

            cell = Entity(
                model='quad',
                scale=(cell_size * 0.95, cell_size * 0.95),
                rotation_x=90,
                position=(x, 0.05, z),
                color=color.rgba(0, 0, 0, 0),   # shuru mein invisible
            )
            cell_row.append(cell)
            visit_counts[(row, col)] = 0
        cells.append(cell_row)

    return cells, visit_counts, cell_size


def update_heatmap(drone_position, cells, visit_counts, cell_size):
    """
    Drone ki current position ke hisaab se uski grid-cell dhoondta hai,
    visit count badhata hai, aur cell ka color update karta hai
    (jyada visits = jyada bright/warm color).
    """
    col = int((drone_position.x / cell_size) + GRID_RESOLUTION / 2)
    row = int((drone_position.z / cell_size) + GRID_RESOLUTION / 2)

    if 0 <= row < GRID_RESOLUTION and 0 <= col < GRID_RESOLUTION:
        visit_counts[(row, col)] += 1
        intensity = min(visit_counts[(row, col)] / 30, 1.0)  # 30 visits = max bright

        r = int(255 * intensity)
        g = int(80 * (1 - intensity))
        cells[row][col].color = color.rgba(r, g, 40, int(120 + intensity * 100))


