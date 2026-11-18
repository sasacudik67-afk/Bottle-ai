[app]

title = Бутылка ИИ
package.name = bottleai
package.domain = org.bottleai
source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Поддержка большинства современных Android-устройств, включая Android 12
android.minapi = 21
android.api = 35
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

# Данные приложения будут храниться в приватной папке приложения.
