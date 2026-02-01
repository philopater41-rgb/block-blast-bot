from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
import os

# KV Layout
KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 20
    
    Label:
        text: "Block Blast Bot Helper"
        font_size: 32
        size_hint_y: 0.2
        
    Label:
        text: "1. Grant 'Display Over Other Apps' permission.\\n2. Grant 'Storage' permission.\\n3. Click Start to show the overlay.\\n4. Open Game.\\n5. Take a screenshot manually if auto-capture fails."
        text_size: self.width, None
        halign: 'center'
        valign: 'middle'
            
    Button:
        text: "START OVERLAY"
        font_size: 24
        size_hint_y: 0.2
        on_release: app.start_service()
        background_color: 0, 0.7, 0, 1

    Button:
        text: "STOP"
        font_size: 24
        size_hint_y: 0.2
        on_release: app.stop_service()
        background_color: 0.7, 0, 0, 1
'''

class MainApp(App):
    def build(self):
        return Builder.load_string(KV)

    def start_service(self):
        if platform == 'android':
            from jnius import autoclass
            service = autoclass('org.kivy.android.PythonService').mService
            if service:
                # Service already running
                return
            
            from android import start_service
            start_service(title='Bot Service',
                          description='Block Blast Bot Overlay',
                          arg='')
            
    def stop_service(self):
        if platform == 'android':
            from jnius import autoclass
            service = autoclass('org.kivy.android.PythonService').mService
            if service:
                service.stopSelf()

if __name__ == '__main__':
    MainApp().run()
