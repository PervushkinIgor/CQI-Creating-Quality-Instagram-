from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard

import json
from PIL import Image as PILImage
import os
import base64
from dotenv import load_dotenv

# Безопасный импорт Plyer для кроссплатформенности
try:
    # noinspection PyUnresolvedReferences
    from plyer import share
except ImportError:
    share = None

load_dotenv()
API_KEY = os.getenv("MY_API_KEY")

Window.size = (360, 740)


class InstaHelperApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_preview = None
        self.resolution_label = None
        self.alt_text_input = None
        self.hashtags_input = None
        self.generate_button = None
        self.publish_button = None
        self.popup = None
        self.current_filepath = None
        self.is_optimal_resolution = False

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"

        root = MDBoxLayout(orientation='vertical', spacing=15, padding=20)

        load_button = MDRaisedButton(
            text="LOAD PHOTO",
            size_hint=(1, None),
            height=50,
            md_bg_color=self.theme_cls.primary_color
        )
        load_button.bind(on_press=self.show_load_dialog)
        root.add_widget(load_button)

        img_card = MDCard(
            size_hint=(1, 0.4),
            radius=[15],
            elevation=2,
            padding=5
        )
        self.image_preview = Image(source='', allow_stretch=True, keep_ratio=True)
        img_card.add_widget(self.image_preview)
        root.add_widget(img_card)

        scroll_view = ScrollView(size_hint=(1, 0.5))
        content_layout = MDBoxLayout(orientation='vertical', spacing=20, size_hint_y=None, padding=[0, 10, 0, 10])
        content_layout.bind(minimum_height=content_layout.setter('height'))

        self.resolution_label = MDLabel(
            text='Load an image for analysis.',
            theme_text_color="Hint",
            halign='center',
            size_hint_y=None,
            height=60
        )
        content_layout.add_widget(self.resolution_label)

        self.alt_text_input = MDTextField(
            hint_text="Caption / Alt Text (AI)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=120
        )
        content_layout.add_widget(self.alt_text_input)

        self.hashtags_input = MDTextField(
            hint_text="Hashtags (AI)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=100
        )
        content_layout.add_widget(self.hashtags_input)

        btns_layout = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=120)

        self.generate_button = MDRaisedButton(
            text="GENERATE (AI)",
            size_hint=(1, None),
            height=50,
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        self.generate_button.bind(on_press=self.generate_ai_content)

        self.publish_button = MDRaisedButton(
            text="SHARE TO INSTAGRAM",
            size_hint=(1, None),
            height=50,
            disabled=True,
            md_bg_color=(0.8, 0.2, 0.5, 1)
        )
        self.publish_button.bind(on_press=self.share_to_instagram)

        btns_layout.add_widget(self.generate_button)
        btns_layout.add_widget(self.publish_button)
        content_layout.add_widget(btns_layout)

        scroll_view.add_widget(content_layout)
        root.add_widget(scroll_view)

        return root

    def show_load_dialog(self, _instance):
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        btns_box = MDBoxLayout(size_hint_y=None, height=50, spacing=10, padding=[0, 10, 0, 0])

        cancel_btn = MDFlatButton(text="CANCEL", text_color=self.theme_cls.primary_color)
        select_btn = MDRaisedButton(text="SELECT")

        btns_box.add_widget(cancel_btn)
        btns_box.add_widget(select_btn)

        popup_layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(filechooser)
        popup_layout.add_widget(btns_box)

        self.popup = Popup(title='Select File', content=popup_layout, size_hint=(0.9, 0.9),
                           background_color=(1, 1, 1, 1))
        cancel_btn.bind(on_press=self.popup.dismiss)
        select_btn.bind(on_press=lambda x: self.load_selected_image(filechooser.selection))
        self.popup.open()

    def load_selected_image(self, selection):
        if selection:
            filepath = selection[0]
            self.image_preview.source = filepath
            self.current_filepath = filepath
            self.publish_button.disabled = True

            try:
                with PILImage.open(filepath) as img:
                    width, height = img.size
                    self.analyze_resolution(width, height)
            except Exception as e:
                self.resolution_label.text = f"File error: {e}"

            self.popup.dismiss()

    def analyze_resolution(self, width, height):
        ratio = width / height
        size_str = f"{width}x{height}"
        self.is_optimal_resolution = False

        if width == 1080 and height == 1080:
            status_text = f"✅ Perfect (Square 1:1)\n{size_str}"
            self.is_optimal_resolution = True
        elif width == 1080 and height == 1350:
            status_text = f"✅ Perfect (Portrait 4:5)\n{size_str}"
            self.is_optimal_resolution = True
        elif width == 1080 and height == 566:
            status_text = f"✅ Perfect (Landscape 1.91:1)\n{size_str}"
            self.is_optimal_resolution = True
        elif width == 1080 and height == 1440:
            status_text = f"✅ Perfect (Original 3:4)\n{size_str}"
            self.is_optimal_resolution = True
        else:
            if 0.98 <= ratio <= 1.02:
                status_text = f"⚠️ Close to square.\nRecommend 1080x1080. Current: {size_str}"
            elif 0.78 <= ratio <= 0.82:
                status_text = f"⚠️ Close to portrait (4:5).\nRecommend 1080x1350. Current: {size_str}"
            elif 0.73 <= ratio <= 0.77:
                status_text = f"⚠️ Close to original (3:4).\nRecommend 1080x1440. Current: {size_str}"
            elif 1.88 <= ratio <= 1.94:
                status_text = f"⚠️ Close to landscape (1.91:1).\nRecommend 1080x566. Current: {size_str}"
            else:
                status_text = f"❌ Non-standard format. Instagram might crop it.\nCurrent: {size_str}"

        self.resolution_label.text = status_text
        if self.is_optimal_resolution:
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (0.2, 0.7, 0.2, 1)
            self.publish_button.disabled = False
        else:
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (1, 0.5, 0, 1)

    def generate_ai_content(self, _instance):
        if not hasattr(self, 'current_filepath') or not self.current_filepath:
            self.alt_text_input.text = "Select a photo first!"
            return
        if not API_KEY:
            self.alt_text_input.text = "Error: Insert API KEY in the code!"
            return

        self.generate_button.text = "THINKING..."
        self.generate_button.disabled = True

        try:
            with open(self.current_filepath, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            mime_type = 'image/jpeg' if not self.current_filepath.lower().endswith('.png') else 'image/png'
        except Exception as e:
            self.alt_text_input.text = f"Read error: {e}"
            self.generate_button.disabled = False
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"
        prompt = "Analyze the image for Instagram. Return ONLY JSON: {\"altText\": \"...\", \"hashtags\": [\"#tag1\"]}"
        payload = {
            "contents": [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": mime_type, "data": image_base64}}]}],
            "generationConfig": {"responseMimeType": "application/json"}}
        headers = {'Content-Type': 'application/json'}

        UrlRequest(url, req_body=json.dumps(payload), req_headers=headers, on_success=self.on_success,
                   on_failure=self.on_error, on_error=self.on_error)

    def on_success(self, _req, result):
        self.generate_button.text = "GENERATE (AI)"
        self.generate_button.disabled = False
        try:
            data = json.loads(result['candidates'][0]['content']['parts'][0]['text'])
            self.alt_text_input.text = data.get('altText', '')
            self.hashtags_input.text = " ".join(data.get('hashtags', []))
        except Exception as e:
            self.alt_text_input.text = f"Error: {e}"

    def on_error(self, _req, _error):
        self.generate_button.text = "GENERATE (AI)"
        self.generate_button.disabled = False
        self.alt_text_input.text = "Connection or API error."

    def share_to_instagram(self, _instance):
        if not self.is_optimal_resolution:
            return

        full_text = f"{self.alt_text_input.text}\n\n{self.hashtags_input.text}"
        Clipboard.copy(full_text)

        if share is None:
            self.resolution_label.text = "⚠️ Sharing module not available on this OS."
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (1, 0.5, 0, 1)
            print(f"Copied to clipboard:\n{full_text}")
            return

        try:
            share.share(path=self.current_filepath)
            self.resolution_label.text = "✅ Text copied! Select Instagram in the menu."
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (0.2, 0.7, 0.2, 1)
        except NotImplementedError:
            self.resolution_label.text = "⚠️ Sharing is not supported on this desktop OS."
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (1, 0.5, 0, 1)
            print(f"Copied to clipboard:\n{full_text}")
        except Exception as e:
            self.resolution_label.text = f"❌ Error: {e}"
            self.resolution_label.theme_text_color = "Custom"
            self.resolution_label.text_color = (1, 0, 0, 1)


if __name__ == '__main__':
    InstaHelperApp().run()