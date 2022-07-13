from turtle import title
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QTextEdit, QComboBox, QFormLayout, QGroupBox, QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from requests import request
import requests
import settings
import asyncio
import base64
from PyQt5.QtCore import QByteArray

class APIManager:
    api = 'http://localhost:8080/media'
    
    @staticmethod
    async def getMedia(callback, page_setup, page, sort_field="title", asc=True):
        response = requests.get(APIManager.api, {'page':page, 'asc':asc, 'sort':sort_field})
        response = response.json()

        print(response['totalPages'])
        page_setup(response['totalPages'])
        for ele in response['media']:
            callback(ele)



class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.createUI()
    
    def createUI(self):
        self.title = QLabel("Media")
        self.title.setStyleSheet('''font-size:24px; margin:0px;padding:0px''')
        self.layout = QGridLayout(self)
        self.setFixedWidth(settings.init_width)
        self.setFixedHeight(settings.init_height)
        # self.resize(settings.init_width, settings.init_height)
        self.setStyleSheet('''background-color:rgb(239, 225, 206)''')
        self.media_display = MediaDisplay()
        self.media_form = MediaForm()
        self.media_control = MediaControl()

        # self.layout.addWidget(self.title, 0, 0, 1, 4)
        self.layout.addWidget(self.media_display, 1, 0, 6, 4)
        self.layout.addWidget(self.media_form, 3, 7, 4, 2)
        self.layout.addWidget(self.media_control, 1, 7, 2, 2)
       
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.getMedia(self.media_display.addMedia, self.media_display.setPages, 0))

        self.show()


class PageButtons(QFrame):
    def __init__(self, display, first, prev, next, last):
        super().__init__()
        self.display = display
        self.buttons_heading = ["First", "<", ">", "Last"]
        self.buttons = []
        self.callbacks = [first, prev, next, last]
        self.createUI()
    def createUI(self):
        self.setFixedHeight(50)
        self.layout = QHBoxLayout(self)
        self.setStyleSheet('''border:none''')

        for i in range(4):
            b = QPushButton(self.buttons_heading[i])
            b.clicked.connect(self.callbacks[i])
            b.setStyleSheet('''background-color:grey''')
            self.buttons.append(b)
            self.layout.addWidget(b)

    
        


class MediaPreview(QFrame):
    def __init__(self, title, img_bytes, extension):
        super().__init__()
        self.title = title
        self.img_bytes = base64.b64decode(img_bytes)
        self.extension = extension
        self.createUI()


    def createUI(self):
        self.layout = QVBoxLayout(self)
        self.setFixedWidth(240)
        self.setFixedHeight(300)


        
        self.heading = QLabel(self.title)
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setStyleSheet('''border:none; color:white;''')

        self.img_container = QLabel("image")
        self.img_container.setStyleSheet('''border:none''')

        self.img = QPixmap()
        self.img.loadFromData(self.img_bytes)
        self.img = self.img.scaled(240, 280)
        self.img_container.setPixmap(self.img)
        
        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.img_container)

        self.setStyleSheet('''border:2px solid black; border-radius:4px; background-color:black;''')
        


class MediaDisplay(QFrame):
    def __init__(self):
        super().__init__()
        self.previews = []
        self.i = 0
        self.page_buttons = PageButtons(self, self.firstPage, self.prevPage, self.nextPage, self.lastPage)
        self.cur_page = 0
        self.total_pages = -1
        self.createUI()

    def setPages(self, total_pages):
        self.total_pages = total_pages

    def clear(self):
        for preview in self.previews:
            preview.setParent(None)
        self.previews = []

    def getPage(self, page_num):
        self.i = 0
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.getMedia(self.addMedia, self.setPages, page_num))

    def firstPage(self):
        if self.cur_page ==0:
            return
    
        self.clear()
        self.cur_page = 0
        self.getPage(0)

    def nextPage(self):
        if self.cur_page+1 >= self.total_pages:
            return
        self.clear()
        self.cur_page +=1
        self.getPage(self.cur_page)
    
    def prevPage(self):
        if self.cur_page-1<0:
            return
        self.clear()
        self.cur_page -=1
        self.getPage(self.cur_page)
    
    def lastPage(self):
        if self.cur_page == self.total_pages-1:
            return
        self.clear()
        self.cur_page = self.total_pages-1
        self.getPage(self.cur_page)

    def createUI(self):
        self.content = QVBoxLayout(self)
        self.content.addStretch()
        self.content.setAlignment(Qt.AlignCenter)
        self.media_content = QFrame()
        self.media_content.setFixedWidth(settings.display_width)
        self.media_content.setFixedHeight(settings.display_height)
        self.media_content.setStyleSheet('''border:none;''')
        self.display = QGridLayout(self.media_content)
        self.content.addWidget(self.media_content)
        self.content.addWidget(self.page_buttons)
        self.setStyleSheet('''border:2px solid black; background-color:#c8b7a6''')
    
    def addMedia(self, media):
        media_preview = MediaPreview(media["title"], media["imgBytes"], media['imgExtension'][1:])
        self.previews.append(media_preview)
        self.display.addWidget(media_preview, (self.i//3) * 3, (self.i%3)*5, 3, 4)
        self.i +=1



class MediaForm(QGroupBox):
    def __init__(self):
        super().__init__("Submit Media")
        self.createUI()
    
    def createUI(self):
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''background-color:#c8b7a6; color:black; border:2px solid black;border-radius:7px;''')
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(5, 25, 5, 5)
        
        self.layout.setVerticalSpacing(10)
        self.layout.setLabelAlignment(Qt.AlignLeft)
        
        self.title_input = QLineEdit()
        self.title_heading = QLabel("Title:")
        self.title_heading.setStyleSheet('''border:none''')


        self.medium_input = QComboBox()
        self.medium_heading = QLabel("Medium:")
        self.medium_heading.setStyleSheet('''border:none''')


        self.bm_input = QLineEdit()
        self.bm_heading = QLabel("Bookmark(ep/chp):")
        self.bm_heading.setStyleSheet('''border:none''')


        self.rating_input = QLineEdit()
        self.rating_heading = QLabel("Rating:")
        self.rating_heading.setStyleSheet('''border:none''')


        self.notes_input = QTextEdit()
        self.notes_heading = QLabel("Notes")
        self.notes_heading.setStyleSheet('''border:none''')


        self.layout.addRow(self.title_heading, self.title_input)
        self.layout.addRow(self.medium_heading, self.medium_input)
        self.layout.addRow(self.bm_heading, self.bm_input)
        self.layout.addRow(self.rating_heading, self.rating_input)
        self.layout.addRow(self.notes_heading, self.notes_input)



class MediaControl(QGroupBox):
    def __init__(self):
        super().__init__("Controls")
        self.createUI()
    
    def createUI(self):
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''background-color:#c8b7a6; color:black; border:2px solid black;border-radius:7px;''')
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(5, 25, 5, 5)
        
        self.layout.setVerticalSpacing(10)
        self.layout.setLabelAlignment(Qt.AlignLeft)
        

        self.sort_input = QComboBox()
        self.sort_heading = QLabel("Sort:")
        self.sort_heading.setStyleSheet('''border:none''')

        self.layout.addRow(self.sort_heading, self.sort_input)




class MediaCard(QFrame):
    def __init__(self):
        super().__init__()
        self.createUI()
    
    def createUI(self):
        self.layout = QVBoxLayout
        self.setStyleSheet('''border: 2px solid white''')




