import os
from configs import *
import flet as ft
from filescanner import FileScanner
from currentsong import CurrentSong

def main(page: ft.Page):
  page.window.min_width = 300
  page.window.min_height = 600
  page.fonts = {
    "Arial Unicode": "assets/fonts/ARIALUNI.TTF",
    "Ubuntu": "assets/fonts/Ubuntu-B.ttf",
  }
  page.theme = ft.Theme(font_family="Arial Unicode")
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = DARKCOLOR
  page.title = "NastyRadio - Music Player"

  def route_change(e: ft.RouteChangeEvent) -> None:
    page.views.clear()

    # Index
    page.views.append(
      ft.View(
        route='/',
        controls=[
          nav,
          songlist,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4
      )
    )

    if page.route == "/search":
      
      def handle_search(e):  
        searchlv.controls.clear()
        string = e.control.value
        searchbar.title.content.suffix_icon = ft.icons.SEARCH_ROUNDED
        searchbar.title.content.suffix = []
        if bool(string and not string.isspace()):
          searchbar.title.content.suffix_icon = False
          searchbar.title.content.suffix = ft.Container(
            ft.IconButton(
              icon=ft.icons.CLEAR,
              icon_size=12,
              on_click=handle_clear
            ),
            padding=ft.padding.all(-8),
            margin=ft.margin.only(left=0,right=2,top=0,bottom=0),
            width=15,
            height=15
          )
          for music in database.get():
            if music["title"].upper().find(string.upper()) != -1:
              searchlv.controls.append(SongTile(music["id"]))
        # print(s.value)
        page.update()

      def handle_clear(e):
        searchbar.title.content.value = ""
        page.update()
        
      searchlv = ft.ListView() 
      searchbar = ft.AppBar(
        leading_width=40,
        title=ft.Container(
          padding=0,
          margin=ft.margin.only(right=10),
          content=ft.TextField(
            hint_text="Search",
            hint_style=ft.TextStyle(color=LIGHTCOLOR, size=12, weight=ft.FontWeight.BOLD),
            text_style=ft.TextStyle(color=LIGHTCOLOR, size=12, weight=ft.FontWeight.BOLD), 
            border_radius=ft.border_radius.all(12),
            border_color=LIGHTCOLOR,
            text_align=ft.CrossAxisAlignment.CENTER,
            cursor_color=LIGHTCOLOR,
            on_change=handle_search,
            suffix_icon=ft.icons.SEARCH_ROUNDED,
            content_padding=ft.padding.only(left=16, right=12, top=0, bottom=0),
          ),
        ),
        title_spacing=2
      )
      querylist = ft.Card(
        content=searchlv,
        color=DARKCOLOR,
        margin=ft.margin.symmetric(horizontal=2)
      )

      page.views.append(
        ft.View(
          route='/search',
          controls=[
            searchbar,
            querylist,
          ],
          vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
      )

    """ ---------------------------------------------------------- PLAY SONG -------------------------------------------------------------------------------- """
    if page.route == "/play":
      
      def tabButton(**kwargs):
        title = kwargs.get('title')
        icon = kwargs.get('icon')
        return ft.TextButton(
          content=ft.Row(
            [
              ft.Text(title, size=8, font_family='Ubuntu'),
              ft.Icon(name=icon, size=13)
            ],
            spacing=4,
          ),
          style=ft.ButtonStyle(color=LIGHTCOLOR, bgcolor=DARKCOLOR, shape=ft.RoundedRectangleBorder(radius=15)),
        )
      
      myTabs = ft.AppBar(
        leading_width=40,
        title_spacing=5,
        title=ft.Row(
          [
            tabButton(title='Queue', icon=ft.icons.QUEUE_MUSIC),
            tabButton(title='Song', icon=ft.icons.MUSIC_NOTE),     
          ],
          spacing=6,
        ),
        actions=[
          ft.Container(
            ft.IconButton(
              icon=ft.icons.MORE_VERT,
              icon_color=LIGHTCOLOR,
              icon_size=18,
              # on_click=lambda _: page.open()
            ),
          ),
        ]
      )
      
      cover_photo = ft.Image(
        src=os.path.normcase("assets/svgs/music.svg"),
        height=250,
        width=300,
        color=LIGHTCOLOR,
      )
      
      mySong = CurrentSong(data=database.access(database.current_id), page=page, metadata=database.access(database.current_id)["metadata"])
        
      page.views.append(
        ft.View(
          route="/play",
          controls=[
            myTabs,
            ft.Card(
              content=ft.Container(
                expand=True,
                content=ft.Column(
                  controls=[ 
                    cover_photo,
                    mySong.hud,
                  ],
                  expand=True,
                  alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                bgcolor=DARKCOLOR,
              )
            )
          ],
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
      )
    
    page.update()
  
  def view_pop(e: ft.ViewPopEvent) -> None:
    page.views.pop()
    top_view: ft.View = page.views[-1]
    page.go(top_view.route)

  def SongConfig(music):
    return ft.BottomSheet(
      dismissible=True,
      enable_drag=True,
      content=ft.Container(
        ft.Column(
          controls=[
            ft.Row(
              [ 
                ft.Icon(name=ft.icons.IMAGE, size=30),
                ft.Text(music["title"], expand=1, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, theme_style=ft.TextThemeStyle.TITLE_SMALL, color=ft.colors.WHITE70),
                ft.Row(
                  [
                    ft.Container(ft.IconButton(icon=ft.icons.INFO, icon_size=15, icon_color=LIGHTCOLOR), width=18, height=18, padding=-10),
                    ft.Container(ft.IconButton(icon=ft.icons.IOS_SHARE, icon_size=15, icon_color=LIGHTCOLOR), width=18, height=18, padding=-10),
                  ],
                  spacing=6
                )
              ],
              spacing=12
            ),
            # Main Contents
            ft.ListView(
              controls=[
                ft.ListTile(
                )
              ]
            )
          ],
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=6)
      )
    )

  def SongTile(songID):
    def handle_click(e):
      database.current_id = songID
      page.go('/play')

    song_config = SongConfig(database.access(songID))
    songtile = ft.ListTile(
      leading=ft.Icon(ft.icons.MUSIC_NOTE_ROUNDED, color=LIGHTCOLOR),
      title=ft.Text(database.access(songID)["title"], max_lines=1, size=13, overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.W_600, color=ft.colors.WHITE70),
      title_alignment=ft.ListTileTitleAlignment.TITLE_HEIGHT,
      trailing=ft.Container(
        ft.IconButton(
          icon=ft.icons.MORE_VERT,
          icon_color=LIGHTCOLOR,
          icon_size=18,
          on_click=lambda _: page.open(song_config)
        ),
        padding=0,
        margin=-5,
      ),
      horizontal_spacing=10,
      content_padding=ft.padding.symmetric(horizontal=6),
      on_click=handle_click
    )
    return songtile

  nav = ft.Container(
    ft.Row(
      controls = [
        ft.Text(
          value="NastyRadio", 
          weight=ft.FontWeight.BOLD, 
          text_align=ft.TextAlign.CENTER,
          color=LIGHTCOLOR,
          size=16,
          font_family="Ubuntu"
        ),
        ft.Row(
          controls=[
            ft.IconButton(icon=ft.icons.SEARCH, icon_color=LIGHTCOLOR, on_click=lambda _: page.go("/search")),
            ft.IconButton(icon=ft.icons.SETTINGS, icon_color=LIGHTCOLOR),
          ],
          spacing=2,
          alignment=ft.alignment.center
        )
      ],
      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    ),
  )
  
  database = FileScanner(ROOT_DIR, (".mp3", ".wav"))
  
  songlist = ft.Card(
    content=ft.ListView(
      controls=[ SongTile(music["id"]) for music in database.get() ],
    ),
    color=DARKCOLOR,
    margin=ft.margin.symmetric(horizontal=2)
  )

  page.on_route_change = route_change
  page.on_view_pop = view_pop
  page.go(page.route)



if __name__ == '__main__':
  ft.app(target=main, assets_dir=ROOT_DIR)
