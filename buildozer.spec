[app]

# (str) Title of your application
title = BlockBlastBot

# (str) Package name
package.name = blockblastbot

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of exclusions using pattern matching
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# Do not include custom patterns if they are not needed.

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,numpy,opencv,pyjnius,android

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY
services = BotService:service.py

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = SYSTEM_ALERT_WINDOW,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 19b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (str) Android entry point, default is 'org.kivy.android.PythonActivity'
#android.entrypoint = org.kivy.android.PythonActivity

# (list) Android apptheme
#android.branch = master

# (str) Python for android git clone directory (if empty, it will be automatically cached)
#p4a.branch = master

# (list) Python for android dists to use
#p4a.dist_name = mydist

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.hook =

# (str) P4A whitelist
#p4a.whitelist =

# (str) Path to a custom whitelist file
#p4a.whitelist_src =

# (str) Path to a custom blacklist file
#p4a.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
#  their classes. Don't use this for .aar files, use android.add_aars instead.
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
#  directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap)
#android.add_aars =

# (list) Put these files or directories in the apk assets directory.
# Either form may be used, and they may be mixed.
# 1) source:destination
# 2) source
#android.add_assets =

# (list) Gradle dependencies to add (currently works only with sdl2_gradle
# bootstrap)
#android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package that depends on AndroidX.
android.enable_androidx = True

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# The default is GAME, but it may be APP
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
#android.manifest.intent_filters =

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (str) XML file to include as an intent filters in <service> tag
#android.manifest.service_intent_filters =

# (str) Modifies the `manifestPlaceholders` in `build.gradle` (key=value)
#android.gradle_placeholders = {
#    'customKey': 'customValue'
#}

# (list) List of Java classes to add to the compilation.
#android.add_compile_options =

# (list) List of Gradle repositories to add (url or local path)
#android.gradle_repositories =

# (list) List of packaging options to add
#android.packaging_options =

# (list) List of native libraries to include in the apk
#android.native_lib_dirs =

# (int) Android min SDK version to use
#android.min_sdk_version = 21

# (int) Android target SDK version to use
#android.target_sdk_version = 33

# (bool) Use a custom build script
#p4a.use_custom_build_script = False

# (str) Path to a custom build script
#p4a.custom_build_script_path =

# (str) Python for android dists to use
#p4a.dist_name = mydist
