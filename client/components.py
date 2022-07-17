from email.mime import base
from turtle import title
from PyQt5.QtWidgets import QMessageBox,QGridLayout, QStackedWidget, QSpacerItem, QFileDialog, QLineEdit, QTextEdit, QComboBox, QFormLayout, QGroupBox, QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from requests import request
import requests
import settings
import asyncio
import base64
import json

class APIManager:
    api = 'http://localhost:8080/media'

    @staticmethod
    async def deleteMedia(callback, media_id):
        response = requests.delete(APIManager.api, params={"mediaId":media_id})
        response = response.json()
        print(response)
        callback(response)


    
    @staticmethod
    async def getMedia(callback, after, page_setup, page, sort_field="title", asc=True):
        print(sort_field)
        print(asc)
        response = requests.get(APIManager.api, {'page':page, 'asc':asc, 'sort':sort_field})
        response = response.json()

        page_setup(response['totalPages'])
        for ele in response['media']:
            callback(ele)
        
        after()

    @staticmethod
    async def postMedia(callback, title, medium, bookmark, rating, notes, img_filename):
        with open(img_filename, "rb") as f:
            im_bytes = f.read()        
        im_b64 = base64.b64encode(im_bytes).decode("utf8")

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        index = img_filename.rfind('.')
        
        payload = json.dumps({"mediaId": -1, "imgBytes": im_b64, "title": title, "bookmark":bookmark, "rating":rating, "notes":notes, "medium":medium, "imgExtension":img_filename[index:]})

        response = requests.post(APIManager.api, data=payload, headers=headers)
        callback(True)

    @staticmethod
    async def putMedia(callback, media_id, title, medium, bookmark, rating, notes, img, ext):

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = json.dumps({"mediaId": media_id, "imgBytes": img, "title": title, "bookmark":bookmark, "rating":rating, "notes":notes, "medium":medium, "imgExtension":ext})

        response = requests.put(APIManager.api, data=payload, headers=headers)
        callback(True)
    
    @staticmethod
    def process_image(img):
        with open(img, "rb") as f:
            im_bytes = f.read()        
        im_b64 = base64.b64encode(im_bytes).decode("utf8")
        index = img.rfind('.')
        ext = img[index:]
        return (im_bytes, im_b64, ext)



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
        # self.setStyleSheet('''background-color:rgb(239, 225, 206)''')
        self.setStyleSheet('''background-color:#e7dfdd''')
        self.filters = MediaControl()
        self.media_display = MediaDisplay(self.filters)
        self.filters.set_btn_action(self.media_display.first_page_refresh)
        self.media_form = MediaForm(self.media_display, "Add Media", "Submit", self.media_display.firstPage)

        # self.layout.addWidget(self.title, 0, 0, 1, 4)
        self.layout.addWidget(self.media_display, 1, 0, 6, 4)
        self.layout.addWidget(self.media_form, 3, 7, 4, 2)
        self.layout.addWidget(self.filters, 1, 7, 2, 2)
       
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.getMedia(self.media_display.addMedia, self.media_display.spacers, self.media_display.setPages, 0))

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
            b.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
            self.buttons.append(b)
            self.layout.addWidget(b)

    
        


class MediaPreview(QFrame):
    def __init__(self, title, medium, bookmark, rating, notes, img_bytes, extension, media_card, media_id):
        super().__init__()
        self.media_id = media_id
        self.title = title
        self.medium = medium
        self.bookmark = bookmark
        self.rating = rating
        self.notes = notes
        self.extension = extension
        self.media_card = media_card
        self.img_bytes = img_bytes
        self.createUI()

    def mousePressEvent(self, e):
        self.media_card.setMedia(self.title, self.medium, self.bookmark, self.rating, self.notes, self.img_bytes, self.extension,self.media_id)

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
        self.img.loadFromData(base64.b64decode(self.img_bytes))
        self.img = self.img.scaled(240, 280)
        self.img_container.setPixmap(self.img)
        
        self.layout.addWidget(self.heading)
        self.layout.addWidget(self.img_container)

        self.setStyleSheet('''border:2px solid black; border-radius:4px; background-color:black;''')
        

