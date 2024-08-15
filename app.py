from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pytubefix import YouTube, Playlist

app = FastAPI()

allowed_cors_origins = ['*']
app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

class Video:
  def __init__(self, video: YouTube):
    self.title = video.title
    self.url = video.watch_url
    self.thumbnail = video.thumbnail_url
  def to_dict(self):
    return {
      'title': self.title,
      'url': self.url,
      'thumbnail': self.thumbnail
    }

class Task:
  PENDING = 0
  COMPLETE = 1
  ERROR = 2
  def __init__(self, task_id, status=PENDING, statusMsg='', data=None):
    self.task_id = task_id
    self.status = status
    self.statusMsg = statusMsg
    self.data = data
    self.error = None
  def setStatus(self, status, msg=''):
    self.status = status
    self.statusMsg = msg
  def setData(self, data):
    self.data = data
  def to_dict(self):
    if self.status == self.ERROR:
      return {
        'task_id': self.task_id,
        'status': self.statusMsg or 'Error',
        'error': self.error
      }
    if self.status == self.PENDING:
      return {
        'task_id': self.task_id,
        'status': self.statusMsg or 'Pending',
        'data': self.data
      }
    if self.status == self.COMPLETE:
      return {
        'task_id': self.task_id,
        'status': self.statusMsg or 'Complete',
        'data': self.data
      }
    return {
      'task_id': self.task_id,
      'status': 'Unknown',
      'error': 'Unknown status'
    }

tasks = {}

@app.get("/info")
async def init_video(url: str):
  if tasks.get(url):
    return tasks[url]
  tasks[url] = Task(url)
  try:
    videos = []
    if 'list' in url:
      playlist = Playlist(url)
      videos = [Video(video).to_dict() for video in playlist.videos]
    else:
      videos = [Video(YouTube(url))]
    tasks[url].setData([video.to_dict() for video in videos])
    return tasks[url]
  except Exception as e:
    tasks[url].setStatus('error')
    raise HTTPException(status_code=400, detail=str(e))

@app.get('/status')
async def get_status(task_id: str):
  if tasks.get(task_id):
    return tasks[task_id].to_dict()
  raise HTTPException(status_code=404, detail='Task not found')

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app)