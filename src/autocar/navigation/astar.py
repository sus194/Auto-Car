import heapq
from typing import List, Tuple, Dict, Optional

Grid = List[List[int]]  # 0=free, 1=obstacle

def astar(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    h = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    w, hg = len(grid[0]), len(grid)

    def nbrs(x, y):
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < hg and grid[ny][nx] == 0:
                yield (nx, ny)

    openq = [(h(start, goal), 0, start)]
    came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    g_costs = {start: 0}

    while openq:
        _, g_cost, u = heapq.heappop(openq)

        if u == goal:
            path = [u]
            while came_from[path[-1]] is not None:
                path.append(came_from[path[-1]])
            return list(reversed(path))

        for v in nbrs(*u):
            new_g_cost = g_cost + 1
            if v not in g_costs or new_g_cost < g_costs[v]:
                g_costs[v] = new_g_cost
                came_from[v] = u
                f_cost = new_g_cost + h(v, goal)
                heapq.heappush(openq, (f_cost, new_g_cost, v))
    return []
