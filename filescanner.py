import os
from tinytag import TinyTag

class FileScanner:
  def __init__(self, directory, extensions) -> None:
    self.current_id = 0
    titles, filepaths, metadatas = self._scan_audios(os.path.normcase(directory), extensions)
    self._database = [{"id": i, "cover": None, "title": title, "filepath": filepath, "metadata": metadata} for i, (title, filepath, metadata) in enumerate(zip(titles, filepaths, metadatas))]

  def _scan_audios(self, directory, extensions):
    titles = []
    filepaths = []
    metadatas = []
    excluded = ['.venv', 'Photos']
    for root, dirs, files in os.walk(directory, topdown=True):
      dirs[:] = [d for d in dirs if d not in excluded]
      for file in files:
        if file.endswith(extensions):
          name, _ = os.path.splitext(file)
          titles.append(name)
          filepaths.append(os.path.normcase(file))
          tag = TinyTag.get(os.path.join(root, file))
          metadatas.append(tag) 
    return titles, filepaths, metadatas
  
  def get(self):
    return self._database

  def access(self, music_id: int):
    return self._database[music_id]
