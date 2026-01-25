package com.blockblast.bot

import android.graphics.Bitmap
import org.opencv.android.Utils
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import java.util.ArrayList

class Vision {

    enum class Theme { DARK, BLUE, GREEN }
    
    data class BoardGeometry(
        val boardX: Int,
        val boardY: Int,
        val cellSize: Int
    )

    data class GameState(
        val board: Array<IntArray>,
        val shapes: List<List<Shapes.Point>>, // The logical shapes
        val shapeBBoxes: List<Rect>, // Screen coordinates for clicking/dragging
        val geometry: BoardGeometry
    )

    private var boardX = 0
    private var boardY = 0
    private var boardSize = 0
    private var cellSize = 0

    fun analyze(bitmap: Bitmap): GameState? {
        val mat = Mat()
        Utils.bitmapToMat(bitmap, mat)
        
        // Convert to BGR if needed, OpenCV usually loads Bitmap as RGBA
        // We might want to work in BGR for compatibility with Python logic checks
        val bgr = Mat()
        Imgproc.cvtColor(mat, bgr, Imgproc.COLOR_RGBA2BGR)
        
        parseBoardCoordinates(bgr)
        val theme = detectTheme(bgr)
        
        val board = parseBoard(bgr, theme)
        val shapesData = parseShapes(bgr, theme)
        
        val logicalShapes = shapesData.map { it.first }
        val bboxes = shapesData.map { it.second }

        val geometry = BoardGeometry(boardX, boardY, cellSize)
        return GameState(board, logicalShapes, bboxes, geometry)
    }

    private fun parseBoardCoordinates(image: Mat) {
        val h = image.rows()
        val w = image.cols()
        val aspectRatio = h.toDouble() / w.toDouble()

        if (aspectRatio < 1.5) {
            // Short/Square (Cropped)
            val maxBoardH = (h * 0.70).toInt()
            val targetBoardW = (w * 0.92).toInt()
            boardSize = Math.min(targetBoardW, maxBoardH)
            boardX = (w - boardSize) / 2
            boardY = (h * 0.05).toInt()
        } else {
            // Phone Screen
            boardX = 65 // Python hardcode, maybe dynamic is better?
            boardY = 584
            boardSize = 950
            
            // Adjust to be relative if resolution differs from 1080p
            // Assuming 1080 width baseline from Python code logic.
            // Let's make it relative to be safe
            boardSize = (w * 0.92).toInt()
            boardX = (w - boardSize) / 2
            boardY = (h * 0.23).toInt() // Approx
            
            // Fix overlap
            if (boardY + boardSize > h) {
                boardY = (h * 0.15).toInt()
            }
        }
        cellSize = boardSize / 8
    }

    private fun detectTheme(image: Mat): Theme {
        // Sample background color (bottom area)
        val h = image.rows()
        val sampleY = (h * 0.70).toInt()
        val sampleROI = image.submat(sampleY, sampleY + 10, 10, 20)
        val avg = Core.mean(sampleROI)
        
        val b = avg.`val`[0]
        val g = avg.`val`[1]
        val r = avg.`val`[2]
        
        return when {
            b < 100 && g < 100 && r < 100 -> Theme.DARK
            b > g + 20 -> Theme.BLUE
            else -> Theme.GREEN
        }
    }

    private fun parseBoard(image: Mat, theme: Theme): Array<IntArray> {
        val board = Array(8) { IntArray(8) }
        val boardROI = image.submat(boardY, boardY + boardSize, boardX, boardX + boardSize)
        
        if (boardROI.empty()) return board
        
        for (r in 0 until 8) {
            for (c in 0 until 8) {
                val x1 = c * cellSize
                val y1 = r * cellSize
                val padding = (cellSize * 0.15).toInt()
                
                val cellROI = boardROI.submat(
                    y1 + padding, y1 + cellSize - padding,
                    x1 + padding, x1 + cellSize - padding
                )
                
                var isFilled = false
                
                if (theme == Theme.BLUE) {
                    // Blue logic
                    val gray = Mat()
                    Imgproc.cvtColor(cellROI, gray, Imgproc.COLOR_BGR2GRAY)
                    val avgGray = Core.mean(gray).`val`[0]
                    
                    val hsv = Mat()
                    Imgproc.cvtColor(cellROI, hsv, Imgproc.COLOR_BGR2HSV)
                    val avgSat = Core.mean(hsv).`val`[1]
                    
                    if (avgGray < 150 && avgSat > 150) isFilled = true
                    
                } else if (theme == Theme.DARK) {
                    // Dark logic
                    val hsv = Mat()
                    Imgproc.cvtColor(cellROI, hsv, Imgproc.COLOR_BGR2HSV)
                    val avgSat = Core.mean(hsv).`val`[1]
                    val avgVal = Core.mean(hsv).`val`[2]
                    
                    if (avgSat > 100 && avgVal > 80) isFilled = true
                    
                } else {
                    // Green logic
                    val avgColor = Core.mean(cellROI).`val`[0] // just taking B for simplicity or avg
                    // Python logic: avg_color > 100.
                    // OpenCV mean returns Scalar(B, G, R, A)
                    val mean = Core.mean(cellROI)
                    val avgIntensity = (mean.`val`[0] + mean.`val`[1] + mean.`val`[2]) / 3
                    if (avgIntensity > 100) isFilled = true
                }
                
                if (isFilled) board[r][c] = 1
            }
        }
        return board
    }

