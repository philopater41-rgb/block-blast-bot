package com.blockblast.bot

import java.util.PriorityQueue

class Solver {

    data class Move(val shapeIdx: Int, val r: Int, val c: Int)
    
    // Using Int Array for board (0=empty, 1=filled)
    // Board is 8x8
    
    // Beam Search State
    data class State(
        val negScore: Double, // Negative score for Min-Heap
        val board: Array<IntArray>,
        val path: List<Move>,
        val remainingIndices: List<Int>,
        val streak: Int,
        val secured: Boolean
    ) : Comparable<State> {
        override fun compareTo(other: State): Int {
            return this.negScore.compareTo(other.negScore)
        }
    }

    private val gridSize = 8

    fun solve(board: Array<IntArray>, shapes: List<List<Shapes.Point>>, currentCombo: Int = 0): List<Move> {
        val validIndices = shapes.indices.filter { shapes[it].isNotEmpty() }
        if (validIndices.isEmpty()) return emptyList()

        // Beam Search
        val beamWidth = 20
        var beam = Utils.priorityQueueOf<State>()
        
        // Initial State
        beam.add(State(0.0, copyBoard(board), emptyList(), validIndices, currentCombo, false))

        for (step in validIndices.indices) {
            val candidates = Utils.priorityQueueOf<State>()
            
            while (beam.isNotEmpty()) {
                val current = beam.poll() ?: break
                
                if (current.remainingIndices.isEmpty()) {
                    candidates.add(current)
                    continue
                }

                for (i in current.remainingIndices) {
                    val shape = shapes[i]
                    val validMoves = getValidMoves(current.board, shape)
                    if (validMoves.isEmpty()) continue
                    
                    // Optimization: Top 8 moves only
                    val movesToCheck = if (validMoves.size > 8) {
                        validMoves.sortedByDescending { (r, c) ->
                            val dist = Math.abs(r - 3.5) + Math.abs(c - 3.5)
                            
                            // Check clear
                            val tempBoard = placeShape(current.board, shape, r, c)
                            val (clearedBoard, lines) = clearLines(tempBoard)
                            val clears = lines > 0
                            
                            if (clears && !current.secured) 1000.0 else dist * 10.0
                        }.take(8)
                    } else validMoves

                    for ((r, c) in movesToCheck) {
                        val nextBoard = placeShape(current.board, shape, r, c)
                        val (finalBoard, cleared) = clearLines(nextBoard)
                        
                        val newStreak = if (cleared > 0) current.streak + 1 else 0
                        val newSecured = current.secured || (cleared > 0)
                        
                        val moveScore = evaluateBoard(finalBoard, cleared, newSecured, newStreak)
                        val newTotalNeg = current.negScore - moveScore // accum? Python logic was confusing. 
                        // Python: new_total = -neg_score + move_score.
                        // Python stored -score in heap.
                        // So neg_score is POSITIVE value of score * -1? No.
                        // Let's stick to standard: Store -Score.
                        // current.negScore is already negative.
                        // new score = (current.negScore) - moveScore (making it more negative = better)
                        
                        val newPath = current.path + Move(i, r, c)
                        val newRemaining = current.remainingIndices.filter { it != i }
                        
                        candidates.add(State(newTotalNeg, finalBoard, newPath, newRemaining, newStreak, newSecured))
                    }
                }
            }
            
            if (candidates.isEmpty()) return emptyList()
            
            // Keep top BeamWidth
            beam = Utils.priorityQueueOf<State>()
            var count = 0
            while (candidates.isNotEmpty() && count < beamWidth) {
                beam.add(candidates.poll())
                count++
            }
        }
        
        return beam.peek()?.path ?: emptyList()
    }

    private fun getValidMoves(board: Array<IntArray>, shape: List<Shapes.Point>): List<Pair<Int, Int>> {
        val moves = mutableListOf<Pair<Int, Int>>()
        if (shape.isEmpty()) return moves
        
        val maxR = shape.maxOf { it.r }
        val maxC = shape.maxOf { it.c }
        
        for (r in 0 until (gridSize - maxR)) {
            for (c in 0 until (gridSize - maxC)) {
                if (canPlace(board, shape, r, c)) {
                    moves.add(r to c)
                }
            }
        }
        return moves
    }

    private fun canPlace(board: Array<IntArray>, shape: List<Shapes.Point>, r: Int, c: Int): Boolean {
        for (p in shape) {
            if (board[r + p.r][c + p.c] == 1) return false
        }
        return true
    }

