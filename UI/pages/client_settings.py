import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, QLineEdit,
    QCheckBox, QSlider, QPushButton, QMessageBox, QLabel, QGroupBox,
    QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from UI.translate import lang
from UI.windows import windowAbs
from UI.windows.windowAbs import DialogAbs


class ClientSettingsDialog(DialogAbs):
    def __init__(self, build_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang.ClientSettings.title)
        self.setMinimumWidth(400)
        self.options_path = os.path.join(build_path, 'options.txt')
        self.opts = {}
        self._load_options()
        self._build_ui()
        self._apply_options_to_ui()

    def _load_options(self):
        if not os.path.exists(self.options_path):
            return
        self.opts = {}
        with open(self.options_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, val = line.split(':', 1)
                self.opts[key] = val.strip()

    def _build_ui(self):
        self._central = QWidget()
        main_layout = QVBoxLayout(self._central)
        self.setCentralWidget(self._central)
        self.tabs = QTabWidget()
        self.video_tab = QWidget()
        self.audio_tab = QWidget()
        self.control_tab = QWidget()
        self.lang_tab = QWidget()
        self._build_video_tab()
        self._build_audio_tab()
        self._build_control_tab()
        self._build_language_tab()
        self.tabs.addTab(self.video_tab, lang.ClientSettings.tab_video)
        self.tabs.addTab(self.audio_tab, lang.ClientSettings.tab_audio)
        self.tabs.addTab(self.control_tab, lang.ClientSettings.tab_control)
        self.tabs.addTab(self.lang_tab, lang.ClientSettings.tab_language)
        main_layout.addWidget(self.tabs)
        save_btn = QPushButton(lang.ClientSettings.save)
        save_btn.clicked.connect(self._save_options)
        main_layout.addWidget(save_btn)

    def _apply_options_to_ui(self):
        gamma = float(self.opts.get('gamma', '1.0'))
        self.gamma_slider.setValue(int(gamma * 100))

        try:
            render_distance = int(self.opts.get('renderDistance', '8'))
        except ValueError:
            render_distance = 8
        self.render_spinbox.setValue(render_distance)

        fullscreen_val = self.opts.get('fullscreen', 'false').lower() == 'true'
        self.fullscreen_checkbox.setChecked(fullscreen_val)

        fov_coeff = float(self.opts.get('fov', '0.0'))
        angle = 70 + fov_coeff * 40
        if angle < 30:
            angle = 30
        if angle > 110:
            angle = 110
        self.fov_input.setText(str(round(angle, 1)))

        vsync_val = self.opts.get('enableVsync', 'true').lower() == 'true'
        self.vsync_checkbox.setChecked(vsync_val)

        max_fps_val = int(self.opts.get('maxFps', '120'))
        if max_fps_val < 10 or max_fps_val > 240:
            max_fps_val = 120
        self.max_fps_spinbox.setValue(max_fps_val)

        for key, slider in self.sound_sliders.items():
            val = self.opts.get(f"soundCategory_{key}", "1.0")
            try:
                fval = float(val)
                slider.setValue(int(fval * 100))
            except:
                slider.setValue(100)

        sensitivity = float(self.opts.get('mouseSensitivity', '0.5'))
        self.mouse_sens_slider.setValue(int(sensitivity * 100))

        invert_mouse_val = self.opts.get('invertYMouse', 'false').lower() == 'true'
        self.invert_mouse_checkbox.setChecked(invert_mouse_val)

        current_lang = self.opts.get('lang', 'en_us')
        for i, code in enumerate(self.langs.values()):
            if code == current_lang:
                self.lang_combo.setCurrentIndex(i)
                break

    def _build_video_tab(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(0, 100)
        form.addRow(lang.ClientSettings.gamma, self.gamma_slider)

        self.render_spinbox = QSpinBox()
        self.render_spinbox.setRange(2, 64)
        form.addRow(lang.ClientSettings.render_distance, self.render_spinbox)

        self.fullscreen_checkbox = QCheckBox(lang.ClientSettings.fullscreen)
        form.addRow(self.fullscreen_checkbox)

        self.fov_input = QLineEdit()
        form.addRow(lang.ClientSettings.fov, self.fov_input)

        self.max_fps_spinbox = QSpinBox()
        self.max_fps_spinbox.setRange(10, 260)
        form.addRow(lang.ClientSettings.max_fps, self.max_fps_spinbox)

        self.vsync_checkbox = QCheckBox(lang.ClientSettings.vsync)
        form.addRow(self.vsync_checkbox)

        group = QGroupBox(lang.ClientSettings.group_video)
        group.setLayout(form)
        layout.addWidget(group)
        self.video_tab.setLayout(layout)

    def _build_audio_tab(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.sound_sliders = {}
        categories = [
            ("master", lang.ClientSettings.sound_master),
            ("music", lang.ClientSettings.sound_music),
            ("record", lang.ClientSettings.sound_record),
            ("weather", lang.ClientSettings.sound_weather),
            ("block", lang.ClientSettings.sound_block),
            ("hostile", lang.ClientSettings.sound_hostile),
            ("neutral", lang.ClientSettings.sound_neutral),
            ("player", lang.ClientSettings.sound_player),
            ("ambient", lang.ClientSettings.sound_ambient),
            ("voice", lang.ClientSettings.sound_voice),
        ]
        for key, label in categories:
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            form.addRow(label, slider)
            self.sound_sliders[key] = slider
        group = QGroupBox(lang.ClientSettings.group_audio)
        group.setLayout(form)
        layout.addWidget(group)
        self.audio_tab.setLayout(layout)

    def _build_control_tab(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.mouse_sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.mouse_sens_slider.setRange(0, 200)
        form.addRow(lang.ClientSettings.sensitivity, self.mouse_sens_slider)
        self.invert_mouse_checkbox = QCheckBox(lang.ClientSettings.invert_mouse)
        form.addRow(self.invert_mouse_checkbox)
        group = QGroupBox(lang.ClientSettings.group_control)
        group.setLayout(form)
        layout.addWidget(group)
        self.control_tab.setLayout(layout)

    def _build_language_tab(self):
        layout = QVBoxLayout(self.lang_tab)
        self.lang_combo = QComboBox()
        self.langs = {
            'af_za': 'Afrikaans (Suid-Afrika)',
            'ar_sa': 'اللغة العربية',
            'ast_es': 'Asturianu',
            'az_az': 'Azərbaycanca (Azərbaycan)',
            'ba_ru': 'Башҡортса',
            'bar': 'Boarisch',
            'be_by': 'Беларуская (Беларусь)',
            'bg_bg': 'Български (България)',
            'br_fr': 'Brezhoneg (Breizh)',
            'brb': 'Braobans',
            'bs_ba': 'Bosanski (Bosna i Hercegovina)',
            'ca_es': 'Català (Catalunya)',
            'cs_cz': 'Čeština (Česko)',
            'cy_gb': 'Cymraeg (Cymru)',
            'da_dk': 'Dansk (Danmark)',
            'de_at': 'Österreichisches Deitsch',
            'de_ch': 'Schwiizerdutsch',
            'de_de': 'Deutsch',
            'el_gr': 'Ελληνικά (Ελλάδα)',
            'en_au': 'English (Australia)',
            'en_ca': 'English (Canada)',
            'en_gb': 'English (United Kingdom)',
            'en_nz': 'English (New Zealand)',
            'en_pt': 'Pirate Speak',
            'en_ud': 'ɥsᴉꞁᵷuƎ (uʍoᗡ ǝpᴉsd∩)',
            'en_us': 'English (US)',
            'enp': 'Anglish',
            'enws': 'Shakespearean English',
            'eo_uy': 'Esperanto',
            'es_ar': 'Español (Argentina)',
            'es_cl': 'Español (Chile)',
            'es_ec': 'Español (Ecuador)',
            'es_es': 'Español (España)',
            'es_mx': 'Español (México)',
            'es_uy': 'Español (Uruguay)',
            'es_ve': 'Español (Venezuela)',
            'esan': 'Andalûh',
            'et_ee': 'Eesti (Eesti)',
            'eu_es': 'Euskara (Euskal Herria)',
            'fa_ir': 'فارسی',
            'fi_fi': 'Suomi (Suomi)',
            'fil_ph': 'Filipino (Pilipinas)',
            'fo_fo': 'Føroyskt (Føroyar)',
            'fr_ca': 'Français (Québec)',
            'fr_fr': 'Français (France)',
            'fra_de': 'Fränggisch (Franggn)',
            'fur_it': 'Furlan (Friûl)',
            'fy_nl': 'Frysk (Fryslân)',
            'ga_ie': 'Gaeilge (Éire)',
            'gd_gb': 'Gàidhlig (Alba)',
            'gl_es': 'Galego (Galicia)',
            'haw_us': 'ʻŌlelo Hawaiʻi (Hawaiʻi)',
            'he_il': 'עברית',
            'hi_in': 'हिन्दी',
            'hr_hr': 'Hrvatski (Hrvatska)',
            'hu_hu': 'Magyar (Magyarország)',
            'hy_am': 'Հայերեն',
            'id_id': 'Bahasa Indonesia (Indonesia)',
            'ig_ng': 'Igbo (Naijiria)',
            'io_en': 'Ido',
            'is_is': 'Íslenska (Ísland)',
            'isv': 'Medžuslovjansky',
            'it_it': 'Italiano (Italia)',
            'ja_jp': '日本語',
            'jbo_en': 'la .lojban.',
            'ka_ge': 'ქართული',
            'kk_kz': 'Қазақша',
            'kn_in': 'ಕನ್ನಡ',
            'ko_kr': '한국어',
            'ksh': 'Kölsch/Ripoarisch',
            'kw_gb': 'Kernewek (Kernow)',
            'la_la': 'Latina (Latium)',
            'lb_lu': 'Lëtzebuergesch (Lëtzebuerg)',
            'li_li': 'Limburgs',
            'lmo': 'Lombard (Lombardia)',
            'lol_us': 'LOLCAT (Kingdom of Cats)',
            'lt_lt': 'Lietuvių',
            'lv_lv': 'Latviešu (Latvija)',
            'lzh': '文言（華夏）',
            'mk_mk': 'Македонски',
            'mn_mn': 'Монгол',
            'ms_my': 'Bahasa Melayu (Malaysia)',
            'mt_mt': 'Malti (Malta)',
            'nah': 'Mēxikatlahtōlli (Mēxiko)',
            'nds_de': 'Platdüütsk',
            'nl_be': 'Vlaams (Vlaanderen)',
            'nl_nl': 'Nederlands (Nederland)',
            'nn_no': 'Norsk nynorsk (Norge)',
            'no_no': 'Norsk Bokmål (Norge)',
            'oc_fr': 'Occitan',
            'ovd': 'Övdalsk',
            'pl_pl': 'Polski (Polska)',
            'pt_br': 'Português (Brasil)',
            'pt_pt': 'Português (Portugal)',
            'qya_aa': 'Quenya',
            'ro_ro': 'Română (România)',
            'rpr': 'Дореформенный русскiй',
            'ru_ru': 'Русский',
            'ry_ua': 'Руснацькый',
            'sah_sah': 'Сахалыы',
            'se_no': 'Davvisámegiella',
            'sk_sk': 'Slovenčina (Slovensko)',
            'sl_si': 'Slovenščina',
            'so_so': 'Af-Soomaali (Soomaaliya)',
            'sq_al': 'Shqip (Shqiperia)',
            'sr_cs': 'Srpski (Srbija)',
            'sr_sp': 'Српски (Србија)',
            'sv_se': 'Svenska (Sverige)',
            'sxu': 'Säggs\'sch',
            'szl': 'Ślōnskŏ',
            'ta_in': 'தமிழ்',
            'th_th': 'ไทย',
            'tl_ph': 'Tagalog (Pilipinas)',
            'tlh_aa': 'tlhIngan Hol',
            'tok': 'toki pona (ma pona)',
            'tr_tr': 'Türkçe (Türkiye)',
            'tt_ru': 'Татарча',
            'uk_ua': 'Українська',
            'val_es': 'Català (Valencià)',
            'vec_it': 'Vèneto',
            'vi_vn': 'Tiếng Việt (Việt Nam)',
            'yi_de': 'ייִדיש',
            'yo_ng': 'Yorùbá',
            'zh_cn': '简体中文（中国大陆）',
            'zh_hk': '繁體中文（香港特別行政區）',
            'zh_tw': '繁體中文（台灣）',
            'zlm_arab': 'بهاس ملايو'
        }

        self.lang_combo.addItems(self.langs.keys())
        layout.addWidget(QLabel(lang.ClientSettings.lang_label))
        layout.addWidget(self.lang_combo)
        layout.addStretch()

    def _save_options(self):
        self.opts['gamma'] = f"{self.gamma_slider.value() / 100:.2f}"
        self.opts['renderDistance'] = str(self.render_spinbox.value())
        self.opts['fullscreen'] = 'true' if self.fullscreen_checkbox.isChecked() else 'false'
        try:
            angle = float(self.fov_input.text().strip())
            if angle < 30:
                angle = 30
            if angle > 110:
                angle = 110
            fov_coeff = (angle - 70) / 40
        except ValueError:
            fov_coeff = 0.0
        self.opts['fov'] = f"{fov_coeff:.2f}"
        self.opts['maxFps'] = str(self.max_fps_spinbox.value())
        self.opts['enableVsync'] = 'true' if self.vsync_checkbox.isChecked() else 'false'
        for key, slider in self.sound_sliders.items():
            self.opts[f"soundCategory_{key}"] = f"{slider.value() / 100:.2f}"
        self.opts['mouseSensitivity'] = f"{self.mouse_sens_slider.value() / 100:.2f}"
        self.opts['invertYMouse'] = 'true' if self.invert_mouse_checkbox.isChecked() else 'false'
        self.opts['lang'] = self.langs[self.lang_combo.currentText()]
        try:
            with open(self.options_path, 'w', encoding='utf-8') as f:
                for k, v in self.opts.items():
                    f.write(f"{k}:{v}\n")
            windowAbs.information(self, lang.ClientSettings.success, lang.ClientSettings.saved, btn_text=lang.Dialogs.ok)
        except Exception as e:
            windowAbs.critical(self, lang.ClientSettings.error, f"{lang.ClientSettings.save_failed}:\n{e}", btn_text=lang.Dialogs.ok)
