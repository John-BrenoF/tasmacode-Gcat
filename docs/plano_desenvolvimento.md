# Plano de Desenvolvimento 11.0Beta - 7 Dias

## Dia 1: Sistema de Undo/Redo + Validação de Estado

### Manhã: Implementar Redo Granular
- Completar o método `redo()` em `DocumentBuffer` [1](#4-0) 
- Implementar lógica para re-apagar seleções e re-inserir textos
- Testar com cenários complexos (multi-cursor, grandes textos)

### Tarde: Adicionar Validação de Estado
- Corrigir `get_matching_bracket()` para validar `line` negativo [2](#4-1) 
- Adicionar validação de `col` negativo em `select_word_at()` [3](#4-2) 
- Implementar validações em todos os métodos públicos do buffer

## Dia 2: Ajuste de Cursores + Auto-Pairing

### Manhã: Completar Ajuste de Cursores
- Implementar ajuste de cursores vizinhos na mesma linha [4](#4-3) 
- Implementar ajuste vertical de cursores (shift negativo) [5](#4-4) 
- Testar com múltiplos cursores em operações de deleção

### Tarde: Refatorar Auto-Pairing
- Mover lógica de auto-pairing do `InputMapper` para comandos registráveis [6](#4-5) 
- Implementar wrapping de seleção (TODO existente)
- Criar configuração para habilitar/desabilitar auto-pairing

## Dia 3: Performance - Renderização + Busca de Brackets

### Manhã: Implementar Viewport Culling
- Modificar `CodeEditor.paintEvent()` para renderizar apenas linhas visíveis
- Implementar repintura seletiva baseada em regiões modificadas
- Otimizar cache de métricas de fonte

### Tarde: Otimizar Busca de Brackets
- Melhorar algoritmo de `get_matching_bracket()` [7](#4-6) 
- Implementar cache de posições de brackets
- Remover limite arbitrário de 1000 linhas

## Dia 4: API de Plugins + Tratamento de Erros

### Manhã: Expandir API de Plugins
- Adicionar métodos para acessar estrutura de arquivos do projeto
- Implementar capacidade de registrar atalhos de teclado
- Adicionar hooks para eventos do editor (buffer modificado, arquivo aberto, etc.)

### Tarde: Melhorar Tratamento de Erros
- Implementar fallback para terminal no Windows [8](#4-7) 
- Adicionar fallback para fontes não encontradas
- Implementar logging de erros centralizado

## Dia 5: Refatoração da MainWindow

### Manhã: Extrair Lógica de Inicialização
- Criar `AppInitializer` class para instanciar subsistemas [9](#4-8) 
- Mover registro de comandos para `CommandRegistrar` [10](#4-9) 
- Criar `SignalConnector` para gerenciar conexões [11](#4-10) 

### Tarde: Implementar Builder Pattern
- Criar `MainWindowBuilder` para construir a UI
- Implementar injeção de dependências via builder
- Reduzir responsabilidades da `JCodeMainWindow`

## Dia 6: Configurações + Testes

### Manhã: Limpar Configurações Experimentais
- Remover ou implementar funcionalidades experimentais [12](#4-11) 
- Validar todas as configurações têm efeito prático
- Documentar opções de configuração

### Tarde: Implementar Testes Unitários
- Criar testes para `DocumentBuffer` (undo/redo, multi-cursor)
- Testar `InputMapper` com diversos cenários
- Implementar testes de integração para plugins

## Dia 7: Redução de Acoplamento + Documentação

### Manhã: Criar Abstrações
- Definir interfaces para componentes principais
- Implementar injeção de dependências onde falta
- Reduzir acoplamento entre widgets e lógica de negócio

### Tarde: Documentação e Release
- Atualizar documentação da arquitetura
- Criar guia de desenvolvimento de plugins
- Preparar release notes da 11.0Beta
- Test final de regressão

---

## Priorização Justificada

1. **Dias 1-2**: Problemas críticos que afetam diretamente a experiência do usuário
2. **Dias 3-4**: Performance e extensibilidade (impacto significativo)
3. **Dias 5-6**: Dívida técnica e qualidade do código
4. **Dia 7**: Polimento e preparação para release

Este plano equilibre correção de bugs críticos com melhorias de arquitetura, garantindo uma versão beta estável e mais robusta.

## Notes

O plano foca primeiro em problemas que impactam diretamente o usuário (undo/redo, cursores, auto-pairing) e depois em melhorias de arquitetura e performance. A refatoração da MainWindow é essencial para manutenibilidade futura, mas não bloqueia o uso do editor.

Wiki pages you might want to explore:
- [Architecture Overview (John-BrenoF/tasmacode-Gcat)](/wiki/John-BrenoF/tasmacode-Gcat#1.1)

### Citations

**File:** src/core/editor_logic/buffer.py (L392-392)
```python
            # TODO: Ajustar cursores vizinhos na mesma linha
```

**File:** src/core/editor_logic/buffer.py (L401-401)
```python
            # TODO: Ajustar cursores abaixo (shift vertical negativo)
```

**File:** src/core/editor_logic/buffer.py (L407-412)
```python
        if line >= len(self._lines): return None
        
        text = self._lines[line]
        # Adiciona verificação de segurança para evitar IndexError se o estado do cursor estiver corrompido
        if col > len(text):
            return None
```

**File:** src/core/editor_logic/buffer.py (L427-446)
```python
        # Busca simplificada (limitada a +/- 1000 linhas para performance)
        balance = 0
        current_line = line
        current_col = col
        
        while 0 <= current_line < len(self._lines):
            line_txt = self._lines[current_line]
            start_search = current_col + direction if current_line == line else (0 if direction == 1 else len(line_txt) - 1)
            
            range_iter = range(start_search, len(line_txt)) if direction == 1 else range(start_search, -1, -1)
            
            for i in range_iter:
                c = line_txt[i]
                if c == char: balance += 1
                elif c == target:
                    if balance == 0: return (current_line, i)
                    balance -= 1
            
            current_line += direction
            if abs(current_line - line) > 1000: break
```

**File:** src/core/editor_logic/buffer.py (L450-454)
```python
    def select_word_at(self, line: int, col: int):
        """Seleciona a palavra na posição do cursor."""
        if line >= len(self._lines): return
        line_text = self._lines[line]
        if col > len(line_text): return
```

**File:** src/core/editor_logic/buffer.py (L539-539)
```python
            pass # TODO: Implementar Redo granular
```

**File:** src/core/ui_logic/input_mapper.py (L84-89)
```python
            # Auto-pairing logic
            pairing_map = {'(': '()', '[': '[]', '{': '{}', '"': '""', "'": "''"}
            if text in pairing_map:
                # TODO: Add logic to wrap selection if it exists
                self.registry.execute("edit.insert_pair", pairing_map[text])
                return True
```

**File:** src/ui/main.py (L61-77)
```python
        self.highlighter = SyntaxHighlighter()
        self.search_manager = SearchManager()
        self.extension_bridge = ExtensionBridge()
        
        themes_path = os.path.join(root_dir, "themes")
        self.theme_manager = ThemeManager(themes_path)
        
        self.command_registry = CommandRegistry()
        self.session_manager = SessionManager()
        self.config_manager = ConfigManager()
        self.input_mapper = InputMapper(self.command_registry)
        self.github_auth = GithubAuth(self.config_manager.config_dir)
        self.github_auth.auth_changed.connect(self._update_user_avatar)
        
        self.live_server_manager = LiveServerManager()
        self.event_handler = EventHandler(self.extension_bridge, None) # Buffer será definido dinamicamente
        self.viewport_controller = ViewportController()
```

**File:** src/ui/main.py (L323-376)
```python
    def _register_core_commands(self):
        """Registra os comandos fundamentais do editor."""
        def get_active_buffer_and_execute(func_name, *args, **kwargs):
            """Wrapper para executar um comando no buffer ativo."""
            if self.active_editor and self.active_editor.buffer:
                buffer = self.active_editor.buffer
                func = getattr(buffer, func_name)
                func(*args, **kwargs)
                self._on_buffer_modified()

        r = self.command_registry
        
        # Comandos de Edição
        r.register("type_char", lambda t: get_active_buffer_and_execute("insert_text", t))
        r.register("edit.insert_pair", lambda p: get_active_buffer_and_execute("insert_paired_text", p))
        r.register("edit.backspace", lambda: get_active_buffer_and_execute("delete_backspace"))
        r.register("edit.new_line", lambda: get_active_buffer_and_execute("insert_text", "\n"))
        r.register("edit.indent", lambda: get_active_buffer_and_execute("insert_text", "    "))
        
        # Comandos de Cursor
        r.register("cursor.move_up", lambda: get_active_buffer_and_execute("move_cursors", -1, 0))
        r.register("cursor.move_down", lambda: get_active_buffer_and_execute("move_cursors", 1, 0))
        r.register("cursor.move_left", lambda: get_active_buffer_and_execute("move_cursors", 0, -1))
        r.register("cursor.move_right", lambda: get_active_buffer_and_execute("move_cursors", 0, 1))
        r.register("cursor.select_up", lambda: get_active_buffer_and_execute("move_cursors", -1, 0, True))
        r.register("cursor.select_down", lambda: get_active_buffer_and_execute("move_cursors", 1, 0, True))
        r.register("cursor.select_left", lambda: get_active_buffer_and_execute("move_cursors", 0, -1, True))
        r.register("cursor.select_right", lambda: get_active_buffer_and_execute("move_cursors", 0, 1, True))
        r.register("cursor.add_up", lambda: get_active_buffer_and_execute("add_cursor_relative", -1))
        r.register("cursor.add_down", lambda: get_active_buffer_and_execute("add_cursor_relative", 1))
        
        # Comandos de Histórico
        def safe_undo():
            if self.active_editor and self.active_editor.buffer and self.active_editor.buffer.can_undo:
                get_active_buffer_and_execute("undo")
        
        def safe_redo():
            if self.active_editor and self.active_editor.buffer and self.active_editor.buffer.can_redo:
                get_active_buffer_and_execute("redo")

        r.register("edit.undo", safe_undo)
        r.register("edit.redo", safe_redo)

        # Comandos de Área de Transferência
        r.register("edit.cut", self._cut_selection)
        r.register("edit.copy", self._copy_selection)
        r.register("edit.paste", self._paste_from_clipboard)
        
        r.register("view.command_palette", self.command_palette.show_palette)
        r.register("view.find", self._show_search_panel)
        r.register("view.switch_project", self._show_project_launcher)
        r.register("edit.rename", self._quick_rename)
        r.register("file.save", self._save_file)
        r.register("file.save_as", self._save_file_as)
```

**File:** src/ui/main.py (L433-471)
```python
    def _setup_logic_connections(self):
        """Conecta a lógica de UI aos widgets."""
        # Instala o filtro de eventos no editor
        # self.event_handler.install_on(self.editor_group) # O filtro agora é por editor
        
        # Conecta o controlador de viewport ao editor
        # self.viewport_controller.attach_to(self.editor) # Será conectado por aba
        
        # Exemplo de conexão de sinal: Atualizar statusbar ao scrollar
        self.viewport_controller.visible_lines_changed.connect(
            lambda first, last: self.custom_statusbar.showMessage(f"Linhas visíveis: {first} - {last}")
        )
        
        # CONEXÃO BIDIRECIONAL:
        # Conecta o sinal de modificação do buffer a um slot que atualiza a UI
        # self.event_handler.buffer_modified.connect(self._on_buffer_modified) # Não mais global
        
        # Conexões da Sidebar
        self.sidebar.open_folder_clicked.connect(self._open_project_dialog)
        self.sidebar.open_project_clicked.connect(self._open_project_dialog)
        self.sidebar.file_clicked.connect(self._open_file)
        self.sidebar.file_created.connect(self._open_file)
        self.sidebar.status_message.connect(self.custom_statusbar.showMessage)

        # Conexão do EditorGroup
        self.editor_group.active_editor_changed.connect(self._on_active_editor_changed)

        # Conexões do Painel de Busca
        self.search_panel.closed.connect(self._hide_search_panel)
        self.search_panel.find_next.connect(self._on_find)
        self.search_panel.replace_one.connect(self._on_replace_one)
        self.search_panel.replace_all.connect(self._on_replace_all)

        # Conexões do Live Server
        self.custom_statusbar.live_server_toggle_requested.connect(self._on_live_server_toggle)
        self.live_server_manager.server_started.connect(self._on_live_server_started)
        self.live_server_manager.server_stopped.connect(self._on_live_server_stopped)
        self.live_server_manager.error.connect(lambda msg: self.custom_statusbar.flash_message(msg, color="#dc3545"))
        self.custom_statusbar.avatar_clicked.connect(self._on_avatar_clicked)
```
