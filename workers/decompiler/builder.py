import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class BuilderService:
    def __init__(self):
        pass

    def prepare_gradle_project(self, project_dir: str):
        """Создает базовую структуру Gradle для декомпилированного проекта"""
        logger.info(f"Preparing Gradle project in {project_dir}...")
        
        # Создаем build.gradle
        build_gradle_content = """
plugins {
    id 'com.android.application' version '8.1.1'
}

android {
    namespace 'com.example.rebuilt'
    compileSdk 33
    defaultConfig {
        applicationId "com.example.rebuilt"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }
    sourceSets {
        main {
            java.srcDirs = ['sources/src/main/java']
            res.srcDirs = ['resources/res']
            manifest.srcFile 'resources/AndroidManifest.xml'
        }
    }
}
"""
        with open(os.path.join(project_dir, "build.gradle"), "w") as f:
            f.write(build_gradle_content)
            
        # Создаем settings.gradle
        with open(os.path.join(project_dir, "settings.gradle"), "w") as f:
            f.write("rootProject.name = 'rebuilt_apk'\n")

    def build_apk(self, project_dir: str):
        """Запускает процесс сборки через Gradle с реальным Android SDK"""
        try:
            logger.info(f"Starting build in {project_dir} using SDK at {os.getenv('ANDROID_HOME')}...")
            
            # Убеждаемся, что локальные свойства проекта указывают на SDK
            with open(os.path.join(project_dir, "local.properties"), "w") as f:
                f.write(f"sdk.dir={os.getenv('ANDROID_HOME')}\n")

            result = subprocess.run(
                ["gradle", "assembleDebug", "--no-daemon"],
                cwd=project_dir,
                capture_output=True, text=True,
                env={**os.environ, "JAVA_OPTS": "-Xmx2g"}
            )
            if result.returncode == 0:
                apk_path = os.path.join(project_dir, "build/outputs/apk/debug/app-debug.apk")
                logger.info(f"Build successful! APK at {apk_path}")
                return "success", apk_path
            else:
                logger.warning(f"Build failed: {result.stderr}")
                return "failed", result.stderr
        except Exception as e:
            logger.error(f"Error during build: {str(e)}")
            return "error", str(e)
