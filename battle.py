import sys
import copy
from itertools import combinations
N = -1  # global variable for dimension of board. START FROM 1


def read_from_input(file):
    """read from input file"""
    f = open(file, "r")
    line = f.readline()
    row = [int(x) for x in line.strip()]
    line = f.readline()
    column = [int(x) for x in line.strip()]
    line = f.readline()
    ships = []
    for s in range(0, len(line.strip())):
        if s == 0:
            ships.append(int(line.strip()[s]))
        elif s == 1:
            ships.append(int(line.strip()[s]))
        elif s == 2:
            ships.append(int(line.strip()[s]))
        else:
            ships.append(int(line.strip()[s]))
    if len(ships) == 3:
        ships.append(0)
    init = {}
    for r in range(0, len(row)):
        line = f.readline()
        for c in range(0, len(column)):
            if line[c] == "0":
                init[(r, c)] = ["S", "W", "L", "R", "T", "B", "M"]
            else:
                init[(r, c)] = [line[c]]
    f.close()
    global N
    N = len(row)
    return row, column, ships, init


def check_goal(board, row_con, col_con):
    """return true if every key has assigned a value"""
    global N
    for key in board:
        if len(board[key]) != 1:
            return False
    for r in range(0, N):
        r_count = 0
        for c in range(0, N):
            if "W" not in board[(r,c)]:
                r_count += 1
        if r_count != row_con[r]:
            return False
    for c in range(0, N):
        c_count = 0
        for r in range(0, N):
            if "W" not in board[(r, c)]:
                c_count += 1
        if c_count != col_con[c]:
            return False
    return True


def check_receive(board):  # True == empty, False == not empty
    return board == {}


def delete(board, key, value):
    """remove a value from the domain"""
    if value in board[key]:
        board[key].remove(value)
    return board


def modify(board, key, remain):
    """ remove values in the domain of the current position, except the ones in remain
    key = (r, c)
    remain = [str]
    use everytime after using modify function:
                    if new_b == {}:
                    return {}
    """
    #new_b = copy.deepcopy(board)
    if board == {}:
        return {}
    i = 0
    while i != len(board[key]):
        if board[key][i] not in remain:
            board[key].remove(board[key][i])
        else:
            i += 1
    if len(board[key]) == 0:
        return {}
    return board


