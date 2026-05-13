import pygame
import os
import random

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_dir = "assets/audio"
        self.current_track = None
        self.tracks = {
            "menu": "menu_theme.mp3",
            "level": "level_theme.mp3",
            "corruption": "glitch_ambience.mp3"
        }
        self.enabled = True

    def play_music(self, track_key, loop=-1):
        if not self.enabled:
            return

        track_path = os.path.join(self.music_dir, self.tracks.get(track_key, ""))
        
        # Se o arquivo não existir, não tentamos carregar para evitar erros
        if not os.path.exists(track_path):
            print(f"Aviso: Arquivo de áudio não encontrado: {track_path}")
            return

        try:
            if self.current_track == track_key and pygame.mixer.music.get_busy():
                return
            
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loop)
            self.current_track = track_key
        except Exception as e:
            print(f"Erro ao reproduzir música: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def update_volume(self, corruption_level):
        """Ajusta volume ou aplica 'glitches' no áudio baseados na corrupção."""
        if not pygame.mixer.music.get_busy():
            return

        # Volume base diminui levemente conforme o sistema falha, ou fica instável
        base_vol = 0.5
        if corruption_level > 0.8:
            # Oscilação de volume em alta corrupção (efeito de rádio quebrado)
            vol = base_vol * random.uniform(0.3, 1.0)
        else:
            vol = base_vol
        
        pygame.mixer.music.set_volume(vol)
