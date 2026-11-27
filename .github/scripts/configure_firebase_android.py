#!/usr/bin/env python3
"""Apply Firebase Android SDK integration to the extracted AI Studio project."""
from pathlib import Path

root = Path(".")
gradle = root / "app/build.gradle.kts"
text = gradle.read_text(encoding="utf-8")
text = text.replace("  // implementation(platform(libs.firebase.bom))",
                    "  implementation(platform(libs.firebase.bom))")
text = text.replace("  // Uncomment to use Firestore:\n  // implementation(libs.firebase.firestore)",
                    "  implementation(libs.firebase.firestore)")
text = text.replace("  // implementation(libs.firebase.auth)",
                    "  implementation(libs.firebase.auth)")
if "implementation(libs.firebase.functions)" not in text:
    text = text.replace(
        "  implementation(libs.firebase.auth)",
        "  implementation(libs.firebase.auth)\\n  implementation(libs.firebase.functions)"
    )
gradle.write_text(text, encoding="utf-8")

catalog = root / "gradle/libs.versions.toml"
text = catalog.read_text(encoding="utf-8")
if "firebase-functions =" not in text:
    text = text.replace(
        "firebase-firestore = { group = \"com.google.firebase\", name = \"firebase-firestore\" }",
        "firebase-firestore = { group = \"com.google.firebase\", name = \"firebase-firestore\" }\n"
        "firebase-functions = { group = \"com.google.firebase\", name = \"firebase-functions\" }"
    )
catalog.write_text(text, encoding="utf-8")

manifest = root / "app/src/main/AndroidManifest.xml"
text = manifest.read_text(encoding="utf-8")
if "android.permission.INTERNET" not in text:
    text = text.replace(
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    xmlns:tools="http://schemas.android.com/tools">',
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n'
        '    xmlns:tools="http://schemas.android.com/tools">\n'
        '    <uses-permission android:name="android.permission.INTERNET" />'
    )
manifest.write_text(text, encoding="utf-8")

backend = root / "app/src/main/java/com/example/FirebaseBackend.kt"
backend.parent.mkdir(parents=True, exist_ok=True)
backend.write_text("""package com.example

import android.content.Context
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.functions.FirebaseFunctions

/** Firebase services are available only when the real app config is present. */
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
    fun functions(): FirebaseFunctions? = firebaseApp?.let { FirebaseFunctions.getInstance(it) }
}
""", encoding="utf-8")

activity = root / "app/src/main/java/com/example/MainActivity.kt"
text = activity.read_text(encoding="utf-8")
needle = "        enableEdgeToEdge()\n        setContent {"
if "FirebaseBackend.initialize(applicationContext)" not in text:
    if needle not in text:
        raise SystemExit("MainActivity insertion point not found; refusing to patch.")
    text = text.replace(needle,
        "        enableEdgeToEdge()\n        FirebaseBackend.initialize(applicationContext)\n        setContent {", 1)
activity.write_text(text, encoding="utf-8")
print("Firebase Android SDK integration applied.")