    private fun placeShape(board: Array<IntArray>, shape: List<Shapes.Point>, r: Int, c: Int): Array<IntArray> {
        val newBoard = copyBoard(board)
        for (p in shape) {
            newBoard[r + p.r][c + p.c] = 1
        }
        return newBoard
    }
    
    private fun clearLines(board: Array<IntArray>): Pair<Array<IntArray>, Int> {
        val rowsToClear = (0 until gridSize).filter { r -> board[r].all { it == 1 } }
        val colsToClear = (0 until gridSize).filter { c -> (0 until gridSize).all { r -> board[r][c] == 1 } }
        
        val count = rowsToClear.size + colsToClear.size
        if (count == 0) return board to 0
        
        val newBoard = copyBoard(board)
        for (r in rowsToClear) {
            for (c in 0 until gridSize) newBoard[r][c] = 0
        }
        for (c in colsToClear) {
            for (r in 0 until gridSize) newBoard[r][c] = 0
        }
        return newBoard to count
    }

    private fun evaluateBoard(board: Array<IntArray>, linesCleared: Int, isSecured: Boolean, streak: Int): Double {
        val holes = countHoles(board)
        val roughness = calculateRoughness(board)
        
        var score = 0.0
        score -= holes * 600
        score -= roughness * 40
        
        score += calculateSurvivalScore(board)
        
        if (!isSecured && linesCleared == 0) {
            // Hungry Mode
            score += 500
        } else {
             // Setup Mode
             score += calculateSetupScore(board)
        }
        
        if (linesCleared > 0) {
            var bonus = (streak + 1) * 8000.0
            if (!isSecured) bonus *= 2
            score += bonus
        }
        
        return score
    }

    private fun calculateSurvivalScore(board: Array<IntArray>): Double {
        var dangerousMissed = 0
        
        for (shape in Shapes.ALL_POSSIBLE_SHAPES) {
            var canFit = false
            val h = shape.maxOf { it.r } + 1
            val w = shape.maxOf { it.c } + 1
            
            // Quick check
            loop@ for (r in 0 until gridSize - h + 1) {
                for (c in 0 until gridSize - w + 1) {
                    if (canPlace(board, shape, r, c)) {
                        canFit = true
                        break@loop
                    }
                }
            }
            
            if (!canFit) {
                val size = shape.size
                if (size >= 9) dangerousMissed += 5000
                else if (size >= 5) dangerousMissed += 2000
                else dangerousMissed += 100
            }
        }
        return -dangerousMissed.toDouble()
    }
    
    private fun calculateSetupScore(board: Array<IntArray>): Double {
        var score = 0.0
        // Rows
        for (r in 0 until gridSize) {
             val filled = board[r].count { it == 1 }
             if (filled == 6) score += 50
             else if (filled == 7) score += 150
        }
        // Cols
        for (c in 0 until gridSize) {
            var filled = 0
             for (r in 0 until gridSize) if (board[r][c] == 1) filled++
             if (filled == 6) score += 50
             else if (filled == 7) score += 150
        }
        return score
    }

    private fun countHoles(board: Array<IntArray>): Int {
        var holes = 0
        // Simple hole check: 0 surrounded by 1s (or edges)
        // Python code used pad logic.
        // Let's do simple neighbor check.
        for (r in 0 until gridSize) {
            for (c in 0 until gridSize) {
                if (board[r][c] == 0) {
                    var neighbors = 0
                    if (r == 0 || board[r-1][c] == 1) neighbors++
                    if (r == gridSize-1 || board[r+1][c] == 1) neighbors++
                    if (c == 0 || board[r][c-1] == 1) neighbors++
                    if (c == gridSize-1 || board[r][c+1] == 1) neighbors++
                    
                    if (neighbors == 4) holes++
                }
            }
        }
        return holes
    }
    
    private fun calculateRoughness(board: Array<IntArray>): Int {
        var roughness = 0
        val peaks = IntArray(gridSize)
        for (c in 0 until gridSize) {
            var peak = 0
            for (r in 0 until gridSize) {
                if (board[r][c] == 1) {
                    peak = gridSize - r
                    break // Find first logic? Python was argmax (first 1)
                }
            }
            peaks[c] = peak
        }
        
        for (i in 0 until gridSize - 1) {
            roughness += Math.abs(peaks[i] - peaks[i+1])
        }
        return roughness
    }

    private fun copyBoard(board: Array<IntArray>): Array<IntArray> {
        return Array(gridSize) { r -> board[r].clone() }
    }
}

object Utils {
    fun <T> priorityQueueOf(): PriorityQueue<T> {
        return PriorityQueue<T>()
    }
}
