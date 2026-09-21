# Changelog

Todas as versões publicadas do Easy Connect.

## 1.0.2 - 2026-09-21

- Corrigido o encoding do instalador Windows (acentos e Ç).
- Removido o popup desnecessário após a primeira configuração do cofre/comando.
- Página de download com ícones dos agentes, nota de CLI e footer atualizado.

## 1.0.1 - 2026-09-21

- Primeira versão pública estável.
- Menu de agentes em cascata, com ações extras de logs Docker e prompt personalizado.
- Janela de conversa para o prompt customizado, com ícones dos agentes, anexos e envio por Enter.
- Exportação de instrução LLM sem expor caminhos de chave privada ou pública.
- Botão de adicionar arquivo de exportação ao lado do seletor de modelo.
- Script `packaging/release.ps1` para bump de versão e compilação de instalador e pacote portátil.

## 0.0.5 - 2026-09-21

- Os agentes Cursor, Antigravity, Codex e Claude passam a executar o CLI com a tarefa já no prompt, sem abrir o editor nem pedir para colar o texto.
- Se o CLI do agente não estiver instalado, o terminal instala e em seguida dispara a tarefa.
- Em Configurações, cada agente tem um seletor de pasta de instalação.
- O prompt vai em uma linha só e manda o agente começar na hora, sem perguntar o objetivo.
- A página de download lista os requisitos por sistema operacional.
- Cards de conexão, menu de agentes em dois passos e cópia do comando foram ajustados.

## 0.0.4 - 2026-09-21

- A sessão do cofre permanece válida até o computador reiniciar.
- Integrações iniciais com Claude Code, Cursor, Antigravity e Codex.
- Botão para abrir um terminal já conectado e cópia dos comandos.
- Página de download no GitHub Pages, com pacotes para Windows e Linux.
- Licença CC0 1.0.
- Instalador Windows, pacote portátil e correção do crash ao abrir a lista de conexões.
