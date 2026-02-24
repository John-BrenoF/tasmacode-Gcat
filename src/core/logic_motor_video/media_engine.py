from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QObject, Signal
import logging

logger = logging.getLogger("MediaEngine")

class MediaEngine(QObject):
    """
    Responsável exclusivamente pela lógica de controle de mídia (Audio/Video).
    Gerencia o QMediaPlayer e QAudioOutput.
    """
    
    # Sinais para desacoplar a UI do estado do player
    position_changed = Signal(int)      # Emite a posição atual em ms
    duration_changed = Signal(int)      # Emite a duração total em ms
    state_changed = Signal(int)         # Emite o estado (Playing, Paused, Stopped)
    error_occurred = Signal(str)        # Emite mensagens de erro
    media_loaded = Signal(str)          # Emite quando uma mídia é carregada

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        
        # Conecta o áudio ao player
        self._player.setAudioOutput(self._audio_output)
        
        # Configurações iniciais
        self._audio_output.setVolume(0.7) # 70% volume padrão
        
        self._connect_signals()

    def _connect_signals(self):
        """Conecta os sinais internos do QMediaPlayer aos sinais públicos da Engine."""
        self._player.positionChanged.connect(lambda pos: self.position_changed.emit(pos))
        self._player.durationChanged.connect(lambda dur: self.duration_changed.emit(dur))
        self._player.playbackStateChanged.connect(lambda state: self.state_changed.emit(state))
        self._player.errorOccurred.connect(self._handle_error)

    def set_video_output(self, video_surface: QObject):
        """Define onde o vídeo será renderizado (Injeção de Dependência)."""
        self._player.setVideoOutput(video_surface)

    def load_source(self, file_path: str):
        """Carrega um arquivo de mídia local."""
        if not file_path:
            return
        
        url = QUrl.fromLocalFile(file_path)
        self._player.setSource(url)
        self.media_loaded.emit(file_path)
        logger.info(f"Mídia carregada: {file_path}")

    def play(self):
        """Inicia ou retoma a reprodução."""
        self._player.play()
        logger.debug("Reprodução iniciada.")

    def pause(self):
        """Pausa a reprodução."""
        self._player.pause()
        logger.debug("Reprodução pausada.")

    def stop(self):
        """Para a reprodução e retorna ao início."""
        self._player.stop()
        logger.debug("Reprodução parada.")

    def seek(self, position_ms: int):
        """Altera a posição de reprodução (em milissegundos)."""
        self._player.setPosition(position_ms)

    def set_volume(self, volume: int):
        """Define o volume (0 a 100)."""
        # QAudioOutput aceita float de 0.0 a 1.0
        normalized_volume = max(0, min(volume, 100)) / 100.0
        self._audio_output.setVolume(normalized_volume)

    def get_state(self):
        return self._player.playbackState()

    def get_duration(self):
        return self._player.duration()

    def get_position(self):
        return self._player.position()

    def _handle_error(self):
        """Trata erros internos do player."""
        error_msg = self._player.errorString()
        logger.error(f"Erro no MediaEngine: {error_msg}")
        self.error_occurred.emit(error_msg)