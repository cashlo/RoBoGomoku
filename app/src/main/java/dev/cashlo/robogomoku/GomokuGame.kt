package dev.cashlo.robogomoku


import kotlin.math.max
import kotlin.math.min
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.concurrent.Executors

val BACKGROUND = Executors.newFixedThreadPool(1)

class GomokuGame {

    var onBoardUpdate = {}
    var board = GomokuBoard(IntArray(SIZE*SIZE){0}, -1, (0 until SIZE*SIZE).toHashSet())
    var gomokuSearcher = MonteCarloSearch(2000, 1f)
    var gomokuSearchTree = GomokuSearchNode(null, board.clone(), WHITE)


    fun resetBoard(){
        board = GomokuBoard(IntArray(SIZE*SIZE){0}, -1, (0 until SIZE*SIZE).toHashSet())
        gomokuSearchTree = GomokuSearchNode(null, board.clone(), WHITE)
        onBoardUpdate()
    }


    fun myMove(lastMove: Int) {
        gomokuSearchTree = gomokuSearchTree.createFromMove(lastMove)
        val move = (gomokuSearcher.search(gomokuSearchTree) as GomokuSearchNode).getMove()
        board.placeMove(move, WHITE)
        gomokuSearchTree = gomokuSearchTree.createFromMove(move)
        onBoardUpdate()
    }

    fun yourMove(index: Int) {
        if (!board.canPlace(index)) return
        board.placeMove(index, BLACK)
        onBoardUpdate()
        if (board.checkBoard() == IN_PROGRESS) {
            myMove(index)
        }
    }

    class GomokuBoard(var board: IntArray, var lastMove: Int, var movesLeft: HashSet<Int>) {

        fun clone(): GomokuBoard {
            return GomokuBoard(board.clone(), lastMove, movesLeft.clone() as HashSet<Int>)
        }

        fun canPlace(move: Int): Boolean {
            return movesLeft.contains(move)
        }

        fun randomMove(): Int {
            return movesLeft.random()
        }

        fun placeMove(move: Int, player: Int){
             if (board[move] != EMPTY || !movesLeft.contains(move)) {
                throw Exception("Invalid Placement")
            }
            board[move] = player
            lastMove = move
            movesLeft.remove(move)
        }

        fun checkBoard(): Int {
            if (lastMove == -1) return IN_PROGRESS
            if (movesLeft.isEmpty()) return DRAW

            val x = lastMove%SIZE
            val y = lastMove/SIZE
            val cell = board[lastMove]

            val minX = max(0, x-4)
            val minY = max(0, y-4)

            val maxX = min(SIZE-1, x+4)
            val maxY = min(SIZE-1, y+4)

            val mainDiagonalStart = lastMove - (SIZE+1)*min(y-minY, x-minX)
            val mainDiagonalEnd   = lastMove + (SIZE+1)*min(maxY-y, maxX-x)

            val antiDiagonalStart = lastMove - (SIZE-1)*min(y-minY, maxX-x)
            val antiDiagonalEnd   = lastMove + (SIZE-1)*min(maxY-y, x-minX)

            val moveLineList = arrayOf(
                arrayOf(SIZE*y+minX, SIZE*y+maxX+1, 1),
                arrayOf(SIZE*minY+x, SIZE*maxY+x+1, SIZE),
                arrayOf(mainDiagonalStart, mainDiagonalEnd+1, SIZE+1),
                arrayOf(antiDiagonalStart, antiDiagonalEnd+1, SIZE-1)
            )

            for (line in moveLineList) {
                var count = 0
                for (i in line[0] until line[1] step line[2]) {
                    if (board[i] == cell){
                        count += 1
                    } else {
                        count = 0
                    }
                    if (count == 5) {
                        return cell
                    }
                }
            }
            return IN_PROGRESS
        }
    }
    class GomokuSearchNode(parent: GomokuSearchNode?, private val nodeBoard: GomokuBoard, private val lastPlayer: Int) : MonteCarloSearchNode(parent) {
        override fun createFromMove(move: Int): GomokuSearchNode {
            if (children.contains(move)) {
                return children[move] as GomokuSearchNode
            }
            val childBoard = nodeBoard.clone()
            childBoard.placeMove(move, other(lastPlayer))
            return GomokuSearchNode(this, childBoard, other(lastPlayer))
        }

        fun getMove(): Int {
            return nodeBoard.lastMove
        }

        override fun rollOut(): Float {
            val simulationBoard = nodeBoard.clone()
            var nextPlayer = other(lastPlayer)
            var boardStatus = simulationBoard.checkBoard()
            while (boardStatus == IN_PROGRESS) {
                val move = simulationBoard.randomMove()
                simulationBoard.placeMove(move, nextPlayer)
                nextPlayer = other(nextPlayer)
                boardStatus = simulationBoard.checkBoard()
            }
            if (boardStatus == lastPlayer) return 1f
            if (boardStatus == DRAW) return 0f
            return -1f
        }

        override fun getAllPossibleMoves(): ArrayList<Int> {
            if (isTerminal()) return ArrayList()

            return ArrayList(nodeBoard.movesLeft)
        }

        override fun isTerminal(): Boolean {
           return nodeBoard.checkBoard() != IN_PROGRESS
        }
    }

    companion object {
        const val EMPTY = 0
        const val BLACK = 1
        const val WHITE = 2

        const val IN_PROGRESS = 0
        const val DRAW = 3
        
        const val SIZE = 7


        fun other(player: Int): Int {
            return 3 - player
        }

    }
}
