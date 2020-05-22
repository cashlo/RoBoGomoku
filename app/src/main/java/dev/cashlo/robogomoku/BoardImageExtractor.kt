package dev.cashlo.robogomoku

import android.graphics.Bitmap
import android.graphics.Rect
import android.os.SystemClock
import android.util.Log
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import java.nio.ByteBuffer


class BoardImageExtractor : ImageAnalysis.Analyzer  {
    var measureMode = false

    private var lastAnalyzedTimestamp = 0L
    val gameSize = 15

    var onBitmapUpdate = {i: Int, bm: Bitmap -> }
    var onMeasurement = {}
    /**
     * Helper extension function used to extract a byte array from an
     * image plane buffer
     */
    private fun ByteBuffer.toByteArray(): ByteArray {
        rewind()    // Rewind the buffer to zero
        val data = ByteArray(remaining())
        get(data)   // Copy the buffer into a byte array
        return data // Return the byte array
    }

    fun imageProxyToBitmap(image: ImageProxy): Bitmap {
        val yRowStride = image.planes[0].rowStride
        val uvRowStride = image.planes[1].rowStride
        val uvPixelStride = image.planes[1].pixelStride
        val rgbBytes = IntArray(image.width * image.height)

        ImageUtils.convertYUV420ToARGB8888(image.planes[0].buffer.toByteArray(),
            image.planes[1].buffer.toByteArray(),
            image.planes[2].buffer.toByteArray(),
            image.width,
            image.height,
            yRowStride,
            uvRowStride,
            uvPixelStride,
            rgbBytes
        )
        val rgbBitmap = Bitmap.createBitmap(image.width, image.height, Bitmap.Config.ARGB_8888)
        rgbBitmap.setPixels(rgbBytes, 0, image.width, 0,0, image.width, image.height)
        return rgbBitmap
    }

    private fun cropCells(bitmap: Bitmap): List<Bitmap> {
        val cropRectList = ArrayList<Rect>()
        val leftOffset = (1280-720)/2f + 5/2f
        val topOffset = 5/2f
        val cellHeight = (720-5)/(gameSize-1)

        for (r in 0 until gameSize) {
            for (c in 0 until gameSize) {
                cropRectList.add(Rect(
                    (leftOffset+cellHeight*(c-0.5)).toInt(),
                    (topOffset+cellHeight*(r-0.5)).toInt(),
                    (leftOffset+cellHeight*(c+0.5)).toInt(),
                    (topOffset+cellHeight*(r+0.5)).toInt()))
            }
        }

        return cropRectList.map { cropRect ->
            val cameraRect = projectorRectToCameraRect(cropRect)
            Bitmap.createBitmap(bitmap, cameraRect.left, cameraRect.top, cameraRect.width(), cameraRect.height())
        }
    }

    private val projectorTopOffset = 226
    private val projectorHeight = 537 - projectorTopOffset

    private val projectorTopLeftOffset = 290
    private val projectorTopWidth = 657 - projectorTopLeftOffset

    private val projectorBottomLeftOffset = 332
    private val projectorBottomWidth = 618 - projectorBottomLeftOffset

    private fun projectorRectToCameraRect(projectorRect: Rect): Rect {
        val top = projectorRect.top*projectorHeight/720f + projectorTopOffset
        val bottom = projectorRect.bottom*projectorHeight/720f +projectorTopOffset

        val midY = (projectorRect.top+projectorRect.bottom)/2f/720f
        val width = midY*projectorTopWidth+(1-midY)*projectorBottomWidth
        val leftOffset = midY*projectorTopLeftOffset+(1-midY)*projectorBottomLeftOffset

        val left = (projectorRect.left - 1280/2)/720f*width + leftOffset + width/2
        val right = (projectorRect.right - 1280/2)/720f*width + leftOffset + width/2

        return Rect(left.toInt(), top.toInt(), right.toInt(), bottom.toInt())
    }

    val topOffsetList = IntArray(10)
    val heightList = IntArray(10)


    fun startMeasure(){
        measureMode = true
    }

