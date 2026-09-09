CQI-Creating-Quality-Instagram is a modern, cross-platform mobile and desktop application built with Python and KivyMD that helps SMM specialists and content creators optimize, analyze, and share their images for Instagram using Artificial Intelligence (Google Gemini).

🚀 Features
Image Resolution & Aspect Ratio Analysis: Checks if your photo meets Instagram standards and provides smart recommendations:

Square 1:1 (1080x1080)

Portrait 4:5 (1080x1350)

Original/Vertical 3:4 (1080x1440) (New!)

Landscape 1.91:1 (1080x566)

AI Alt Text Generation: Automatically generates descriptive alternative text for accessibility and SEO using Google Gemini.

AI Hashtag Generation: Suggests relevant hashtags based on the image content to boost engagement.

Native Device Integration (plyer):

In-App Camera: Capture photos directly within the app for instant processing.

Native Share Sheet: Seamlessly pass images and copy captions to share directly to Instagram without storing files on external cloud servers.

Haptic Feedback: Subtle vibration triggers upon successful text copying and sharing.

Modern UI/UX: Built with KivyMD (Material Design) featuring rounded cards, styled text fields, and clean layouts.

Cross-Platform: Designed to run on Android, iOS, Windows, macOS, and Linux.

🛠️ Tech Stack
Python 3

Kivy & KivyMD (UI Framework & Material Design)

Pillow (Image Processing)

Google Gemini API (AI Model for image analysis)

Plyer (Cross-platform native hardware integration)

📦 Installation

Clone the repository:

git clone https://github.com/PervushkinIgor/CQI-Creating-Quality-Instagram-.git
cd CQI-Creating-Quality-Instagram-


Create a virtual environment (optional but recommended):

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


🔑 Configuration
Get a Google Gemini API Key from Google AI Studio.

Create a .env file in the root directory of the project.

Add your API key to the .env file:
MY_API_KEY=your_google_gemini_api_key_here

(Note: For security reasons, do not commit your real API key to GitHub!)

▶️ Usage

Run the application:

python main.py

Workflow:

1. Click "GALLERY" to select an existing image (.jpg, .png) or "TAKE PHOTO" to capture a new one using your camera.

2. Review the Resolution analysis to ensure your image matches optimal Instagram formats.

3. Click "GENERATE (AI)" to let Google Gemini analyze the image and populate the caption/alt text and hashtags.

4. Click "SHARE TO INSTAGRAM" to copy the text to your clipboard with haptic feedback and trigger the native system share sheet.

📱 Mobile Build Requirements (Buildozer)
If you are compiling this application into an APK for Android using Buildozer, make sure your buildozer.spec includes the following configuration:
1. Requirements:
requirements = python3, kivy, kivymd, pillow, python-dotenv, urllib3, plyer, pyjnius
2. Android Permissions:
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, VIBRATE
3. FileProvider Configuration (for Android 7+ sharing security):
android.add_xml_provider = <provider android:name="androidx.core.content.FileProvider" android:authorities="%(packagename)s.fileprovider" android:exported="false" android:grantUriPermissions="true"><meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths"/></provider>
android.add_xml_file_paths = <paths><external-path name="external_files" path="."/></paths>

📄 License

This project is open-source and available under the MIT License.
