[app]

# (str) Title of your application
title = PM2.5 AQI Calculator

# (str) Package name
package.name = pm25_aqi_calculator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,matplotlib,numpy,pandas,openpyxl,plyer

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
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info
# change the copyright to your company name
author = Your Name

# (str) JSON file to manifest orientation
#orientation.manifest =

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain only)
# Available values corresponds to colors that can be set in android
# R = red, G = green, B = blue
# R, G, B range = 0-255
# 255,255,255 = white
# 0,0,0 = black
#presplash.color = 0,0,0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path = /home/runner/android-sdk

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an Android SDK is available but not installed via the Android tool
#android.skip_update = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
#android.apptheme = @android:style/Theme.NoTitleBar

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (same as add jar, but should be used for aar)
#android.add_aars =

# (list) Gradle dependencies to add (same as add jar but for gradle dependencies)
#android.gradle_dependencies =

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' property
#android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"
# see https://developer.android.com/studio/write/java8-support
#android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Android Services to declare
#android.services = com.example.ExampleService:com.example.ExampleService

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a_bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for debug builds)
#p4a.port =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy
# Uncomment to use a custom checkout
#ios.ios_deploy_dir = ../ios_deploy
# Or specify URL and branch
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_exts.
#    Instead of source.exclude_exts = spec
#    This can be translated into:
#
#    [app:source.exclude_exts]
#    spec
#
#    -----------------------------------------------------------------------------
#
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#    [app@demo]
#    title = My Application (demo)
#
#    [app:source.exclude_dirs@demo]
#    images/hd/*
#
#    -----------------------------------------------------------------------------
#    Important notes
#
#    - Android:
#        - Binaries with extension different than .so, will not be copied to the APK
#        - Android extension: .so
#        - iOS extension: .dylib
#        - Windows extension: .dll
#        - MacOSX extension: .dylib
#        - Linux extension: .so
#
#    - iOS:
#        - Binaries with extension different than .dylib, will not be copied to the IPA
#
#    - Windows:
#        - Binaries with extension different than .dll, will not be copied to the package
#
#    - MacOSX:
#        - Binaries with extension different than .dylib, will not be copied to the package
#
#    - Linux:
#        - Binaries with extension different than .so, will not be copied to the package
#
#    -----------------------------------------------------------------------------