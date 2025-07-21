TEMPLATE_STYLE = """
    * {
        color: #E0E0E0;
        background-color: #121212;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 9pt;
    }

    QWidget {
        background-color: transparent;
        border: none;
    }

    QLabel#title {
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
    }

    QLabel#section_title {
        font-size: 10px;
        font-weight: bold;
        color: #A0A0A0;
        text-transform: uppercase;
    }

    QLabel#warning {
        color: #F14C4C;
        font-size: 8pt;
    }

    QLineEdit {
        background-color: #252526;
        border: 1px solid #3F3F46;
        border-radius: 4px;
        padding: 6px;
    }

    QLineEdit:focus {
        border: 1px solid #0078D7;
    }

    QLineEdit[invalid="true"] {
        border: 1px solid #F14C4C;
    }

    QPushButton {
        background-color: #121212;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
        min-height: 24px;
    }

    QPushButton:hover {
        background-color: #171717;
    }

    QPushButton:pressed {
        background-color: #2e2e2e;
    }

    QPushButton:disabled {
        background-color: #090909;
        color: #7F7F7F;
    }
    
    QPushButton:focus { 
        outline: none;
    }
    
    QPushButton#stop {
        background-color: #D32F2F;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QPushButton#stop:hover {
        background-color: #B71C1C;
    }
    
    QPushButton#stop:pressed {
        background-color: #8E0000;
    }
    
    QPushButton#SettingsButton {
        background-color: rgba(40, 40, 40, 230);
        border-radius: 4px;
    }
    
    QPushButton#SettingsButton:hover {
        background-color: rgba(40, 40, 40, 150);
    }
    
    QPushButton#SelectionButton {
        background-color: rgba(40, 40, 40, 230);
        border: none;
        border-radius: 4px;
    }
    
    QPushButton#SelectionButton:hover {
        background-color: rgba(40, 40, 40, 150);
    }
    
    QPushButton#SelectionButton:checked {
        border-bottom: 2px solid white;
        color: white;
    }
    
    QPushButton#NavigationPanelButton {
        background-color: transparent;
        color: white;
        border: none;
        border-radius: 4px;
    }
    
    QPushButton#NavigationPanelButton:hover {
        background-color: rgba(40, 40, 40, 250);
    }
    
    QPushButton#SettingsTabButton {
        background-color: rgba(40, 40, 40, 230);
        color: white;
        border: none;
    }
    
    QPushButton#SettingsTabButton:hover {
        background-color: rgba(40, 40, 40, 150);
    }

    QPushButton#secondary {
        background-color: #3F3F46;
        font-size: 8pt;
    }

    QPushButton#select {
        background-color: #238636;
        font-weight: bold;
    }

    QPushButton#select:hover {
        background-color: #2FA046;
    }

    QPushButton#launch {
        background-color: #5E8C31;
        font-weight: bold;
    }

    QPushButton#launch:hover {
        background-color: #6FA040;
    }

    QFrame#build_card {
        background-color: #252526;
        border: 1px solid #3F3F46;
        border-radius: 6px;
        padding: 8px;
    }

    QFrame#build_card[active="true"] {
        border: 2px solid #0078D7;
    }

    #success_message {
        background-color: #238636;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
    }

    #warning_message {
        background-color: #B34747;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
    }

    #info_message {
        background-color: #3F3F46;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
    }

    QFrame, QWidget#container {
        background-color: transparent;
        border: none;
    }

    QScrollArea, QScrollArea > QWidget > QWidget {
        background-color: transparent;
        border: none;
        border-radius: 6px;
    }

    QListWidget {
        background-color: #252526;
        border: 1px solid #3F3F46;
        border-radius: 4px;
    }

    QListWidget::item {
        padding: 6px;
    }

    QListWidget::item:selected {
        background-color: #0078D7;
    }

    QTextEdit {
        background-color: #252526;
        border: 1px solid #3F3F46;
        border-radius: 4px;
        padding: 6px;
    }

    QGroupBox {
        border: 1px solid #3F3F46;
        border-radius: 6px;
        margin-top: 16px;
        padding: 8px 0px 0px 0px;
        font-weight: bold;
        color: #A0A0A0;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 5px;
    }

    QPushButton#image_btn {
        background-color: #3F3F46;
        border: 1px dashed #5F5F66;
        padding: 16px;
    }

    QPushButton#image_btn:hover {
        background-color: #4F4F56;
    }

    #detail_card {
        background-color: #252526;
        border: 1px solid #3F3F46;
        border-radius: 8px;
        padding: 16px;
    }

    #detail_title {
        font-size: 18px;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 8px;
    }

    #detail_subtitle {
        font-size: 12px;
        color: #A0A0A0;
        margin-bottom: 16px;
    }

    #detail_label {
        font-weight: bold;
        color: #A0A0A0;
        margin-top: 8px;
    }
"""