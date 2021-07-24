from other_bots import heuristic


class Player45:
    def __init__(self):
        self.grid = {
            '00': ['01', '10'],
            '01': ['00', '02'],
            '02': ['01', '12'],
            '10': ['00', '20'],
            '11': ['11'],
            '12': ['02', '22'],
            '20': ['10', '21'],
            '21': ['20', '22'],
            '22': ['12', '21'],
        }

    def PossibleMoves(self, board, block, old_move):
        # first move of the game
        if old_move == (-1, -1):
            valid_moves = []
            for i in range(9):
                for j in range(9):
                    valid_moves.append((i, j))
            return valid_moves

        x = old_move[0] % 3
        y = old_move[1] % 3
        arr = self.grid[str(x) + str(y)]
        valid_moves = []
        for k in arr:
            X = int(k[0])
            Y = int(k[1])
            PossibleBlock = 3 * X + Y
            if block[PossibleBlock] != '-':
                continue
            for i in range(3):
                for j in range(3):
                    # print(3*X+i,3*Y+j)
                    if board[3 * X + i][3 * Y + j] == '-':
                        valid_moves.append([3 * X + i, 3 * Y + j])
        # case of free move
        if len(valid_moves) == 0:
            for X in range(3):
                for Y in range(3):
                    PossibleBlock = 3 * X + Y
                    if block[PossibleBlock] != '-':
                        continue
                    for i in range(3):
                        for j in range(3):
                            if board[3 * X + i][3 * Y + j] == '-':
                                valid_moves.append([3 * X + i, 3 * Y + j])
        return valid_moves

    def check_win(self, board, moveX, moveY, cur):

        if board[moveX][0] == cur and board[moveX][1] == cur and board[moveX][2] == cur:
            return cur

        elif (
            board[0][moveY] == cur and board[1][moveY] == cur and board[2][moveY] == cur
        ):
            return cur

        elif (
            moveX == moveY
            and board[0][0] == cur
            and board[1][1] == cur
            and board[2][2] == cur
        ):
            return cur

        elif (
            moveX + moveY == 2
            and board[0][2] == cur
            and board[1][1] == cur
            and board[2][0] == cur
        ):
            return cur

        else:
            for i in range(3):
                for j in range(3):
                    if board[i][j] == '-':
                        return '-'
            return 'D'

    def terminaltest(self, block, player):
        row = [True] * 3
        col = [True] * 3
        diag = [True] * 2
        for i in range(3):
            for j in range(3):
                if block[3 * i + j] != player:
                    row[i] = False
                    col[j] = False
                    if i + j == 2:
                        diag[1] = False
                    if i == j:
                        diag[0] = False
        return (
            row[0]
            or row[1]
            or row[2]
            or col[0]
            or col[1]
            or col[2]
            or diag[0]
            or diag[1]
        )

    def update(self, board, block, move, player):

        temp_board = []
        for i in range(9):
            temp = []
            for j in range(9):
                temp.append(board[i][j])
            temp_board.append(temp)

        temp_board[move[0]][move[1]] = player

        temp_block = []
        for i in range(9):
            temp_block.append(block[i])

        tiny = []
        startX = (move[0] // 3) * 3
        startY = (move[1] // 3) * 3
        for i in range(startX, startX + 3):
            temp = []
            for j in range(startY, startY + 3):
                temp.append(temp_board[i][j])
            tiny.append(temp)

        block_index = startX + (move[1] // 3)
        temp_block[block_index] = self.check_win(
            temp_board, move[0] % 3, move[1] % 3, player
        )

        return temp_board, temp_block

    def alphabeta(
        self, board, block, old_move, flag, depth, alpha, beta, maximizingPlayer
    ):

        me = flag
        op = 'x'
        if me == 'x':
            op = 'o'

        if depth == 5 or self.terminaltest(block, 'x') or self.terminaltest(block, 'o'):

            return heuristic.check(board, block, flag)

        next_moves = self.PossibleMoves(board, block, old_move)

        bestchild = None

        if maximizingPlayer:
            utility = -1000
            for child in next_moves:
                temp_board, temp_block = self.update(board, block, child, me)
                child_utility = self.alphabeta(
                    temp_board, temp_block, child, flag, depth + 1, alpha, beta, False
                )
                if child_utility > utility:
                    utility = child_utility
                    bestchild = child
                alpha = max(alpha, utility)
                if beta <= alpha:
                    break
            if depth > 0:
                return utility
            else:
                return bestchild

        else:
            utility = 1000
            for child in next_moves:
                temp_board, temp_block = self.update(board, block, child, op)
                child_utility = self.alphabeta(
                    temp_board, temp_block, child, flag, depth + 1, alpha, beta, True
                )
                if child_utility < utility:
                    utility = child_utility
                    bestchild = child
                beta = min(beta, utility)
                if beta <= alpha:
                    break
            return utility

    def move(self, board, block, old_move, flag):
        return tuple(self.alphabeta(board, block, old_move, flag, 0, -1000, 1000, True))
