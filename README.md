# 🎬 PPL Player

**Professional Video Player with Advanced Features**

> Um reprodutor de vídeo moderno e profissional, desenvolvido em Python com PySide6, focado em performance e produtividade para análise de conteúdo audiovisual.

## 📋 Índice

- [✨ Features](#-features)
- [🎯 Características Técnicas](#-características-técnicas)
- [🚀 Tecnologias](#-tecnologias)
- [⚙️ Instalação](#️-instalação)
- [🎮 Uso](#-uso)
- [🔧 Configuração](#-configuração)
- [📡 Sistema de Atualização](#-sistema-de-atualização)
- [🎨 Interface](#-interface)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔄 Sistema de Build](#-sistema-de-build)
- [📞 Suporte](#-suporte)

## ✨ Features

### 🎥 **Reprodução de Vídeo**
- **Formatos Suportados**: `.mp4`, `.avi`, `.mkv`, `.dav`, `.dav_`
- **Engine VLC**: Performance otimizada com configurações customizadas
- **Alta Velocidade**: Reprodução até 32x sem perda de qualidade
- **Navegação Frame-by-Frame**: Controle preciso quadro a quadro
- **Auto-Pause Inteligente**: Pausas automáticas em vídeos longos (25%, 50%, 75%)

### 🎮 **Controles Avançados**
- **Atalhos Customizáveis**: Sistema completo de keybinds configuráveis
- **Velocidades Múltiplas**: 1x, 2x, 4x, 6x, 8x, 10x, 12x, 16x, 32x
- **Volume Inteligente**: Controle com steps configuráveis
- **Navegação Temporal**: Avanço/retrocesso em segundos precisos
- **Tela Cheia**: Modo fullscreen otimizado

### 🔍 **Sistema de Zoom**
- **Zoom Digital**: Ampliação de 10x até 40x
- **Área Selecionável**: Escolha da região de interesse
- **Controles Visuais**: Interface intuitiva com sliders
- **Posicionamento Livre**: Movimentação da área de zoom

### 📝 **Modal de Croqui**
- **Visualização de Imagens**: Suporte a PNG, JPG, JPEG, BMP, GIF, TIFF, WebP
- **Interface Adaptativa**: Redimensionamento automático por DPI
- **Integração CLI**: Abertura via linha de comando
- **Tema Escuro**: Interface consistente

### 📋 **Sistema de Playlist**
- **Gerenciamento Visual**: Interface drag-and-drop
- **Navegação Rápida**: Salto entre vídeos
- **Indicador Visual**: Destaque do vídeo atual
- **Organização**: Listagem estruturada

### ⚙️ **Configurações Avançadas**
- **Temas Personalizáveis**: Cores e estilos configuráveis
- **Keybinds Customizáveis**: Remapeamento completo de teclas
- **Performance Tuning**: Configurações de cache e threading
- **Persistência**: Salvamento automático de preferências

## 🎯 Características Técnicas

### 🏗️ **Arquitetura**
- **Thread-Safe**: Operações multi-thread seguras
- **Event-Driven**: Sistema baseado em sinais Qt
- **Modular**: Componentes independentes e reutilizáveis
- **Extensível**: Arquitetura plugin-ready

### 🚀 **Performance**
- **VLC Engine**: Backend otimizado para reprodução
- **Hardware Acceleration**: Suporte a decodificação por hardware
- **Cache Inteligente**: Sistema de buffer otimizado
- **Memory Management**: Gerenciamento eficiente de recursos

### 🔒 **Confiabilidade**
- **Error Handling**: Tratamento robusto de exceções
- **Safe Shutdown**: Fechamento limpo com cleanup de recursos
- **Thread Cleanup**: Finalização segura de threads daemon
- **Resource Management**: Liberação automática de recursos VLC

## 🚀 Tecnologias

### **Frontend**
- **PySide6**: Framework Qt6 para Python - Interface gráfica moderna
- **Qt Widgets**: Componentes nativos de alta performance
- **Qt Signals/Slots**: Sistema de comunicação thread-safe

### **Backend**
- **Python 3.9+**: Linguagem principal
- **VLC Python**: Binding para libVLC media player
- **Threading**: Processamento paralelo e assíncrono
- **AsyncIO**: Operações de rede não-bloqueantes

### **Sistema de Atualização**
- **Flask API**: Servidor de atualizações
- **HTTP Requests**: Download de updates
- **Subprocess**: Gerenciamento de processos
- **ZIP Compression**: Empacotamento de atualizações

### **Build & Deploy**
- **PyInstaller**: Compilação para executável
- **Inno Setup**: Instalador Windows profissional
- **GitHub Actions**: CI/CD automatizado (configurável)

### **Utilitários**
- **JSON**: Configurações e metadados
- **OS Path**: Manipulação de arquivos multiplataforma
- **ArgParse**: Interface de linha de comando
- **Signal Handling**: Captura de sinais do sistema

## ⚙️ Instalação

### **Pré-requisitos**
```bash
Python 3.9+
VLC Media Player (libVLC)
```

### **Instalação via Source**
```bash
# Clone o repositório
git clone https://github.com/Haxsc/PERPLAN-MEDIA-PLAYER.git
cd PERPLAN-MEDIA-PLAYER

# Instale dependências
pip install -r requirements.txt

# Execute o player
python main.py
```

### **Instalação via Executável**
1. Baixe o instalador `PPL Player Setup.exe`
2. Execute o instalador
3. Siga o assistente de instalação
4. Execute via atalho na área de trabalho

## 🎮 Uso

### **Linha de Comando**
```bash
# Reproduzir vídeo específico
python main.py --video "caminho/para/video.mp4"

# Abrir com croqui
python main.py --croqui "caminho/para/imagem.png" --video "video.mp4"

# Apenas croqui
python main.py --croqui "esquema.jpg"
```

### **Atalhos de Teclado Padrão**
| Função | Tecla |
|--------|-------|
| Play/Pause | `Space` |
| Frame Anterior | `Q` |
| Próximo Frame | `E` |
| Retroceder 1s | `←` |
| Avançar 1s | `→` |
| Volume - | `↓` |
| Volume + | `↑` |
| Tela Cheia | `F` |
| Velocidade - | `-` |
| Velocidade + | `+` |

### **Interface Gráfica**
- **Abrir Vídeo**: Botão de abertura de arquivo
- **Playlist**: Gerenciamento de lista de reprodução
- **Configurações**: Acesso às preferências
- **Zoom**: Controle de ampliação
- **Croqui**: Modal de visualização de imagens

## 🔧 Configuração

### **config.py - Configurações Principais**
```python
# Performance
UI_UPDATE_INTERVAL = 500  # ms
DEFAULT_VOLUME = 50
SPEED_MAX = 32

# Rede
API_URL = "https://perplan.tech"
HOST = "localhost"
MEDIA_PORT = 1337

# Auto-pause
AUTO_PAUSE_MIN_DURATION = 50  # minutos
AUTO_PAUSE_POSITIONS = [0.25, 0.5, 0.75]
```

### **Personalização de Tema**
```python
THEME_COLORS = {
    "background": "#181818",
    "text": "#ffffff",
    "button": "#262626",
    "button_hover": "#3A3A3A",
    "slider_groove": "#404040",
    "slider_handle": "#ffffff"
}
```

## 📡 Sistema de Atualizações

### **Auto-Update**
- **Verificação Automática**: Check na inicialização
- **Download Inteligente**: Progress bar com feedback visual
- **Instalação Silenciosa**: Processo transparente ao usuário
- **Rollback**: Capacidade de reverter atualizações

### **API de Updates**
```python
# Endpoint de versão
GET /mediaplayer/api/version
Response: {"version": "4.1", "changelog": "..."}

# Download de atualização
GET /mediaplayer/api/download
Response: update_package.zip
```

### **Fluxo de Atualização**
1. **Verificação**: Compara versão local vs remota
2. **Confirmação**: Dialog thread-safe para usuário
3. **Download**: Progress visual com stages
4. **Extração**: Descompactação dos arquivos
5. **Instalação**: Execução do updater.exe
6. **Reinício**: Fechamento limpo e restart

## 🎨 Interface

### **Design System**
- **Dark Theme**: Interface escura profissional
- **Modern UI**: Componentes Qt6 estilizados
- **Responsive**: Adaptação a diferentes resoluções
- **Accessibility**: Controles acessíveis por teclado

### **Componentes Principais**
- **Video Frame**: Área de reprodução com overlay de controles
- **Control Bar**: Barra inferior com play, volume, timeline
- **Menu Bar**: Acesso a funcionalidades avançadas
- **Status Bar**: Informações de tempo e status
- **Modal Dialogs**: Playlist, Zoom, Configurações, Croqui

### **Notificações**
- **Toast Messages**: Feedback visual temporário
- **Progress Dialogs**: Indicadores de progresso
- **Error Handling**: Mensagens de erro elegantes
- **Status Updates**: Indicadores de estado em tempo real

## 📁 Estrutura do Projeto

```
PPL-Player/
├── 📄 main.py              # Entry point e update system
├── 🎬 video_player.py      # Classe principal do player
├── 🎨 ui_elements.py       # Componentes de interface
├── 🎯 styles.py            # Sistema de temas
├── ⚙️ config.py            # Configurações centralizadas
├── 🔧 utils.py             # Utilitários e helpers
├── 📋 playlist.py          # Modal de playlist
├── 🔍 zoom.py              # Modal de zoom
├── 🖼️ croqui_modal.py      # Modal de croqui
├── ⚙️ settings.py          # Modal de configurações
├── 🎭 splash_screen.py     # Tela inicial
├── 📡 api/
│   ├── api.py              # Servidor Flask de updates
│   ├── version.json        # Controle de versão
│   └── updates/            # Pacotes de atualização
├── 🔄 Updater/
│   ├── updater.py          # Sistema de instalação
│   └── updater.spec        # Build do updater
├── 🎨 icons/               # Ícones da aplicação
├── 📦 Installer/           # Scripts de instalação
├── 🔨 build/               # Arquivos de build
├── 📦 dist/                # Executáveis compilados
└── 📋 PPL Player.spec      # Configuração PyInstaller
```

## 🔄 Sistema de Build

### **PyInstaller Configuration**
```python
# PPL Player.spec
a = Analysis(['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('icons', 'icons')],
    hiddenimports=['PySide6', 'vlc'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
```

### **Build Commands**
```bash
# Compilar aplicação
pyinstaller "PPL Player.spec"

# Compilar updater
pyinstaller "Updater/updater.spec"

# Gerar instalador
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

### **Distribuição**
- **Executável**: `dist/PPL Player.exe`
- **Instalador**: `Output/PPL Player Setup.exe`
- **Updater**: `dist/updater.exe` (incluído no pacote)

## 📊 Recursos do Sistema

### **Suporte a Formatos**
| Tipo | Formatos |
|------|----------|
| **Vídeo** | MP4, AVI, MKV, DAV, DAV_ |
| **Imagem** | PNG, JPG, JPEG, BMP, GIF, TIFF, WebP |

### **Requisitos de Sistema**
| Componente | Especificação |
|------------|---------------|
| **OS** | Windows 10+ (64-bit) |
| **RAM** | 4GB mínimo, 8GB recomendado |
| **CPU** | Dual-core 2.0GHz+ |
| **GPU** | DirectX compatible |
| **HDD** | 500MB espaço livre |

### **Performance Benchmarks**
- **Startup Time**: < 2 segundos
- **Video Loading**: < 1 segundo (arquivos locais)
- **Memory Usage**: ~150MB em idle
- **CPU Usage**: ~5% durante reprodução normal

## 🛠️ Desenvolvimento

### **Ambiente de Desenvolvimento**
```bash
# Setup do ambiente
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Executar em modo debug
python main.py --debug
```

### **Arquitetura de Componentes**
- **ModernVideoPlayer**: Classe principal do reprodutor
- **UpdateChecker**: Sistema de atualizações thread-safe
- **PlaylistModal**: Gerenciamento de playlists
- **ZoomModal**: Controle de zoom avançado
- **CroquiModal**: Visualizador de imagens

### **Padrões de Design**
- **Singleton**: UpdateChecker global
- **Observer**: Sistema de sinais Qt
- **Factory**: Criação de componentes UI
- **Strategy**: Diferentes engines de reprodução

## 📞 Suporte

### **Documentação**
- **API Reference**: Documentação inline no código
- **Configuration Guide**: Comentários detalhados em config.py
- **Troubleshooting**: Logs detalhados para debug

### **Debugging**
```python
# Ativar logs detalhados
print("[APP] Informações de debug habilitadas")
import traceback
traceback.print_exc()
```

### **Logs do Sistema**
- `[APP]`: Eventos da aplicação principal
- `[VIDEO_PLAYER]`: Eventos do reprodutor
- `[UPDATER]`: Sistema de atualizações
- `[API]`: Comunicação com servidor

---

## 🏆 **PPL Player** - *Professional Video Analysis Made Simple*

> Desenvolvido com ❤️ em Python | Powered by Qt6 & VLC

**Versão**: 4.1+ | **Status**: Ativo | **Licença**: Proprietária

---

### 📈 **Estatísticas do Projeto**
- **Linhas de Código**: ~2,500+
- **Arquivos**: 15+ módulos Python
- **Dependências**: PySide6, VLC-Python, Flask, Requests
- **Plataforma**: Windows (com potencial multiplataforma)
- **Performance**: Reprodução até 32x velocidade