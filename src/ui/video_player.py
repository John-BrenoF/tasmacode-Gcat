from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QStyle
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from src.core.logic_motor_video import MediaEngine, VideoSurface

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = MediaEngine(self)
        self.surface = VideoSurface(self)
        self.engine.set_video_output(self.surface)
        
        self._setup_ui()
        
        # Conecta sinais do motor à UI
        self.engine.position_changed.connect(self._on_position_changed)
        self.engine.duration_changed.connect(self._on_duration_changed)
        self.engine.state_changed.connect(self._on_state_changed)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de vídeo
        layout.addWidget(self.surface)
        
        # Controles
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 5)
        
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_play.clicked.connect(self._toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self._on_slider_moved)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.slider)
        
        layout.addLayout(controls_layout)
        
        self._is_seeking = False

    def load_file(self, path):
        self.engine.load_source(path)
        self.engine.play()

    def _toggle_play(self):
        if self.engine.get_state() == QMediaPlayer.PlaybackState.PlayingState:
            self.engine.pause()
        else:
            self.engine.play()

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def _on_position_changed(self, position):
        if not self._is_seeking:
            self.slider.setValue(position)

    def _on_duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def _on_slider_moved(self, position):
        pass

    def _on_slider_pressed(self):
        self._is_seeking = True

    def _on_slider_released(self):
        self._is_seeking = False
        self.engine.seek(self.slider.value())

    def closeEvent(self, event):
        """Garante que o vídeo pare ao fechar a aba."""
        self.engine.stop()
        super().closeEvent(event)

    def hideEvent(self, event):
        """Pausa o vídeo ao trocar de aba ou minimizar, evitando áudio em background."""
        self.engine.pause()
        super().hideEvent(event)