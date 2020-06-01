package dev.cashlo.robogomoku

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color.*
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import java.lang.Math.*

/**
 * TODO: document your custom view class.
 */
class GomokuBoardView : View {
    val game = GomokuGame()


    constructor(context: Context) : super(context) {
        init(null, 0)
    }

    constructor(context: Context, attrs: AttributeSet) : super(context, attrs) {
        init(attrs, 0)
    }

    constructor(context: Context, attrs: AttributeSet, defStyle: Int) : super(context, attrs, defStyle) {
        init(attrs, defStyle)
    }

    private fun init(attrs: AttributeSet?, defStyle: Int) {
        game.onBoardUpdate = {
            invalidate()
        }
    }

    private fun drawBoard(canvas: Canvas, leftOffset: Float, topOffset: Float, height: Float, lineWidth: Float, drawAllPieces: Boolean) {

        val boardPaint = Paint()
        with(boardPaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = GRAY
            style = Paint.Style.FILL_AND_STROKE
            strokeWidth = lineWidth
            textSize = 80f
        }

        val whitePiecePaint = Paint()
        with(whitePiecePaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = 0xFFFFC0CB.toInt()
            style = Paint.Style.FILL_AND_STROKE
            strokeWidth = lineWidth
        }

        val blackPiecePaint = Paint()
        with(blackPiecePaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = BLACK
            style = Paint.Style.FILL
            strokeWidth = lineWidth
        }

        with(canvas) {

            val rowHeight = (height-lineWidth)/(GomokuGame.SIZE)

            when (game.board.checkBoard()) {
                GomokuGame.BLACK -> drawText("You won!", 0f, 70f, boardPaint)
                GomokuGame.WHITE   -> drawText("I won!", 0f, 70f, boardPaint)
                GomokuGame.DRAW    -> drawText("Draw...", 0f, 70f, boardPaint)
            }

            for (r in 0 until GomokuGame.SIZE) {
                drawLine(
                    leftOffset+rowHeight/2,
                    topOffset+rowHeight*(r+0.5f)+lineWidth/2,
                    leftOffset+height-rowHeight/2,
                    topOffset+rowHeight*(r+0.5f)+lineWidth/2,
                    boardPaint)

                drawLine(
                    leftOffset+rowHeight*(r+0.5f)+lineWidth/2,
                    topOffset+rowHeight/2,
                    leftOffset+rowHeight*(r+0.5f)+lineWidth/2,
                    topOffset+height-rowHeight/2,
                    boardPaint)
            }
            for (r in 0 until GomokuGame.SIZE) {
                for (c in 0 until GomokuGame.SIZE) {
                    if (game.board.board[r * GomokuGame.SIZE + c] == GomokuGame.BLACK) {
                        if (drawAllPieces) {
                            drawCircle(
                                leftOffset + rowHeight * (c + 0.5f) + lineWidth / 2,
                                topOffset + rowHeight * (r + 0.5f) + lineWidth / 2,
                                rowHeight / 2 * 0.8f,
                                whitePiecePaint
                            )
                            drawCircle(
                                leftOffset + rowHeight * (c + 0.5f) + lineWidth / 2,
                                topOffset + rowHeight * (r + 0.5f) + lineWidth / 2,
                                rowHeight / 2 * 0.8f,
                                blackPiecePaint
                            )
                        } else {
                            drawCircle(
                                leftOffset + rowHeight * (c + 0.5f) + lineWidth / 2,
                                topOffset + rowHeight * (r + 0.5f) + lineWidth / 2,
                                rowHeight / 2 * 0.8f,
                                blackPiecePaint
                            )
                        }
                    }

                    if (game.board.board[r * GomokuGame.SIZE + c] == GomokuGame.WHITE) {
                        drawCircle(
                            leftOffset + rowHeight * (c + 0.5f) + lineWidth / 2,
                            topOffset + rowHeight * (r + 0.5f) + lineWidth / 2,
                            rowHeight / 2 * 0.8f,
                            whitePiecePaint
                        )
                    }



                }
            }
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val leftOffset = (1280-720)/2f
        drawBoard(canvas, leftOffset, 0f, 720f, 5f,false)
        //drawBoard(canvas, 20f, 240f, 240f, 1f,true)

    }

    companion object {
        val TAG = MainActivity::class.java.simpleName
    }
}
