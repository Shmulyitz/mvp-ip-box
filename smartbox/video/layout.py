from dataclasses import dataclass


@dataclass
class CellGeometry:
    cell_index: int
    x: int
    y: int
    width: int
    height: int


def compute_grid(grid_size: int) -> list[CellGeometry]:
    if grid_size == 1:
        return [CellGeometry(0, 0, 0, 1920, 1080)]
    if grid_size == 4:
        out = []
        for i in range(4):
            row = i // 2
            col = i % 2
            out.append(CellGeometry(i, col * 960, row * 540, 960, 540))
        return out
    if grid_size == 9:
        out = []
        for i in range(9):
            row = i // 3
            col = i % 3
            out.append(CellGeometry(i, col * 640, row * 360, 640, 360))
        return out
    if grid_size == 16:
        out = []
        for i in range(16):
            row = i // 4
            col = i % 4
            out.append(CellGeometry(i, col * 480, row * 270, 480, 270))
        return out
    raise ValueError("Unsupported grid size")
