package ai.wetu.studio

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.*
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import java.net.URI

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private lateinit var urlInput: EditText
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private val prefs by lazy { getSharedPreferences("wetu", MODE_PRIVATE) }
    private val defaultUrl = "http://10.0.2.2:8787"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        showConnectScreen()
    }

    private fun showConnectScreen() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 56, 28, 28)
            setBackgroundColor(android.graphics.Color.rgb(7, 9, 13))
        }
        val brand = TextView(this).apply {
            text = "WETU"
            textSize = 34f
            setTextColor(android.graphics.Color.WHITE)
            setTypeface(null, android.graphics.Typeface.BOLD)
        }
        val subtitle = TextView(this).apply {
            text = "Creator Studio • Android"
            textSize = 16f
            setTextColor(android.graphics.Color.LTGRAY)
            setPadding(0, 8, 0, 32)
        }
        urlInput = EditText(this).apply {
            hint = "Adresse HTTPS du serveur WETU"
            setText(prefs.getString("base_url", defaultUrl) ?: defaultUrl)
            setSingleLine(true)
            setTextColor(android.graphics.Color.WHITE)
            setHintTextColor(android.graphics.Color.GRAY)
        }
        val connect = Button(this).apply {
            text = "Connecter à WETU"
            setOnClickListener { connectToServer() }
        }
        val note = TextView(this).apply {
            text = "Le serveur doit exposer /api/runtime/health et l'interface Creator. Aucun secret fournisseur n'est stocké dans l'APK."
            textSize = 12f
            setTextColor(android.graphics.Color.GRAY)
            setPadding(0, 24, 0, 0)
        }
        root.addView(brand)
        root.addView(subtitle)
        root.addView(urlInput, LinearLayout.LayoutParams(-1, -2))
        root.addView(connect, LinearLayout.LayoutParams(-1, -2))
        root.addView(note)
        setContentView(root)
    }

    private fun connectToServer() {
        val raw = urlInput.text.toString().trim().removeSuffix("/")
        val uri = runCatching { URI(raw) }.getOrNull()
        if (uri == null || uri.host.isNullOrBlank() || (uri.scheme != "https" && raw != defaultUrl)) {
            Toast.makeText(this, "Utilise une URL HTTPS valide.", Toast.LENGTH_LONG).show()
            return
        }
        prefs.edit().putString("base_url", raw).apply()

        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.settings.allowContentAccess = true
        webView.settings.mediaPlaybackRequiresUserGesture = false
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val host = runCatching { URI(raw).host }.getOrNull()
                return request.url.host != host
            }
        }
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView,
                uploadMsg: ValueCallback<Array<Uri>>,
                fileChooserParams: FileChooserParams
            ): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = uploadMsg
                val intent = fileChooserParams.createIntent().apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                }
                startActivityForResult(intent, 1001)
                return true
            }
        }
        webView.setDownloadListener { url, _, _, _, _ ->
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        }
        webView.loadUrl(raw)
        setContentView(webView)
    }

    @Deprecated("Android activity result API retained for broad device compatibility")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 1001) {
            val result = if (resultCode == RESULT_OK && data?.data != null) arrayOf(data.data!!) else null
            fileCallback?.onReceiveValue(result)
            fileCallback = null
        }
    }

    override fun onDestroy() {
        fileCallback?.onReceiveValue(null)
        fileCallback = null
        if (::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }
}
