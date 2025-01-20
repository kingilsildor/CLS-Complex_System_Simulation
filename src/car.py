class Car:
    def __init__(self, grid, position, direction):
        self.grid = grid
        self.position = position
        self.direction = direction
        self.in_rotary = False
        self.flag = 0

        x,y = position
        if self.grid.grid[x, y] == 1 or self.grid.grid[x, y] == 2 or self.grid.grid[x, y] == 4:
            self.grid.grid[x, y] = 10
        else:
            raise ValueError("Invalid starting position for the car.")
        

    def can_move_into(self, cell_code, check_rotary=True):
        if self.direction in ['N', 'S']:
            allowed = [1]
            if check_rotary:
                allowed.append(4)
        else:
            allowed = [2]
            if check_rotary:
                allowed.append(4)
        return (cell_code in allowed)

    def move_car(self):
        x, y = self.position

        if not self.in_rotary:
            new_x, new_y = self.next_position(x, y)
            if new_x is None or new_y is None:
                return #No suitable next cell
            
            next_code = self.grid.grid[new_x, new_y]
            
            if next_code == 4:
                self.enter_rotary(new_x, new_y)
            elif self.can_move_into(next_code, check_rotary=False):
                self.move_to(new_x, new_y, old_code = self.road_code_for_direction())
                
        else:
            self.move_rotary()
        
    def next_position(self, x, y):
        if self.direction == 'N' and x > 0:
            return (x - 1, y)
        elif self.direction == 'S' and x < self.grid.size - 1:
            return (x + 1, y)
        elif self.direction == 'E' and y < self.grid.size - 1:
            return (x, y + 1)
        elif self.direction == 'W' and y > 0:
            return (x, y - 1)
        return (None, None)


    def enter_rotary(self, new_x, new_y):
        x, y = self.position
        if self.grid.grid[new_x, new_y] == 4:
            self.grid.grid[x, y] = self.road_code_for_direction()
            self.grid.grid[new_x, new_y] = 3
            self.position = (new_x, new_y)
            self.in_rotary = True

    def move_rotary(self):
        x, y = self.position
        f = self.grid.flag[x,y]

        if f == 0:
            exit_x, exit_y = self.get_exit_position()
            if exit_x is not None and self.can_move_into(self.grid.grid[exit_x, exit_y], check_rotary=False):
                # Exit the rotary, turn last cell back to 'rotary', set new cell to car and update position
                self.grid.grid[x, y] = 4
                self.grid.grid[exit_x, exit_y] = 3
                self.position = (exit_x, exit_y)
                self.in_rotary = False
                return
            
            rotate_x, rotate_y = self.rotate_rotary(x, y)
            #Check if next rotary cell is free
            if rotate_x is not None and self.grid.grid[rotate_x, rotate_y] == 4:
                self.grid.grid[x, y] = 4
                self.grid.grid[rotate_x, rotate_y] = 3
                self.position = (rotate_x, rotate_y)
            # car stays in place
        else:
            # f1 == 1, car rotates anyway
            rotate_x, rotate_y = self.rotate_rotary(x, y)
            if rotate_x is not None and self.grid.grid[rotate_x, rotate_y] == 4:
                self.grid.grid[x, y] = 4
                self.grid.grid[rotate_x, rotate_y] = 3
                self.position = (rotate_x, rotate_y)
            # else car stays in place


    
    def get_next_rotary_position(self, position):
        x, y = position 
        rotary_pos = [
            (x, y + 1),  # Right
            (x + 1, y),  # Down
            (x, y - 1),  # Left
            (x - 1, y),  # Up
        ]
        for pos in rotary_pos:
            if 0 <= pos[0] <self.grid.size and 0 <= pos[1] < self.grid.size:
                return pos
        return None
    
    def move_to(self, new_x, new_y, old_code):
        x, y = self.position
        self.grid.grid[x, y] = old_code
        self.grid.grid[new_x, new_y] = 3
        self.position = (new_x, new_y)

    def road_code_for_direction(self):
        """
        N/S => 1 (vertical)
        E/W => 2 (horizontal)
        """
        if self.direction in ['N', 'S']:
            return 1
        else:
            return 2

    def get_exit_position(self):
        return self.next_position(*self.position)
    
    def rotate_rotary(self, x, y):
        for ring in self.grid.rotary_dict:
            if (x,y) in ring:
                idx = ring.index((x,y))
                next_idx = (idx + 1) % len(ring)
                return ring[next_idx]
        
        return (None, None)

    