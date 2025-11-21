import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
import json
from PIL import Image as PILImage
import os
import base64

# --- SETTINGS ---
# INSERT YOUR API KEY HERE INSIDE THE QUOTES:
#Get an API Key from Google Gemini:
#Go to Google AI Studio.
#Generate a key.
#Paste it into the API_KEY variable in the code below (I've marked this location).
#Update libraries: Make sure kivy and pillow are installed.
API_KEY = ""

# Set the window size to the same as the phone for PC testing
Window.size = (360, 740)


class InstaHelperApp(App):

    def build(self):
        # Main container
        root = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # 1. Download button
        self.load_button = Button(
            text='Загрузить фото',
            size_hint=(1, 0.1),
            background_color=(0.1, 0.5, 0.8, 1)
        )
        self.load_button.bind(on_press=self.show_load_dialog)
        root.add_widget(self.load_button)

        # 2. Preview image
        self.image_preview = Image(
            source='',
            size_hint=(1, 0.4),
            allow_stretch=True,
            keep_ratio=True
        )
        root.add_widget(self.image_preview)

        # Scroll for content
        scroll_view = ScrollView(size_hint=(1, 0.5))

        content_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))

        #3. Permission Card
        res_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=80)
        self.resolution_label = Label(
            text='Upload an image for analysis.',
            color=(0.5, 0.5, 0.5, 1),
            text_size=(300, None),  # Для переноса текста
            halign='left',
            valign='middle'
        )
        self.resolution_label.bind(size=self.resolution_label.setter('text_size'))
        res_box.add_widget(self.resolution_label)
        content_layout.add_widget(res_box)

        #4. Card "Alt Text"
        alt_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=120)
        alt_box.add_widget(Label(text='Alt Текст (ИИ):', size_hint_y=None, height=30))
        self.alt_text_input = TextInput(
            hint_text='There will be a description here...',
            multiline=True,
            size_hint=(1, None),
            height=80
        )
        alt_box.add_widget(self.alt_text_input)
        content_layout.add_widget(alt_box)

        # 5. Hashtags Card
        hash_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=150)
        hash_box.add_widget(Label(text='Hashtags (AI):', size_hint_y=None, height=30))
        self.hashtags_input = TextInput(
            hint_text='Hashtags will be here...',
            multiline=True,
            size_hint=(1, None),
            height=100
        )
        hash_box.add_widget(self.hashtags_input)
        content_layout.add_widget(hash_box)

        # 6. Generate button
        self.generate_button = Button(
            text='Generate (AI)',
            size_hint=(1, None),
            height=50,
            background_color=(0.5, 0.2, 0.8, 1)
        )
        self.generate_button.bind(on_press=self.generate_ai_content)
        content_layout.add_widget(self.generate_button)

        scroll_view.add_widget(content_layout)
        root.add_widget(scroll_view)

        return root

    def show_load_dialog(self, instance):
        # Create a file selection widget
        # filters limit the selection to images only
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])

        # Cancel button inside the popup
        cancel_btn = Button(text="Отмена", size_hint_y=None, height=50)

        # Pop-up layout
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(filechooser)
        popup_layout.add_widget(cancel_btn)

        self.popup = Popup(title='Select file', content=popup_layout, size_hint=(0.9, 0.9))

        # Bind actions
        cancel_btn.bind(on_press=self.popup.dismiss)
        filechooser.bind(on_selection=self.load_selected_image)

        self.popup.open()

    def load_selected_image(self, chooser, selection):
        if selection:
            filepath = selection[0]
            self.image_preview.source = filepath
            self.current_filepath = filepath

            # Resolution analysis
            try:
                with PILImage.open(filepath) as img:
                    width, height = img.size
                    self.analyze_resolution(width, height)
            except Exception as e:
                self.resolution_label.text = f"File Error: {e}"

            self.popup.dismiss()

    def analyze_resolution(self, width, height):
        ratio = width / height
        size_str = f"{width}x{height}"

        # Verification logic (simplified version)
        # Ideal ratios: 1:1 (1.0), 4:5 (0.8), 1.91:1 (1.91)

        status_text = ""
        is_optimal = False

        if width == 1080 and height == 1080:
            status_text = f"✅ Ideal (Square 1:1)\n{size_str}"
            is_optimal = True
        elif width == 1080 and height == 1350:
            status_text = f"✅ Ideal (Portrait 4:5)\n{size_str}"
            is_optimal = True
        elif width == 1080 and height == 566:
            status_text = f"✅ Perfect (Album 1.91:1)\n{size_str}"
            is_optimal = True
        else:
            # Checking for proximity to formats
            if 0.98 <= ratio <= 1.02:
                status_text = f"⚠️ Close to square.\nWe recommend 1080x1080. Now: {size_str}"
            elif 0.78 <= ratio <= 0.82:
                status_text = f"⚠️ Close to portrait (4:5).\nWe recommend 1080x1350. Now: {size_str}"
            elif 1.88 <= ratio <= 1.94:
                status_text = f"⚠️ Close to album (1.91:1).\nWe recommend 1080x566. Now: {size_str}"
            else:
                status_text = f"❌ Non-standard format.\nInstagram may crop the photo. Currently: {size_str}"

        self.resolution_label.text = status_text
        if is_optimal:
            self.resolution_label.color = (0.2, 0.8, 0.2, 1)  # Green
        else:
            self.resolution_label.color = (1, 0.6, 0, 1)  # Orange

    def generate_ai_content(self, instance):
        # 1. Checks
        if not hasattr(self, 'current_filepath') or not self.current_filepath:
            self.alt_text_input.text = "First, choose a photo!"
            return

        if not API_KEY:
            self.alt_text_input.text = "Error: Insert API KEY into code!"
            return

        # 2. UI in download mode
        self.generate_button.text = "Think..."
        self.generate_button.disabled = True

        # 3. Preparing the image
        try:
            with open(self.current_filepath, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            mime_type = 'image/jpeg'
            if self.current_filepath.lower().endswith('.png'):
                mime_type = 'image/png'

        except Exception as e:
            self.alt_text_input.text = f"Reading error: {e}"
            self.generate_button.disabled = False
            return

        #4. Request to Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"

        prompt = """Parse an image for Instagram.
        Return the response ONLY in JSON format, without Markdown formatting.
        Structure JSON:
        {
            "altText": "description for people with visual impairments",
            "hashtags": ["#tag1", "#tag2", "#tag3"]
        }
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": mime_type, "data": image_base64}}
                ]
            }],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        headers = {'Content-Type': 'application/json'}

        UrlRequest(
            url,
            req_body=json.dumps(payload),
            req_headers=headers,
            on_success=self.on_success,
            on_failure=self.on_error,
            on_error=self.on_error
        )

    def on_success(self, req, result):
        self.generate_button.text = "Generate (AI)"
        self.generate_button.disabled = False

        try:
            # Kivy UrlRequest sometimes returns a dict, sometimes a string, depending on the headers
            # But Gemini returns a complex structure
            text_content = result['candidates'][0]['content']['parts'][0]['text']
            data = json.loads(text_content)

            self.alt_text_input.text = data.get('altText', 'Failed to create description')
            tags = data.get('hashtags', [])
            self.hashtags_input.text = " ".join(tags)

        except Exception as e:
            self.alt_text_input.text = f"Error reading response: {e}"

    def on_error(self, req, error):
        self.generate_button.text = "Generate (AI)"
        self.generate_button.disabled = False
        self.alt_text_input.text = "Connection or API error."
        print(error)


if __name__ == '__main__':
    InstaHelperApp().run()
