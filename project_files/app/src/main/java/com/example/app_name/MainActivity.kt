package com.example.{app_name_lower}

import android.os.Bundle
import android.view.LayoutInflater
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity
import android.webkit.WebSettings

class MainActivity: AppCompatActivity() {
    private lateinit var webView: WebView
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        webView = LayoutInflater.from(this).inflate(R.layout.main, null) as WebView
        webView.settings.javaScriptEnabled = true
        webView.settings.allowFileAccess = true
        webView.settings.cacheMode = WebSettings.LOAD_CACHE_ELSE_NETWORK
         
        webView.loadHTML(Project.html)
        setContentView(webView)
    }

}

fun WebView.loadHTML(html:String){
    this.loadDataWithBaseURL(null, html, "text/html", "utf-8", null)
}