from heapq import *
import pygame, time, numpy, sys, math, ctypes, random

#class with storing coordinates
class Move:
    row = -1
    col = -1
    def __init__(self):
        self.row = -1
        self.col = -1

#class of Decision Al
class AI:
    cellsP = 0
    cellsO = 0

    #hardcoded AI reaction on first player turn
    def getPrecomputedMove(self, row, col):
        result = Move
        #if player's turn is at center, computer's turn will be at corner
        if row == 1 and col == 1:
            result.row = 0
            result.col = 0
        #else at center
        else:
            result.row = 1
            result.col = 1
        return result


    def isPosFree2(self, num, cellsP, cellsO):
        return (cellsP >> num) & 1 == 0 and(cellsO >> num) & 1 == 0

    #true if the line contains both computer and player turns
    def isLineBroken(self, line1, line2):
        return line1 * line2 != 0

    #true if line is filled
    def isLineFilled(self, line):
        return line == 0b111

    #return numbers of lines which contain given cell (row, col)
    def getLineNumbers(self, row, col):
        result = []
        result.append(row)
        result.append(col + 3)
        if row == col:
            result.append(6)
        if row + col == 2:
            result.append(7)
        return result


    def getLine(self, num, cells):
        if num < 3:
            return (cells >> num * 3) & 0b000000111
        elif num < 6:
            n = num - 3
            return ((cells >> (0 + n)) & 1) | (((cells >> (n + 3)) & 1) << 1) | (((cells >> (n + 6)) & 1) << 2)
        elif num == 6:
            return ((cells >> 0) & 1) | (((cells >> 4) & 1) << 1) | (((cells >> 8) & 1) << 2)
        else:
            return ((cells >> 6) & 1) | (((cells >> 4) & 1) << 1) | (((cells >> 2) & 1) << 2)

    def isMovesLeft2(self):
        for i in range(8):
            if not self.isLineBroken(self.getLine(i, self.cellsP), self.getLine(i, self.cellsO)):
                return True
        return False


    def evaluate2(self):
        for i in range(8):
            if self.isLineFilled(self.getLine(i, self.cellsP)):
                return 10, i
        for i in range(8):
            if self.isLineFilled(self.getLine(i, self.cellsO)):
                return -10, i
        return 0, -1;


    def minimax2(self, depth, isMax):
        score, line = self.evaluate2()
        if abs(score) == 10:
            return score
        if self.isMovesLeft2() == False:
            return 0
        if isMax == True:
            best = -1000
            for i in range(9):
                if self.isPosFree2(i, self.cellsP, self.cellsO):
                    self.cellsP = self.cellsP | (1 << i)
                    best = max(best, self.minimax2(depth + 1, not isMax))
                    self.cellsP = self.cellsP & ((~(1 << i)) & 0b111111111)
            return best
        else:
            best = 1000
            for i in range(9):
                if self.isPosFree2(i, self.cellsP, self.cellsO):
                    self.cellsO = self.cellsO | (1 << i)
                    best = min(best, self.minimax2(depth + 1, not isMax))
                    self.cellsO = self.cellsO & ((~(1 << i)) & 0b111111111)
            return best

    #searches best turn
    def findBestMove(self):
        bestVal = -1000
        bestMove = Move()
        for i in range(9):
            if self.isPosFree2(i, self.cellsP, self.cellsO):
                self.cellsP = self.cellsP | (1 << i)
                moveVal = self.minimax2(0, False)
                self.cellsP = self.cellsP & ((~(1 << i)) & 0b111111111)
                if moveVal > bestVal or moveVal == bestVal and random.randint(0, 5) < 3: #"b) From all possible moves"
                    bestMove.row = math.floor(i / 3)
                    bestMove.col = i % 3
                    bestVal = moveVal
        return bestMove

#draw the line
def drawLine(screen, num, w, h):
    if num < 3:
        pygame.draw.line(screen, (255, 0, 0), (0, num * h + h / 2), (w * 3, num * h + h / 2))
    elif num < 6:
        pygame.draw.line(screen, (255, 0, 0), ((num - 3) * w + w / 2, 0), ((num -3) * w + w / 2, h * 3))
    elif num == 6:
        pygame.draw.line(screen, (255, 0, 0), (0, 0), (w * 3, h * 3))
    else:
        pygame.draw.line(screen, (255, 0, 0), (0, h * 3), (w * 3, 0))

def drawCross(screen, x, y):
    pygame.draw.line(screen, (0, 0, 255), (x - 30, y - 30), (x + 30, y + 30))
    pygame.draw.line(screen, (0, 0, 255), (x - 30, y + 30), (x + 30, y - 30))


#init pygame
pygame.init()

w, h = 64, 64

size = w * 3, h * 3

screen = pygame.display.set_mode(size) #устанавливаем размер окна/поверхности для рисования

#draw the cells
y = h/2
for row in range(3):
    x = w/2
    for col in range(3):
        pygame.draw.rect(screen, (255, 255, 255), (x - 30, y - 30, 60, 60))
        x += w
    y += h
pygame.display.flip()

ai = AI()
gameover = False
turns = 0
#бесконечный цикл в ожидании выхода
while(True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONUP: #if mouse clicked
                pos = pygame.mouse.get_pos() #get mouse position and cell's coordinates
                x, y = pos
                rowNum = math.floor(y / h)
                colNum = math.floor(x / w)
                cellNum = rowNum * 3 + colNum
                if ai.isPosFree2(cellNum, ai.cellsP, ai.cellsO) and not gameover: #if cell is free and game is not over
                    ai.cellsO = ai.cellsO | (1 << cellNum)
                    pygame.draw.circle(screen, (0, 255, 0), (colNum * w + math.floor(w / 2), rowNum * h + math.floor(h / 2)), 29, 1)
                    turns = turns + 1

                    score, line = ai.evaluate2() #check if somebody winds
                    if score == -10: #if player won
                        gameover = True
                        drawLine(screen, line, w, h)
                        pygame.display.flip()
                        ctypes.windll.user32.MessageBoxW(0, "You win", "Game result", 1)

                    if not gameover:

                        if turns < 2: #if this is first AI turn, don't build decision tree, use simplified logic - "a) to improve efficiency ..."
                            bestMove = ai.getPrecomputedMove(rowNum, colNum)
                        else: #build decision tree to calculate turn
                            bestMove = ai.findBestMove()

                        if bestMove.row >= 0: #if turn exists
                            ai.cellsP = ai.cellsP | (1 << bestMove.row * 3 + bestMove.col)
                            drawCross(screen, bestMove.col * w + w / 2, bestMove.row * h + h / 2)
                            turns = turns + 1

                            score, line = ai.evaluate2() #check if somebody winds
                            if score == 10: #if computer won
                                gameover = True
                                drawLine(screen, line, w, h)
                                pygame.display.flip()
                                ctypes.windll.user32.MessageBoxW(0, "You lose", "Game result", 1)
                        

                        else: #if AI has no turns, end the game with draw
                            pygame.display.flip()
                            ctypes.windll.user32.MessageBoxW(0, "Draw", "Game result", 1)

                    pygame.display.flip()

                    
                    
                    

                    
