# -*- coding: utf-8 -*-
"""
JARVIS - Android Sesli Asistan (Kivy)
======================================
"Dinle" butonuna bas, komutunu söyle, Jarvis cevap versin.

Desteklenen komutlar (Türkçe):
- "saat kaç"
- "bugünün tarihi"
- "not al [metin]"
- "notlarımı oku"
- "hatırlat [dakika] dakika sonra [mesaj]"
- "hesapla [sayı] [işlem] [sayı]"
- "[konu] ara"

Not: Android'in güvenlik kuralları yüzünden telefonun HER şeyini kontrol eden
sınırsız bir asistan yapmak mümkün değil; bu uygulama izin verilen alanlarda
(bildirim, tarayıcı açma, uygulama kendi içinde not tutma) çalışır.
"""

import os
import re
import threading
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock, mainthread
from kivy.core.window import Window

try:
    from plyer import tts
except Exception:
    tts = None

try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except Exception:
    ANDROID = False

NUMBER_WORDS = {
    "sıfır": 0, "bir": 1, "iki": 2, "üç": 3, "dört": 4, "beş": 5,
    "altı": 6, "yedi": 7, "sekiz": 8, "dokuz": 9, "on": 10,
}
OPERATOR_WORDS = {
    "artı": "+", "topla": "+", "eksi": "-", "çıkar": "-",
    "çarpı": "*", "kere": "*", "bölü": "/", "böl": "/",
}


def get_notes_path():
    from kivy.app import App as _App
    app_dir = _App.get_running_app().user_data_dir
    return os.path.join(app_dir, "notes.txt")


class JarvisUI(BoxLayout):
    pass


