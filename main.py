import requests
import pygame_canvas as c
from datetime import datetime
import pytz
import webbrowser
import threading as t
import json as js

build = "1.2.0b"
settings = []
with open("data/settings.json", "r") as f:
    settings = js.load(f)
json = {}
request_filtering = 0

class color:
    dark = (20,20,30)
    darker = (16,16,24)
    medium = (30,30,45)
    light = (40,40,60)
    lighter = (50,50,77)
    lightest = (60,60,90)
    white = (255,255,255)
    black = (0,0,0)
    grey = (100,100,100)
    yellow = (255,255,0)
    orange = (255,150,0)
    red = (255,0,0)

def date():
    current_time = datetime.now(pytz.timezone('America/New_York'))
    
    month = current_time.month
    day = current_time.day
    hour = current_time.hour
    minute = current_time.minute
    
    time_string = f"{month:02d}{day:02d}{hour:02d}{minute:02d}"
    
    return int(time_string)

def get_weekly_json():
    global json, request_filtering
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    response = requests.get(url)
    response = requests.get(url)
    print(f"Trying")
    if response.status_code == 429:
        with open("data/cached.json", "r") as f:
            json = js.load(f)
        print("Reading from cache")
    elif response.status_code == 200:
        json_data = response.json()
        with open("data/cached.json", "w") as f:
            js.dump(json_data, f)
        print("Reading from url, caching")
        json = json_data
    request_filtering = 1

def get_json():
    thread = t.Thread(target=get_weekly_json)
    thread.start()

c.window(1150,600, f"My Forex News - {build}", can_resize=1, smallest_window_sizes=(1150,600), icon="data/icon.png")

tg = 0
scroll = 0
BAR_SIZE = 60
MARGINY = 30
MARGINX = 50
GAP = 20
SIZE_X = 700
SIZE_Y = 60
WIDTH, HEIGHT = c.screen_size()
SMOOTH = 15
REACTIVITY = 75
MENU_X = 400
SHOW_FPS = 0

get_json()
weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
buttons = []
data = []
font = c.pygame.Font(None, 25)

