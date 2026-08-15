class CSPSolver:
    def __init__(self, grid_size, grid_matrix, connectors_list):
        self.size = grid_size
        self.grid = grid_matrix
        self.connectors = connectors_list
        self.half_size = grid_size // 2

        self.variables = [(r, c) for r in range(grid_size) for c in range(grid_size)]
        self.domains = self._initialize_domains()

    def _initialize_domains(self):
        domains = {}
        for r in range(self.size):
            for c in range(self.size):
                state = self.grid[r][c].state
                if state == 0:
                    domains[(r, c)] = {1, 2}
                else:
                    domains[(r, c)] = {state}
        return domains

    def is_valid_grid(self):
        for i in range(self.size):
            for j in range(self.size - 2):
                h1, h2, h3 = (
                    self.domains[(i, j)],
                    self.domains[(i, j + 1)],
                    self.domains[(i, j + 2)],
                )
                if len(h1) == 1 and h1 == h2 and h2 == h3:
                    return False, f"3-in-a-row violation in row {i}"

                v1, v2, v3 = (
                    self.domains[(j, i)],
                    self.domains[(j + 1, i)],
                    self.domains[(j + 2, i)],
                )
                if len(v1) == 1 and v1 == v2 and v2 == v3:
                    return False, f"3-in-a-row violation in column {i}"

        for i in range(self.size):
            row_vars = [(i, c) for c in range(self.size)]
            col_vars = [(r, i) for r in range(self.size)]

            for line_name, line_vars in [("row", row_vars), ("column", col_vars)]:
                count_1 = sum(1 for var in line_vars if self.domains[var] == {1})
                count_2 = sum(1 for var in line_vars if self.domains[var] == {2})

                if count_1 > self.half_size:
                    return False, f"Too many Xs in {line_name} {i}"
                if count_2 > self.half_size:
                    return False, f"Too many Os in {line_name} {i}"

        for conn in self.connectors:
            if conn.state != 0:
                d1, d2 = self.domains[conn.tile1_pos], self.domains[conn.tile2_pos]

                if len(d1) == 1 and len(d2) == 1:
                    if conn.state == 1 and d1 != d2:
                        return (
                            False,
                            f"Equal connector (=) violation at {conn.tile1_pos} & {conn.tile2_pos}",
                        )
                    if conn.state == 2 and d1 == d2:
                        return (
                            False,
                            f"Opposite connector (X) violation at {conn.tile1_pos} & {conn.tile2_pos}",
                        )

        return True, "Valid"

    def _get_triplet_neighbors(self, t1, t2):
        r1, c1 = t1
        r2, c2 = t2
        neighbors = []

        if r1 == r2:
            min_c, max_c = min(c1, c2), max(c1, c2)
            if min_c - 1 >= 0:
                neighbors.append((r1, min_c - 1))
            if max_c + 1 < self.size:
                neighbors.append((r1, max_c + 1))

        elif c1 == c2:
            min_r, max_r = min(r1, r2), max(r1, r2)
            if min_r - 1 >= 0:
                neighbors.append((min_r - 1, c1))
            if max_r + 1 < self.size:
                neighbors.append((max_r + 1, c1))

        return neighbors

    def propagate_connectors(self):
            changed = False

            for conn in self.connectors:
                if conn.state != 0:
                    t1, t2 = conn.tile1_pos, conn.tile2_pos
                    d1, d2 = self.domains[t1], self.domains[t2]

                    if conn.state == 1:
                        # an equals connector forces both cells to share a symbol, so intersect their domains
                        common = d1.intersection(d2)

                        if len(d1) > len(common):
                            self.domains[t1] = common
                            changed = True

                        if len(d2) > len(common):
                            self.domains[t2] = common
                            changed = True

                        # if a fixed neighbor next to an equals pair would make 3 in a row, force the pair to the opposite symbol
                        for symbol in (1, 2):
                            opp_symbol = 2 if symbol == 1 else 1
                        
                            for t3 in self._get_triplet_neighbors(t1, t2):
                                if self.domains[t3] == {symbol}:
                                    if len(self.domains[t1]) > 1 or self.domains[t1] == {symbol}:
                                        self.domains[t1] = {opp_symbol}
                                        changed = True
                                    if len(self.domains[t2]) > 1 or self.domains[t2] == {symbol}:
                                        self.domains[t2] = {opp_symbol}
                                        changed = True

                    elif conn.state == 2:
                        # once one side of a cross connector is fixed, the other side is forced to the opposite symbol
                        if len(d1) == 1:
                            val = next(iter(d1))
                            opp_val = 1 if val == 2 else 2
                            if len(d2) > 1:
                                self.domains[t2] = {opp_val}
                                changed = True

                        if len(d2) == 1:
                            val = next(iter(d2))
                            opp_val = 1 if val == 2 else 2
                            if len(d1) > 1:
                                self.domains[t1] = {opp_val}
                                changed = True

            return changed

    def _check_triplets(self, v1, v2, v3):
        changed = False

        # if two cells in a window of three share a symbol, the third is forced to the opposite one
        for a, b, c in [(v1, v2, v3), (v2, v3, v1), (v1, v3, v2)]:
            for symbol in (1, 2):
                opp_symbol = 2 if symbol == 1 else 1

                if self.domains[a] == {symbol} and self.domains[b] == {symbol}:
                    if len(self.domains[c]) > 1:
                        self.domains[c] = {opp_symbol}
                        changed = True

        return changed

    def propagate_no_three_in_a_row(self):
        changed = False

        for i in range(self.size):
            for j in range(self.size - 2):
                h_v1, h_v2, h_v3 = (i, j), (i, j + 1), (i, j + 2)
                if self._check_triplets(h_v1, h_v2, h_v3):
                    changed = True

                v_v1, v_v2, v_v3 = (j, i), (j + 1, i), (j + 2, i)
                if self._check_triplets(v_v1, v_v2, v_v3):
                    changed = True

        return changed

    def _has_three_in_a_row(self, line_values, symbol):
        for k in range(len(line_values) - 2):
            if (
                line_values[k] == symbol
                and line_values[k + 1] == symbol
                and line_values[k + 2] == symbol
            ):
                return True
        return False

    def _balance_line(self, line_vars):
        changed = False

        count_1 = sum(1 for var in line_vars if self.domains[var] == {1})
        count_2 = sum(1 for var in line_vars if self.domains[var] == {2})

        # once a line hits its quota for a symbol, every remaining undecided cell in it is forced to the other symbol
        if count_1 == self.half_size:
            for var in line_vars:
                if len(self.domains[var]) > 1:
                    self.domains[var] = {2}
                    changed = True

        if count_2 == self.half_size:
            for var in line_vars:
                if len(self.domains[var]) > 1:
                    self.domains[var] = {1}
                    changed = True

        unassigned = [var for var in line_vars if len(self.domains[var]) > 1]

        # if a cell taking a symbol would complete the quota and force a three-in-a-row, rule that symbol out for it
        for symbol in (1, 2):
            current_count = count_1 if symbol == 1 else count_2
            opp_symbol = 2 if symbol == 1 else 1

            if current_count == self.half_size - 1:

                for test_var in unassigned:
                    temp_line = []
                    for var in line_vars:
                        if var == test_var:
                            temp_line.append(symbol)
                        elif len(self.domains[var]) == 1:
                            temp_line.append(next(iter(self.domains[var])))
                        else:
                            temp_line.append(opp_symbol)

                    if self._has_three_in_a_row(temp_line, opp_symbol):
                        self.domains[test_var] = {opp_symbol}
                        changed = True

        # same as above but for a whole equals pair at once, since its two cells move together
        line_set = set(line_vars)
        for conn in self.connectors:
            if conn.state != 1:
                continue

            t1, t2 = conn.tile1_pos, conn.tile2_pos
            if t1 not in line_set or t2 not in line_set:
                continue

            if len(self.domains[t1]) == 1 or len(self.domains[t2]) == 1:
                continue

            for symbol in (1, 2):
                current_count = count_1 if symbol == 1 else count_2
                opp_symbol = 2 if symbol == 1 else 1

                if current_count == self.half_size - 2:
                    temp_line = []
                    for var in line_vars:
                        if var == t1 or var == t2:
                            temp_line.append(symbol)
                        elif len(self.domains[var]) == 1:
                            temp_line.append(next(iter(self.domains[var])))
                        else:
                            temp_line.append(opp_symbol)

                    if self._has_three_in_a_row(temp_line, opp_symbol):
                        self.domains[t1] = {opp_symbol}
                        self.domains[t2] = {opp_symbol}
                        changed = True
        return changed

    def propagate_balance(self):
        changed = False

        for i in range(self.size):
            row_vars = [(i, c) for c in range(self.size)]
            if self._balance_line(row_vars):
                changed = True

            col_vars = [(r, i) for r in range(self.size)]
            if self._balance_line(col_vars):
                changed = True

        return changed

    def solve(self):
        is_valid, message = self.is_valid_grid()
        if not is_valid:
            return None, message

        while True:
            c1 = self.propagate_connectors()
            c2 = self.propagate_balance()
            c3 = self.propagate_no_three_in_a_row()

            if not c1 and not c2 and not c3:
                break

        for var in self.variables:
            if len(self.domains[var]) > 1:
                return None, None

        return {var: next(iter(self.domains[var])) for var in self.variables}, None

def solve_mambo(grid_size, grid_matrix, connectors_list):
    solver = CSPSolver(grid_size, grid_matrix, connectors_list)
    solution, message = solver.solve()

    if solution:
        for (r, c), state in solution.items():
            grid_matrix[r][c].state = state
        return True, None
    return False, message