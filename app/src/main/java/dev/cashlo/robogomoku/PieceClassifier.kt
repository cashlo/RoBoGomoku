/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

package dev.cashlo.robogomoku

import android.content.Context
import android.content.res.AssetManager
import android.graphics.Bitmap
import android.util.Log
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.io.FileInputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.channels.FileChannel

class PieceClassifier(private val context: Context) {
  private var interpreter: Interpreter? = null

  var isInitialized = false
    private set

  private var inputImageWidth: Int = 0 // will be inferred from TF Lite model.
  private var inputImageHeight: Int = 0 // will be inferred from TF Lite model.
  private var modelInputSize: Int = 0 // will be inferred from TF Lite model.

  private val boardResultHistory = Array(GomokuGame.SIZE*GomokuGame.SIZE) {
    arrayListOf(FloatArray(2))
  }

  private val HISTORY_SIZE = 2
  private val THRESHOLD = 0.9f

  fun initialize() {
    return initializeInterpreter()
  }

  @Throws(IOException::class)
  private fun initializeInterpreter() {
    // Load the TF Lite model from the asset folder.
    val assetManager = context.assets
    val model = loadModelFile(assetManager, "model.tflite")
    val options = Interpreter.Options()
    //options.addDelegate(GpuDelegate())
    options.setUseNNAPI(true)
    options.setNumThreads(4)
    val interpreter = Interpreter(model, options)

    // Read input shape from model file
    val inputShape = interpreter.getInputTensor(0).shape()
    inputImageWidth = inputShape[1]
    inputImageHeight = inputShape[2]
    modelInputSize = FLOAT_TYPE_SIZE * inputImageWidth * inputImageHeight * PIXEL_SIZE

// Finish interpreter initialization
    this.interpreter = interpreter

    isInitialized = true
    Log.d(TAG, "Initialized TFLite interpreter.")
  }

  @Throws(IOException::class)
  private fun loadModelFile(assetManager: AssetManager, filename: String): ByteBuffer {
    val fileDescriptor = assetManager.openFd(filename)
    val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
    val fileChannel = inputStream.channel
    val startOffset = fileDescriptor.startOffset
    val declaredLength = fileDescriptor.declaredLength
    return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
  }


    private fun loadImage(bitmap: Bitmap): TensorImage {
        val tf_image = TensorImage.fromBitmap(bitmap)

        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(inputImageWidth, inputImageHeight, ResizeOp.ResizeMethod.NEAREST_NEIGHBOR))
            .add(NormalizeOp(0f, 255f))
            .build()
      val normalizedImage = imageProcessor.process(tf_image)
        return normalizedImage
    }

  fun classify(bitmap: Bitmap): FloatArray {
    check(isInitialized) { "TF Lite Interpreter is not initialized yet." }

    // Define an array to store the model output.
    val output = Array(1) { FloatArray(OUTPUT_CLASSES_COUNT) }

    // Run inference with the input data.
    interpreter?.run(loadImage(bitmap).getBuffer(), output)

    val result = output[0]
    return result
  }

  fun getRollingResult(boardIndex: Int, result: FloatArray): Int {
    if(result[0].isNaN()){
      return -1
    }
    boardResultHistory[boardIndex].add(result)
    if (boardResultHistory[boardIndex].size > HISTORY_SIZE) {
      boardResultHistory[boardIndex].removeAt(0)
    }
    val classSum = FloatArray(3)
    for (class_result in boardResultHistory[boardIndex]){
      for ((class_index, confident) in class_result.withIndex()){
        classSum[class_index] += confident
      }
    }
    if (boardResultHistory[boardIndex].size == HISTORY_SIZE && classSum.max()!! > HISTORY_SIZE * THRESHOLD) {
      return classSum.indices.maxBy { classSum[it] } ?: -1
    }
    return -1
  }

  fun close() {
    interpreter?.close()
    Log.d(TAG, "Closed TFLite interpreter.")
  }

  companion object {
    private const val TAG = "PieceClassifier"

    private const val FLOAT_TYPE_SIZE = 4
    private const val PIXEL_SIZE = 1

    private const val OUTPUT_CLASSES_COUNT = 2
  }
}