sounds = c.sprite([c.rectangle(MENU_X, HEIGHT, color.darker)], (WIDTH - MENU_X//2,HEIGHT//2),sounds=("data/select.wav",), top_left=0)
author = c.sprite(["data/author.png",], (0,0), scale=26, top_left=0)
author_name = c.sprite([c.get_text_surface("Dev: @gioseaxmc",color=color.white)], (WIDTH - MARGINX*3, HEIGHT - MARGINX + 2), top_left=0)
bar = c.sprite([c.rectangle(WIDTH, BAR_SIZE, color.lighter)], (WIDTH//2,BAR_SIZE//2), top_left=0)
title = c.sprite([c.get_text_surface("My Forex News",30 ,color=color.white)], (WIDTH//2,BAR_SIZE//2), top_left=0)

class news:
    def __init__(self, data, id) -> None:
        self.id = id
        self.jsondate = data["date"]
        self.name = data["title"]
        self.country = data["country"]
        self.impact = data["impact"]
        self.previous = data["previous"]
        self.forecast = data["forecast"]
        self.date = data["date"][:10]
        self.time = data["date"][11:16]
        self.background = c.sprite((c.rectangle(SIZE_X, SIZE_Y, (color.light)),), top_left=0)
        self.title = c.sprite((c.get_text_surface(self.name, color=color.white),), top_left=0)
        self.props = c.sprite((c.get_text_surface(f"{self.country}                   {self.date}      {self.time}", color=color.white),), top_left=0)
        if self.impact == "Low":
            self.color = c.sprite((c.rectangle(10, SIZE_Y, (color.yellow)),), top_left=0)
        elif self.impact == "Medium":
            self.color = c.sprite((c.rectangle(10, SIZE_Y, (color.orange)),), top_left=0)
        elif self.impact == "High":
            self.color = c.sprite((c.rectangle(10, SIZE_Y, (color.red)),), top_left=0)
        elif self.impact == "Holiday":
            self.color = c.sprite((c.rectangle(10, SIZE_Y, (color.grey)),), top_left=0)
        else:
            self.color = c.sprite((c.rectangle(10, SIZE_Y, (color.lightest)),), top_left=0)
        self.oldCond = 0

        self.position = 0,0

    def get_date(self):
        return int(f"{self.date[5:7]}{self.date[8:10]}{self.time[0:2]}{self.time[3:5]}")
    
    def get_day(self):
        try:
            return int(self.date[8:10])
        except ValueError:
            return 999999

    def draw(self,):
        cond = self.background.touching_mouse()
        self.position = (WIDTH - MENU_X)//2 + (cond)*REACTIVITY, MARGINY + BAR_SIZE + SIZE_Y//2 + self.id*(SIZE_Y + GAP) + scroll
        self.background.brightness = 200 + 55*cond
        self.background.slide_to(SMOOTH,self.position)
        hiding = not min(HEIGHT + SIZE_X//2, max(SIZE_X//-2, self.background.get_position()[1])) == self.background.get_position()[1]
        self.background.hide = hiding
        self.color.hide = hiding
        self.title.hide = hiding
        self.props.hide = hiding
        x = self.title.get_sizes()[0]
        self.title.slide_to(SMOOTH,self.position[0] +20 - SIZE_X//2 + x//2, self.position[1])
        self.props.slide_to(SMOOTH,self.position[0] +527 - SIZE_X//2, self.position[1])
        self.color.slide_to(SMOOTH,self.position[0] + 5 - SIZE_X//2, self.position[1])
        if not hiding:
            if cond:
                c.debug_list("","Previous:",self.previous,"Forecast",self.forecast,
                            position=c.mouse_position(),
                            font = font)
                if not self.oldCond:
                    sounds.play_sound("data/select.wav")
            self.oldCond = cond

    def delete(self):
        self.background.kill()
        self.color.kill()
        self.title.kill()
        self.props.kill()

class switch:
    def __init__(self, text, desc, index) -> None:
        self.index = index
        self.pos = (WIDTH - MENU_X + MARGINX, MARGINY + self.index*(GAP+20))
        self.desc = desc
        self.value: bool = 0
        self.button = c.sprite(("data/switch.png",),self.pos, scale=75, top_left=0)
        self.text = c.sprite((c.get_text_surface(text, color=color.white),), top_left=0)
        self.x , self.y = self.text.get_sizes()
        self.text.set_position(self.x//2 + self.pos[0] + 30, self.pos[1])
        self.button.brightness = 180 + 75*self.value
        self.button.set_direction(180 * self.value)
        self.button.set_position(self.pos)

    def change_texture(self):
        self.button.brightness = 180 + 75*self.value
        self.button.set_direction(180 * self.value)

    def flick(self):
        self.value = not self.value
        self.change_texture()
        self.button.update()
        settings[buttons.index(self)] = self.value
        with open("data/settings.json", "w") as f:
            js.dump(settings, f)
        print(settings)

    def update(self):
        if self.button.touching_mouse() or self.text.touching_mouse():
            c.debug_list("",self.desc,
                         position=c.mouse_position(),
                         font = font)
        if c.is_updating_sizes():
            self.pos = (WIDTH - MENU_X + MARGINX, BAR_SIZE + MARGINY + self.button.get_sizes()[1]//2 + self.index*(GAP+20))
            self.text.set_position(self.x//2 + self.pos[0] + 30, self.pos[1])
            self.button.brightness = 180 + 75*self.value
            self.button.set_direction(180 * self.value)
            self.button.set_position(self.pos)

def load_buttons():
    buttons.clear()
    button_names = ("Show old news","Show only today's news", "Filter out yellow news", "Filter out orange news", "Only show USD and EUR news", "Show only most volatile news")
    button_descs = ("Also show already played out news.","", "", "", "", "Show the most aggressive news")
    for index, button in enumerate(button_names):
        buttons.append(switch(button,button_descs[index],index))
    if settings:
        for index, button in enumerate(buttons):
            button.value = settings[index]
            button.change_texture()
    else:
        for button in buttons:
            settings.append(button.value)
load_buttons()

def filter_news():
    global SMOOTH; SMOOTH = 1
    global scroll; scroll = 0
    global data
    for i in data:
        i.delete()
    data = []
    added = 0
    for _, item in enumerate(json):
        temp = news(item, 0)
        condition = temp.get_date() >= date()


        if buttons[0].value:
            condition = condition or 1
        if buttons[1].value:
            condition = condition and temp.get_day() == datetime.now().day
        if buttons[2].value:
            condition = condition and not temp.impact == "Low"
        if buttons[3].value:
            condition = condition and not temp.impact == "Medium"
        if buttons[4].value:
            condition = condition and temp.country in ("EUR", "USD")
        if buttons[5].value:
            string = temp.name
            substrings = ["cpi", "fomc", "powell", "chair", "employment", "payroll", "earnings"]
            condition = condition and any(sub in string.lower() for sub in substrings)
            condition = condition and not temp.impact == "Low"
        if condition:
            if (data and temp.get_day() > data[-1].get_day()) or not data:
                data.append(news({"title": f"||======================================||                     {temp.date}  -  {weekdays[datetime.strptime(temp.date, '%Y-%m-%d').weekday()]}", "country": "", "date":"", "impact": "", "forecast": "", "previous": ""}, added))
                added += 1
            temp.id = added
            added += 1
            data.append(temp)
        else:
            temp.delete()
    for item in data:
        item.draw()
    SMOOTH = 15
    bar.set_depth(0)
    title.set_depth(0)
filter_news()

def update_display():
    global SMOOTH; SMOOTH = 15
    global WIDTH, HEIGHT; WIDTH, HEIGHT = c.screen_size()
    if c.is_updating_sizes():
        SMOOTH = 1
    for d in data:
        d.draw()
    for button in buttons:
        button.update()
        if button.button.clicked():
            button.flick()
    if c.is_updating_sizes():
            sounds.sprite_images[0] = c.rectangle(MENU_X, HEIGHT, color.darker)
            sounds.set_position(WIDTH - MENU_X//2,HEIGHT//2)
            sounds.update(1)
            author.set_position(WIDTH - MARGINX,HEIGHT - MARGINX)
            author_name.set_position(WIDTH - MARGINX*3, HEIGHT - MARGINX + 2)
            bar.sprite_images[0] = c.rectangle(WIDTH, BAR_SIZE, color.lighter)
            bar.set_position(WIDTH//2,BAR_SIZE//2)
            bar.update(1)
            title.set_position(WIDTH//2,BAR_SIZE//2)
            title.update(1)
update_display()

while c.loop(60, color.dark):
    if c.keys_clicked("r", c.pygame.K_F5) or request_filtering:
        filter_news()
        request_filtering = 0

    scroll += (c.get_wheel())*(SIZE_Y+GAP)*2
    scroll += (c.key_clicked(c.pygame.K_UP) - c.key_clicked(c.pygame.K_DOWN))*(SIZE_Y+GAP)
    if data:
        scroll = min(max(scroll, -(MARGINY + SIZE_Y//2 + data[-1].id*(SIZE_Y + GAP) - HEIGHT + SIZE_Y*3)), 0)
    else:
        scroll = 0

    if author.clicked():
        webbrowser.open_new_tab("https://x.com/gioseaxmc")
    author.set_scale(26 + 3*author.touching_mouse())

    update_display()

    SHOW_FPS = c.flick(c.keys_clicked(c.pygame.K_F3, "f"), SHOW_FPS)[0]
    if SHOW_FPS:
        c.debug_list(f"build ver: {build}",
                     f"fps: {c.get_FPS()}",
                     f"loaded news: {len(data)}",
                     f"performance: {round(c.get_FPS()/60*100, 1)}%",
                     f"mouse position: {c.mouse_position()}",
                     " - ",
                     "Press F or F3 to close this debug menu",
                     font = font)
