package com.blockblast.bot

import android.app.Application

class BotApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize OpenCV
        System.loadLibrary("opencv_java4")
    }
}
