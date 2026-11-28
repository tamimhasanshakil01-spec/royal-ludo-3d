from pathlib import Path

gradle = Path("app/build.gradle.kts")
g = gradle.read_text(encoding="utf-8")
dep = '  implementation("com.google.android.gms:play-services-ads:23.6.0")'
if dep not in g:
    if "dependencies {" not in g: raise SystemExit("Gradle dependencies block not found")
    g = g.replace("dependencies {", "dependencies {\\n" + dep, 1)
if 'buildConfigField("String", "ADMOB_BANNER_ID"' not in g:
    anchor = '    versionName = "1.0"'
    addition = r'''
    buildConfigField("String", "ADMOB_BANNER_ID", "\\\"${System.getenv("ADMOB_BANNER_ID") ?: "ca-app-pub-3940256099942544/6300978111"}\\\"")
    manifestPlaceholders["ADMOB_APP_ID"] = System.getenv("ADMOB_APP_ID") ?: "ca-app-pub-3940256099942544~3347511713"'''
    g = g.replace(anchor, anchor + addition, 1)
gradle.write_text(g, encoding="utf-8")

manifest = Path("app/src/main/AndroidManifest.xml")
m = manifest.read_text(encoding="utf-8")
if 'com.google.android.gms.ads.APPLICATION_ID' not in m:
    m = m.replace('        android:allowBackup=', '        <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="${ADMOB_APP_ID}" />\\n        android:allowBackup=', 1)
manifest.write_text(m, encoding="utf-8")

game = Path("app/src/main/java/com/example/game/SnakesAndLaddersScreen.kt")
s = game.read_text(encoding="utf-8")
if "import com.google.android.gms.ads.AdRequest" not in s:
    s = s.replace("package com.example.game", """package com.example.game

import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.AdView
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView""", 1)
if "fun RoyalAdBanner()" not in s:
    s += '''

@Composable
private fun RoyalAdBanner() {
    AndroidView(
        modifier = Modifier.fillMaxWidth().height(56.dp),
        factory = { ctx ->
            AdView(ctx).apply {
                setAdSize(AdSize.BANNER)
                adUnitId = com.example.BuildConfig.ADMOB_BANNER_ID
                loadAd(AdRequest.Builder().build())
            }
        }
    )
}
'''
needle = '        else SnakesAndLaddersScreen(isBangla = isBangla, modifier = Modifier.weight(1f))'
if "        RoyalAdBanner()" not in s:
    s = s.replace(needle, needle + "\\n        RoyalAdBanner()", 1)
game.write_text(s, encoding="utf-8")
print("AdMob SDK and banner integrated; production release must supply real AdMob IDs.")
