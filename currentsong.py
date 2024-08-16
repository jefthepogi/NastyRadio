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

    self.max_duration = int(self.metadata.duration) * 1000
    self.start: int = 0
    self.end: int = self.max_duration
    self.audio_current = self._timeStamp(self.start)
    self.audio_remaining = self._timeStamp(self.end)
    self.page.overlay.append(self.audio)
    self.page.add(ft.Container(expand=True)) # TODO: Issue fixed temporarily: Page container needs control child to append an audio.
    self.audio_slider = ft.Container(expand=3, padding=ft.padding.symmetric(horizontal=-15), margin=0, content=ft.Slider(min=0, max=self.max_duration, label="{value}", active_color=LIGHTCOLOR, round=2, on_change_end=lambda e: self._handle_seek(round(float(e.data)))))
    self.play_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW, icon_size=30, icon_color=LIGHTCOLOR, on_click=lambda _: self._toggle_play(True))
    self.pause_btn = ft.IconButton(icon=ft.icons.PAUSE_CIRCLE, icon_size=30, icon_color=LIGHTCOLOR, on_click=lambda _: self._toggle_play(False))
    self.play_anim = ft.AnimatedSwitcher(
      content=ft.Container(content=self.play_btn, padding=-15, margin=1, alignment=ft.alignment.center),
      transition=ft.AnimatedSwitcherTransition.SCALE,
      duration=200,
      reverse_duration=100,
      switch_in_curve=ft.AnimationCurve.BOUNCE_IN,
      switch_out_curve=ft.AnimationCurve.BOUNCE_OUT,
      expand=1,
    )

    self.hud = ft.Column(
      [
        # TODO: Scrolling Title
        ft.Row(
          [
            ft.Text(f"{self.data["title"]}", max_lines=1, text_align=ft.TextAlign.CENTER, theme_style=ft.TextThemeStyle.TITLE_SMALL, overflow=ft.TextOverflow.FADE, expand=1),
          ],
          alignment=ft.alignment.center,
        ),
        ft.Row(
          [
            self.audio_current,
            self.audio_slider,
            self.audio_remaining,
          ],
        ),
        ft.Row(
          [
            ft.Container(expand=.2, padding=-15, width=10, height=10, content=ft.IconButton(icon=ft.icons.REPLAY_10, icon_size=18, icon_color=LIGHTCOLOR)),
            ft.IconButton(expand=.2, icon=ft.icons.SKIP_PREVIOUS, icon_color=LIGHTCOLOR),
            self.play_anim,
            ft.IconButton(expand=.2, icon=ft.icons.SKIP_NEXT, icon_color=LIGHTCOLOR),
            ft.Container(expand=.2, padding=-15, width=10, height=10, content=ft.IconButton(icon=ft.icons.FORWARD_10, icon_size=18, icon_color=LIGHTCOLOR)),
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
    self.audio_slider.value = delta
    self.audio_slider.update()

  def _handle_seek(self, delta):
    self.start = delta
    self.end = self.max_duration - delta
    self.audio.seek(self.start)
    self._update_slider(delta)

  def _toggle_play(self, s: bool):
        if s:
          self.audio.play() if self.audio.get_current_position() == 0 else self.audio.resume()
          self.play_anim.content.content = self.pause_btn
          self.play_anim.update()
        else:
          self.audio.pause() # TODO: Do something on exiting the song also. Release the cum
          self.play_anim.content.content = self.play_btn
          self.play_anim.update()

  def _format_timestamp(self, value: int) -> str:
    milliseconds: int = value
    minutes, seconds = divmod(milliseconds / 1000, 60)
    return "{:02}:{:02}".format(int(minutes), int(seconds))
      
  def _timeStamp(self, val: int):
    return ft.Text(expand=.5, value=self._format_timestamp(val), size=10, weight=ft.FontWeight.W_200, text_align=ft.TextAlign.CENTER)
  
  def _update_timestamps(self, start: int, end: int):
    self.audio_current.value = self._format_timestamp(start)
    self.audio_remaining.value = self._format_timestamp(end)
    self.audio_current.update()
    self.audio_remaining.update()