def diagonal_constraint(board, key):
    """return a new board with removing everything else other than "w" in diagonal of ships
    return "DWO" if cannot be satisfied"""
    new_b = copy.deepcopy(board)
    if len(new_b[key]) == 0:
        return {}
    if "W" not in new_b[key]:
        if key[0] - 1 >= 0:
            if key[1] - 1 >= 0:
                new_b = modify(new_b, (key[0] - 1, key[1] - 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if key[1] + 1 < N:
                new_b = modify(new_b, (key[0] - 1, key[1] + 1), ["W"])
                if check_receive(new_b):
                    return {}
        if key[0] + 1 < N:
            if key[1] - 1 >= 0:
                new_b = modify(new_b, (key[0] + 1, key[1] - 1), ["W"])
                if check_receive(new_b):
                    return {}
            if key[1] + 1 < N:
                new_b = modify(new_b, (key[0] + 1, key[1] + 1), ["W"])
                if check_receive(new_b):
                    return {}
    return new_b


def submarine_constraint(board, key):
    """if position is submarine, all space around should be water"""
    if board[key] == ["S"]:
        curr_r = key[0]
        curr_c = key[1]
        global N
        if len(board[key]) == 0:
            return {}
        new_b = diagonal_constraint(board, key)  # diagonal, then top bottom left right
        if check_receive(new_b):  # DWO
            return {}
        else:
            if curr_r - 1 >= 0:  # top
                new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r + 1 < N:  # bottom
                new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c - 1 >= 0:  # left
                new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c + 1 < N:  # right
                new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        return new_b
    else:
        return board


def top_constraint(board, key):
    global N
    if key[0] == N - 1:
        board = delete(board, key, "T")
    if board[key] == ["T"]:
        curr_r = key[0]
        curr_c = key[1]
        new_b = diagonal_constraint(board, key)
        if check_receive(new_b):
            return {}
        else:
            if curr_r - 1 >= 0:  # top space above T can only be water
                new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r + 1 < N:
                new_b = modify(new_b, (curr_r + 1, curr_c), ["M", "B"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c - 1 >= 0:  # left as well
                new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c + 1 < N:  # right as well
                new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        return new_b
    else:
        return board


def bottom_constraint(board, key):
    """if current piece is bottom (B), there must have a piece above it (T or M)."""
    global N
    if key[0] == 0:
        board = delete(board, key, "B")
    if board[key] == ["B"]:
        curr_r = key[0]
        curr_c = key[1]
        global N
        new_b = diagonal_constraint(board, key)
        if check_receive(new_b):
            return {}
        else:
            if curr_r + 1 < N:  # bottom space below B can only be water
                new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r - 1 >= 0:  # top space above B can only be top or mid
                new_b = modify(new_b, (curr_r - 1, curr_c), ["T", "M"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c - 1 >= 0:  # left as well
                new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c + 1 < N:  # right as well
                new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        return new_b
    else:
        return board


def left_constraint(board, key):
    global N
    if key[1] == N - 1:
        board = delete(board, key, "L")
    if board[key] == ["L"]:
        curr_r = key[0]
        curr_c = key[1]

        new_b = diagonal_constraint(board, key)
        if check_receive(new_b):
            return {}
        else:
            if curr_c - 1 >= 0:  # left space beside L can only be water
                new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c + 1 < N:
                new_b = modify(new_b, (curr_r, curr_c + 1), ["M", "R"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r - 1 >= 0:  # top as well
                new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r + 1 < N:  # bottom as well
                new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        return new_b
    else:
        return board


def right_constraint(board, key):
    global N
    if key[1] == 0:
        board = delete(board, key, "R")
    if board[key] == ["R"]:
        curr_r = key[0]
        curr_c = key[1]
        global N
        new_b = diagonal_constraint(board, key)
        if check_receive(new_b):
            return {}
        else:
            if curr_c + 1 < N:  # right space beside R can only be water
                new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_c - 1 >= 0:
                new_b = modify(new_b, (curr_r, curr_c - 1), ["M", "L"])
            if curr_r - 1 >= 0:  # top as well
                new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            if curr_r + 1 < N:  # bottom as well
                new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        return new_b
    else:
        return board


def middle_constraint(board, key):
    global N
    if (key[0] == 0 and key[1] == 0) or (key[0] == N - 1 and key[1] == N - 1) or (key[0] == 0 and key[1] == N - 1) or \
        (key[0] == 0 and key[1] == N - 1):
        board = delete(board, key, "M")
    if board[key] == ["M"]:
        curr_r = key[0]
        curr_c = key[1]
        new_b = diagonal_constraint(board, key)
        if check_receive(new_b):
            return {}
        else:
            if (curr_r - 1 >= 0 and board[(curr_r - 1, curr_c)] in [["T", "M"]]) or (curr_r + 1 < N and
                                                                                     board[(curr_r + 1, curr_c)] in
                                                                                     [["B", "M"]]):
                if curr_c - 1 >= 0:  # if top position only has T or M or both, or bottom position only has B or M
                    new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])  # change left and right to "W"
                    if check_receive(new_b):  # if it is empty, return right away
                        return {}
                if curr_c + 1 < N:  # right as well
                    new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
                    if check_receive(new_b):  # if it is empty, return right away
                        return {}
                new_b = modify(new_b, (curr_r - 1, curr_c), ["T", "M"]) # if self = M only, top and bottom must be
                new_b = modify(new_b, (curr_r + 1, curr_c), ["B", "M"]) # T/M or B/M
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
            elif (curr_c - 1 >= 0 and board[(curr_r, curr_c - 1)] in [["L", "M"]]) or (curr_c + 1 < N and
                                                                                       board[(curr_r, curr_c + 1)] in
                                                                                       [["R", "M"]]):
                if curr_r - 1 >= 0:  # top as well
                    new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
                    if check_receive(new_b):  # if it is empty, return right away
                        return {}
                if curr_r + 1 < N:  # bottom as well
                    new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
                    if check_receive(new_b):  # if it is empty, return right away
                        return {}
                new_b = modify(new_b, (curr_r, curr_c - 1), ["L", "M"])
                new_b = modify(new_b, (curr_r, curr_c + 1), ["R", "M"])
                if check_receive(new_b):  # if it is empty, return right away
                    return {}
        if curr_r == 0: # bottom must be water  ##### the four boundaries cases
            new_b = modify(new_b, (curr_r + 1, curr_c), ["W"])
            if curr_c - 1 >= 0:
                new_b = modify(new_b, (curr_r, curr_c - 1), ["L", "M"])
            if curr_c + 1 < N:
                new_b = modify(new_b, (curr_r, curr_c + 1), ["R", "M"])
            if check_receive(new_b):  # if it is empty, return right away
                return {}
        elif curr_r == N - 1: # top must be water
            new_b = modify(new_b, (curr_r - 1, curr_c), ["W"])
            if curr_c - 1 >= 0:
                new_b = modify(new_b, (curr_r, curr_c - 1), ["L", "M"])
            if curr_c + 1 < N:
                new_b = modify(new_b, (curr_r, curr_c + 1), ["R", "M"])
            if check_receive(new_b):  # if it is empty, return right away
                return {}
        elif curr_c == 0: # right must be water
            new_b = modify(new_b, (curr_r, curr_c + 1), ["W"])
            if curr_r - 1 >= 0:
                new_b = modify(new_b, (curr_r - 1, curr_c), ["T", "M"])
            if curr_r + 1 < N:
                new_b = modify(new_b, (curr_r + 1, curr_c), ["B", "M"])
            if check_receive(new_b):  # if it is empty, return right away
                return {}
        elif curr_c == N - 1: # left must be water
            new_b = modify(new_b, (curr_r, curr_c - 1), ["W"])
            if curr_r - 1 >= 0:
                new_b = modify(new_b, (curr_r - 1, curr_c), ["T", "M"])
            if curr_r + 1 < N:
                new_b = modify(new_b, (curr_r + 1, curr_c), ["B", "M"])
            if check_receive(new_b):  # if it is empty, return right away
                return {}
        return new_b
    else:
        return board


def row_constraints(r_con, row, board):
    """ r_con is the constraint of the row, i.e. the maximal number of ship in row"""
    new_b = copy.deepcopy(board)
    global N
    if r_con == 0:
        for column in range(0, N):
            new_b = modify(new_b, (row, column), ["W"])
            if check_receive(new_b):
                return {}
    else:
        count = 0  # count if row constraint is satisfied, if greater => return empty
        for column in range(0, N):
            if "W" not in new_b[row, column]:  # no "W" => has to be a ship
                count += 1
        if count > r_con:
            return {}
        elif count == r_con:
            for column in range(0, N):  # if exactly equal, then the ones that have water
                if "W" in new_b[row, column]:  # can only contain "W"
                    new_b = modify(new_b, (row, column), ["W"])
                    if check_receive(new_b):
                        return {}
    return new_b


def column_constraints(c_con, column, board):
    new_b = copy.deepcopy(board)
    global N
    if c_con == 0:
        for row in range(0, N):
            new_b = modify(new_b, (row, column), ["W"])
            if check_receive(new_b):
                return {}
    else:
        count = 0  # count if row constraint is satisfied, if greater => return empty
        for row in range(0, N):
            if "W" not in new_b[row, column]:
                count += 1
        if count > c_con:
            return {}
        elif count == c_con:
            for row in range(0, N):  # if exactly equal, then the ones that have multiple variables
                if "W" in new_b[row, column]:  # can only contain "W"
                    new_b = modify(new_b, (row, column), ["W"])
                    if check_receive(new_b):
                        return {}
    return new_b


def check_ship_con(ship_con, board):
    """ship_con = tuple         return true if ship_con is satisified, i.e. all ships found.
    [0] = submarines
    [1] = destoryers
    [2] = curisers
    [3] = battleships """
    global N
    submarines = 0
    destoryers = 0
    curisers = 0
    battleships = 0
    for key in board:
        if len(board[key]) == 1:
            if "S" in board[key]:
                submarines += 1
            elif "T" in board[key]:
                if len(board[(key[0] + 1, key[1])]) == 1 and "B" in board[(key[0] + 1, key[1])]:
                    destoryers += 1
                elif len(board[(key[0] + 1, key[1])]) == 1 and "M" in board[(key[0] + 1, key[1])]:
                    if len(board[(key[0] + 2, key[1])]) == 1 and "B" in board[(key[0] + 2, key[1])]:
                        curisers += 1
                    elif len(board[(key[0] + 2, key[1])]) == 1 and "M" in board[(key[0] + 2, key[1])]:
                        if len(board[(key[0] + 3, key[1])]) == 1 and "B" in board[(key[0] + 3, key[1])]:
                            battleships += 1
            elif "L" in board[key]:
                if len(board[(key[0], key[1] + 1)]) == 1 and "R" in board[(key[0], key[1] + 1)]:
                    destoryers += 1
                elif len(board[(key[0], key[1] + 1)]) == 1 and "M" in board[(key[0], key[1] + 1)]:
                    if len(board[(key[0], key[1] + 2)]) == 1 and "R" in board[(key[0], key[1] + 2)]:
                        curisers += 1
                    elif len(board[(key[0], key[1] + 2)]) == 1 and "M" in board[(key[0], key[1] + 2)]:
                        if len(board[(key[0], key[1] + 3)]) == 1 and "R" in board[(key[0], key[1] + 3)]:
                            battleships += 1
    return submarines == ship_con[0] and destoryers == ship_con[1] and curisers == ship_con[2] and battleships == \
           ship_con[3]


def find_all_battleship(board):
    possible_head = [] ## list of tuple of (len(domain), keys, "T" or "L"), each representing a possible head
    for key in board:
        curr_r = key[0]
        curr_c = key[1]
        if curr_r + 3 < N and "T" in board[key]:
            if "M" in board[(curr_r + 1, curr_c)] and "M" in board[(curr_r + 2, curr_c)] and "B" in board[(curr_r + 3, curr_c)]:
                possible_head.append(("battleship", key, "T"))
        if curr_c + 3 < N and "L" in board[key]:
            if "M" in board[(curr_r, curr_c + 1)] and "M" in board[(curr_r, curr_c + 2)] and "R" in board[(curr_r, curr_c + 3)]:
                possible_head.append(("battleship", key, "L"))
    if len(possible_head) == 0:
        return []   # no possibility
    return possible_head


def check_b_validity(possibility, board, row_con, col_con):
    """e.g. possibility = ((ship_type, key, "T"), (ship_type, key, "L"))"""
    new_b = copy.deepcopy(board)
    for each in possibility:
        curr_r = each[1][0]
        curr_c = each[1][1]
        if each[2] == "T":
            new_b = modify(new_b, (curr_r, curr_c), ["T"])
            new_b = modify(new_b, (curr_r + 1, curr_c), ["M"])
            new_b = modify(new_b, (curr_r + 2, curr_c), ["M"])
            new_b = modify(new_b, (curr_r + 3, curr_c), ["B"])
        elif each[2] == "L":
            new_b = modify(new_b, (curr_r, curr_c), ["L"])
            new_b = modify(new_b, (curr_r, curr_c + 1), ["M"])
            new_b = modify(new_b, (curr_r, curr_c + 2), ["M"])
            new_b = modify(new_b, (curr_r, curr_c + 3), ["R"])
        new_b = check_arc_con(row_con[curr_r], col_con[curr_c], curr_r, curr_c, new_b)
        if check_receive(new_b):  # if DWO
            return False
    return True     #new_b is able to fit all positions in this posibility


def all_battleship(row_con, col_con, ship_con, board):
    """return all possibilities of battleship, recurse on each possible combination of them"""
    all_start = find_all_battleship(board) ## all possible head
    if len(all_start) < ship_con[3]:     # if no possible position
        return []
    new_b = copy.deepcopy(board)
    possible_combination = list(combinations(all_start, ship_con[3])) # list of tuples, each tuple = one possibility
    if ship_con[3] != 1:
        i = 0
        while i != len(possible_combination):
            k = (-1, -1)
            flag = False
            for item in possible_combination[i]:
                if item[1] == k:
                    flag = True
                    break
                else:
                    k = item[1]
            if flag: # if two spaces are the same
                possible_combination.remove(possible_combination[i])
            else:
                i += 1  # delete from possible_combination
    i = 0
    while i != len(possible_combination):
        if check_b_validity(possible_combination[i], new_b, row_con, col_con): #if true, move on to check the next comb; if false, delete from possible_combination
            i += 1
        else:
            possible_combination.remove(possible_combination[i])
    return possible_combination


def find_all_cruiser(board):
    possible_head = []  ## list of tuple of (len(domain), keys, "T" or "L"), each representing a possible head
    for key in board:
        curr_r = key[0]
        curr_c = key[1]
        if curr_r + 2 < N and "T" in board[key]:
            if "M" in board[(curr_r + 1, curr_c)] and "B" in board[(curr_r + 2, curr_c)]:
                possible_head.append(("cruiser", key, "T"))
        if curr_c + 2 < N and "L" in board[key]:
            if "M" in board[(curr_r, curr_c + 1)] and "R" in board[(curr_r, curr_c + 2)]:
                possible_head.append(("cruiser", key, "L"))
    if len(possible_head) == 0:
        return []
    return possible_head


def check_c_validity(possibility, board, row_con, col_con):
    new_b = copy.deepcopy(board)
    for each in possibility:
        curr_r = each[1][0]
        curr_c = each[1][1]
        if each[2] == "T":
            new_b = modify(new_b, (curr_r, curr_c), ["T"])
            new_b = modify(new_b, (curr_r + 1, curr_c), ["M"])
            new_b = modify(new_b, (curr_r + 2, curr_c), ["B"])
        elif each[2] == "L":
            new_b = modify(new_b, (curr_r, curr_c), ["L"])
            new_b = modify(new_b, (curr_r, curr_c + 1), ["M"])
            new_b = modify(new_b, (curr_r, curr_c + 2), ["R"])
        new_b = check_arc_con(row_con[curr_r], col_con[curr_c], curr_r, curr_c, new_b)
        if check_receive(new_b):  # if not DWO
            return False
    return True


def all_cruiser(row_con, col_con, ship_con, board):
    all_start = find_all_cruiser(board)  ## all possible head
    if len(all_start) < ship_con[2]:  # if no possible position
        return []
    new_b = copy.deepcopy(board)
    possible_combination = list(combinations(all_start, ship_con[2]))  # list of tuples, each tuple = one possibility
    if ship_con[2] != 1:
        i = 0
        while i != len(possible_combination):
            k = (-1, -1)
            flag = False
            for item in possible_combination[i]:
                if item[1] == k:
                    flag = True
                    break
                else:
                    k = item[1]
            if flag: # if two spaces are the same
                possible_combination.remove(possible_combination[i])
            else:
                i += 1  # delete from possible_combination
    i = 0
    while i != len(possible_combination):
        if check_c_validity(possible_combination[i], new_b, row_con, col_con):  # if true, move on to check the next comb; if false,
            i += 1                                          # delete from possible_combination
        else:
            possible_combination.remove(possible_combination[i])
    return possible_combination


def find_all_destroyer(board):
    possible_head = []  ## list of tuple of (len(domain), keys, "T" or "L"), each representing a possible head
    for key in board:
        curr_r = key[0]
        curr_c = key[1]
        if curr_r + 1 < N and "T" in board[key]:
            if "B" in board[(curr_r + 1, curr_c)]:
                possible_head.append(("destroyer", key, "T"))
        if curr_c + 1 < N and "L" in board[key]:
            if "R" in board[(curr_r, curr_c + 1)]:
                possible_head.append(("destroyer", key, "L"))
    if len(possible_head) == 0:
        return []
    return possible_head


def check_d_validity(possibility, board, row_con, col_con):
    new_b = copy.deepcopy(board)
    for each in possibility:
        curr_r = each[1][0]
        curr_c = each[1][1]
        if each[2] == "T":
            new_b = modify(new_b, (curr_r, curr_c), ["T"])
            new_b = modify(new_b, (curr_r + 1, curr_c), ["B"])
        elif each[2] == "L":
            new_b = modify(new_b, (curr_r, curr_c), ["L"])
            new_b = modify(new_b, (curr_r, curr_c + 1), ["R"])
        new_b = check_arc_con(row_con[curr_r], col_con[curr_c], curr_r, curr_c, new_b)
        if check_receive(new_b):  # if not DWO
            return False
    return True


def all_destroyer(row_con, col_con, ship_con, board):
    """found = list of (key tuple)ships found
    num are the numbers of each ship found
    impossible is the list of """
    all_start = find_all_destroyer(board)  ## all possible head
    if len(all_start) < ship_con[1]:  # if no possible position
        return []
    new_b = copy.deepcopy(board)
    possible_combination = list(combinations(all_start, ship_con[1]))  # list of tuples, each tuple = one possibility
    if ship_con[1] != 1:
        i = 0
        while i != len(possible_combination):
            k = (-1, -1)
            flag = False
            for item in possible_combination[i]:
                if item[1] == k:
                    flag = True
                    break
                else:
                    k = item[1]
            if flag: # if two spaces are the same
                possible_combination.remove(possible_combination[i])
            else:
                i += 1  # delete from possible_combination
    i = 0
    while i != len(possible_combination):
        if check_d_validity(possible_combination[i], new_b, row_con, col_con):  # if true, move on to check the next comb; if false,
            i += 1                                          # delete from possible_combination
        else:
            possible_combination.remove(possible_combination[i])
    return possible_combination


def find_all_submarine(board):
    possible_head = []  ## list of tuple of (len(domain), keys, "T" or "L"), each representing a possible head
    for key in board:
        if "S" in board[key]:
            possible_head.append(("submarine", key))
    if len(possible_head) == 0:
        return []
    return possible_head


def check_s_validity(possibility, board, row_con, col_con):
    new_b = copy.deepcopy(board)
    for each in possibility:
        curr_r = each[1][0]
        curr_c = each[1][1]
        new_b = modify(new_b, (curr_r, curr_c), ["S"])
        new_b = check_arc_con(row_con[curr_r], col_con[curr_c], curr_r, curr_c, new_b)
        if check_receive(new_b):  # if DWO
            return False
    return True


def all_submarine(row_con, col_con, ship_con, board):
    all_start = find_all_submarine(board)  ## all possible head
    if len(all_start) < ship_con[0]:  # if no possible position
        return []
    new_b = copy.deepcopy(board)
    possible_combination = list(combinations(all_start, ship_con[0]))  # list of tuples, each tuple = one possibility
    if ship_con[0] != 1:
        i = 0
        while i != len(possible_combination):
            k = (-1, -1)
            flag = False
            for item in possible_combination[i]:
                if item[1] == k:
                    flag = True
                    break
                else:
                    k = item[1]
            if flag: # if two spaces are the same
                possible_combination.remove(possible_combination[i])
            else:
                i += 1  # delete from possible_combination
    i = 0
    while i != len(possible_combination):
        if check_s_validity(possible_combination[i], new_b, row_con, col_con):  # if true, move on to check the next comb; if false,
            i += 1  # delete from possible_combination
        else:
            possible_combination.remove(possible_combination[i])
    return possible_combination


def apply_change(row_con, col_con, possibility, board):
    """modify the board to apply possibility on board
    "e.g. possibility = ((ship_type, key, "T"), (ship_type, key, "L"))"""
    for each in possibility:
        curr_r = each[1][0]
        curr_c = each[1][1]
        if each[0] == "battleship":
            if each[2] == "T":
                board = modify(board, (curr_r, curr_c), ["T"])
                board = modify(board, (curr_r + 1, curr_c), ["M"])
                board = modify(board, (curr_r + 2, curr_c), ["M"])
                board = modify(board, (curr_r + 3, curr_c), ["B"])
            elif each[2] == "L":
                board = modify(board, (curr_r, curr_c), ["L"])
                board = modify(board, (curr_r, curr_c + 1), ["M"])
                board = modify(board, (curr_r, curr_c + 2), ["M"])
                board = modify(board, (curr_r, curr_c + 3), ["R"])
        elif each[0] == "cruiser":
            if each[2] == "T":
                board = modify(board, (curr_r, curr_c), ["T"])
                board = modify(board, (curr_r + 1, curr_c), ["M"])
                board = modify(board, (curr_r + 2, curr_c), ["B"])
            elif each[2] == "L":
                board = modify(board, (curr_r, curr_c), ["L"])
                board = modify(board, (curr_r, curr_c + 1), ["M"])
                board = modify(board, (curr_r, curr_c + 2), ["R"])
        elif each[0] == "destroyer":
            if each[2] == "T":
                board = modify(board, (curr_r, curr_c), ["T"])
                board = modify(board, (curr_r + 1, curr_c), ["B"])
            elif each[2] == "L":
                board = modify(board, (curr_r, curr_c), ["L"])
                board = modify(board, (curr_r, curr_c + 1), ["R"])
        elif each[0] == "submarine":
            board = modify(board, (curr_r, curr_c), ["S"])
        board = check_arc_con(row_con[curr_r], col_con[curr_c], curr_r, curr_c, board)
    return board


def find_s(row_con, col_con, ship_con, board):
    """given board modified by battleship, cruisers and destroyers, find submarine"""
    if ship_con[0] == 0:
        if check_ship_con(ship_con, board) and check_goal(board):
            return board
        else:
            return {}
    else:
        submarine = all_submarine(row_con, col_con, ship_con, board)
        if not submarine:
            return {}
        for each_s in submarine:
            new_b = copy.deepcopy(board)
            new_b = apply_change(row_con, col_con, each_s, new_b)
            for key in new_b: ### check arc constraint after fitting everything
                new_b = check_arc_con(row_con[key[0]], col_con[key[1]], key[0], key[1], new_b)
                if check_receive(new_b):
                    return {}
            if check_ship_con(ship_con, new_b) and check_goal(new_b, row_con, col_con):
                return new_b
        return {} # if nothing can satisfy problem


def find_d_s(row_con, col_con, ship_con, board):
    "given board modified by battleship and cruisers, find destroyers"
    if ship_con[1] == 0:
        return find_s(row_con, col_con, ship_con, board)
    else:
        destroyer = all_destroyer(row_con, col_con, ship_con, board)
        if not destroyer:
            return {}
        for each_d in destroyer: # all destroyer comb that won't cause trouble by themselves given current ships
            new_b = copy.deepcopy(board)
            new_b = apply_change(row_con, col_con, each_d, new_b)
            result = find_s(row_con, col_con, ship_con, new_b)
            if check_ship_con(ship_con, result) and check_goal(result, row_con, col_con):
                return result
        return {} # if nothing can satisfy problem


def find_c_d_s(row_con, col_con, ship_con, board):
    """given board modified by battleship, find cruisers """
    global N
    if ship_con[2] == 0:
        return find_d_s(row_con, col_con, ship_con, board)
    else:
        cruiser = all_cruiser(row_con, col_con, ship_con, board)
        if not cruiser:
            return {}
        for each_c in cruiser:# all cruiser comb that won't cause trouble by themselves given current battleship
            new_b = copy.deepcopy(board)
            new_b = apply_change(row_con, col_con, each_c, new_b)
            result = find_d_s(row_con, col_con, ship_con, new_b)
            if check_ship_con(ship_con, result) and check_goal(result, row_con, col_con):
                return result
        return {} # if nothing can satisfy problem


def search_solution(row_con, col_con, ship_con, board):
    """constraints, then board, then number of each type of ships found, tracker = explored units = [(),()]
    all_ship functions return list of possibility
    e.g. possibility = ((len, key, "T"), (len, key, "L"))"""
    if ship_con[3] == 0:
        return find_c_d_s(row_con, col_con, ship_con, board)
    else:
        battleship = all_battleship(row_con, col_con, ship_con, board)
        for each_b in battleship: # all battleship comb that won't cause trouble by themselves
            new_b = copy.deepcopy(board)
            new_b = apply_change(row_con, col_con, each_b, new_b)
            result = find_c_d_s(row_con, col_con, ship_con, new_b)
            if check_ship_con(ship_con, result) and check_goal(result, row_con, col_con):
                return result


def check_arc_con(row_con, col_con, row, column, board):
    """ row_con should be a number"""
    global N
    if check_receive(board):  # check after modification
        return {}
    new_b = copy.deepcopy(board)
    if board[(row, column)] == ["S"]:
        new_b = submarine_constraint(new_b, (row, column))
    elif board[(row, column)] == ["T"]:
        new_b = top_constraint(new_b, (row, column))
    elif board[(row, column)] == ["B"]:
        new_b = bottom_constraint(new_b, (row, column))
    elif board[(row, column)] == ["L"]:
        new_b = left_constraint(new_b, (row, column))
    elif board[(row, column)] == ["R"]:
        new_b = right_constraint(new_b, (row, column))
    elif board[(row, column)] == ["M"]:
        new_b = middle_constraint(new_b, (row, column))
    if check_receive(new_b):  # check after modification
        return {}
    new_b = row_constraints(row_con, row, new_b)
    if check_receive(new_b):
        return {}
    new_b = column_constraints(col_con, column, new_b)
    if check_receive(new_b):
        return {}
    if new_b != board:
        check_arc_con(row_con,col_con, row, column, new_b)
    return new_b


if __name__ == '__main__':
    filename = sys.argv[1]
    # store in list of list; first list = first line of file
    row_c, column_c, number_of_ships, initial_board = read_from_input(filename)
    board = copy.deepcopy(initial_board)
    for r in range(0, N):  # do arc constraint before searching
        for c in range(0, N):
            board = check_arc_con(row_c[r], column_c[c], r, c, board)
    board = search_solution(row_c, column_c, number_of_ships, board)
    line = ""
    for r in range(0, N):
        for c in range(0, N):
            line = line + board[(r,c)][0]
        line += "\n"
    filename = sys.argv[2]
    f = open(filename, "w")
    f.write(line)
    f.close()
