package dev.cashlo.robogomoku

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

class ProjectorMeasurementView : View {
    private var mPaint = Paint()

    val game = GomokuGame()


    constructor(context: Context) : super(context) {
        init(null, 0)
    }

    constructor(context: Context, attrs: AttributeSet) : super(context, attrs) {
        init(attrs, 0)
    }

    constructor(context: Context, attrs: AttributeSet, defStyle: Int) : super(
        context,
        attrs,
        defStyle
    ) {
        init(attrs, defStyle)
    }

    private fun init(attrs: AttributeSet?, defStyle: Int) {
        // Set up a default TextPaint object
        with(mPaint){
            flags = Paint.ANTI_ALIAS_FLAG
            color = Color.RED
            style = Paint.Style.STROKE
            strokeWidth = 12f
            textSize = 80f
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val leftOffset = (1280-720)/2f

        canvas.drawPoint(leftOffset,0f, mPaint)
        canvas.drawPoint(leftOffset + 720f,0f, mPaint)
        canvas.drawPoint(leftOffset,720f, mPaint)
        canvas.drawPoint(leftOffset + 720f,720f, mPaint)

    }
}