from pathlib import Path
import re

gradle = Path("app/build.gradle.kts")
g = gradle.read_text(encoding="utf-8")
dep = '  implementation("com.google.android.gms:play-services-ads:23.6.0")'
if dep not in g:
    anchor = "dependencies {"
    if anchor not in g: raise SystemExit("Gradle dependencies block not found")
    g = g.replace(anchor, anchor + "\\n" + dep, 1)
if 'buildConfigField("String", "ADMOB_BANNER_ID"' not in g:
    anchor = '    versionName = "1.0"'
    g = g.replace(anchor, anchor + '''
    buildConfigField("String", "ADMOB_BANNER_ID", "\\"\u0024{System.getenv("ADMOB_BANNER_ID") ?: "ca-app-pub-3940256099942544/6300978111"}\\"")
    manifestPlaceholders["ADMOB_APP_ID"] = System.getenv("ADMOB_APP_ID") ?: "ca-app-pub-3940256099942544~3347511713"''', 1)
gradle.write_text(g, encoding="utf-8")

manifest = Path("app/src/main/AndroidManifest.xml")
m = manifest.read_text(encoding="utf-8")
if 'com.google.android.gms.ads.APPLICATION_ID' not in m:
    m = m.replace('<application', '<application\\n        android:usesCleartextTraffic="false"', 1)
    m = m.replace('        android:allowBackup=', '        <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="\u0024{ADMOB_APP_ID}" />\\n        android:allowBackup=', 1)
manifest.write_text(m, encoding="utf-8")

game = Path("app/src/main/java/com/example/game/SnakesAndLaddersScreen.kt")
s = game.read_text(encoding="utf-8")
if "import android.content.Context" not in s:
    s = s.replace("package com.example.game", "package com.example.game\\n\\nimport android.content.Context\\nimport com.google.android.gms.ads.AdRequest\\nimport com.google.android.gms.ads.AdSize\\nimport com.google.android.gms.ads.AdView\\nimport androidx.compose.ui.platform.LocalContext\\nimport androidx.compose.ui.viewinterop.AndroidView", 1)
if "fun RoyalAdBanner()" not in s:
    s += '''

@Composable
private fun RoyalAdBanner() {
    val context = LocalContext.current
    AndroidView(
        modifier = Modifier.fillMaxWidth().height(56.dp),
        factory = { ctx ->
            AdView(ctx).apply {
                setAdSize(AdSize.BANNER)
                adUnitId = com.example.BuildConfig.ADMOB_BANNER_ID
                loadAd(AdRequest.Builder().build())
            }
        },
        update = { }
    )
}
'''
s = s.replace('''        if (selected == 0) OnlineGameScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
        else SnakesAndLaddersScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
''','''        if (selected == 0) OnlineGameScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
        else SnakesAndLaddersScreen(isBangla = isBangla, modifier = Modifier.weight(1f))
        RoyalAdBanner()
''')
game.write_text(s, encoding="utf-8")
print("AdMob SDK, manifest app ID, and test-banner placement integrated. Release must supply production AdMob IDs.")
