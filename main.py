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

# Set window size to mobile dimensions for PC testing
Window.size = (360, 740)


class InstaHelperApp(App):

    def build(self):
        # Main container
        root = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # 1. Load button
        self.load_button = Button(
            text='Load Photo',
            size_hint=(1, 0.1),
            background_color=(0.1, 0.5, 0.8, 1)
        )
        self.load_button.bind(on_press=self.show_load_dialog)
        root.add_widget(self.load_button)

        # 2. Image Preview
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

        # 3. Card "Resolution"
        res_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=80)
        self.resolution_label = Label(
            text='Load an image for analysis.',
            color=(0.5, 0.5, 0.5, 1),
            text_size=(300, None),  # For text wrapping
            halign='left',
            valign='middle'
        )
        self.resolution_label.bind(size=self.resolution_label.setter('text_size'))
        res_box.add_widget(self.resolution_label)
        content_layout.add_widget(res_box)

        # 4. Card "Alt Text"
        alt_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=120)
        alt_box.add_widget(Label(text='Alt Text (AI):', size_hint_y=None, height=30))
        self.alt_text_input = TextInput(
            hint_text='Description will be here...',
            multiline=True,
            size_hint=(1, None),
            height=80
        )
        alt_box.add_widget(self.alt_text_input)
        content_layout.add_widget(alt_box)

        # 5. Card "Hashtags"
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

        # 6. Generate Button
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
        # File chooser widget
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])

        # Container for bottom buttons
        btns_box = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(text="Cancel")
        select_btn = Button(text="Select", background_color=(0.1, 0.5, 0.8, 1))

        btns_box.add_widget(cancel_btn)
        btns_box.add_widget(select_btn)

        # Popup layout
        popup_layout = BoxLayout(orientation='vertical', spacing=10)
        popup_layout.add_widget(filechooser)
        popup_layout.add_widget(btns_box)

        self.popup = Popup(title='Select File', content=popup_layout, size_hint=(0.9, 0.9))

        # Bind actions
        cancel_btn.bind(on_press=self.popup.dismiss)

        # "Select" button triggers loading function
        select_btn.bind(on_press=lambda x: self.load_selected_image(filechooser.selection))

        self.popup.open()

    def load_selected_image(self, selection):
        # Check if a file is selected
        if selection:
            filepath = selection[0]
            self.image_preview.source = filepath
            self.current_filepath = filepath

            # Analyze resolution
            try:
                with PILImage.open(filepath) as img:
                    width, height = img.size
                    self.analyze_resolution(width, height)
            except Exception as e:
                self.resolution_label.text = f"File error: {e}"

            self.popup.dismiss()
        else:
            print("No file selected!")

    def analyze_resolution(self, width, height):
        ratio = width / height
        size_str = f"{width}x{height}"

        status_text = ""
        is_optimal = False

        if width == 1080 and height == 1080:
            status_text = f"✅ Perfect (Square 1:1)\n{size_str}"
            is_optimal = True
        elif width == 1080 and height == 1350:
            status_text = f"✅ Perfect (Portrait 4:5)\n{size_str}"
            is_optimal = True
        elif width == 1080 and height == 566:
            status_text = f"✅ Perfect (Landscape 1.91:1)\n{size_str}"
            is_optimal = True
        else:
            if 0.98 <= ratio <= 1.02:
                status_text = f"⚠️ Close to square.\nRecommend 1080x1080. Current: {size_str}"
            elif 0.78 <= ratio <= 0.82:
                status_text = f"⚠️ Close to portrait (4:5).\nRecommend 1080x1350. Current: {size_str}"
            elif 1.88 <= ratio <= 1.94:
                status_text = f"⚠️ Close to landscape (1.91:1).\nRecommend 1080x566. Current: {size_str}"
            else:
                status_text = f"❌ Non-standard format.\nInstagram might crop the photo. Current: {size_str}"

        self.resolution_label.text = status_text
        if is_optimal:
            self.resolution_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.resolution_label.color = (1, 0.6, 0, 1)

    def generate_ai_content(self, instance):
        if not hasattr(self, 'current_filepath') or not self.current_filepath:
            self.alt_text_input.text = "Select a photo first!"
            return

        if not API_KEY:
            self.alt_text_input.text = "Error: Insert API KEY in the code!"
            return

        self.generate_button.text = "Thinking..."
        self.generate_button.disabled = True

        try:
            with open(self.current_filepath, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            mime_type = 'image/jpeg'
            if self.current_filepath.lower().endswith('.png'):
                mime_type = 'image/png'

        except Exception as e:
            self.alt_text_input.text = f"Read error: {e}"
            self.generate_button.disabled = False
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"

        prompt = """Analyze the image for Instagram.
        Return the response ONLY in JSON format without markdown formatting.
        JSON structure:
        {
            "altText": "description for visually impaired people",
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
            text_content = result['candidates'][0]['content']['parts'][0]['text']
            data = json.loads(text_content)

            self.alt_text_input.text = data.get('altText', 'Failed to generate description')
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