class SpacerItem(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.layout = QSpacerItem(self, width, height)
        self.layout.changeSize(width, height)

class MediaDisplay(QFrame):
    def __init__(self, filters):
        super().__init__()
        self.filters = filters
        self.previews = []
        self.i = 0
        self.page_buttons = PageButtons(self, self.firstPage, self.prevPage, self.nextPage, self.lastPage)
        self.cur_page = 0
        self.total_pages = -1
        self.media_card = MediaCard(self)
        self.createUI()

    def setPages(self, total_pages):
        self.total_pages = total_pages

    def clear(self):
        for preview in self.previews:
            preview.setParent(None)
        self.previews = []


    def first_page_refresh(self):
        self.firstPage(refresh=True, inner_task=False)

    def getPage(self, page_num, inner_task=False):
        self.i = 0
        loop = asyncio.get_event_loop()
        order_by = self.filters.order_by()
        direction = self.filters.direction()
        if inner_task:
            loop.create_task(APIManager.getMedia(self.addMedia, self.spacers, self.setPages, page_num,order_by, direction == 'asc'))
        else:
            loop.run_until_complete(APIManager.getMedia(self.addMedia, self.spacers, self.setPages, page_num,order_by, direction == 'asc'))

    def spacers(self):
        for r in range(self.i, 6):
            spacer = QSpacerItem(240, 300)
            self.display.addItem(spacer, (r//3) * 3, (r%3)*5, 3, 4)


    def firstPage(self, refresh=False, inner_task=False):
        if self.cur_page ==0 and not refresh:
            return
    
        self.clear()
        self.cur_page = 0
        self.getPage(0, inner_task)

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
        # self.setStyleSheet('''border:2px solid black; background-color:#c8b7a6''')
        self.setStyleSheet('''border:2px solid black; background-color:#F2F3F4''')
    
    def addMedia(self, media):
        media_id = media["mediaId"]
        title = media["title"]
        medium = media["medium"]
        rating = media["rating"]
        bookmark = media["bookmark"]
        notes = media["notes"]
        imgBytes = media["imgBytes"]
        ext = media["imgExtension"][1:]

        media_preview = MediaPreview(title, medium, bookmark, rating, notes, imgBytes, ext, self.media_card, media_id)
        self.previews.append(media_preview)
        self.display.addWidget(media_preview, (self.i//3) * 3, (self.i%3)*5, 3, 4)
        self.i +=1




class MediaForm(QGroupBox):
    def __init__(self, media_display, heading, btn_name, callback, post=True):
        super().__init__(heading)
        self.post = post
        self.new_image= False
        self.callback = callback
        self.filenames = []
        self.btn_name = btn_name
        self.media_display = media_display
        self.media_id = None
        self.img = None
        self.ext = None
        self.createUI()
    
    def get_img(self):
        return self.img
    
    def set_img(self, img):
        self.img = img

    def set_media_id(self, media_id):
        self.media_id = media_id

    def set_ext(self, ext):
        self.ext = ext
    
    def get_file_name(self):
        return self.filenames[0]

    def has_new_file(self):
        return self.new_image

    def reset_new_image(self):
        self.new_image = False

    def setTitle(self, title):
        self.title_input.setText(title)

    def setMedium(self, medium):
        if medium == "ANIME":
            self.medium_input.setCurrentIndex(1)
        else:
            self.medium_input.setCurrentIndex(0)
        pass

    def setRating(self, rating):
        self.rating_input.setText(str(rating))

    def setBookmark(self, bookmark):
        self.bm_input.setText(str(bookmark))

    def setNotes(self, notes):
        self.notes_input.setPlainText(notes)
    
    def createUI(self):

        self.dlg = QFileDialog()
        self.dlg.setFileMode(QFileDialog.AnyFile)
        # self.dlg.setFilter()

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''background-color:#F2F3F4; color:black; border:2px solid black;border-radius:7px;''')
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(5, 25, 5, 5)
        
        self.layout.setVerticalSpacing(10)
        self.layout.setLabelAlignment(Qt.AlignLeft)
        
        self.title_input = QLineEdit()
        self.title_heading = QLabel("Title:")
        self.title_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
        self.title_heading.setStyleSheet('''border:none''')


        self.medium_input = QComboBox()
        self.medium_input.addItems(["MANGA", "ANIME"])
        width = self.medium_input.minimumSizeHint().width();
        self.medium_input.setMinimumWidth(width)
        self.medium_heading = QLabel("Medium:")
        self.medium_heading.setStyleSheet('''border:none''')
        self.medium_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')


        self.bm_input = QLineEdit()
        self.bm_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
        self.bm_heading = QLabel("Bookmark(ep/chp):")
        self.bm_heading.setStyleSheet('''border:none''')


        self.rating_input = QLineEdit()
        self.rating_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
        self.rating_heading = QLabel("Rating:")
        self.rating_heading.setStyleSheet('''border:none''')


        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
        self.notes_heading = QLabel("Notes")
        self.notes_heading.setStyleSheet('''border:none''')

        self.open_file = QPushButton("Select Image")
        self.file_name = QLabel("None")
        self.open_file.clicked.connect(self.get_image_file)
        self.open_file.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')
        self.file_name.setStyleSheet('''border:none''')

        self.layout.addRow(self.title_heading, self.title_input)
        self.layout.addRow(self.medium_heading, self.medium_input)
        self.layout.addRow(self.bm_heading, self.bm_input)
        self.layout.addRow(self.rating_heading, self.rating_input)
        self.layout.addRow(self.notes_heading, self.notes_input)
        self.layout.addRow(self.open_file)

        self.submit_btn = QPushButton(self.btn_name)
        if self.post:
            self.submit_btn.clicked.connect(self.submit_form)
        else:
            self.submit_btn.clicked.connect(self.put_form)
        self.submit_btn.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')

        self.layout.addRow(self.submit_btn)

    def get_image_file(self):
        if self.dlg.exec_():
            self.filenames = self.dlg.selectedFiles()
            self.new_image = True
        
    
    def submit_form(self):
        title = self.title_input.text()
        medium = self.medium_input.currentText()
        bookmark = self.bm_input.text()
        rating = self.rating_input.text()
        notes = self.notes_input.toPlainText()
        file_name = self.filenames[0] if len(self.filenames)>0 else None
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.postMedia(self.callback, title, medium, bookmark, rating, notes, file_name))

    def put_form(self):
        title = self.title_input.text()
        medium = self.medium_input.currentText()
        bookmark = self.bm_input.text()
        rating = self.rating_input.text()
        notes = self.notes_input.toPlainText()


        if self.new_image:
            temp = APIManager.process_image(self.get_file_name())
            self.set_img(temp[1])
            self.set_ext(temp[2])
            self.new_image = False
        
        img_bytes = self.img
        ext = self.ext

        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.putMedia(self.callback,self.media_id, title, medium, bookmark, rating, notes, img_bytes, ext))

        


class MediaControl(QGroupBox):
    def __init__(self):
        super().__init__("Filters")
        self.createUI()
    
    def createUI(self):
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''background-color:#F2F3F4; color:black; border:2px solid black;border-radius:7px;''')
        self.layout = QFormLayout(self)
        self.layout.setContentsMargins(5, 25, 5, 5)
        
        self.layout.setVerticalSpacing(10)
        self.layout.setLabelAlignment(Qt.AlignLeft)
        

        self.sort_input = QComboBox()
        self.sort_input.addItems(["Title", "Rating", "Medium", "Last Updated"])
        width = self.sort_input.minimumSizeHint().width()
        self.sort_input.setMinimumWidth(width)
        self.sort_heading = QLabel("Sort:")
        self.sort_heading.setStyleSheet('''border:none''')
        self.sort_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')

        self.dir_heading = QLabel("Direction:")
        self.dir_heading.setStyleSheet('''border:none''')
        self.dir_input = QComboBox()
        self.dir_input.addItems(["Asc", "Desc"])
        width = self.dir_input.minimumSizeHint().width()
        self.dir_input.setMinimumWidth(width)
        self.dir_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')

        self.search_heading=QLabel("Keyword:")
        self.search_heading.setStyleSheet('''border:none''')
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')

        self.filter_btn = QPushButton("Filter")
        self.filter_btn.setFixedWidth(100)
        self.filter_btn.setStyleSheet('''background-color:#555555;border-radius:7px; color:white''')

        self.layout.addRow(self.sort_heading, self.sort_input)
        self.layout.addRow(self.dir_heading, self.dir_input)
        self.layout.addRow(self.search_heading, self.search_input)
        self.layout.addRow("", self.filter_btn)



    def set_btn_action(self, action):
        self.filter_btn.clicked.connect(action)

    def order_by(self):
        orderBy = self.sort_input.currentText().lower()
        if orderBy == "last updated":
            orderBy = "lastModified"
        return orderBy
    def direction(self):
        return self.dir_input.currentText().lower()



class MediaCard(QStackedWidget):
    def __init__(self, media_display):
        super().__init__()
        self.media_display = media_display
        self.popup = QMessageBox()
        self.setUp()


    def setMedia(self, title, medium, bookmark, rating, notes, img, ext, media_id):
        self.media_id = media_id
        self.img = img
        self.ext = ext

        img_cont = QPixmap()
        img_cont.loadFromData(base64.b64decode(img))
        img_cont = img_cont.scaled(390, 570)

        self.img_label.setPixmap(img_cont)
        self.form.setTitle(title)
        self.form.setMedium(medium)
        self.form.setBookmark(bookmark)
        self.form.setRating(rating)
        self.form.setNotes(notes)
        self.form.set_media_id(self.media_id)
        self.form.set_ext(self.ext)
        self.form.set_img(img)

        self.show()

    def deleted(self, status):
        if(status == "SUCCESS"):
            self.popup.setText("Deleted")
            self.media_display.firstPage(True, True)
            self.close()
            self.popup.exec()
        else:
            self.popup.setText("Failed to delete")
            self.popup.exec()

    def tryDeleting(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(APIManager.deleteMedia(self.deleted, self.media_id))

    def update_media(self, updated):
        if not updated:
            return
        img_cont = QPixmap()
        img_cont.loadFromData(base64.b64decode(self.form.get_img()))
        img_cont = img_cont.scaled(390, 570)

        self.img_label.setPixmap(img_cont)
        self.media_display.firstPage(refresh=True, inner_task=True)
        
    
    
    def setUp(self):
        self.setStyleSheet('''background-color:#e7dfdd''')
        self.setFixedWidth(780)
        self.view_widget = QFrame()
        self.view_container = QHBoxLayout(self.view_widget)
        

        self.image_cont = QFrame()
        self.image_cont_layout = QVBoxLayout(self.image_cont)

        self.view_widget.setFixedHeight(610)

        self.img_label = QLabel()
        self.img_label.setStyleSheet('''border:2px solid black;border-radius:7px''')
        self.img_label.setFixedHeight(500)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet('''background-color:#555555;border-radius:7px''')
        self.delete_btn.clicked.connect(self.tryDeleting)
        self.image_cont_layout.addWidget(self.img_label)
        self.image_cont_layout.addWidget(self.delete_btn)


        self.form = MediaForm(self.media_display, "Update Media", "Update", self.update_media, post=False)

        self.view_container.addWidget(self.image_cont)
        self.view_container.addWidget(self.form)
        self.addWidget(self.view_widget)


