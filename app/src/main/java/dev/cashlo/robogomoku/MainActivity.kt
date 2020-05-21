package dev.cashlo.robogomoku

import android.content.*
import android.graphics.Bitmap
import android.os.*
import android.util.Size
import android.view.View.*
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import jp.co.sharp.android.rb.projectormanager.ProjectorManagerServiceUtil
import kotlinx.android.synthetic.main.activity_main.*
import java.io.*


class MainActivity : AppCompatActivity() {
    private var isProjected: Boolean = false
    private var mProjectorEventReceiver = ProjectorEventReceiver()
    private val imageAnalyzer = BoardImageExtractor()
    private var digitClassifier = PieceClassifier(this)
    private lateinit var  imageHandler : Handler

    private inner class ProjectorEventReceiver : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.action) {
                ProjectorManagerServiceUtil.ACTION_PROJECTOR_PREPARE, ProjectorManagerServiceUtil.ACTION_PROJECTOR_PAUSE, ProjectorManagerServiceUtil.ACTION_PROJECTOR_RESUME -> {
                }
                ProjectorManagerServiceUtil.ACTION_PROJECTOR_START -> {
                    acquireWakeLock()
                    startCamera()
                    isProjected = true
                    window.decorView.systemUiVisibility = SYSTEM_UI_FLAG_IMMERSIVE or
                            SYSTEM_UI_FLAG_FULLSCREEN or
                            SYSTEM_UI_FLAG_HIDE_NAVIGATION
                }
                ProjectorManagerServiceUtil.ACTION_PROJECTOR_END, ProjectorManagerServiceUtil.ACTION_PROJECTOR_END_FATAL_ERROR, ProjectorManagerServiceUtil.ACTION_PROJECTOR_END_ERROR, ProjectorManagerServiceUtil.ACTION_PROJECTOR_TERMINATE -> {
                    releaseWakeLock()
                    isProjected = false
                }
                else -> {
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        startButton.setOnClickListener {
           startService(getIntentForProjector())
        }
        resetButton.setOnClickListener {
            gameBoard.game.resetBoard()
        }
        measureButton.setOnClickListener {
            startButton.visibility = GONE
            resetButton.visibility = GONE
            measureButton.visibility = GONE
            gameBoard.visibility = GONE
            measurementView.visibility = VISIBLE

            imageAnalyzer.startMeasure()
            imageAnalyzer.onMeasurement = {
                startButton.visibility = VISIBLE
                resetButton.visibility = VISIBLE
                measureButton.visibility = VISIBLE
                gameBoard.visibility = VISIBLE
                measurementView.visibility = GONE
            }
        }

        // Setup digit classifier.
        digitClassifier.initialize()

        setProjectorEventReceiver()
    }

    override fun onDestroy() {
        digitClassifier.close()
        unregisterReceiver(mProjectorEventReceiver)
        super.onDestroy()
    }
    private fun startCamera() {
        // Setup image analysis pipeline that computes average pixel luminance
        val analyzerConfig = ImageAnalysisConfig.Builder().apply {
            // Use a worker thread for image analysis to prevent glitches
            val analyzerThread = HandlerThread(
                "LuminosityAnalysis").apply { start() }
            imageHandler = Handler(analyzerThread.looper)
            setCallbackHandler(imageHandler)
            // In our analysis, we care more about the latest image than
            // analyzing *every* image
            setImageReaderMode(
                ImageAnalysis.ImageReaderMode.ACQUIRE_LATEST_IMAGE)

            setTargetResolution(Size(1280, 720))
        }.build()

        // Build the image analysis use case and instantiate our analyzer
        val analyzerUseCase = ImageAnalysis(analyzerConfig).apply {
            imageAnalyzer.onBitmapUpdate = {
                index, bitmap ->
                //if (saveImageButton.isChecked) {
                if (true) {
                    val storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
                    var imageFile: File? = null
                    try {
                        imageFile = File.createTempFile(
                            "robopic-%d".format(System.currentTimeMillis()),
                            ".png",
                            storageDir
                        )
                    } catch (e: IOException) {
                        e.printStackTrace()
                    }
                    try {
                        FileOutputStream(imageFile).use { out ->
                            bitmap.compress(
                                Bitmap.CompressFormat.PNG,
                                100,
                                out
                            ) // bmp is your Bitmap instance
                        }
                    } catch (e: IOException) {
                        e.printStackTrace()
                    }
                }



                if (digitClassifier.isInitialized) {
                        val result = digitClassifier.classify(bitmap)
                        this@MainActivity.runOnUiThread {
                            val rollingResult = digitClassifier.getRollingResult(index, result)
                            if (rollingResult != 1) return@runOnUiThread
                            gameBoard.game.yourMove(index, rollingResult)
                    }
                }
            }
            analyzer = imageAnalyzer
        }

        CameraX.bindToLifecycle(this, analyzerUseCase)
    }

    private var mWakelock: PowerManager.WakeLock? = null

    private val mLock = Any()

    private fun acquireWakeLock() {
        val pm = applicationContext.getSystemService(Context.POWER_SERVICE) as PowerManager
        synchronized(mLock) {
            if (mWakelock == null || !mWakelock!!.isHeld) {
                mWakelock = pm.newWakeLock(
                    PowerManager.SCREEN_DIM_WAKE_LOCK
                            or PowerManager.ACQUIRE_CAUSES_WAKEUP
                            or PowerManager.ON_AFTER_RELEASE, MainActivity::class.java.name
                )
                mWakelock!!.acquire()
            }
        }
    }

    /**
     * WakeLockを開放する.
     */
    private fun releaseWakeLock() {
        synchronized(mLock) {
            if (mWakelock != null && mWakelock!!.isHeld) {
                mWakelock!!.release()
                mWakelock = null
            }
        }
    }

    private fun getIntentForProjector(): Intent {
        val intent = Intent()
        val componentName = ComponentName(
            ProjectorManagerServiceUtil.PACKAGE_NAME,
            ProjectorManagerServiceUtil.CLASS_NAME
        )
        //逆方向で照射する
        intent.putExtra(
            ProjectorManagerServiceUtil.EXTRA_PROJECTOR_OUTPUT,
            ProjectorManagerServiceUtil.EXTRA_PROJECTOR_OUTPUT_VAL_REVERSE
        )
        //足元に照射する
        intent.putExtra(
            ProjectorManagerServiceUtil.EXTRA_PROJECTOR_DIRECTION,
            ProjectorManagerServiceUtil.EXTRA_PROJECTOR_DIRECTION_VAL_UNDER
        )
        intent.component = componentName
        return intent
    }

    private fun setProjectorEventReceiver() {
        val intentFilter = IntentFilter()
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_PREPARE)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_START)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_PAUSE)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_RESUME)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_END)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_END_ERROR)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_END_FATAL_ERROR)
        intentFilter.addAction(ProjectorManagerServiceUtil.ACTION_PROJECTOR_TERMINATE)
        registerReceiver(mProjectorEventReceiver, intentFilter)
    }


    fun saveData(fileName : String, data: ByteArray) {
        val storageDir = getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS)
        val dataFile = File(storageDir, fileName)

        val dos = DataOutputStream(FileOutputStream(dataFile))
        dos.write(data)
        dos.close()
    }
}
