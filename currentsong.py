import os
import flet as ft
from configs import *

class CurrentSong:
  def __init__(self, data: any, metadata: any, page: ft.Page) -> None:
    self.page = page
    self.data = data
    self.metadata = metadata
    self.audio = ft.Audio(
      src=os.path.normcase(self.data["filepath"]),
      autoplay=False,
      volume=1,
      on_loaded=lambda _: print("Loaded"),
      on_position_changed=lambda e: self._update(int(e.data)),
      on_state_changed=lambda e: print("State changed:", e.data),
    )

    self.max_duration: int = 0
    self.start: int = 0
    self.end: int = 0
    self.audio_current = self._timeStamp(self.start)
    self.audio_remaining = self._timeStamp(self.end)
    self.page.overlay.append(self.audio)
    self.page.add(ft.Container(expand=True)) # TODO: Issue fixed temporarily: Page container needs control child to append an audio.
    self.audio_slider = ft.Container(
      padding=ft.padding.symmetric(horizontal=-15), 
      margin=0, 
      content=ft.Slider(
        expand=1,
        min=0,
        label="{value}", 
        active_color=LIGHTCOLOR, 
        round=2,
        on_change=lambda _: self._update_duration(),
        on_change_end=lambda e: self._handle_seek(
          round(float(e.data))
        )
      )
    )
    self.play_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW, icon_size=30, icon_color=LIGHTCOLOR, on_click=lambda _: self._toggle_play(True))
    self.pause_btn = ft.IconButton(icon=ft.icons.PAUSE_CIRCLE, icon_size=30, icon_color=LIGHTCOLOR, on_click=lambda _: self._toggle_play(False))
    self.toggleBTN = ft.Container(expand=1, content=self.play_btn, padding=-15, margin=1, alignment=ft.alignment.center)
    self.hud = ft.Column(
      [
        # TODO: Scrolling Title
        ft.Row(
          [
            ft.Text(f"{self.data["title"]}", max_lines=1, text_align=ft.TextAlign.CENTER, theme_style=ft.TextThemeStyle.TITLE_SMALL, overflow=ft.TextOverflow.CLIP, expand=1),
          ],
          alignment=ft.alignment.center,
        ),
        self.audio_slider,
        ft.Row(
          [
            self.audio_current,
            self.audio_remaining,
          ],
          alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Row(
          [
            ft.Container(expand=.4, padding=-15, width=10, height=10, content=ft.IconButton(icon=ft.icons.REPLAY_10, icon_size=18, icon_color=LIGHTCOLOR)),
            ft.IconButton(expand=.4, icon=ft.icons.SKIP_PREVIOUS, icon_color=LIGHTCOLOR),
            self.toggleBTN,
            ft.IconButton(expand=.4, icon=ft.icons.SKIP_NEXT, icon_color=LIGHTCOLOR),
            ft.Container(expand=.4, padding=-15, width=10, height=10, content=ft.IconButton(icon=ft.icons.FORWARD_10, icon_size=18, icon_color=LIGHTCOLOR)),
          ],
          alignment=ft.MainAxisAlignment.CENTER,
        )
      ],
      alignment=ft.CrossAxisAlignment.CENTER,
    )
    
  def _update(self, delta: int):
    self.start += 1000
    self.end -= 1000
    self._update_slider(delta)
    self._update_timestamps(self.start, self.end)

  def _update_slider(self, delta: int):
    self.audio_slider.content.value = delta
    self.audio_slider.content.update()

  def _update_duration(self):
    self.max_duration = self.audio.get_duration() + 1000
    self.audio_slider.content.max = self.max_duration
    if self.audio.get_current_position() < 1500:
      self.end = self.max_duration

  def _handle_seek(self, delta):
    self.start = delta
    self.end = self.max_duration - delta
    self.audio.seek(self.start)
    self._update_slider(delta)

  def _toggle_play(self, s: bool):
    if s:
      self.audio.play() if self.audio.get_current_position() < 1000 else self.audio.resume()
      self.toggleBTN.content = self.pause_btn
      self.toggleBTN.update()
    else:
      self.audio.pause() # TODO: Do something on exiting the song also. Release the cum
      self.toggleBTN.content = self.play_btn
      self.toggleBTN.update()
    self._update_duration()
    
          
  def _format_timestamp(self, value: int) -> str:
    milliseconds: int = value
    minutes, seconds = divmod(milliseconds / 1000, 60)
    return "{:02}:{:02}".format(int(minutes), int(seconds))
      
  def _timeStamp(self, val: int):
    return ft.Text(expand=.5, value=self._format_timestamp(val), size=10, weight=ft.FontWeight.W_200, text_align=ft.TextAlign.CENTER)
  
  def _update_timestamps(self, start: int, end: int):
    self.audio_current.value = self._format_timestamp(start)
    self.audio_remaining.value = f"-{self._format_timestamp(end)}"
    self.audio_current.update()
    self.audio_remaining.update()