    override fun analyze(image: ImageProxy, rotationDegrees: Int) {

        val currentTimestamp = System.currentTimeMillis()
        if (currentTimestamp - lastAnalyzedTimestamp < 50) {
            return
        }
        lastAnalyzedTimestamp = currentTimestamp

        val startTimeForLoadImage = System.currentTimeMillis()
        val rgbBitmap = imageProxyToBitmap(image)

        Log.d("TimeLog", "Timecost of imageProxyToBitmap: " +  (System.currentTimeMillis() - startTimeForLoadImage))
        if (measureMode) {
            val topLeftPixels = IntArray(rgbBitmap.width*rgbBitmap.height/4)
            val topRightPixels = IntArray(rgbBitmap.width*rgbBitmap.height/4)
            val bottomLeftPixels = IntArray(rgbBitmap.width*rgbBitmap.height/4)
            val bottomRightPixels = IntArray(rgbBitmap.width*rgbBitmap.height/4)

            rgbBitmap.getPixels(topLeftPixels, 0, rgbBitmap.width/2, 0,0, rgbBitmap.width/2, rgbBitmap.height/2)
            rgbBitmap.getPixels(topRightPixels, 0, rgbBitmap.width/2, rgbBitmap.width/2,0, rgbBitmap.width/2, rgbBitmap.height/2)
            rgbBitmap.getPixels(bottomLeftPixels, 0, rgbBitmap.width/2, 0,rgbBitmap.height/2, rgbBitmap.width/2, rgbBitmap.height/2)
            rgbBitmap.getPixels(bottomRightPixels, 0, rgbBitmap.width/2, rgbBitmap.width/2,rgbBitmap.height/2, rgbBitmap.width/2, rgbBitmap.height/2)

            val topLeftmaxIndex = topLeftPixels.indices.maxBy { topLeftPixels[it] and 0xff0000 }?: -1
            val topRightIndex = topRightPixels.indices.maxBy { topRightPixels[it] and 0xff0000 }?: -1
            val bottomLeftIndex = bottomLeftPixels.indices.maxBy { bottomLeftPixels[it] and 0xff0000 }?: -1
            val bottomRightIndex = bottomRightPixels.indices.maxBy { bottomRightPixels[it] and 0xff0000 }?: -1

            Log.d("luminanceArray", "Top left Y: " + topLeftmaxIndex/(rgbBitmap.width/2f) + " X: " +  topLeftmaxIndex%(rgbBitmap.width/2f))
            Log.d("luminanceArray", "Top right Y: " + topRightIndex/(rgbBitmap.width/2f) + " X: " +  (topRightIndex%(rgbBitmap.width/2f)+rgbBitmap.width/2f))
            Log.d("luminanceArray", "Bottom left Y: " + (bottomLeftIndex/(rgbBitmap.width/2f)+rgbBitmap.height/2f) + " X: " +  bottomLeftIndex%(rgbBitmap.width/2f))
            Log.d("luminanceArray", "Bottom right Y: " + (bottomRightIndex/(rgbBitmap.width/2f)+rgbBitmap.height/2f) + " X: " +  (bottomRightIndex%(rgbBitmap.width/2f)+rgbBitmap.width/2f))


            Log.d("luminanceArray", "Height: " + (bottomLeftIndex/(rgbBitmap.width/2f)+rgbBitmap.height/2f-topLeftmaxIndex/(rgbBitmap.width/2f)) + ": " + (bottomRightIndex/(rgbBitmap.width/2f)+rgbBitmap.height/2f-topRightIndex/(rgbBitmap.width/2f)))
            Log.d("luminanceArray", "Top width: " + (topRightIndex%(rgbBitmap.width/2f)+rgbBitmap.width/2f-topLeftmaxIndex%(rgbBitmap.width/2f)) + "Bottom width:" + (bottomRightIndex%(rgbBitmap.width/2f)+rgbBitmap.width/2f-bottomLeftIndex%(rgbBitmap.width/2f)))

        }


        val startTimeForAllUpdate = System.currentTimeMillis()

        for ((index,cropBitmap) in cropCells(rgbBitmap).withIndex()) {
            onBitmapUpdate(gameSize*gameSize - 1 - index, cropBitmap)
        }

        Log.d("TimeLog", "Timecost of All onBitmapUpdate: " +  (System.currentTimeMillis() - startTimeForAllUpdate))
    }
}