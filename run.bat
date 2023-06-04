@echo off
python main.py && android\gradlew assembleDebug -b android/build.gradle && android\gradlew installDebug -b android/build.gradle