import random
import copy

class Player5:
	def __init__(self):
		self.DEbug=True

		self.validBlocks= [[0 for i in range(3)] for j in range(3)]
		self.validBlocks[0][0]=((1,0),(0, 1))
		self.validBlocks[0][1]=((0,0),(0, 2))
		self.validBlocks[0][2]=((0,1),(1, 2))
		self.validBlocks[1][0]=((0,0),(2, 0))
		self.validBlocks[1][1]=((1,1),)
		self.validBlocks[1][2]=((0,2),(2, 2))
		self.validBlocks[2][0]=((1, 0),(2, 1))
		self.validBlocks[2][1]=((2,0),(2, 2))
		self.validBlocks[2][2]=((2,1),(1, 2))

		self.allList = ((0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2))

		self.heuristicDict={}
		self.scoreDict = {}
		#0 - Empty
		#1 - Our Marking
		#2 - Opponent Marking
		#3 - Draw(Only valid for blocks)
		self.weGetOne = 3
		self.weGetTwo = 30
		self.weGetAll = 300
		self.theyGetOne = -3
		self.theyGetTwo = -90
		self.theyGetAll = -300
		self.neutral = 0

		self.scoreDict[(0,0,0)] = self.neutral
		self.scoreDict[(0,0,1)] = self.weGetOne
		self.scoreDict[(0,1,1)] = self.weGetTwo
		self.scoreDict[(0,0,2)] = self.theyGetOne
		self.scoreDict[(0,1,2)] = self.neutral
		self.scoreDict[(0,2,2)] = self.theyGetTwo
		self.scoreDict[(1,1,1)] = self.weGetAll
		self.scoreDict[(1,1,2)] = self.neutral
		self.scoreDict[(1,2,2)] = self.neutral
		self.scoreDict[(2,2,2)] = self.theyGetAll

	def checkAllowedBlocks(self,prevMove, BlockStatus):
		if prevMove[0] < 0 and prevMove[1] < 0:
			return self.allList
		allowedBlocks = self.validBlocks[prevMove[0]%3][prevMove[1]%3]
		finalAllowedBlocks = []
		for i in allowedBlocks:
			if BlockStatus[i[0]][i[1]] == 0:
				finalAllowedBlocks.append(i)
		if len(finalAllowedBlocks)==0:
			for i in self.allList:
				if BlockStatus[i[0]][i[1]] == 0:
					finalAllowedBlocks.append(i)
		return finalAllowedBlocks

	def checkAllowedMarkers(self,block):
		allowed=[]
		for i in range(3):
			for j in range(3):
				if block[i][j] == 0:
					allowed.append((i, j))
		allowed = tuple(allowed)
		return allowed

	def getAllowedMoves(self, currentBoard, currentBlockStatus, prevMove):
		moveList=[]
		for allowedBlock in self.checkAllowedBlocks(prevMove, currentBlockStatus):
			moveList += [(3*allowedBlock[0]+move[0], 3*allowedBlock[1]+move[1]) for move in self.checkAllowedMarkers(currentBoard[allowedBlock[0]][allowedBlock[1]])]
		return moveList

	def getBlockScore(self,heuristicBlock):
		heuristicBlock = tuple([tuple(heuristicBlock[i]) for i in range(3)])
		if heuristicBlock not in self.heuristicDict:
			currentScore = 0
			blockOwner = 0
			for i in range(3):
				currow=[heuristicBlock[i][j] for j in range(3)]
				currow.sort()

				curcol=[heuristicBlock[j][i] for j in range(3)]
				curcol.sort()

				rowScore = self.scoreDict[tuple(currow)]
				colScore = self.scoreDict[tuple(curcol)]
				if rowScore == self.weGetAll or colScore == self.weGetAll:
					blockOwner = 1
					break
				elif rowScore == self.theyGetAll or colScore == self.theyGetAll:
					blockOwner = 2
					break
				currentScore += rowScore+colScore

			diagonal1 = [heuristicBlock[0][0], heuristicBlock[1][1], heuristicBlock[2][2]]
			diagonal2 = [heuristicBlock[0][2], heuristicBlock[1][1], heuristicBlock[2][0]]
			diagonal1.sort()
			diagonal2.sort()
			diagonal1Score = self.scoreDict[tuple(diagonal1)]
			diagonal2Score = self.scoreDict[tuple(diagonal2)]
			if diagonal1Score == self.weGetAll or diagonal2Score == self.weGetAll:
				blockOwner = 1
			elif diagonal1Score == self.theyGetAll or diagonal2Score == self.theyGetAll:
				blockOwner = 2

			currentScore += diagonal1Score + diagonal2Score

			if blockOwner == 1:
				currentScore = self.weGetAll
			elif blockOwner == 2:
				currentScore = self.theyGetAll

			self.heuristicDict[heuristicBlock] = currentScore

		return self.heuristicDict[heuristicBlock]

	def getBoardScore(self, currentBoard, currentBlockStatus):
		terminalStat, terminalScore = self.terminalCheck(currentBoard, currentBlockStatus)
		if terminalStat:
			return terminalScore
		boardScore = 0
		pseudoBlock = copy.deepcopy(currentBlockStatus)
		for i in range(3):
			for j in range(3):
				boardScore += self.getBlockScore(currentBoard[i][j])
				if pseudoBlock[i][j] == 3:
					pseudoBlock[i][j] = 0
		boardScore += 9*self.getBlockScore(pseudoBlock)
		return boardScore

	def getBlockStatus(self, block):
		blockScore = self.getBlockScore(block)
		if blockScore == self.weGetAll:
			return 1
		elif blockScore == self.theyGetAll:
			return 2
		elif len(self.checkAllowedMarkers(block)) == 0:
			return 3
		else:
			return 0

	def move(self, currentBoard, currentBlockStatus, oldMove, flag):
		# new 3*3*3*3 array for board
		formattedBoard = [[[[0]*3 for i in range(3)] for j in range(3)] for j in range(3)]
		# new 3*3 array for block status
		formattedBlockStatus = [[0]*3 for i in range(3)]

		# copy data to formattedBoard
		for i in range(9):
			for j in range(9):
				if currentBoard[i][j] == flag:
					formattedBoard[i//3][j//3][i%3][j%3] = 1
				elif currentBoard[i][j] == '-':
					formattedBoard[i//3][j//3][i%3][j%3] = 0
				else:
					formattedBoard[i//3][j//3][i%3][j%3] = 2

		# copy data to formattedBlockStatus
		for i in range(3):
			for j in range(3):
				if currentBlockStatus[i*3+j] == flag:
					formattedBlockStatus[i][j] = 1
				elif currentBlockStatus[i*3+j] == '-':
					formattedBlockStatus[i][j] = 0
				elif currentBlockStatus[i*3+j] == 'D':
					formattedBlockStatus[i][j] = 3
				else:
					formattedBlockStatus[i][j] = 2

		if oldMove[0] < 0 or oldMove[1] < 0:
			uselessScore, nextMove = 0, (3, 3)
		else:
			uselessScore, nextMove = self.alphaBetaPruning(formattedBoard, formattedBlockStatus, -100000000, 100000000, True, oldMove, 4)
		if self.DEbug:
			print("move : returning",nextMove,uselessScore)
		return nextMove

	def terminalCheck(self, currentBoard, currentBlockStatus):
		terminalStat = 0
		for i in range(3):
			if currentBlockStatus[i][0] == currentBlockStatus[i][1] == currentBlockStatus[i][2] and currentBlockStatus[i][0] in (1, 2):
				terminalStat = currentBlockStatus[i][0]
			if currentBlockStatus[0][i] == currentBlockStatus[1][i] == currentBlockStatus[2][i] and currentBlockStatus[0][i] in (1, 2):
				terminalStat = currentBlockStatus[0][i]
		if currentBlockStatus[0][0] == currentBlockStatus[1][1] == currentBlockStatus[2][2] and currentBlockStatus[1][1] in (1, 2):
			terminalStat = currentBlockStatus[1][1]
		if currentBlockStatus[0][2] == currentBlockStatus[1][1] == currentBlockStatus[2][0] and currentBlockStatus[1][1] in (1, 2):
			terminalStat = currentBlockStatus[1][1]
		if terminalStat == 0:
			for i in range(3):
				for j in range(3):
					if currentBlockStatus[i][j] == 0:
						return False, 0
			terminalStat = 3
		if terminalStat:
			if terminalStat == 1:
				return True, 1000000
			elif terminalStat == 2:
				return True, -1000000
			else:
				blockCount=0
				for i in range(3):
					for j in range(3):
						if currentBlockStatus[i][j] == 1:
							blockCount += 1
						elif currentBlockStatus[i][j] == 2:
							blockCount -= 1
				if blockCount > 0:
					return True, 999999
				elif blockCount < 0:
					return True, -999999
				else:
					blockCount=0
					for i in range(3):
						for j in range(3):
							if currentBoard[i][j][1][1] == 1:
								blockCount += 1
							elif currentBoard[i][j][1][1] == 2:
								blockCount -= 1
					if blockCount > 0:
						return True, 999999
					elif blockCount < 0:
						return True, -999999
					else:
						True, 900000


	def alphaBetaPruning(self, currentBoard, currentBlockStatus, alpha, beta, flag, prevMove, depth):
		#make a copy of lists
		tempBoard = copy.deepcopy(currentBoard)
		tempBlockStatus = copy.deepcopy(currentBlockStatus)
		terminalStat, terminalScore = self.terminalCheck(currentBoard, currentBlockStatus)
		if terminalStat:
			return terminalScore, ()
		if depth<=0:
			return self.getBoardScore(currentBoard, currentBlockStatus),()
		if flag:
			possibMoves = self.getAllowedMoves(currentBoard, currentBlockStatus, prevMove)
			random.shuffle(possibMoves)
			bestMove=()
			v=-100000000
			for move in possibMoves:
				#implement the move
				tempBoard[move[0]//3][move[1]//3][move[0]%3][move[1]%3] = 1
				tempBlockStatus[move[0]//3][move[1]//3] = self.getBlockStatus(tempBoard[move[0]//3][move[1]//3])

				childScore, childBest = self.alphaBetaPruning(tempBoard, tempBlockStatus, alpha, beta, not flag, move, depth-1)
				if childScore >= v:
					v = childScore
					bestMove = move
				alpha = max(alpha, v)

				#revert the implemented move
				tempBoard[move[0]//3][move[1]//3][move[0]%3][move[1]%3] = 0
				tempBlockStatus[move[0]//3][move[1]//3] = self.getBlockStatus(tempBoard[move[0]//3][move[1]//3])

				if alpha >= beta:
					return v, bestMove

			return v, bestMove
		else:
			possibMoves = self.getAllowedMoves(currentBoard, currentBlockStatus, prevMove)
			random.shuffle(possibMoves)
			bestMove=()
			v=100000000
			for move in possibMoves:
				#implement the move
				tempBoard[move[0]//3][move[1]//3][move[0]%3][move[1]%3] = 2
				tempBlockStatus[move[0]//3][move[1]//3] = self.getBlockStatus(tempBoard[move[0]//3][move[1]//3])

				childScore, childBest = self.alphaBetaPruning(tempBoard, tempBlockStatus, alpha, beta, not flag, move, depth-1)
				if childScore <= v:
					v = childScore
					bestMove = move
				beta = min(beta, v)

				#revert the implemented move
				tempBoard[move[0]//3][move[1]//3][move[0]%3][move[1]%3] = 0
				tempBlockStatus[move[0]//3][move[1]//3] = self.getBlockStatus(tempBoard[move[0]//3][move[1]//3])

				if alpha >= beta:
					return v, bestMove
			return v, bestMove