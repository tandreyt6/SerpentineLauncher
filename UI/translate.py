class RU:
    name = "RU"
    class Elements:
        builds = "Сборки"
        cores = "Ядра"
        mods = "Моды"
        settings = "Настройки"
        profile = "Профиль"
        select_version = "Выбрать версию Minecraft и ядро"
        create_build = "Создать сборку"
        play = "Играть"
        edit = "Изменить"
        delete = "Удалить"
        detailed_view = "Детальный просмотр"
        client_settings_btn = "Настройки Клиента"
        create_shortcut_btn = "Создать ярлык"
        stop = "Остановить"
        build_new_minecraft = "Создай свою уникальную сборку Minecraft"
        enter_build_name = "Введите название сборки"
        open_build_folder = "Открыть папку сборки"
        open_launcher_folder = "Открыть папку лаунчера"
        about_changes_title = "О отличие лаунчера"
        download_launcher = "Скачать Лаунчер"
        show_console = "Показать консоль"
        hide_console = "Спрятать консоль"
        installed_cores_title = "Установленные ядра Minecraft"
        search_placeholder = "Поиск..."
        update_cores_elements = "Обновить список"
        no_available_installed_cores = "Ни одно ядро поддерживаемое не установленно"
        install = "Установить"
        reinstall = "Переустановить"
        about_core = "О Ядре"
        core_type = "Тип ядра:"
        core_version = "Версия ядра:"
        minecraft_version = "Версия Minecraft:"
        installed = "Установлено"
        core_installed = "{type} {version} установлена"
        core_deleted = "Ядро {type} {version} удалена"

    class ClientSettings:
        title = "Настройки клиента"
        error = "Ошибка"
        not_found = "Файл настроек не найден"
        save = "Сохранить"
        success = "Успешно"
        saved = "Настройки сохранены"
        save_failed = "Не удалось сохранить настройки"
        tab_video = "Видео"
        tab_audio = "Звук"
        tab_control = "Управление"
        tab_language = "Язык"
        group_video = "Настройки видео"
        group_audio = "Настройки звука"
        group_control = "Настройки управления"
        gamma = "Гамма"
        render_distance = "Дальность прорисовки"
        fullscreen = "Полноэкранный режим"
        fov = "Поле зрения (FOV)"
        vsync = "Вертикальная синхронизация (VSync)"
        sound_master = "Основная громкость"
        sound_music = "Музыка"
        sound_record = "Пластинки"
        sound_weather = "Звуки погоды"
        sound_block = "Звуки блоков"
        sound_hostile = "Враги"
        sound_neutral = "Нейтральные существа"
        sound_player = "Игрок"
        sound_ambient = "Окружающие звуки"
        sound_voice = "Голос"
        sensitivity = "Чувствительность мыши"
        invert_mouse = "Инвертировать мышь"
        lang_label = "Выбор языка клиента"
        max_fps = "Максимальный FPS"

    class Html:
        about_changes = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SerpentineLauncher — Уникальные особенности</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #121212;
            --card-bg: #1e1e1e;
            --primary: #bb86fc;
            --primary-hover: #d0a5ff;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --border: #333;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --success: #03dac5;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: var(--bg-dark);
            background-image: radial-gradient(circle at 25% 25%, rgba(40, 40, 40, 0.8) 0%, transparent 55%);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            position: relative;
        }
        
        h1 {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 1.5rem 0 0.8rem;
            letter-spacing: -0.5px;
        }
        
        .logo {
            font-size: 3.5rem;
            color: var(--primary);
            margin-bottom: 1rem;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.2rem;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.7;
        }
        
        .tabs-container {
            background: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
            margin-bottom: 3rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .tab-header {
            display: flex;
            background: rgba(30, 30, 30, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
        }
        
        .tab-btn {
            flex: 1;
            background: none;
            border: none;
            color: var(--text-secondary);
            padding: 1.4rem;
            font-size: 1.15rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .tab-btn:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .tab-btn.active {
            color: var(--primary);
            background: rgba(187, 134, 252, 0.08);
        }
        
        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--primary);
            border-radius: 3px 3px 0 0;
        }
        
        .tab-content {
            padding: 2.8rem;
            display: none;
            animation: fadeIn 0.4s ease-out;
        }
        
        .tab-content.active {
            display: block;
        }
        
        h3 {
            font-size: 1.9rem;
            margin-bottom: 1.8rem;
            color: var(--primary);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        h3 i {
            font-size: 1.6rem;
        }
        
        p {
            margin-bottom: 1.4rem;
            font-size: 1.15rem;
            line-height: 1.8;
        }
        
        code {
            background: rgba(187, 134, 252, 0.15);
            color: var(--primary);
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-family: 'Fira Code', monospace;
            font-size: 1rem;
            border: 1px solid rgba(187, 134, 252, 0.3);
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem 0;
            border-left: 4px solid var(--primary);
        }
        
        .comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin: 2rem 0;
        }
        
        .comparison-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1.8rem;
        }
        
        .comparison-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.2rem;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .viper-badge {
            background: rgba(3, 218, 197, 0.15);
            color: var(--success);
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        footer {
            text-align: center;
            color: var(--text-secondary);
            padding-top: 3rem;
            font-size: 0.95rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .footer-links a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: var(--transition);
        }
        
        .footer-links a:hover {
            color: var(--primary);
        }
        
        @media (max-width: 900px) {
            .comparison {
                grid-template-columns: 1fr;
            }
            
            body {
                padding: 1.5rem;
            }
            
            .tab-header {
                flex-direction: column;
            }
            
            .tab-content {
                padding: 1.8rem;
            }
            
            h1 {
                font-size: 2.3rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Чем отличается SerpentineLauncher</h1>
            <p class="subtitle">Уникальная архитектура и передовые решения, выделяющие наш лаунчер среди аналогов вроде TLauncher</p>
        </header>
        
        <div class="tabs-container">
            <div class="tab-header">
                <button class="tab-btn" data-tab="Storage">
                    <i class="fas fa-database"></i> Хранение сборок
                </button>
                <button class="tab-btn" data-tab="Behavior">
                    <i class="fas fa-cogs"></i> Поведение лаунчера
                </button>
                <button class="tab-btn" data-tab="CLI">
                    <i class="fas fa-terminal"></i> Командная строка
                </button>
            </div>
            
            <div id="Storage" class="tab-content">
                <h3><i class="fas fa-database"></i> Умная система хранения</h3>
                
                <div class="comparison">
                    <div class="comparison-item">
                        <div class="comparison-title">
                            <i class="fas fa-folder"></i> TLauncher
                        </div>
                        <p>Ядро (например, Forge) хранится вместе со сборкой в одной папке, а версии находятся в <code>./versions</code>.</p>
                    </div>
                    
                    <div class="comparison-item">
                        <div class="comparison-title">
                            <i class="fas fa-folder-tree"></i> SerpentineLauncher
                        </div>
                        <p>Ядро версии хранится в <code>./versions</code>, а сами сборки — в <code>./builds</code>.</p>
                        <div class="viper-badge">
                            <i class="fas fa-star"></i> Преимущество
                        </div>
                        <p>Позволяет скачать ядро один раз и использовать его для всех совместимых сборок.</p>
                    </div>
                </div>
                
                <div class="feature-card">
                    <p><strong>Экономия ресурсов:</strong> Устраняет дублирование файлов и уменьшает занимаемое место на диске до 40% для коллекций сборок.</p>
                </div>
            </div>
            
            <div id="Behavior" class="tab-content">
                <h3><i class="fas fa-cogs"></i> Оптимизированная работа</h3>
                
                <p>SerpentineLauncher реализует интеллектуальное управление экземплярами:</p>
                
                <div class="feature-card">
                    <ul style="padding-left: 1.5rem; margin: 1rem 0;">
                        <li>Архитектура с одним экземпляром предотвращает множественные запуски</li>
                        <li>Попытка открыть второй экземпляр активирует существующее окно</li>
                        <li>Поддержка одновременного запуска нескольких сборок</li>
                    </ul>
                </div>
                
                <p>Этот подход сокращает потребление ресурсов на 60% по сравнению с традиционными лаунчерами, сохраняя полную функциональность.</p>
                
                <div class="viper-badge" style="margin-top: 1.5rem;">
                    <i class="fas fa-bolt"></i> Производительность
                </div>
                <p>Один процесс лаунчера управляет всеми активными сборками, уменьшая нагрузку на систему.</p>
            </div>
            
            <div id="CLI" class="tab-content">
                <h3><i class="fas fa-terminal"></i> Расширенные CLI возможности</h3>
                
                <p>Полноценное управление через командную строку для автоматизации и сложных задач:</p>
                
                <div class="feature-card">
                    <p><strong>Доступ к документации:</strong></p>
                    <code>SerpentineLauncher.exe --help</code>
                    
                    <p style="margin-top: 1.5rem;"><strong>Запуск без графического интерфейса:</strong></p>
                    <code>SerpentineLauncher.exe --launch "НазваниеСборки" --no-gui</code>
                    
                    <p style="margin-top: 1.5rem;"><strong>Управление версиями:</strong></p>
                    <code>SerpentineLauncher.exe --install-version 1.19.2 --with-forge</code>
                </div>
                
                <p>Поддерживаются все основные операции, что позволяет использовать лаунчер в скриптах и на серверах без GUI.</p>
            </div>
        </div>
        
        <footer>
            <p>SerpentineLauncher &copy; 2025 | Инновационный подход к игровым лаунчерам</p>
        </footer>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabBtns = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabBtns[0].classList.add('active');
            tabContents[0].classList.add('active');
            
            tabBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    
                    tabBtns.forEach(b => b.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                    this.classList.add('active');
                    document.getElementById(tabId).classList.add('active');
                });
            });
        });
    </script>
