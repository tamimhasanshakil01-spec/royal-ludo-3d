#!/usr/bin/env python3
"""Apply the Firebase Android SDK integration to the extracted AI Studio project."""
from pathlib import Path

root = Path(".")
gradle = root / "app/build.gradle.kts"
text = gradle.read_text(encoding="utf-8")
text = text.replace(
    "  // implementation(platform(libs.firebase.bom))",
    "  implementation(platform(libs.firebase.bom))"
)
text = text.replace(
    "  // Uncomment to use Firestore:\\n  // implementation(libs.firebase.firestore)",
    "  implementation(libs.firebase.firestore)"
)
text = text.replace(
    "  // implementation(libs.firebase.auth)",
    "  implementation(libs.firebase.auth)"
)
gradle.write_text(text, encoding="utf-8")

manifest = root / "app/src/main/AndroidManifest.xml"
text = manifest.read_text(encoding="utf-8")
permission = '    <uses-permission android:name="android.permission.INTERNET" />\\n'
if "android.permission.INTERNET" not in text:
    text = text.replace(
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\\n'
        '    xmlns:tools="http://schemas.android.com/tools">',
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\\n'
        '    xmlns:tools="http://schemas.android.com/tools">\\n\\n' + permission.rstrip()
    )
manifest.write_text(text, encoding="utf-8")

backend = root / "app/src/main/java/com/example/FirebaseBackend.kt"
backend.parent.mkdir(parents=True, exist_ok=True)
backend.write_text("""package com.example

import android.content.Context
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore

/**
 * Firebase access point. Services are exposed only when a valid
 * google-services.json has configured this Android application.
 */
object FirebaseBackend {
    @Volatile private var firebaseApp: FirebaseApp? = null
    @Volatile private var attempted = false

    @Synchronized
    fun initialize(context: Context): Boolean {
        if (attempted) return firebaseApp != null
        attempted = true
        firebaseApp = try {
            FirebaseApp.initializeApp(context.applicationContext)
        } catch (_: Exception) {
            null
        }
        return firebaseApp != null
    }

    val isConfigured: Boolean get() = firebaseApp != null
    fun auth(): FirebaseAuth? = firebaseApp?.let { FirebaseAuth.getInstance(it) }
    fun firestore(): FirebaseFirestore? = firebaseApp?.let { FirebaseFirestore.getInstance(it) }
}
""", encoding="utf-8")

activity = root / "app/src/main/java/com/example/MainActivity.kt"
text = activity.read_text(encoding="utf-8")
needle = "        enableEdgeToEdge()\\n        setContent {"
if "FirebaseBackend.initialize(applicationContext)" not in text:
    if needle not in text:
        raise SystemExit("MainActivity insertion point not found; refusing to patch.")
    text = text.replace(needle, "        enableEdgeToEdge()\\n        FirebaseBackend.initialize(applicationContext)\\n        setContent {", 1)
activity.write_text(text, encoding="utf-8")
print("Firebase SDK dependencies, internet permission, guarded bootstrap and app startup hook applied.")
