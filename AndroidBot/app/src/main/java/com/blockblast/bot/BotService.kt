package com.blockblast.bot

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Context
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.graphics.Path
import android.hardware.display.DisplayManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.FrameLayout
import android.widget.TextView
import kotlinx.coroutines.*
import java.util.concurrent.Executor
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

class BotService : AccessibilityService() {

    private var windowManager: WindowManager? = null
    private var overlayView: View? = null
    private var isBotRunning = false
    
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private val vision = Vision()
    private val solver = Solver()
    
    // UI Elements
    private var statusText: TextView? = null
    private var btnAction: Button? = null

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d("BotService", "Service Connected")
        setupOverlay()
    }

    private fun setupOverlay() {
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        
        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) 
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY 
            else 
                WindowManager.LayoutParams.TYPE_PHONE,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        )
        layoutParams.gravity = Gravity.TOP or Gravity.START
        layoutParams.x = 0
        layoutParams.y = 200

        val inflater = LayoutInflater.from(this)
        overlayView = inflater.inflate(R.layout.service_overlay, null)
        
        statusText = overlayView?.findViewById(R.id.tv_status)
        btnAction = overlayView?.findViewById(R.id.btn_action)
        
        btnAction?.setOnClickListener {
            if (isBotRunning) stopBot() else startBot()
        }

        try {
            windowManager?.addView(overlayView, layoutParams)
        } catch (e: Exception) {
            Log.e("BotService", "Error adding overlay", e)
        }
    }

    private fun startBot() {
        isBotRunning = true
        btnAction?.text = "STOP"
        statusText?.text = "Running..."
        
        scope.launch {
            botLoop()
        }
    }

    private fun stopBot() {
        isBotRunning = false
        btnAction?.text = "START"
        statusText?.text = "Idle"
    }

    private suspend fun botLoop() {
        while (isBotRunning) {
            val bitmap = captureScreen()
            if (bitmap == null) {
                updateStatus("Capture Failed")
                delay(1000)
                continue
            }
            
            updateStatus("Analyzing...")
            val startT = System.currentTimeMillis()
            
            // Analyze in BG
            val gameState = withContext(Dispatchers.Default) {
                vision.analyze(bitmap)
            }
            
            if (gameState == null || gameState.shapes.isEmpty()) {
                updateStatus("No Shapes Found")
                delay(1000)
                continue
            }
            
            // Check if game over or empty
            
            updateStatus("Solving...")
            val moves = withContext(Dispatchers.Default) {
                solver.solve(gameState.board, gameState.shapes)
            }
            
            if (moves.isEmpty()) {
                updateStatus("No Moves!")
                delay(2000) // Wait hoping for something to change?
                continue
            }
            
            updateStatus("Executing ${moves.size} moves")
            for (move in moves) {
                if (!isBotRunning) break
                
                // Get Source Coordinates
                val bbox = gameState.shapeBBoxes.getOrNull(move.shapeIdx) ?: continue
                val startX = bbox.left + bbox.width() / 2
                val startY = bbox.top + bbox.height() / 2
                
                // Get Destination Coordinates
                val geo = gameState.geometry
                val destX = geo.boardX + (move.c * geo.cellSize) + (geo.cellSize / 2)
                val destY = geo.boardY + (move.r * geo.cellSize) + (geo.cellSize / 2)
                
                performGesture(startX.toFloat(), startY.toFloat(), destX.toFloat(), destY.toFloat())
                
                delay(400) // Wait between moves
            }
            
            val endT = System.currentTimeMillis()
            updateStatus("Loop: ${endT - startT}ms")
            delay(500) // Wait for animations
        }
    }

    private suspend fun captureScreen(): Bitmap? = suspendCoroutine { cont ->
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            takeScreenshot(
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                mainExecutor,
                object : AccessibilityService.TakeScreenshotCallback {
                    override fun onSuccess(screenshot: AccessibilityService.ScreenshotResult) {
                        val bitmap = Bitmap.wrapHardwareBuffer(
                            screenshot.hardwareBuffer,
                            screenshot.colorSpace
                        )
                        // Copy to software bitmap because HardwareBuffer is tricky
                        val copy = bitmap?.copy(Bitmap.Config.ARGB_8888, false)
                        screenshot.hardwareBuffer.close()
                        cont.resume(copy)
                    }

                    override fun onFailure(errorCode: Int) {
                        Log.e("BotService", "Screenshot Failed: $errorCode")
                        cont.resume(null)
                    }
                }
            )
        } else {
             // Fallback or Error
             cont.resume(null)
        }
    }

    private fun performGesture(startX: Float, startY: Float, endX: Float, endY: Float) {
        val path = Path()
        path.moveTo(startX, startY)
        path.lineTo(endX, endY)
        
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 300)) // 300ms swipe
            .build()
            
        dispatchGesture(gesture, null, null)
    }

    private fun updateStatus(text: String) {
        scope.launch(Dispatchers.Main) {
            statusText?.text = text
        }
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}
    
    override fun onDestroy() {
        super.onDestroy()
        isBotRunning = false
        if (overlayView != null) windowManager?.removeView(overlayView)
    }
}
