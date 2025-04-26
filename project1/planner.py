import sys

def read_vacuum_world(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    cols = int(lines[0])
    rows = int(lines[1])
    grid = [list(lines[i + 2]) for i in range(rows)]

    return cols, rows, grid

def ucs(grid, start_pos, dirty_cells):
    rows, cols = len(grid), len(grid[0])

    generated_nodes = 0
    expanded_nodes = 0

    # directions mapping (N, S, E, W)
    direction_map = {
        (-1, 0): 'N',  # up = north
        (1, 0): 'S',   # down = south
        (0, -1): 'W',  # left = west
        (0, 1): 'E'    # right = east
    }

    # initial state: (cost, position, remaining dirt, path, directions)
    frontier = [(0, start_pos, frozenset(dirty_cells), [start_pos], [])]
    visited = set()

    best_dirt_left = dirty_cells
    best_path = []

    while frontier:
        # SORT frontier by cost (first element of the tuple)
        # ! this is what makes it different from dfs bc we keep track of cost
        frontier.sort()

        # get the option with the least cost
        cost, pos, dirt_left, path, directions = frontier.pop(0)

        # incrememnt expanded nodes since we are looking at a new node
        expanded_nodes += 1

        # skip already visited nodes
        if (pos, dirt_left) in visited:
            continue

        # add this node to visited
        visited.add((pos, dirt_left))

        # check if the current path has cleaned more dirty cells
        if len(dirt_left) < len(best_dirt_left):
            best_dirt_left = dirt_left
            best_path = directions

        # all clean
        if not dirt_left:
            return directions, generated_nodes, expanded_nodes

        # explore neighboring cells (up, down, left, right)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = pos[0] + dr, pos[1] + dc

            # make sure we can visit this position (not out of bounds or blocked)
            if 0 <= r < rows and 0 <= c < cols and grid[r][c] != '#':
                new_pos = (r, c)
                new_dirt = dirt_left - {new_pos} if new_pos in dirt_left else dirt_left
                new_path = path + [new_pos]
                new_directions = directions + [direction_map[(dr, dc)]]

                # vacumn dirty spaces
                if new_pos in dirt_left:
                    new_directions.append('V')

                # add the new state to the frontier and count it as generated
                frontier.append((cost + 1, new_pos, new_dirt, new_path, new_directions))
                # incremement generated because we are generating new possibilites to explore
                generated_nodes += 1

    # if we can't clean all cells (blocked, etc.), and no more to visit
    return best_path, generated_nodes, expanded_nodes

def dfs(grid, start_pos, dirty_cells):
    rows, cols = len(grid), len(grid[0])
    
    direction_map = {
        (-1, 0): 'N',
        (1, 0): 'S',
        (0, -1): 'W',
        (0, 1): 'E'
    }

    stack = [(start_pos, frozenset(dirty_cells), [start_pos], [])]
    visited = set()

    generated_nodes = 0
    expanded_nodes = 0

    best_dirt_left = dirty_cells
    best_path = []

    while stack:
        # just pop off the next direction to take (no cost in consideration)
        pos, dirt_left, path, directions = stack.pop()
        expanded_nodes += 1

        # if already visited, don't go again
        if (pos, dirt_left) in visited:
            continue
        # else, add it to visited
        visited.add((pos, dirt_left))

        # check if the current path has cleaned more dirty cells
        if len(dirt_left) < len(best_dirt_left):
            best_dirt_left = dirt_left
            best_path = directions

        # return if everything is clean
        if not dirt_left:
            return directions, generated_nodes, expanded_nodes

        r, c = pos
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # get the new positions to explore from this position
            nr, nc = r + dr, c + dc

            # make sure we can visit this position (not out of bounds or blocked)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
                # update the stack w this position
                new_pos = (nr, nc)
                new_dirt = dirt_left - {new_pos} if new_pos in dirt_left else dirt_left
                new_path = path + [new_pos]
                new_directions = directions + [direction_map[(dr, dc)]]

                # vacumn when on dirty cell
                if new_pos in dirt_left:
                    new_directions.append('V')

                stack.append((new_pos, new_dirt, new_path, new_directions))
                generated_nodes += 1

    return best_path, generated_nodes, expanded_nodes

def main():
    # usage: python3 planner.py [algorithm] [world−file]
    if len(sys.argv) < 3:
        print("Usage: python planner.py [algorithm] [world−file]")
        sys.exit(1)

    algo = sys.argv[1]
    file = sys.argv[2]

    cols, rows, grid = read_vacuum_world(file)

    # print(f"Grid size: {rows}x{cols}")
    # for row in grid:
    #     print(" ".join(row))

    start = None
    dirty = set()

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '@':
                start = (r, c)
            elif grid[r][c] == '*':
                dirty.add((r, c))

    if algo == "uniform-cost":
        path, generated, expanded = ucs(grid, start, dirty)
    elif algo == "depth-first":
        path, generated, expanded = dfs(grid, start, dirty)
    else:
        print("Unidentified algorithm specified")

    # print results
    for i in path:
        print(i)

    print("Nodes Generated: ", generated)
    print("Nodes Expanded: ", expanded)

if __name__ == "__main__":
    main()