    private fun parseShapes(image: Mat, theme: Theme): List<Pair<List<Shapes.Point>, Rect>> {
        // Just porting the Blue/Adaptive logic for now as it's the most robust
        // In real app we need all 3.
        
        val h = image.rows()
        val spawnY1 = boardY + boardSize + (h * 0.02).toInt()
        val spawnY2 = h - 10
        
        if (spawnY1 >= spawnY2) return emptyList()
        
        val shapeArea = image.submat(spawnY1, spawnY2, 0, image.cols())
        
        // HSV processing as per Python
        val hsv = Mat()
        Imgproc.cvtColor(shapeArea, hsv, Imgproc.COLOR_BGR2HSV)
        
        val mask = Mat()
        if (theme == Theme.DARK) {
             // Dark Theme: Sat > 100, Val > 80
             val maskSat = Mat()
             val maskVal = Mat()
             Core.inRange(hsv, Scalar(0.0, 100.0, 80.0), Scalar(180.0, 255.0, 255.0), mask)
        } else {
             // Blue/Green: standard threshold logic
             // Simplified for this artifact: Use simple Value threshold
             // In Python: Value < 230 (inv) OR Sat > 180
             val v = ArrayList<Mat>()
             Core.split(hsv, v)
             val vCh = v[2]
             val sCh = v[1]
             
             val maskDark = Mat()
             Imgproc.threshold(vCh, maskDark, 230.0, 255.0, Imgproc.THRESH_BINARY_INV)
             
             val maskSat = Mat()
             Imgproc.threshold(sCh, maskSat, 180.0, 255.0, Imgproc.THRESH_BINARY)
             
             Core.bitwise_or(maskDark, maskSat, mask)
        }
        
        // Dilate
        val kernel = Imgproc.getStructuringElement(Imgproc.MORPH_RECT, Size(5.0, 5.0))
        Imgproc.dilate(mask, mask, kernel)
        
        val contours = ArrayList<MatOfPoint>()
        val hierarchy = Mat()
        Imgproc.findContours(mask, contours, hierarchy, Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE)
        
        val parsedShapes = ArrayList<Pair<List<Shapes.Point>, Rect>>()
        val slotWidth = image.cols() / 3
        val slots = Array(3) { ArrayList<MatOfPoint>() }
        
        // Group by slot
        for (cnt in contours) {
            val rect = Imgproc.boundingRect(cnt)
            if (rect.area() < 100 || rect.width < 15) continue
            
            val centerX = rect.x + rect.width / 2
            val slotIdx = (centerX / slotWidth).coerceIn(0, 2)
            slots[slotIdx].add(cnt)
        }
        
        val blockSizeRef = (boardSize / 8 * 0.85).toInt()
        
        for (i in 0 until 3) {
            if (slots[i].isEmpty()) continue
            
            // Combine contours (quick/dirty via bounding rect of all)
            // Ideally we draw them on a mask and find bbox of non-zero
            var minX = Int.MAX_VALUE
            var minY = Int.MAX_VALUE
            var maxX = Int.MIN_VALUE
            var maxY = Int.MIN_VALUE
            
            for (cnt in slots[i]) {
                val r = Imgproc.boundingRect(cnt)
                minX = Math.min(minX, r.x)
                minY = Math.min(minY, r.y)
                maxX = Math.max(maxX, r.x + r.width)
                maxY = Math.max(maxY, r.y + r.height)
            }
            
            val w = maxX - minX
            val h = maxY - minY
            
            val cols = Math.max(1, Math.round(w.toDouble() / blockSizeRef).toInt())
            val rows = Math.max(1, Math.round(h.toDouble() / blockSizeRef).toInt())
            
            val cellW = w.toDouble() / cols
            val cellH = h.toDouble() / rows
            
            val shapeMatrix = ArrayList<Shapes.Point>()
            
            // Sample the grid
            // We need to sample from the mask we created
            for (r in 0 until rows) {
                for (c in 0 until cols) {
                    val cx = (c * cellW + cellW/2).toInt()
                    val cy = (r * cellH + cellH/2).toInt()
                    val mx = minX + cx
                    val my = minY + cy
                    
                    // Check pixel at mx, my
                    if (mx in 0 until mask.cols() && my in 0 until mask.rows()) {
                         if (mask.get(my, mx)[0] > 0) {
                             shapeMatrix.add(Shapes.Point(r, c))
                         }
                    }
                }
            }
            
            if (shapeMatrix.isNotEmpty()) {
                val screenRect = Rect(minX, spawnY1 + minY, w, h)
                parsedShapes.add(Pair(shapeMatrix, screenRect))
            }
        }
        
        return parsedShapes
    }
}
