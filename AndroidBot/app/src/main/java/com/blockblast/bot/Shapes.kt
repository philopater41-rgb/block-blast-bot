package com.blockblast.bot

object Shapes {
    data class Point(val r: Int, val c: Int)
    
    // Convert the list of tuples from Python to List of Lists of Points
    val ALL_POSSIBLE_SHAPES = listOf(
        listOf(Point(0, 0), Point(0, 1)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3), Point(0, 4)), // 1x5
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 0)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 0), Point(1, 1), Point(1, 2)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 0), Point(1, 1), Point(1, 2), Point(2, 0), Point(2, 1), Point(2, 2)), // 3x3
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 0), Point(2, 0)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 1)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 2)),
        listOf(Point(0, 0), Point(0, 1), Point(0, 2), Point(1, 2), Point(2, 2)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 0)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1)), // 2x2
        listOf(Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1), Point(2, 0), Point(2, 1)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 0), Point(2, 0)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 1)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 2)),
        listOf(Point(0, 0), Point(0, 1), Point(1, 1), Point(2, 1)),
        listOf(Point(0, 0), Point(1, 0)),
        listOf(Point(0, 0), Point(1, 0), Point(1, 1)),
        listOf(Point(0, 0), Point(1, 0), Point(1, 1), Point(1, 2)),
        listOf(Point(0, 0), Point(1, 0), Point(1, 1), Point(2, 0)),
        listOf(Point(0, 0), Point(1, 0), Point(1, 1), Point(2, 1)),
        listOf(Point(0, 0), Point(1, 0), Point(2, 0)),
        listOf(Point(0, 0), Point(1, 0), Point(2, 0), Point(2, 1)),
        listOf(Point(0, 0), Point(1, 0), Point(2, 0), Point(2, 1), Point(2, 2)),
        listOf(Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)),
        listOf(Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0), Point(4, 0)), // 5x1
        listOf(Point(0, 0), Point(1, 1)),
        listOf(Point(0, 0), Point(1, 1), Point(2, 2)),
        listOf(Point(0, 1), Point(0, 2), Point(1, 0), Point(1, 1)),
        listOf(Point(0, 1), Point(1, 0)),
        listOf(Point(0, 1), Point(1, 0), Point(1, 1)),
        listOf(Point(0, 1), Point(1, 0), Point(1, 1), Point(1, 2)),
        listOf(Point(0, 1), Point(1, 0), Point(1, 1), Point(2, 0)),
        listOf(Point(0, 1), Point(1, 0), Point(1, 1), Point(2, 1)),
        listOf(Point(0, 1), Point(1, 1), Point(2, 0), Point(2, 1)),
        listOf(Point(0, 2), Point(1, 0), Point(1, 1), Point(1, 2)),
        listOf(Point(0, 2), Point(1, 1), Point(2, 0)),
        listOf(Point(0, 2), Point(1, 2), Point(2, 0), Point(2, 1), Point(2, 2))
    )
}
