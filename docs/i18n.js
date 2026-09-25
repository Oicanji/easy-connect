(function () {
  var HTML_LANG = {
    pt: "pt-BR",
    en: "en",
    es: "es",
    de: "de",
    zh: "zh-CN",
  };

  var TEXT = {
    pt: {
      "lang.label": "Idioma",
      lead: "<b>Automação de acesso às suas VMs com segurança!</b> Um comando simples e você ou seu LLM já se conecta ao seu servidor, sem expor senhas ou credenciais para ninguém.",
      installer: "Instalador",
      package: "Pacote",
      source: "Código fonte",
      requirements: "Requisitos",
      "win.req1": "Windows 10 (1809 ou superior) ou Windows 11, 64 bits",
      "win.req2": "Cliente OpenSSH do Windows",
      "win.req3": "Para o instalador: permissão de administrador na primeira instalação",
      "linux.req1": "Python 3.11 ou superior",
      "linux.req2": "Cliente OpenSSH (<code>openssh-client</code>)",
      "linux.req3": "Ambiente gráfico para a interface (Qt/PySide6)",
      unavailable: "Indisponível",
      "mac.req1": "Pacote ainda não disponível para macOS",
      "agents.title": "Agentes LLM (opcional)",
      "agents.label": "Agentes suportados",
      "agents.note": "Necessário utilização de CLI do respectivo agente baixado via irm/npm.",
      "agents.optional": "Totalmente opcional, você pode apenas pedir para o LLM ou ferramenta executar o comando EX:<code>ssh-10-142-0-31</code> diretamente.",
      "changelog.title": "Changelog",
      "changelog.label": "Versão do changelog",
      "cl.110.1": "Cada conexão pode ser ligada ou desligada. Um comando desligado abre o Easy Connect e pede para habilitar.",
      "cl.110.2": "Duplicar ficou junto de editar e excluir.",
      "cl.110.3": "Regras por conexão: permitir sempre, pedir permissão ou nunca executar, para leitura, escrita, exclusão, banco de dados e credenciais. O card mostra a permissão mais restrita.",
      "cl.110.4": "Cada conexão pode ter um ícone escolhido numa lista com busca.",
      "cl.110.5": "Descrição opcional da conexão, incluída na exportação de regras para LLM.",
      "cl.110.6": "Interface em português, inglês, espanhol, alemão e chinês.",
      "cl.102.1": "Corrigido o encoding do instalador Windows (acentos e Ç).",
      "cl.102.2": "Removido o popup desnecessário após a primeira configuração do cofre/comando.",
      "cl.102.3": "Página de download com ícones dos agentes, nota de CLI e footer atualizado.",
      "cl.101.1": "Primeira versão pública estável.",
      "cl.101.2": "Menu de agentes em cascata, com ações extras de logs Docker e prompt personalizado.",
      "cl.101.3": "Janela de conversa para o prompt customizado, com ícones dos agentes, anexos e envio por Enter.",
      "cl.101.4": "Exportação de instrução LLM sem expor caminhos de chave privada ou pública.",
      "cl.101.5": "Botão de adicionar arquivo de exportação ao lado do seletor de modelo.",
      "cl.101.6": "Script de release para bump de versão e compilação de instalador e pacote portátil.",
      "cl.005.1": "Os agentes Cursor, Antigravity, Codex e Claude executam o CLI com a tarefa já no prompt, sem abrir o editor nem pedir para colar o texto.",
      "cl.005.2": "Se o CLI não estiver instalado, o terminal instala e dispara a tarefa.",
      "cl.005.3": "Em Configurações, cada agente tem um seletor de pasta de instalação.",
      "cl.005.4": "O prompt vai em uma linha só e manda o agente começar na hora.",
      "cl.005.5": "A página lista os requisitos por sistema operacional.",
      "cl.005.6": "Cards de conexão, menu de agentes em dois passos e cópia do comando foram ajustados.",
      "cl.004.1": "A sessão do cofre permanece válida até o computador reiniciar.",
      "cl.004.2": "Integrações iniciais com Claude Code, Cursor, Antigravity e Codex.",
      "cl.004.3": "Botão para abrir um terminal já conectado e cópia dos comandos.",
      "cl.004.4": "Página de download no GitHub Pages, com pacotes para Windows e Linux.",
      "cl.004.5": "Licença CC0 1.0.",
      "cl.004.6": "Instalador Windows, pacote portátil e correção do crash ao abrir a lista de conexões.",
      footer: 'Aplicativo de uso livre, licenciado em <a href="https://github.com/Oicanji/easy-connect/blob/main/LICENSE">CC0 1.0</a>. Reprodução e distribuição são permitidas, com os devidos créditos a Ignacio Sepúlveda. Histórico completo em <a href="https://github.com/Oicanji/easy-connect/blob/main/CHANGELOG.md">CHANGELOG.md</a>.',
    },
    en: {
      "lang.label": "Language",
      lead: "<b>Secure automation for access to your VMs!</b> One simple command and you or your LLM are already connected to your server, without exposing passwords or credentials to anyone.",
      installer: "Installer",
      package: "Package",
      source: "Source code",
      requirements: "Requirements",
      "win.req1": "Windows 10 (1809 or later) or Windows 11, 64-bit",
      "win.req2": "Windows OpenSSH client",
      "win.req3": "For the installer: administrator permission on the first install",
      "linux.req1": "Python 3.11 or later",
      "linux.req2": "OpenSSH client (<code>openssh-client</code>)",
      "linux.req3": "A graphical environment for the interface (Qt/PySide6)",
      unavailable: "Unavailable",
      "mac.req1": "Package not available for macOS yet",
      "agents.title": "LLM agents (optional)",
      "agents.label": "Supported agents",
      "agents.note": "The CLI of the matching agent is required, installed via irm/npm.",
      "agents.optional": "Fully optional. You can just ask the LLM or tool to run the command, for example <code>ssh-10-142-0-31</code>, directly.",
      "changelog.title": "Changelog",
      "changelog.label": "Changelog version",
      "cl.110.1": "Each connection can be turned on or off. A disabled command opens Easy Connect and asks to enable it.",
      "cl.110.2": "Duplicate now sits with edit and delete.",
      "cl.110.3": "Per-connection rules: always allow, ask, or never run, for read, write, delete, database, and credential commands. The card shows the strictest permission.",
      "cl.110.4": "Each connection can have an icon chosen from a searchable list.",
      "cl.110.5": "Optional connection description, included in the LLM rules export.",
      "cl.110.6": "Interface in Portuguese, English, Spanish, German, and Chinese.",
      "cl.102.1": "Fixed Windows installer encoding (accents and Ç).",
      "cl.102.2": "Removed the unnecessary popup after the first vault/command setup.",
      "cl.102.3": "Download page with agent icons, CLI note, and updated footer.",
      "cl.101.1": "First stable public release.",
      "cl.101.2": "Cascading agents menu, with extra Docker log actions and a custom prompt.",
      "cl.101.3": "Conversation window for the custom prompt, with agent icons, attachments, and send on Enter.",
      "cl.101.4": "LLM instruction export without exposing private or public key paths.",
      "cl.101.5": "Button to add an export file next to the model selector.",
      "cl.101.6": "Release script for version bump and building the installer and portable package.",
      "cl.005.1": "Cursor, Antigravity, Codex, and Claude agents run the CLI with the task already in the prompt, without opening the editor or asking to paste the text.",
      "cl.005.2": "If the CLI is not installed, the terminal installs it and starts the task.",
      "cl.005.3": "In Settings, each agent has an install-folder picker.",
      "cl.005.4": "The prompt is a single line and tells the agent to start immediately.",
      "cl.005.5": "The page lists requirements per operating system.",
      "cl.005.6": "Connection cards, the two-step agents menu, and command copy were adjusted.",
      "cl.004.1": "The vault session stays valid until the computer restarts.",
      "cl.004.2": "Initial integrations with Claude Code, Cursor, Antigravity, and Codex.",
      "cl.004.3": "Button to open an already connected terminal and copy the commands.",
      "cl.004.4": "Download page on GitHub Pages, with packages for Windows and Linux.",
      "cl.004.5": "CC0 1.0 license.",
      "cl.004.6": "Windows installer, portable package, and a fix for the crash when opening the connection list.",
      footer: 'Free application, licensed under <a href="https://github.com/Oicanji/easy-connect/blob/main/LICENSE">CC0 1.0</a>. Reproduction and distribution are allowed, with credit to Ignacio Sepúlveda. Full history in <a href="https://github.com/Oicanji/easy-connect/blob/main/CHANGELOG.md">CHANGELOG.md</a>.',
    },
    es: {
      "lang.label": "Idioma",
      lead: "<b>¡Automatiza el acceso a tus VM con seguridad!</b> Un comando simple y tú o tu LLM ya se conectan a tu servidor, sin exponer contraseñas ni credenciales a nadie.",
      installer: "Instalador",
      package: "Paquete",
      source: "Código fuente",
      requirements: "Requisitos",
      "win.req1": "Windows 10 (1809 o superior) o Windows 11, 64 bits",
      "win.req2": "Cliente OpenSSH de Windows",
      "win.req3": "Para el instalador: permiso de administrador en la primera instalación",
      "linux.req1": "Python 3.11 o superior",
      "linux.req2": "Cliente OpenSSH (<code>openssh-client</code>)",
      "linux.req3": "Entorno gráfico para la interfaz (Qt/PySide6)",
      unavailable: "No disponible",
      "mac.req1": "Paquete aún no disponible para macOS",
      "agents.title": "Agentes LLM (opcional)",
      "agents.label": "Agentes compatibles",
      "agents.note": "Hace falta el CLI del agente correspondiente, descargado con irm/npm.",
      "agents.optional": "Totalmente opcional. Puedes pedir al LLM o a la herramienta que ejecute el comando, por ejemplo <code>ssh-10-142-0-31</code>, directamente.",
      "changelog.title": "Changelog",
      "changelog.label": "Versión del changelog",
      "cl.110.1": "Cada conexión se puede activar o desactivar. Un comando desactivado abre Easy Connect y pide habilitarla.",
      "cl.110.2": "Duplicar quedó junto a editar y eliminar.",
      "cl.110.3": "Reglas por conexión: permitir siempre, pedir permiso o no ejecutar nunca, para lectura, escritura, eliminación, base de datos y credenciales. La tarjeta muestra el permiso más estricto.",
      "cl.110.4": "Cada conexión puede tener un icono elegido en una lista con búsqueda.",
      "cl.110.5": "Descripción opcional de la conexión, incluida en la exportación de reglas para el LLM.",
      "cl.110.6": "Interfaz en portugués, inglés, español, alemán y chino.",
      "cl.102.1": "Corregida la codificación del instalador de Windows (acentos y Ç).",
      "cl.102.2": "Eliminado el aviso innecesario tras la primera configuración de la caja fuerte/comando.",
      "cl.102.3": "Página de descarga con iconos de los agentes, nota de CLI y pie actualizado.",
      "cl.101.1": "Primera versión pública estable.",
      "cl.101.2": "Menú de agentes en cascada, con acciones extra de logs de Docker y prompt personalizado.",
      "cl.101.3": "Ventana de conversación para el prompt personalizado, con iconos de los agentes, adjuntos y envío con Enter.",
      "cl.101.4": "Exportación de la instrucción LLM sin exponer rutas de clave privada o pública.",
      "cl.101.5": "Botón para agregar un archivo de exportación junto al selector de modelo.",
      "cl.101.6": "Script de release para subir la versión y compilar el instalador y el paquete portátil.",
      "cl.005.1": "Los agentes Cursor, Antigravity, Codex y Claude ejecutan el CLI con la tarea ya en el prompt, sin abrir el editor ni pedir pegar el texto.",
      "cl.005.2": "Si el CLI no está instalado, la terminal lo instala y lanza la tarea.",
      "cl.005.3": "En Configuración, cada agente tiene un selector de carpeta de instalación.",
      "cl.005.4": "El prompt va en una sola línea y le pide al agente empezar de inmediato.",
      "cl.005.5": "La página lista los requisitos por sistema operativo.",
      "cl.005.6": "Se ajustaron las tarjetas de conexión, el menú de agentes en dos pasos y la copia del comando.",
      "cl.004.1": "La sesión de la caja fuerte sigue válida hasta que el equipo se reinicia.",
      "cl.004.2": "Integraciones iniciales con Claude Code, Cursor, Antigravity y Codex.",
      "cl.004.3": "Botón para abrir una terminal ya conectada y copiar los comandos.",
      "cl.004.4": "Página de descarga en GitHub Pages, con paquetes para Windows y Linux.",
      "cl.004.5": "Licencia CC0 1.0.",
      "cl.004.6": "Instalador de Windows, paquete portátil y corrección del fallo al abrir la lista de conexiones.",
      footer: 'Aplicación de uso libre, con licencia <a href="https://github.com/Oicanji/easy-connect/blob/main/LICENSE">CC0 1.0</a>. Se permite la reproducción y la distribución, con el crédito correspondiente a Ignacio Sepúlveda. Historial completo en <a href="https://github.com/Oicanji/easy-connect/blob/main/CHANGELOG.md">CHANGELOG.md</a>.',
    },
    de: {
      "lang.label": "Sprache",
      lead: "<b>Sicherer, automatisierter Zugriff auf Ihre VMs!</b> Ein einfacher Befehl, und Sie oder Ihr LLM sind bereits mit dem Server verbunden, ohne Passwörter oder Zugangsdaten preiszugeben.",
      installer: "Installationsprogramm",
      package: "Paket",
      source: "Quellcode",
      requirements: "Voraussetzungen",
      "win.req1": "Windows 10 (1809 oder neuer) oder Windows 11, 64-Bit",
      "win.req2": "Windows-OpenSSH-Client",
      "win.req3": "Für das Installationsprogramm: Administratorrecht bei der ersten Installation",
      "linux.req1": "Python 3.11 oder neuer",
      "linux.req2": "OpenSSH-Client (<code>openssh-client</code>)",
      "linux.req3": "Grafische Umgebung für die Oberfläche (Qt/PySide6)",
      unavailable: "Nicht verfügbar",
      "mac.req1": "Paket für macOS noch nicht verfügbar",
      "agents.title": "LLM-Agenten (optional)",
      "agents.label": "Unterstützte Agenten",
      "agents.note": "Die CLI des jeweiligen Agenten wird benötigt, installiert über irm/npm.",
      "agents.optional": "Völlig optional. Sie können das LLM oder das Werkzeug einfach bitten, den Befehl direkt auszuführen, zum Beispiel <code>ssh-10-142-0-31</code>.",
      "changelog.title": "Changelog",
      "changelog.label": "Changelog-Version",
      "cl.110.1": "Jede Verbindung lässt sich ein- oder ausschalten. Ein deaktivierter Befehl öffnet Easy Connect und fragt, ob sie aktiviert werden soll.",
      "cl.110.2": "Duplizieren steht jetzt bei Bearbeiten und Löschen.",
      "cl.110.3": "Regeln je Verbindung: immer erlauben, nachfragen oder nie ausführen, für Lesen, Schreiben, Löschen, Datenbank und Zugangsdaten. Die Karte zeigt die strengste Berechtigung.",
      "cl.110.4": "Jede Verbindung kann ein Symbol aus einer durchsuchbaren Liste erhalten.",
      "cl.110.5": "Optionale Beschreibung der Verbindung, enthalten im LLM-Regelexport.",
      "cl.110.6": "Oberfläche auf Portugiesisch, Englisch, Spanisch, Deutsch und Chinesisch.",
      "cl.102.1": "Kodierung des Windows-Installationsprogramms korrigiert (Akzente und Ç).",
      "cl.102.2": "Unnötiges Popup nach der ersten Tresor-/Befehls-Einrichtung entfernt.",
      "cl.102.3": "Download-Seite mit Agenten-Symbolen, CLI-Hinweis und aktualisierter Fußzeile.",
      "cl.101.1": "Erste stabile öffentliche Version.",
      "cl.101.2": "Kaskadierendes Agentenmenü, mit zusätzlichen Docker-Log-Aktionen und eigenem Prompt.",
      "cl.101.3": "Gesprächsfenster für den eigenen Prompt, mit Agenten-Symbolen, Anhängen und Senden mit Enter.",
      "cl.101.4": "Export der LLM-Anweisung, ohne Pfade privater oder öffentlicher Schlüssel offenzulegen.",
      "cl.101.5": "Schaltfläche zum Hinzufügen einer Exportdatei neben der Modellauswahl.",
      "cl.101.6": "Release-Skript für Versionserhöhung sowie Bau von Installationsprogramm und portablem Paket.",
      "cl.005.1": "Die Agenten Cursor, Antigravity, Codex und Claude führen die CLI mit der Aufgabe bereits im Prompt aus, ohne den Editor zu öffnen oder um Einfügen des Textes zu bitten.",
      "cl.005.2": "Wenn die CLI nicht installiert ist, installiert das Terminal sie und startet die Aufgabe.",
      "cl.005.3": "In den Einstellungen hat jeder Agent eine Auswahl des Installationsordners.",
      "cl.005.4": "Der Prompt steht in einer Zeile und weist den Agenten an, sofort zu beginnen.",
      "cl.005.5": "Die Seite listet die Voraussetzungen je Betriebssystem.",
      "cl.005.6": "Verbindungskarten, das zweistufige Agentenmenü und das Kopieren des Befehls wurden angepasst.",
      "cl.004.1": "Die Tresorsitzung bleibt gültig, bis der Computer neu startet.",
      "cl.004.2": "Erste Integrationen mit Claude Code, Cursor, Antigravity und Codex.",
      "cl.004.3": "Schaltfläche, um ein bereits verbundenes Terminal zu öffnen und die Befehle zu kopieren.",
      "cl.004.4": "Download-Seite auf GitHub Pages, mit Paketen für Windows und Linux.",
      "cl.004.5": "Lizenz CC0 1.0.",
      "cl.004.6": "Windows-Installationsprogramm, portables Paket und Behebung des Absturzes beim Öffnen der Verbindungsliste.",
      footer: 'Frei nutzbare Anwendung, lizenziert unter <a href="https://github.com/Oicanji/easy-connect/blob/main/LICENSE">CC0 1.0</a>. Vervielfältigung und Verbreitung sind erlaubt, mit Namensnennung von Ignacio Sepúlveda. Vollständiger Verlauf in <a href="https://github.com/Oicanji/easy-connect/blob/main/CHANGELOG.md">CHANGELOG.md</a>.',
    },
    zh: {
      "lang.label": "语言",
      lead: "<b>安全地自动访问你的虚拟机！</b>一条简单命令，你或你的 LLM 就能连上服务器，而不会向任何人暴露密码或凭据。",
      installer: "安装程序",
      package: "压缩包",
      source: "源代码",
      requirements: "要求",
      "win.req1": "Windows 10（1809 或更高）或 Windows 11，64 位",
      "win.req2": "Windows OpenSSH 客户端",
      "win.req3": "安装程序：首次安装需要管理员权限",
      "linux.req1": "Python 3.11 或更高版本",
      "linux.req2": "OpenSSH 客户端（<code>openssh-client</code>）",
      "linux.req3": "用于界面的图形环境（Qt/PySide6）",
      unavailable: "暂不可用",
      "mac.req1": "尚无适用于 macOS 的安装包",
      "agents.title": "LLM 代理（可选）",
      "agents.label": "支持的代理",
      "agents.note": "需要通过 irm/npm 安装对应代理的 CLI。",
      "agents.optional": "完全可选。你也可以直接让 LLM 或工具运行命令，例如 <code>ssh-10-142-0-31</code>。",
      "changelog.title": "更新日志",
      "changelog.label": "更新日志版本",
      "cl.110.1": "每个连接都可以启用或停用。停用的命令会打开 Easy Connect 并询问是否启用。",
      "cl.110.2": "“复制”现在和“编辑”“删除”放在一起。",
      "cl.110.3": "按连接设置规则：始终允许、弹窗询问或禁止执行，覆盖读取、写入、删除、数据库和凭据命令。卡片会显示最严格的权限。",
      "cl.110.4": "每个连接都可以从可搜索列表中选择一个图标。",
      "cl.110.5": "可选的连接描述，会写入导出给 LLM 的规则。",
      "cl.110.6": "界面支持葡萄牙语、英语、西班牙语、德语和中文。",
      "cl.102.1": "修复了 Windows 安装程序的编码（重音符号和 Ç）。",
      "cl.102.2": "去掉了首次配置保险库/命令后不必要的弹窗。",
      "cl.102.3": "下载页增加了代理图标、CLI 说明，并更新了页脚。",
      "cl.101.1": "第一个稳定的公开版本。",
      "cl.101.2": "级联代理菜单，增加 Docker 日志操作和自定义提示。",
      "cl.101.3": "自定义提示的对话窗口，带有代理图标、附件，以及按 Enter 发送。",
      "cl.101.4": "导出 LLM 指令时不再暴露私钥或公钥路径。",
      "cl.101.5": "在模型选择器旁增加了添加导出文件的按钮。",
      "cl.101.6": "用于升级版本并编译安装程序和便携包的发布脚本。",
      "cl.005.1": "Cursor、Antigravity、Codex 和 Claude 代理会带着任务直接运行 CLI，不再打开编辑器，也不要求粘贴文本。",
      "cl.005.2": "如果尚未安装 CLI，终端会安装并启动任务。",
      "cl.005.3": "在设置中，每个代理都可以选择安装文件夹。",
      "cl.005.4": "提示词只有一行，并要求代理立即开始。",
      "cl.005.5": "页面按操作系统列出要求。",
      "cl.005.6": "调整了连接卡片、两步代理菜单和命令复制。",
      "cl.004.1": "保险库会话在计算机重启前保持有效。",
      "cl.004.2": "初步集成 Claude Code、Cursor、Antigravity 和 Codex。",
      "cl.004.3": "用于打开已连接终端并复制命令的按钮。",
      "cl.004.4": "GitHub Pages 上的下载页，提供 Windows 和 Linux 安装包。",
      "cl.004.5": "CC0 1.0 许可证。",
      "cl.004.6": "Windows 安装程序、便携包，以及打开连接列表时崩溃的修复。",
      footer: '本应用可自由使用，采用 <a href="https://github.com/Oicanji/easy-connect/blob/main/LICENSE">CC0 1.0</a> 许可。允许复制和分发，并应注明 Ignacio Sepúlveda。完整历史见 <a href="https://github.com/Oicanji/easy-connect/blob/main/CHANGELOG.md">CHANGELOG.md</a>。',
    },
  };

  function normalize(code) {
    var text = String(code || "").toLowerCase().split("-")[0];
    return TEXT[text] ? text : "pt";
  }

  function apply(lang) {
    var catalog = TEXT[lang] || TEXT.pt;
    document.documentElement.lang = HTML_LANG[lang] || "pt-BR";
    var nodes = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < nodes.length; i += 1) {
      var node = nodes[i];
      var key = node.getAttribute("data-i18n");
      var value = catalog[key] || TEXT.pt[key] || "";
      var attr = node.getAttribute("data-i18n-attr");
      if (attr) {
        node.setAttribute(attr, value);
      } else if (node.hasAttribute("data-i18n-html")) {
        node.innerHTML = value;
      } else {
        node.textContent = value;
      }
    }
  }

  var language = document.getElementById("site-language");
  var stored = "";
  try {
    stored = localStorage.getItem("easy-connect-lang") || "";
  } catch (error) {
    stored = "";
  }
  var current = normalize(stored || (navigator.language || "pt"));
  if (language) {
    language.value = current;
    language.addEventListener("change", function () {
      current = normalize(language.value);
      try {
        localStorage.setItem("easy-connect-lang", current);
      } catch (error) {
        current = normalize(language.value);
      }
      apply(current);
    });
  }
  apply(current);

  var changelog = document.getElementById("changelog-version");
  if (changelog) {
    changelog.addEventListener("change", function () {
      var panels = document.querySelectorAll(".changelog-notes");
      for (var i = 0; i < panels.length; i += 1) {
        panels[i].hidden = panels[i].id !== changelog.value;
      }
    });
  }
})();