</body>
</html>"""

    class Dialogs:
        close_all = "Закрыть всё"
        hide_launcher = "Скрыть лаунчер"
        ok = "Ок"
        yes = "Да"
        no = "Нет"
        cancel = "Отмена"
        confirm_title = "Подтверждение"
        confirm_text = "Что вы хотите сделать?"
        select_version_title = "Выбор версии"
        search_versions = "Поиск версий..."
        minecraft_version = "Версия Minecraft:"
        core_type = "Тип ядра:"
        core_version = "Версия ядра:"
        minecraft_label = "<b>Minecraft:</b>"
        core_type_label = "<b>Ядро:</b>"
        core_version_label = "<b>Версия ядра:</b>"
        error = "Ошибка"
        select_minecraft_version = "Выберите версию Minecraft!"
        select_core_type = "Выберите тип ядра!"
        select_core_version = "Выберите версию ядра!"
        minecraft_builds = "Сборки Minecraft"
        your_builds = "Ваши сборки"
        no_builds = "У вас пока нет сборок. Создайте первую!"
        no_version_selected = "Версия не выбрана"
        name_too_short = "Название должно быть не менее 3 символов"
        build_exists = "Сборка с таким именем уже существует"
        select_build_first = "Сначала выберите сборку!"
        build_stopped = "Сборка '{name}' остановлена!"
        build_not_running = "Сборка '{name}' не запущена!"
        build_created = "Сборка '{name}' создана!"
        select_build_to_launch = "Сначала выберите сборку для запуска!"
        build_not_exists = "Выбранная сборка больше не существует!"
        core_install_canceled = "Установка ядра была отменена!"
        username_not_specified = "Имя пользователя не указано!"
        build_name_not_specified = "Название сборки не указано!"
        build_not_found = "Сборка не найдена!"
        unsupported_core_type = "Не поддерживаемый тип ядра!"
        launching_build = "Запуск Minecraft {minecraft} с {core_type}..."
        build_already_running = "Сборка '{name}' уже запущена!"
        confirm_deletion = "Подтверждение удаления"
        confirm_delete_build = "Вы уверены, что хотите удалить сборку '{name}'?"
        build_updated = "Сборка '{name}' обновлена!"
        build_update_failed = "Не удалось обновить сборку!"
        build_deleted = "Сборка '{name}' удалена!"
        fabric_tooltip = "Сборка сделана с использованием ядра 'Fabric'"
        forge_tooltip = "Сборка сделана с использованием ядра 'Forge'"
        quilt_tooltip = "Сборка сделана с использованием ядра 'Quilt'"
        vanilla_tooltip = "Сборка не использует дополнительные ядра"
        unknown_tooltip = "Сборка использует не поддерживаемое ядро"
        install_core_title = "Установка ядра"
        start_installation = "Начало установки..."
        installation_success = "Установка завершена успешно!"
        installation_error = "Ошибка установки: {error_msg}"
        cancel_installation = "Отмена установки..."
        close = "Закрыть"
        profiles_title = "Профили Minecraft"
        nickname_label = "Никнейм:"
        token_label = "Токен (не изменяйте, если не знаете):"
        uuid_label = "UUID (не изменяйте, если не знаете):"
        your_profiles = "Ваши профили"
        create_profile = "Создать профиль"
        toggle_tech_params = "Технические параметры ▼"
        toggle_tech_params_expanded = "Технические параметры ▲"
        select_profile = "Установить выбранный профиль"
        delete = "Удалить"
        nickname_placeholder = "Введите ник (3-16 символов)"
        char_counter = "0/16"
        no_profiles = "У вас пока нет профилей. Создайте первый!"
        nickname_length_warning = "Длина ника должна быть 3-16 символов"
        nickname_chars_warning = "Только буквы, цифры и подчёркивание"
        nickname_exists_warning = "Этот ник уже используется"
        confirm_deletion_title = "Подтверждение удаления"
        confirm_deletion_text = "Вы уверены, что хотите удалить профиль '{nickname}'?"
        profile_created = "Профиль '{nickname}' создан!"
        profile_deleted = "Профиль '{nickname}' удалён"
        select_profile_first = "Сначала выберите профиль из списка"
        offline_status = "Автономный"
        active_status = "Автономный ⭐ Активный"
        general_tab = "Общие"
        game_settings_tab = "Игровые настройки"
        advanced_tab = "Расширенные"
        about_tab = "О программе"
        restart_required = "Требуется перезапуск приложения"
        language_label = "Язык"
        use_anim_transitions = "Использовать анимацию переходов (экспериментально)"
        select_java_path = "Выберите путь к исполняемому файлу Java"
        show_console = "Показывать консоль (возможно нужно перезапустить игру)"
        panel_behavior_group = "Поведение панели"
        panel_position_on_top = "Поверх других"
        panel_position_shift = "Смещать"
        panel_state_standard = "Стандартное"
        panel_state_always_expanded = "Всегда развернута"
        panel_state_always_collapsed = "Всегда свернута"
        launcher_behavior_group = "Поведение лаунчера при запуске"
        launcher_hide_completely = "Скрывать полностью"
        launcher_minimize_to_taskbar = "Свернуть в панель задач"
        launcher_do_nothing = "Ничего"
        set_java_memory = "Установите объем памяти для Java"
        memory_suffix = " Mb"
        about_title = "Minecraft Лаунчер"
        about_version = "v2.0-beta"
        about_author = "Tandreyt6"
        about_description = "Компактный лаунчер для Minecraft с удобным управлением профилями и настройками Java."
        about_new_in_version = "Новое в v2.0"
        about_new_features = "Оптимизация памяти, анимации, выбор версий игры и управление окнами."
        about_copyright = "© 2025 Tandreyt6"
        select = "Выбрать"
        select_build = "Выберите сборку:"
        all_loaders = "Все загрузчики"
        filter_by_loader = "Фильтр по загрузчику:"
        enter_mod_name = "Введите название мода..."
        add_to_queue = "Добавить в очередь"
        search_mods = "Поиск модов"
        download_queue = "Очередь загрузки:"
        move_up = "Вверх"
        move_down = "Вниз"
        remove = "Удалить"
        install_all = "Установить все"
        download_queue_tab = "Очередь загрузки"
        installed_mods = "Установленные моды:"
        build_structure = "Структура сборки:"
        file_folder = "Файл/Папка"
        path = "Путь"
        build_management = "Управление сборкой"
        queue_empty_title = "Очередь пустая"
        queue_empty_message = "Добавьте моды в очередь перед установкой."
        no_compatible_versions = "нет совместимых версий"
        completed_with_errors = "Завершено с ошибками"
        success = "Успех"
        all_mods_installed_successfully = "Установка всех модов завершена успешно."
        loading = "Загрузка..."
        no_mods_found = "Моды не найдены"
        search_error = "Ошибка поиска"
        not_supported = "не поддерживает"
        mod_not_supported = "Мод не поддерживает"
        loading_mod_info = "Загрузка информации о моде..."
        failed_to_get_mod_data = "Не удалось получить данные мода"
        mod_data_processing_error = "Ошибка обработки данных мода"
        name = "Название"
        authors = "Авторы"
        description = "Описание"
        game_versions = "Версии игры"
        categories = "Категории"
        project_type = "Тип проекта"
        downloads = "Загрузки"
        select_build_and_mod = "Выберите сборку и мод для добавления!"
        information = "Информация"
        mod_already_in_queue = "Этот мод уже в очереди."
        added = "Добавлено"
        mod_added_to_queue = "{title} добавлен в очередь."
        done = "Готово"
        all_mods_downloaded = "Все моды загружены."
        confirmation = confirm_title
        mod_exists = "Мод {filename} уже существует. Перезаписать?"
        download_failed = "Не удалось скачать мод: HTTP {status}"
        confirm_remove = "Удалить мод {mod}?"
        mod_removed = "Мод удалён!"
        remove_error = "Ошибка удаления: {error}"
        no_build_selected = "Сборка не выбрана"
        mods_dir_not_found = "Директория модов не найдена"
        no_mods_installed = "Моды не установлены"
        mod_load_error = "Ошибка загрузки мода: {mod}"
        toggle_mod_error = "Не удалось переключить мод: {error}"
        delete_mod_error = "Не удалось удалить мод: {error}"
        build = "Сборка"
        untitled = "Без названия"
        mod_installed = "Мод {title} установлен!"
        unknown = "Неизвестно"
        loader = "загрузчик"
        double_click_behavior_group = "Поведение при двойном клике по сборке"
        double_click_launch = "Запустить"
        double_click_info = "Открыть информацию"
        double_click_settings = "Открыть настройки"
        about_changes_question = "Вы хотите ознакомится об отличиях лаунчера от других(например TLauncher)?"
        no_java_selected = "Java не выбрана! перейдите в Настройки -> Расширенные!"
        impossible = "Невозможно"
        error_debug_hide_console = "Невозможно спрятать консоль в режиме отладки!"
        delete_title = "Удаление"
        delete_core = "Вы уверены, что хотите удалить ядро?"
        reinstall_core = "Вы уверены, что хотите переустановить ядро?\nЭто удалит существующие ядро и заново его загрузит"
        error_delete_core = "Ошибка удаления {type} {version} перед переустановкой"

class EN:
    name = "EN"
    class Elements:
        builds = "Builds"
        cores = "Cores"
        mods = "Mods"
        settings = "Settings"
        profile = "Profile"
        select_version = "Select Minecraft Version and Core"
        create_build = "Create Build"
        play = "Play"
        edit = "Edit"
        delete = "Delete"
        detailed_view = "Detailed View"
        stop = "Stop"
        client_settings_btn = "Client Settings"
        create_shortcut_btn = "Create shortcut"
        build_new_minecraft = "Create your own unique Minecraft build"
        enter_build_name = "Enter the name of the build"
        open_build_folder = "Open the build folder"
        open_launcher_folder = "Open the launcher folder"
        about_changes_title = "About the difference of the launcher"
        download_launcher = "Download launcher"
        show_console = "Show console"
        hide_console = "Hide console"
        installed_cores_title = "Installed Minecraft kernels"
        search_placeholder = "Search..."
        update_cores_elements = "Update list"
        no_available_installed_cores = "No supported kernels installed"
        install = "Install"
        reinstall = "Reinstall"
        about_core = "About the Core"
        core_type = "Core type:"
        core_version = "Core version:"
        minecraft_version = "Minecraft version:"
        installed = "Installed"
        core_installed = "{type} {version} installed"
        core_deleted = "Core {type} {version} removed"

    class ClientSettings:
        title = "Client Settings"
        error = "Error"
        not_found = "Settings file not found"
        save = "Save"
        success = "Success"
        saved = "Settings saved"
        save_failed = "Failed to save settings"
        tab_video = "Video"
        tab_audio = "Audio"
        tab_control = "Controls"
        tab_language = "Language"
        group_video = "Video Settings"
        group_audio = "Audio Settings"
        group_control = "Control Settings"
        gamma = "Gamma"
        render_distance = "Render Distance"
        fullscreen = "Fullscreen Mode"
        fov = "Field of View (FOV)"
        vsync = "Vertical Synchronization (VSync)"
        sound_master = "Master Volume"
        sound_music = "Music"
        sound_record = "Records"
        sound_weather = "Weather Sounds"
        sound_block = "Block Sounds"
        sound_hostile = "Hostile Mobs"
        sound_neutral = "Neutral Mobs"
        sound_player = "Player"
        sound_ambient = "Ambient Sounds"
        sound_voice = "Voice"
        sensitivity = "Mouse Sensitivity"
        invert_mouse = "Invert Mouse"
        lang_label = "Select Client Language"
        max_fps = "Max FPS"

    class Html:
        about_changes = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SerpentineLauncher - Key Differences</title>
    <style>
        :root {
            --bg-dark: #121212;
            --card-bg: #1e1e1e;
            --primary: #bb86fc;
            --primary-hover: #d0a5ff;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --border: #333;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: var(--bg-dark);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), #03dac5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .tabs-container {
            background: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 2rem;
        }
        
        .tab-header {
            display: flex;
            background: rgba(30, 30, 30, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
        }
        
        .tab-btn {
            flex: 1;
            background: none;
            border: none;
            color: var(--text-secondary);
            padding: 1.2rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        
        .tab-btn:hover {
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .tab-btn.active {
            color: var(--primary);
        }
        
        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--primary);
            border-radius: 3px 3px 0 0;
        }
        
        .tab-content {
            padding: 2.5rem;
            display: none;
            animation: fadeIn 0.4s ease-out;
        }
        
        .tab-content.active {
            display: block;
        }
        
        h3 {
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: var(--primary);
            font-weight: 600;
        }
        
        p {
            margin-bottom: 1.2rem;
            font-size: 1.05rem;
            line-height: 1.8;
        }
        
        code {
            background: rgba(187, 134, 252, 0.15);
            color: var(--primary);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 0.95rem;
        }
        
        .highlight {
            background: rgba(3, 218, 197, 0.1);
            border-left: 3px solid #03dac5;
            padding: 1.5rem;
            border-radius: 0 8px 8px 0;
            margin: 1.5rem 0;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        footer {
            text-align: center;
            color: var(--text-secondary);
            padding-top: 2rem;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .tab-header {
                flex-direction: column;
            }
            
            .tab-content {
                padding: 1.5rem;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>How SerpentineLauncher Stands Out</h1>
        <p class="subtitle">Advanced architecture and unique features compared to traditional launchers</p>
    </header>
    
    <div class="tabs-container">
        <div class="tab-header">
            <button class="tab-btn" data-tab="Storage">Modular Storage</button>
            <button class="tab-btn" data-tab="Behavior">Smart Behavior</button>
            <button class="tab-btn" data-tab="CLI">Powerful CLI</button>
        </div>
        
        <div id="Storage" class="tab-content">
            <h3>Intelligent Storage Architecture</h3>
            <p>Unlike traditional launchers like TLauncher that store cores with assemblies, SerpentineLauncher implements a modular approach:</p>
            
            <div class="highlight">
                <p><strong>Core Version Storage:</strong> Located in <code>./versions</code> directory</p>
                <p><strong>Assembly Storage:</strong> Dedicated <code>./builds</code> folder for configurations</p>
            </div>
            
            <p>This architecture allows you to download a core once and reuse it across multiple compatible assemblies, reducing redundancy and saving disk space.</p>
        </div>
        
        <div id="Behavior" class="tab-content">
            <h3>Optimized Application Behavior</h3>
            <p>SerpentineLauncher implements intelligent instance management:</p>
            
            <ul style="padding-left: 1.5rem; margin: 1.5rem 0;">
                <li>Single-instance architecture prevents multiple launcher windows</li>
                <li>Attempting to open a second instance focuses the existing window</li>
                <li>Supports launching multiple assemblies concurrently from one instance</li>
            </ul>
            
            <p>This design reduces resource consumption while maintaining full functionality for power users.</p>
        </div>
        
        <div id="CLI" class="tab-content">
            <h3>Advanced Command-Line Integration</h3>
            <p>SerpentineLauncher offers full CLI control for automation and advanced workflows:</p>
            
            <div class="highlight">
                <p><strong>Access help documentation:</strong></p>
                <code>SerpentineLauncher.exe --help</code>
                
                <p style="margin-top: 1rem;"><strong>Launch directly without GUI:</strong></p>
                <code>SerpentineLauncher.exe --launch "BuildName" --no-gui</code>
            </div>
            
            <p>The CLI supports all core functionality, enabling scripting and server-side operations.</p>
        </div>
    </div>
    
    <footer>
        <p>SerpentineLauncher &copy; 2025 | Designed for Efficiency</p>
    </footer>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tabBtns = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabBtns[0].classList.add('active');
            tabContents[0].classList.add('active');
            
            tabBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');

                    tabBtns.forEach(b => b.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));

                    this.classList.add('active');
                    document.getElementById(tabId).classList.add('active');
                });
            });
        });
    </script>
</body>
</html>"""

    class Dialogs:
        close_all = "Close all"
        hide_launcher = "Hide launcher"
        cancel = "Cancel"
        confirm_title = "Confirmation"
        confirm_text = "What do you want to do?"
        select_version_title = "Select Version"
        search_versions = "Search versions..."
        minecraft_version = "Minecraft Version:"
        core_type = "Core Type:"
        core_version = "Core Version:"
        minecraft_label = "<b>Minecraft:</b>"
        core_type_label = "<b>Core:</b>"
        core_version_label = "<b>Core Version:</b>"
        error = "Error"
        select_minecraft_version = "Please select a Minecraft version!"
        select_core_type = "Please select a core type!"
        select_core_version = "Please select a core version!"
        minecraft_builds = "Minecraft Builds"
        your_builds = "Your Builds"
        no_builds = "You don't have any builds yet. Create your first one!"
        no_version_selected = "No version selected"
        name_too_short = "The name must be at least 3 characters long"
        build_exists = "A build with this name already exists"
        select_build_first = "Select a build first!"
        build_stopped = "Build '{name}' stopped!"
        build_not_running = "Build '{name}' is not running!"
        build_created = "Build '{name}' created!"
        select_build_to_launch = "Select a build to launch first!"
        build_not_exists = "The selected build no longer exists!"
        core_install_canceled = "Core installation was canceled!"
        username_not_specified = "Username is not specified!"
        build_name_not_specified = "Build name not specified!"
        build_not_found = "Build not found!"
        unsupported_core_type = "Unsupported core type!"
        launching_build = "Launching Minecraft {minecraft} with {core_type}..."
        build_already_running = "Build '{name}' is already running!"
        confirm_deletion = "Confirm Deletion"
        confirm_delete_build = "Are you sure you want to delete the build '{name}'?"
        build_updated = "Build '{name}' updated!"
        build_update_failed = "Failed to update the build!"
        build_deleted = "Build '{name}' deleted!"
        fabric_tooltip = "Build uses the 'Fabric' core"
        forge_tooltip = "Build uses the 'Forge' core"
        quilt_tooltip = "Build uses the 'Quilt' core"
        vanilla_tooltip = "Build does not use additional cores"
        unknown_tooltip = "Build uses an unsupported core"
        install_core_title = "Installing Core"
        start_installation = "Starting installation..."
        installation_success = "Installation completed successfully!"
        installation_error = "Installation error: {error_msg}"
        cancel_installation = "Canceling installation..."
        ok = "Ok"
        yes = "Yes"
        no = "No"
        close = "Close"
        profiles_title = "Minecraft Profiles"
        nickname_label = "Nickname:"
        token_label = "Token (do not change if unsure):"
        uuid_label = "UUID (do not change if unsure):"
        your_profiles = "Your Profiles"
        create_profile = "Create Profile"
        toggle_tech_params = "Technical Parameters ▼"
        toggle_tech_params_expanded = "Technical Parameters ▲"
        select_profile = "Set Selected Profile"
        delete = "Delete"
        nickname_placeholder = "Enter nickname (3-16 characters)"
        char_counter = "0/16"
        no_profiles = "You have no profiles yet. Create your first one!"
        nickname_length_warning = "Nickname must be 3-16 characters long"
        nickname_chars_warning = "Only letters, numbers, and underscores"
        nickname_exists_warning = "This nickname is already in use"
        confirm_deletion_title = "Confirm Deletion"
        confirm_deletion_text = "Are you sure you want to delete the profile '{nickname}'?"
        profile_created = "Profile '{nickname}' created!"
        profile_deleted = "Profile '{nickname}' deleted"
        select_profile_first = "Select a profile from the list first"
        offline_status = "Offline"
        active_status = "Offline ⭐ Active"
        general_tab = "General"
        game_settings_tab = "Game Settings"
        advanced_tab = "Advanced"
        about_tab = "About"
        restart_required = "Application restart required"
        language_label = "Language"
        use_anim_transitions = "Use transition animations (experimental)"
        select_java_path = "Select path to Java executable"
        show_console = "Show the console (you may need to restart the game)"
        panel_behavior_group = "Panel Behavior"
        panel_position_on_top = "On top of others"
        panel_position_shift = "Shift"
        panel_state_standard = "Standard"
        panel_state_always_expanded = "Always expanded"
        panel_state_always_collapsed = "Always collapsed"
        launcher_behavior_group = "Launcher behavior on startup"
        launcher_hide_completely = "Hide completely"
        launcher_minimize_to_taskbar = "Minimize to taskbar"
        launcher_do_nothing = "Do nothing"
        set_java_memory = "Set memory for Java"
        memory_suffix = " Mb"
        about_title = "Minecraft Launcher"
        about_version = "v2.0-beta"
        about_author = "Tandreyt6"
        about_description = "Compact launcher for Minecraft with convenient profile and Java settings management."
        about_new_in_version = "What's new in v2.0"
        about_new_features = "Memory optimization, animations, game version selection, and window management."
        about_copyright = "© 2025 Tandreyt6"
        select = "Select"
        select_build = "Select build:"
        all_loaders = "All loaders"
        filter_by_loader = "Filter by loader:"
        enter_mod_name = "Enter mod name..."
        add_to_queue = "Add to queue"
        search_mods = "Search mods"
        download_queue = "Download queue:"
        move_up = "Up"
        move_down = "Down"
        remove = "Remove"
        install_all = "Install all"
        download_queue_tab = "Download queue"
        installed_mods = "Installed mods:"
        build_structure = "Build structure:"
        file_folder = "File/Folder"
        path = "Path"
        build_management = "Build management"
        queue_empty_title = "Queue is empty"
        queue_empty_message = "Add mods to the queue before installing."
        no_compatible_versions = "no compatible versions"
        completed_with_errors = "Completed with errors"
        success = "Success"
        all_mods_installed_successfully = "All mods installed successfully."
        loading = "Loading..."
        no_mods_found = "No mods found"
        search_error = "Search error"
        not_supported = "not supported"
        mod_not_supported = "Mod does not support"
        loading_mod_info = "Loading mod information..."
        failed_to_get_mod_data = "Failed to get mod data"
        mod_data_processing_error = "Mod data processing error"
        name = "Name"
        authors = "Authors"
        description = "Description"
        game_versions = "Game versions"
        categories = "Categories"
        project_type = "Project type"
        downloads = "Downloads"
        select_build_and_mod = "Select build and mod to add!"
        information = "Information"
        mod_already_in_queue = "This mod is already in the queue."
        added = "Added"
        mod_added_to_queue = "{title} added to queue."
        done = "Done"
        all_mods_downloaded = "All mods downloaded."
        confirmation = "Confirmation"
        mod_exists = "Mod {filename} already exists. Overwrite?"
        download_failed = "Failed to download mod: HTTP {status}"
        confirm_remove = "Remove mod {mod}?"
        mod_removed = "Mod removed!"
        remove_error = "Remove error: {error}"
        no_build_selected = "No build selected"
        mods_dir_not_found = "Mods directory not found"
        no_mods_installed = "No mods installed"
        mod_load_error = "Mod load error: {mod}"
        toggle_mod_error = "Failed to toggle mod: {error}"
        delete_mod_error = "Failed to delete mod: {error}"
        build = "Build"
        untitled = "Untitled"
        mod_installed = "Mod {title} installed!"
        unknown = "Unknown"
        loader = "loader"
        double_click_behavior_group = "Double-click behavior on build"
        double_click_launch = "Launch"
        double_click_info = "Open info"
        double_click_settings = "Open settings"
        about_changes_question = "Would you like to learn about the differences between the launcher and others (for example, TLauncher)?"
        no_java_selected = "Java is not selected! go to Settings -> Advanced!"
        impossible = "Impossible"
        error_debug_hide_console = "It is impossible to hide the console in debugging mode!"
        delete_title = "Delete"
        delete_core = "Are you sure you want to delete the core?"
        reinstall_core = "Are you sure you want to reinstall the kernel?\This will delete the existing kernel and reload it."
        error_delete_core = "Deletion error {type} {version} before reinstallation"

lang: RU | EN = None