class JarvisApp(App):
    def build(self):
        self.title = "Jarvis"
        Window.clearcolor = (0.05, 0.05, 0.08, 1)

        root = BoxLayout(orientation="vertical", padding=20, spacing=15)

        self.status_label = Label(
            text="Merhaba, ben Jarvis.\nAşağıdaki butona basıp konuş.",
            size_hint=(1, 0.2),
            font_size="18sp",
        )
        root.add_widget(self.status_label)

        scroll = ScrollView(size_hint=(1, 0.6))
        self.log_label = Label(
            text="",
            size_hint_y=None,
            font_size="16sp",
            halign="left",
            valign="top",
        )
        self.log_label.bind(texture_size=self._update_log_height)
        self.log_label.bind(width=lambda *_: self.log_label.setter("text_size")(
            self.log_label, (self.log_label.width, None)))
        scroll.add_widget(self.log_label)
        root.add_widget(scroll)

        self.listen_btn = Button(
            text="🎤  DİNLE",
            size_hint=(1, 0.2),
            font_size="22sp",
            background_color=(0.2, 0.6, 1, 1),
        )
        self.listen_btn.bind(on_release=self.start_listen)
        root.add_widget(self.listen_btn)

        if ANDROID:
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])

        return root

    def _update_log_height(self, *args):
        self.log_label.height = self.log_label.texture_size[1]

    def append_log(self, who, text):
        prefix = "SEN: " if who == "user" else "JARVIS: "
        self.log_label.text += f"\n{prefix}{text}"

    # --------------------------------------------------------------
    # Konuşma -> Metin (Android native SpeechRecognizer, pyjnius ile)
    # --------------------------------------------------------------
    def start_listen(self, *_):
        self.status_label.text = "Dinliyorum..."
        if not ANDROID:
            # Masaüstünde test ederken (Android olmadan) elle metin girmek için
            self.append_log("assistant", "Bu özellik sadece Android cihazda çalışır. "
                                          "Masaüstünde test için jarvis_desktop projesini kullan.")
            self.status_label.text = "Hazır."
            return
        threading.Thread(target=self._android_listen, daemon=True).start()

    def _android_listen(self):
        try:
            from jnius import autoclass, PythonJavaClass, java_method
            from android import mActivity

            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
            Locale = autoclass("java.util.Locale")

            activity = mActivity

            class RecognitionListener(PythonJavaClass):
                __javainterfaces__ = ["android/speech/RecognitionListener"]
                __javacontext__ = "app"

                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback

                @java_method("(Landroid/os/Bundle;)V")
                def onResults(self, results):
                    matches = results.getStringArrayList(
                        SpeechRecognizer.RESULTS_RECOGNITION)
                    if matches and matches.size() > 0:
                        self.callback(matches.get(0))
                    else:
                        self.callback("")

                @java_method("(I)V")
                def onError(self, error):
                    self.callback("")

                @java_method("(Landroid/os/Bundle;)V")
                def onReadyForSpeech(self, params):
                    pass

                @java_method("(F)V")
                def onRmsChanged(self, rmsdB):
                    pass

                @java_method("([B)V")
                def onBufferReceived(self, buffer):
                    pass

                @java_method("()V")
                def onBeginningOfSpeech(self):
                    pass

                @java_method("()V")
                def onEndOfSpeech(self):
                    pass

                @java_method("(ILandroid/os/Bundle;)V")
                def onEvent(self, eventType, params):
                    pass

            recognizer = SpeechRecognizer.createSpeechRecognizer(activity)
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                             RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "tr-TR")

            listener = RecognitionListener(self.on_speech_result)
            recognizer.setRecognitionListener(listener)
            recognizer.startListening(intent)

        except Exception as e:
            self.on_speech_result("")
            self.set_status(f"Hata: {e}")

    @mainthread
    def set_status(self, text):
        self.status_label.text = text

    def on_speech_result(self, text):
        text = (text or "").lower().strip()

        def update(_dt):
            self.status_label.text = "Hazır."
            if text:
                self.append_log("user", text)
                response = self.handle_command(text)
                self.append_log("assistant", response)
                self.speak(response)
            else:
                self.append_log("assistant", "Seni anlayamadım, tekrar dener misin?")

        Clock.schedule_once(update, 0)

    def speak(self, text):
        if tts:
            try:
                tts.speak(message=text)
            except Exception:
                pass

    # --------------------------------------------------------------
    # Komutları işleme (masaüstü sürümüyle aynı mantık)
    # --------------------------------------------------------------
    def handle_command(self, text: str) -> str:
        if "saat kaç" in text:
            return f"Saat şu an {datetime.now().strftime('%H:%M')}."

        if "tarih" in text or "hangi gün" in text:
            gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            now = datetime.now()
            return f"Bugün {now.day}.{now.month}.{now.year}, {gunler[now.weekday()]}."

        if text.startswith("not al") or "not tut" in text:
            note = re.sub(r"^(not al|not tut)\b", "", text).strip()
            if not note:
                return "Ne not almamı istediğini duyamadım."
            try:
                with open(get_notes_path(), "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}\n")
                return "Not edildi."
            except Exception:
                return "Notu kaydederken bir sorun oldu."

        if "notlarımı oku" in text or "notları oku" in text:
            path = get_notes_path()
            if not os.path.exists(path):
                return "Henüz kayıtlı bir notun yok."
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return "Not defterin boş."
            son = [re.sub(r"^\[.*?\]\s*", "", l).strip() for l in lines[-3:]]
            return "Son notların: " + " | ".join(son)

        if "hatırlat" in text:
            m = re.search(r"(\d+)\s*dakika sonra\s*(.*)", text)
            if m:
                minutes = int(m.group(1))
                message = m.group(2).strip() or "hatırlatma"
                self._schedule_reminder(minutes, message)
                return f"Tamam, {minutes} dakika sonra hatırlatacağım: {message}"
            return "Örnek kullanım: beş dakika sonra su iç diye hatırlat"

        if text.startswith("hesapla"):
            return self._calculate(text.replace("hesapla", "", 1).strip())

        if "ara" in text:
            query = re.sub(r"(web'?d?e|internette)?\s*(.*?)\s*ara[a-zçğıöşü]*$", r"\2", text).strip()
            if not query:
                query = text.replace("ara", "").strip()
            self._open_search(query)
            return f"{query} için tarayıcıyı açıyorum."

        return "Bu komutu anlayamadım, tekrar söyler misin?"

    def _schedule_reminder(self, minutes, message):
        def fire():
            self.speak(f"Hatırlatma zamanı geldi: {message}")
            self.append_log("assistant", f"(Hatırlatma) {message}")
        threading.Timer(minutes * 60, fire).start()

    def _calculate(self, text):
        tokens = text.split()
        numbers, operator = [], None
        for tok in tokens:
            if tok.isdigit():
                numbers.append(int(tok))
            elif tok in NUMBER_WORDS:
                numbers.append(NUMBER_WORDS[tok])
            elif tok in OPERATOR_WORDS:
                operator = OPERATOR_WORDS[tok]
            elif tok in ("+", "-", "*", "/"):
                operator = tok
        if len(numbers) >= 2 and operator:
            try:
                return f"Sonuç: {eval(f'{numbers[0]}{operator}{numbers[1]}')}"
            except ZeroDivisionError:
                return "Sıfıra bölme yapılamaz."
        return "Hesabı anlayamadım. Örnek: hesapla beş çarpı üç"

    def _open_search(self, query):
        try:
            from jnius import autoclass
            from android import mActivity
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            intent = Intent(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(f"https://www.google.com/search?q={query}"))
            mActivity.startActivity(intent)
        except Exception:
            pass


if __name__ == "__main__":
    JarvisApp().run()
