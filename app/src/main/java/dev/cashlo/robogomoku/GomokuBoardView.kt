package dev.cashlo.robogomoku

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color.GRAY
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import java.lang.Math.*

/**
 * TODO: document your custom view class.
 */
class GomokuBoardView : View {
    private var mPaint = Paint()

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
        // Set up a default TextPaint object
        with(mPaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = GRAY
            style = Paint.Style.FILL_AND_STROKE
            strokeWidth = 7f
            textSize = 80f
        }
        game.onBoardUpdate = {
            invalidate()
        }
    }

    private fun drawBoard(canvas: Canvas, leftOffset: Float, topOffset: Float, height: Float, lineWidth: Float, drawAllPieces: Boolean) {

        val boardPaint = Paint()
        with(boardPaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = GRAY
            style = Paint.Style.STROKE
            strokeWidth = lineWidth
        }

        with(canvas) {

            val size = game.size
            val rowHeight = (height-lineWidth)/(size-1)

            val offset = 0.3f

            for (r in 0 until size) {
                drawLine(
                    leftOffset,
                    topOffset+rowHeight*r+lineWidth/2,
                    leftOffset+height,
                    topOffset+rowHeight*r+lineWidth/2,
                    boardPaint)

                drawLine(
                    leftOffset+rowHeight*r+lineWidth/2,
                    topOffset,
                    leftOffset+rowHeight*r+lineWidth/2,
                    topOffset+height,
                    boardPaint)
            }

            for (r in 0 until size) {
                for (c in 0 until size) {
                    if (game.board[r*size+c] == 1)
                    drawCircle(leftOffset+rowHeight*c+lineWidth/2, topOffset+rowHeight*r+lineWidth/2, rowHeight/2*0.8f, boardPaint)
                }
            }
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val leftOffset = (1280-720)/2f
        drawBoard(canvas, leftOffset, 0f, 720f, 5f,false)
        drawBoard(canvas, 20f, 240f, 240f, 1f,true)

    }

    companion object {
        val TAG = MainActivity::class.java.simpleName
    }
}
