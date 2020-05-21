package dev.cashlo.robogomoku

import android.util.Log

class GomokuGame {
    val size = 15
    var onBoardUpdate = {}
    var board = Array(size*size) {
        0
    }

    fun resetBoard() {
        TODO("not implemented") //To change body of created functions use File | Settings | File Templates.
    }

    fun yourMove(index: Int, rollingResult: Int) {
        board[index] = rollingResult
        Log.d("move", "move: $index")
        onBoardUpdate()
    }
}
