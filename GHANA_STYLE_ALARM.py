#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import threading
import time
import pygame
import json
import os
import math
from typing import Dict, List, Optional

class GhanaStyleAlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Alarm Clock - Ghana Style")
        self.root.geometry("1200x800")#"widthxheight+x_offset+y_offset"
        self.root.configure(bg='#191414')  # Ghana dark background
        
        # Ghana color scheme
        self.colors = {
            'bg_primary': '#191414',
            'bg_secondary': '#121212', 
            'bg_tertiary': '#282828',
            'accent': '#1DB954',  # Ghana green
            'text_primary': '#FFFFFF',
            'text_secondary': '#B3B3B3',
            'hover': '#383838',
            'card': '#181818',
            'card_hover': '#212121',
            'danger': '#E22134',
            'warning': '#F59E0B',
            'success': '#10B981',
            'border': '#404040'
        }
        
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # Data storage
        self.alarms: List[Dict] = []
        self.alarm_file = "alarms.json"
        self.current_time = datetime.datetime.now()
        self.running = True
        
        # Timer variables
        self.countdown_time = 0
        self.total_countdown_time = 0
        self.timer_running = False
        self.timer_sound_path = ""
        
        # Volume variable (needed for alarm sound)
        self.volume_var = tk.DoubleVar(value=0.7)
        
        # Add some Black Sheriff songs (local paths - you'll need to add actual files)
        self.black_sheriff_songs = [
            {"title": "Kwaku The Traveller", "path": "assets/sounds/kwaku_the_traveller.mp3"},
            {"title": "Second Sermon", "path": "assets/sounds/second_sermon.mp3"},
            {"title": "Destiny", "path": "assets/sounds/destiny.mp3"},
            {"title": "Oil In My Head", "path": "assets/sounds/oil_in_my_head.mp3"},
            {"title": "Soja", "path": "assets/sounds/soja.mp3"}
        ]
        
        # Load saved alarms
        self.load_alarms()
        
        # Create assets directory
        os.makedirs("assets/sounds", exist_ok=True)#we will make a directory to store our pre existing  sounds if that directory does not exist
        
        # Apply custom styles
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Start time update thread
        self.time_thread = threading.Thread(target=self.update_time, daemon=True)
        self.time_thread.start()
        
        # Start alarm checker thread
        self.alarm_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.alarm_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Ghana.TNotebook', #We created a custom style for notebook. TNotebook-> ttk.Notebook .Ghana is just a prefix
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Ghana.TNotebook.Tab',# these are the default styles for tabs
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_secondary'],
                       padding=[20, 10],
                       borderwidth=0)
        
        style.map('Ghana.TNotebook.Tab',# these are the styles when the tab is selected or hovered
                 background=[('selected', self.colors['bg_secondary']),
                            ('active', self.colors['hover'])],
                 foreground=[('selected', self.colors['text_primary']),
                            ('active', self.colors['text_primary'])])

        '''
            In Tkinter, a Notebook is a tabbed widget (like the tabs you see in a browser or settings dialog).
            It allows you to organize your app into multiple pages (tabs) inside a single window.
            Each tab holds its own frame, and you can add widgets to those frames.
        '''
        
        # Enhanced Combobox style
        style.configure('Professional.TCombobox', #Has Professional prefix to distinguish from default ttk.Combobox but it is still creating a combobox
                       selectbackground=self.colors['accent'],
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       insertcolor=self.colors['text_primary'],
                       arrowcolor=self.colors['text_secondary'],
                       focuscolor='none')
        
        style.map('Professional.TCombobox',
                 fieldbackground=[('readonly', self.colors['bg_tertiary']),
                                ('focus', self.colors['hover'])],
                 background=[('readonly', self.colors['bg_tertiary']),
                           ('active', self.colors['hover'])],
                 bordercolor=[('focus', self.colors['accent']),
                            ('!focus', self.colors['border'])],
                 arrowcolor=[('active', self.colors['accent'])])

    '''
        A Combobox is a ttk widget in Tkinter that combines:
        An entry box (where the user can type text), and
        A drop-down list (where the user can pick from predefined options).
    '''

    def create_widgets(self):#skv
        # Create main sidebar and content area (Ghana layout)
        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):
        # Left sidebar - increased width
        self.sidebar = tk.Frame(self.root, bg=self.colors['bg_secondary'], width=280)  #Creating a sidebar with width of 280 pixels within the main window
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        #.pack() arranges widgets relative to each other
        #tk.LEFT stick the sidebar to the left side of the window
        #tk.Y makes the sidebar fill the entire height of the window

        self.sidebar.pack_propagate(False)#turning sidebar auto resizing behavior to fit the children as the screen shrinks or increase.We want to use a constant or permanent width and height .
        
        # Logo/Title
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'], height=80) #creating a logo frame within the sidebar with height of 80 pixels
        logo_frame.pack(fill=tk.X, padx=20, pady=20)#we want the logo frame to fill the entire width of the sidebar and added 30px of space left and right of the logo
        logo_frame.pack_propagate(False)#prevent the logo frame from resizing to fit its children
        
        #style the logo text
        tk.Label(logo_frame, text="🎵", font=('Poppins', 32), 
                fg=self.colors['accent'], bg=self.colors['bg_secondary']).pack(side=tk.LEFT)
        tk.Label(logo_frame, text="AlarmClock", font=('Poppins', 18, 'bold'), 
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=10)
        
        # Navigation
        nav_frame = tk.Frame(self.sidebar, bg=self.colors['bg_secondary'])#creating a navigation frame within the sidebar
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=20)#fill the entire width and height of the sidebar
        
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Home", "home"),
            ("⏰ Set Alarm", "alarm"),
            ("📋 Active Alarms", "active"),
            ("⏲️ Countdown", "countdown")  # Changed from Settings to Countdown
        ]
        
        for text, key in nav_items:#creating buttons for each navigation item and styling it
            btn = tk.Button(nav_frame, text=text, font=('Poppins', 12, 'bold'),
                          bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                          bd=0, pady=15, anchor='w', relief=tk.FLAT,
                          activebackground=self.colors['hover'],
                          activeforeground=self.colors['text_primary'],
                          command=lambda k=key: self.switch_view(k))#when button is clicked, call switch_view with the corresponding key
            btn.pack(fill=tk.X, pady=2)#button should fill the entire width of the navigation frame
            self.nav_buttons[key] = btn #store the button in a dictionary for later access

    def create_main_content(self):
        # Main content area
        self.main_content = tk.Frame(self.root, bg=self.colors['bg_primary'])#creating the main content but this time we don't specify width because it will take the remaining space
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)#fill the entire height and width of the remaining space in the window
        
        # Create different views
        self.views = {}
        self.create_home_view()
        self.create_alarm_view()
        self.create_active_alarms_view()
        self.create_countdown_view()  # Changed from settings to countdown
        
        # Show home view by default
        self.switch_view("home")

    def create_home_view(self):
        """Create a simplified home view with centered clock only"""
        self.views["home"] = tk.Frame(self.main_content, bg=self.colors['bg_primary'])#we create a copy of the main content frame but this time we will add widgets to it
        
        # Main container to center everything
        main_container = tk.Frame(self.views["home"], bg=self.colors['bg_primary'])#applying the copy we have created to a main container
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Clock container - centered
        clock_container = tk.Frame(main_container, bg=self.colors['bg_primary'])
        clock_container.pack(expand=True)
        
        # Current time display (very large and prominent)
        self.current_time_label = tk.Label(clock_container, text="", 
                                          font=('Poppins', 72, 'bold'), 
                                          fg=self.colors['text_primary'], 
                                          bg=self.colors['bg_primary'])
        self.current_time_label.pack()
        
        # Current date display
        self.current_date_label = tk.Label(clock_container, text="", 
                                          font=('Poppins', 20), 
                                          fg=self.colors['text_secondary'], 
                                          bg=self.colors['bg_primary'])
        self.current_date_label.pack(pady=(15, 40))
        
        # Optional: Add alarm count display
        self.alarm_count_label = tk.Label(clock_container, text="", 
                                         font=('Poppins', 14), 
                                         fg=self.colors['text_secondary'], 
                                         bg=self.colors['bg_primary'])
        self.alarm_count_label.pack(pady=(20, 0))#skv

    def create_stat_card(self, parent, title, value, icon):
        card = tk.Frame(parent, bg=self.colors['card'], relief=tk.FLAT, bd=1)
        card.pack(side=tk.LEFT, padx=10, pady=10, ipadx=20, ipady=15)
        
        tk.Label(card, text=icon, font=('Poppins', 24), 
                fg=self.colors['accent'], bg=self.colors['card']).pack()
        tk.Label(card, text=value, font=('Poppins', 20, 'bold'), 
                fg=self.colors['text_primary'], bg=self.colors['card']).pack()
        tk.Label(card, text=title, font=('Poppins', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()

    def create_modern_toggle(self, parent, text, variable, row, col):
        """Create a modern toggle button for day selection"""
        container = tk.Frame(parent, bg=self.colors['card'])
        container.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
        
        # Create the toggle button
        toggle_frame = tk.Frame(container, bg=self.colors['bg_tertiary'], 
                               relief=tk.FLAT, bd=0, padx=15, pady=12)
        toggle_frame.pack(fill=tk.X)
        
        # Day label
        day_label = tk.Label(toggle_frame, text=text, 
                           font=('Poppins', 11, 'bold'),
                           bg=self.colors['bg_tertiary'], 
                           fg=self.colors['text_secondary'])
        day_label.pack(side=tk.LEFT)
        
        # Toggle indicator
        toggle_indicator = tk.Label(toggle_frame, text="○", 
                                  font=('Poppins', 16),
                                  bg=self.colors['bg_tertiary'], 
                                  fg=self.colors['text_secondary'])
        toggle_indicator.pack(side=tk.RIGHT)
        
        def toggle_day():
            current_state = variable.get()
            variable.set(not current_state)
            update_appearance()
        
        def update_appearance():
            if variable.get():
                toggle_frame.config(bg=self.colors['accent'])
                day_label.config(bg=self.colors['accent'], fg=self.colors['text_primary'])
                toggle_indicator.config(bg=self.colors['accent'], fg=self.colors['text_primary'], text="●")
            else:
                toggle_frame.config(bg=self.colors['bg_tertiary'])
                day_label.config(bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'])
                toggle_indicator.config(bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'], text="○")
        
        def on_enter(event):
            if not variable.get():
                toggle_frame.config(bg=self.colors['hover'])
                day_label.config(bg=self.colors['hover'], fg=self.colors['text_primary'])
                toggle_indicator.config(bg=self.colors['hover'], fg=self.colors['text_primary'])
        
        def on_leave(event):
            update_appearance()
        
        # Bind events to all components
        for widget in [toggle_frame, day_label, toggle_indicator]:
            widget.bind("<Button-1>", lambda e: toggle_day())
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        # Initial appearance
        update_appearance()
        
        return container

    def create_professional_spinbox(self, parent, textvariable, from_, to, label_text, width=80):
        """Create a professional-looking spinbox with custom buttons"""
        container = tk.Frame(parent, bg=self.colors['card'])
        
        # Label
        if label_text:
            tk.Label(container, text=label_text, font=('Poppins', 10, 'bold'), 
                    fg=self.colors['text_secondary'], bg=self.colors['card']).pack(pady=(0, 8))
        
        # Spinbox container
        spinbox_container = tk.Frame(container, bg=self.colors['bg_tertiary'], 
                                   relief=tk.FLAT, bd=1, padx=2, pady=2)
        spinbox_container.pack()
        
        # Main frame for spinbox components
        main_frame = tk.Frame(spinbox_container, bg=self.colors['bg_tertiary'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Value display
        value_frame = tk.Frame(main_frame, bg=self.colors['bg_tertiary'], width=width, height=50)
        value_frame.pack(side=tk.LEFT, fill=tk.Y)
        value_frame.pack_propagate(False)
        
        value_label = tk.Label(value_frame, textvariable=textvariable,
                             font=('Poppins', 22, 'bold'), 
                             fg=self.colors['text_primary'], 
                             bg=self.colors['bg_tertiary'])
        value_label.pack(expand=True)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg_tertiary'], width=30)
        buttons_frame.pack(side=tk.RIGHT, fill=tk.Y)
        buttons_frame.pack_propagate(False)
        
        # Up button
        up_btn = tk.Button(buttons_frame, text="▲", 
                          font=('Poppins', 10, 'bold'),
                          bg=self.colors['hover'], 
                          fg=self.colors['text_secondary'],
                          bd=0, relief=tk.FLAT,
                          activebackground=self.colors['accent'],
                          activeforeground=self.colors['text_primary'],
                          command=lambda: self.increment_value(textvariable, to))
        up_btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 1))
        
        # Down button  
        down_btn = tk.Button(buttons_frame, text="▼", 
                           font=('Poppins', 10, 'bold'),
                           bg=self.colors['hover'], 
                           fg=self.colors['text_secondary'],
                           bd=0, relief=tk.FLAT,
                           activebackground=self.colors['accent'],
                           activeforeground=self.colors['text_primary'],
                           command=lambda: self.decrement_value(textvariable, from_))
        down_btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=(1, 2))
        
        # Hover effects
        def on_enter_container(event):
            spinbox_container.config(highlightbackground=self.colors['accent'], 
                                   highlightthickness=1)
        
        def on_leave_container(event):
            spinbox_container.config(highlightthickness=0)
        
        spinbox_container.bind("<Enter>", on_enter_container)
        spinbox_container.bind("<Leave>", on_leave_container)
        value_frame.bind("<Enter>", on_enter_container)
        value_frame.bind("<Leave>", on_leave_container)
        
        return container

    def increment_value(self, var, max_val):
        try:
            current = int(var.get())
            if current < max_val:
                var.set(f"{current + 1:02d}")
        except ValueError:
            var.set("00")

    def decrement_value(self, var, min_val):
        try:
            current = int(var.get())
            if current > min_val:
                var.set(f"{current - 1:02d}")
        except ValueError:
            var.set("00")

    def create_professional_dropdown(self, parent, textvariable, values, label_text):
        """Create a professional dropdown with enhanced styling"""
        container = tk.Frame(parent, bg=self.colors['card'])
        
        # Label
        tk.Label(container, text=label_text, 
                font=('Poppins', 14, 'bold'), 
                fg=self.colors['text_primary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(0, 10))
        
        # Dropdown container with border
        dropdown_container = tk.Frame(container, bg=self.colors['border'], 
                                    relief=tk.FLAT, bd=1, padx=1, pady=1)
        dropdown_container.pack(fill=tk.X, pady=5)
        
        # Inner container
        inner_container = tk.Frame(dropdown_container, bg=self.colors['bg_tertiary'])
        inner_container.pack(fill=tk.BOTH, expand=True)
        
        # Custom dropdown frame
        dropdown_frame = tk.Frame(inner_container, bg=self.colors['bg_tertiary'], padx=15, pady=12)
        dropdown_frame.pack(fill=tk.X)
        
        # Selected value display
        selected_frame = tk.Frame(dropdown_frame, bg=self.colors['bg_tertiary'])
        selected_frame.pack(fill=tk.X)
        
        # Icon and text
        icon_label = tk.Label(selected_frame, text="🎵", 
                            font=('Poppins', 16), 
                            fg=self.colors['accent'], 
                            bg=self.colors['bg_tertiary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        text_label = tk.Label(selected_frame, textvariable=textvariable,
                            font=('Poppins', 12, 'bold'), 
                            fg=self.colors['text_primary'], 
                            bg=self.colors['bg_tertiary'],
                            anchor='w')
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dropdown arrow
        arrow_label = tk.Label(selected_frame, text="▼", 
                             font=('Poppins', 10), 
                             fg=self.colors['text_secondary'], 
                             bg=self.colors['bg_tertiary'])
        arrow_label.pack(side=tk.RIGHT)
        
        # Create actual combobox (hidden)
        combo = ttk.Combobox(inner_container, textvariable=textvariable,
                           values=values, font=('Poppins', 12),
                           state="readonly", style='Professional.TCombobox')
        
        # Custom dropdown behavior
        def show_dropdown(event):
            combo.event_generate('<Button-1>')
            
        def on_selection_change(event):
            # Update icon based on selection
            selection = textvariable.get()
            if "Kwaku" in selection or "Second" in selection or "Destiny" in selection or "Oil" in selection or "Soja" in selection:
                icon_label.config(text="🎤", fg=self.colors['accent'])
            elif "Default" in selection:
                icon_label.config(text="🔔", fg=self.colors['warning'])
            elif "Custom" in selection:
                icon_label.config(text="📁", fg=self.colors['success'])
            else:
                icon_label.config(text="🎵", fg=self.colors['accent'])
        
        # Hover effects
        def on_enter(event):
            dropdown_container.config(bg=self.colors['accent'])
            dropdown_frame.config(bg=self.colors['hover'])
            selected_frame.config(bg=self.colors['hover'])
            for widget in [icon_label, text_label, arrow_label]:
                widget.config(bg=self.colors['hover'])
            arrow_label.config(fg=self.colors['accent'])
        
        def on_leave(event):
            dropdown_container.config(bg=self.colors['border'])
            dropdown_frame.config(bg=self.colors['bg_tertiary'])
            selected_frame.config(bg=self.colors['bg_tertiary'])
            for widget in [icon_label, text_label, arrow_label]:
                widget.config(bg=self.colors['bg_tertiary'])
            arrow_label.config(fg=self.colors['text_secondary'])
        
        # Bind events
        for widget in [dropdown_frame, selected_frame, icon_label, text_label, arrow_label]:
            widget.bind("<Button-1>", show_dropdown)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        combo.bind('<<ComboboxSelected>>', on_selection_change)
        
        # Position hidden combobox
        combo.place(x=-1000, y=-1000)
        
        # Initial icon update
        on_selection_change(None)
        
        return container

    def create_circular_timer(self, parent, size=200):
        """Create a circular timer widget like in the image"""
        container = tk.Frame(parent, bg=self.colors['card'])
        
        # Create canvas for circular timer
        canvas = tk.Canvas(container, width=size, height=size, 
                          bg=self.colors['card'], highlightthickness=0)
        canvas.pack(pady=20)
        
        # Store canvas reference
        self.timer_canvas = canvas
        self.timer_size = size
        
        # Draw initial circle
        self.draw_timer_circle()
        
        # Timer display
        self.timer_display = tk.Label(container, text="00:00", 
                                     font=('Poppins', 24, 'bold'), 
                                     fg=self.colors['text_primary'], 
                                     bg=self.colors['card'])
        self.timer_display.pack(pady=10)
        
        return container

    def draw_timer_circle(self):
        """Draw the circular timer progress"""
        if not hasattr(self, 'timer_canvas'):
            return
            
        canvas = self.timer_canvas
        size = self.timer_size
        canvas.delete("all")
        
        # Calculate center and radius
        center = size // 2
        radius = (size - 20) // 2
        
        # Draw background circle
        canvas.create_oval(center - radius, center - radius, 
                          center + radius, center + radius,
                          outline=self.colors['bg_tertiary'], width=6, fill="")
        
        # Calculate progress if timer is running
        if self.total_countdown_time > 0:
            progress = (self.total_countdown_time - self.countdown_time) / self.total_countdown_time
            
            # Draw progress arc (green color like in image)
            if progress > 0:
                # Convert to degrees (tkinter uses degrees, starting from 3 o'clock, going clockwise)
                extent = 360 * progress
                canvas.create_arc(center - radius, center - radius,
                                center + radius, center + radius,
                                start=90, extent=-extent, 
                                outline=self.colors['accent'], width=6,
                                style='arc')

    def create_alarm_view(self):
        self.views["alarm"] = tk.Frame(self.main_content, bg=self.colors['bg_primary'])
        
        # Header
        header = tk.Label(self.views["alarm"], text="Set New Alarm", 
                         font=('Poppins', 24, 'bold'), 
                         fg=self.colors['text_primary'], 
                         bg=self.colors['bg_primary'])
        header.pack(anchor='w', padx=30, pady=(30, 20))
        
        # Main form container
        form_container = tk.Frame(self.views["alarm"], bg=self.colors['bg_primary'])
        form_container.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Left side - Time and basic settings
        left_panel = tk.Frame(form_container, bg=self.colors['card'], padx=30, pady=30)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Time picker (large and prominent)
        time_label = tk.Label(left_panel, text="Set Time", 
                             font=('Poppins', 18, 'bold'), 
                             fg=self.colors['text_primary'], 
                             bg=self.colors['card'])
        time_label.pack(anchor='w', pady=(0, 20))
        
        time_frame = tk.Frame(left_panel, bg=self.colors['card'])
        time_frame.pack(fill=tk.X, pady=10)
        
        self.hour_var = tk.StringVar(value="07")
        self.minute_var = tk.StringVar(value="00")
        
        # Professional time input with custom spinboxes
        hour_container = self.create_professional_spinbox(time_frame, self.hour_var, 0, 23, "Hour")
        hour_container.pack(side=tk.LEFT, padx=(0, 15))
        
        # Colon separator
        colon_frame = tk.Frame(time_frame, bg=self.colors['card'])
        colon_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(colon_frame, text=":", font=('Poppins', 40, 'bold'), 
                fg=self.colors['accent'], bg=self.colors['card']).pack(pady=20)
        
        minute_container = self.create_professional_spinbox(time_frame, self.minute_var, 0, 59, "Minute")
        minute_container.pack(side=tk.LEFT, padx=(15, 0))
        
        # Alarm label
        label_section = tk.Frame(left_panel, bg=self.colors['card'])    
        label_section.pack(fill=tk.X, pady=(30, 0))
        
        tk.Label(label_section, text="Alarm Name", 
                font=('Poppins', 14, 'bold'), 
                fg=self.colors['text_primary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(0, 10))
        
        self.label_var = tk.StringVar(value="Wake Up")
        
        # Sleek entry field
        entry_frame = tk.Frame(label_section, bg=self.colors['border'], 
                              relief=tk.FLAT, bd=1, padx=1, pady=1)
        entry_frame.pack(fill=tk.X, pady=5)
        
        entry_inner = tk.Frame(entry_frame, bg=self.colors['bg_tertiary'])
        entry_inner.pack(fill=tk.BOTH, expand=True)
        
        label_entry = tk.Entry(entry_inner, textvariable=self.label_var, 
                              font=('Poppins', 14), bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'], bd=0, relief=tk.FLAT,
                              highlightthickness=0, insertbackground=self.colors['text_primary'])
        label_entry.pack(padx=15, pady=12, fill=tk.X)
        
        # Entry hover effects
        def on_entry_focus_in(event):
            entry_frame.config(bg=self.colors['accent'])
        
        def on_entry_focus_out(event):
            entry_frame.config(bg=self.colors['border'])
        
        label_entry.bind("<FocusIn>", on_entry_focus_in)
        label_entry.bind("<FocusOut>", on_entry_focus_out)
        
        # Right side - Days and sound settings
        right_panel = tk.Frame(form_container, bg=self.colors['card'], padx=30, pady=30)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Days selection with modern toggles
        days_label = tk.Label(right_panel, text="Repeat Days", 
                             font=('Poppins', 18, 'bold'), 
                             fg=self.colors['text_primary'], 
                             bg=self.colors['card'])
        days_label.pack(anchor='w', pady=(0, 20))
        
        self.day_vars = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        days_grid = tk.Frame(right_panel, bg=self.colors['card'])
        days_grid.pack(fill=tk.X, pady=10)
        
        # Create modern toggle buttons for days
        for i, day in enumerate(days):
            var = tk.BooleanVar()
            self.day_vars[day] = var
            
            self.create_modern_toggle(days_grid, day[:3], var, i//4, i%4)
        
        # Configure grid weights
        for i in range(4):
            days_grid.columnconfigure(i, weight=1)
        
        # Professional sound selection dropdown
        self.sound_var = tk.StringVar(value="Default Beep")
        sound_options = ["Default Beep"] + [song["title"] for song in self.black_sheriff_songs] + ["Custom Sound"]
        
        sound_dropdown = self.create_professional_dropdown(right_panel, self.sound_var, 
                                                         sound_options, "Alarm Sound")
        sound_dropdown.pack(fill=tk.X, pady=(30, 20))
        
        self.sound_path = ""
        browse_frame = tk.Frame(right_panel, bg=self.colors['card'])
        browse_frame.pack(fill=tk.X, pady=10)
        
        # Modern buttons
        browse_btn = tk.Button(browse_frame, text="📁 Browse Custom Sound",
                              command=self.browse_sound_file,
                              bg=self.colors['bg_tertiary'], 
                              fg=self.colors['text_primary'],
                              font=('Poppins', 12), bd=0, padx=20, pady=12,
                              relief=tk.FLAT, activebackground=self.colors['hover'])
        browse_btn.pack(fill=tk.X, pady=(0, 10))
        
        test_btn = tk.Button(browse_frame, text="🔊 Test Sound",
                            command=self.test_sound,
                            bg=self.colors['accent'], 
                            fg=self.colors['text_primary'],
                            font=('Poppins', 12, 'bold'), bd=0, padx=20, pady=12,
                            relief=tk.FLAT, activebackground='#1ed760')
        test_btn.pack(fill=tk.X)
        
        # Create alarm button
        create_frame = tk.Frame(self.views["alarm"], bg=self.colors['bg_primary'])
        create_frame.pack(fill=tk.X, padx=30, pady=30)
        
        create_btn = tk.Button(create_frame, text="✨ Create Alarm",
                              command=self.create_alarm,
                              bg=self.colors['accent'], 
                              fg=self.colors['text_primary'],
                              font=('Poppins', 16, 'bold'), bd=0, 
                              padx=40, pady=15, relief=tk.FLAT,
                              activebackground='#1ed760')
        create_btn.pack(anchor='center')

    def create_active_alarms_view(self):
        self.views["active"] = tk.Frame(self.main_content, bg=self.colors['bg_primary'])
        
        # Header
        header_frame = tk.Frame(self.views["active"], bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        tk.Label(header_frame, text="Active Alarms", 
                font=('Poppins', 24, 'bold'), 
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_primary']).pack(side=tk.LEFT)
        
        # Control buttons in header
        controls = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        controls.pack(side=tk.RIGHT)
        
        refresh_btn = tk.Button(controls, text="🔄 Refresh",
                               command=self.refresh_alarm_list,
                               bg=self.colors['bg_tertiary'], 
                               fg=self.colors['text_primary'],
                               font=('Poppins', 12), bd=0, padx=15, pady=8,
                               relief=tk.FLAT, activebackground=self.colors['hover'])
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Alarms container
        alarms_container = tk.Frame(self.views["active"], bg=self.colors['bg_primary'])
        alarms_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Scrollable frame for alarm cards
        canvas = tk.Canvas(alarms_container, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(alarms_container, orient="vertical", command=canvas.yview)
        self.alarm_cards_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        self.alarm_cards_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.alarm_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_countdown_view(self):
        """Create the countdown timer view with vertical alignment and sound options"""
        self.views["countdown"] = tk.Frame(self.main_content, bg=self.colors['bg_primary'])
        
        # Header
        header = tk.Label(self.views["countdown"], text="Countdown Timer", 
                         font=('Poppins', 24, 'bold'), 
                         fg=self.colors['text_primary'], 
                         bg=self.colors['bg_primary'])
        header.pack(anchor='w', padx=30, pady=(30, 20))
        
        # Main container - single column layout
        main_container = tk.Frame(self.views["countdown"], bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=20)
        
        # Timer display section (centered at top)
        timer_display_frame = tk.Frame(main_container, bg=self.colors['card'], padx=40, pady=30)
        timer_display_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Timer display (number only)
        self.timer_display = tk.Label(timer_display_frame, text="00:00", 
                                  font=('Poppins', 48, 'bold'), 
                                  fg=self.colors['text_primary'], 
                                  bg=self.colors['card'])
        self.timer_display.pack(pady=10)
        
        # Status label for timer
        self.timer_status_label = tk.Label(timer_display_frame, text="Ready to start", 
                                       font=('Poppins', 16), 
                                       fg=self.colors['text_secondary'], 
                                       bg=self.colors['card'])
        self.timer_status_label.pack(pady=(10, 0))
        
        # Controls section
        controls_frame = tk.Frame(main_container, bg=self.colors['card'], padx=40, pady=30)
        controls_frame.pack(fill=tk.X)
        
        # Time input section
        time_section = tk.Frame(controls_frame, bg=self.colors['card'])
        time_section.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(time_section, text="⏲️ Set Timer Duration", 
                font=('Poppins', 18, 'bold'), 
                fg=self.colors['text_primary'], 
                bg=self.colors['card']).pack(pady=(0, 20))
        
        # Time input controls (horizontal layout)
        time_input_frame = tk.Frame(time_section, bg=self.colors['card'])
        time_input_frame.pack()
        
        # Minutes input
        minutes_container = tk.Frame(time_input_frame, bg=self.colors['card'])
        minutes_container.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(minutes_container, text="Minutes", 
                font=('Poppins', 12, 'bold'), 
                fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(pady=(0, 8))
        
        self.timer_minutes_var = tk.StringVar(value="05")
        minutes_spinbox = self.create_professional_spinbox(minutes_container, self.timer_minutes_var, 0, 59, "")
        minutes_spinbox.pack()
        
        # Colon separator
        colon_frame = tk.Frame(time_input_frame, bg=self.colors['card'])
        colon_frame.pack(side=tk.LEFT, padx=15)
        
        tk.Label(colon_frame, text=":", font=('Poppins', 40, 'bold'), 
                fg=self.colors['accent'], bg=self.colors['card']).pack(pady=20)
        
        # Seconds input
        seconds_container = tk.Frame(time_input_frame, bg=self.colors['card'])
        seconds_container.pack(side=tk.LEFT, padx=(20, 0))
        
        tk.Label(seconds_container, text="Seconds", 
                font=('Poppins', 12, 'bold'), 
                fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(pady=(0, 8))
        
        self.timer_seconds_var = tk.StringVar(value="00")
        seconds_spinbox = self.create_professional_spinbox(seconds_container, self.timer_seconds_var, 0, 59, "")
        seconds_spinbox.pack()
        
        # Control buttons section - Replace "Ready to start" with Start and Stop buttons
        buttons_section = tk.Frame(controls_frame, bg=self.colors['card'])
        buttons_section.pack(fill=tk.X, pady=(20, 0))
        
        # Start button
        self.start_timer_btn = tk.Button(buttons_section, text="🚀 START TIMER",
                                        command=self.start_countdown_timer,
                                        bg=self.colors['accent'], 
                                        fg=self.colors['text_primary'],
                                        font=('Poppins', 18, 'bold'), bd=0, 
                                        padx=50, pady=20, relief=tk.FLAT,
                                        activebackground='#1ed760')
        self.start_timer_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        # Pause button
        self.pause_timer_btn = tk.Button(buttons_section, text="⏸️ PAUSE TIMER",
                                     command=self.pause_timer,
                                     bg=self.colors['warning'], 
                                     fg=self.colors['text_primary'],
                                     font=('Poppins', 18, 'bold'), bd=0, 
                                     padx=50, pady=20, relief=tk.FLAT,
                                     activebackground='#f59e0b')
        self.pause_timer_btn.pack(side=tk.LEFT, padx=(0, 20))
        self.pause_timer_btn.config(state='disabled')  # Initially disabled
    
        # Stop button
        self.stop_timer_btn = tk.Button(buttons_section, text="🛑 STOP TIMER",
                                       command=self.reset_timer,
                                       bg=self.colors['danger'], 
                                       fg=self.colors['text_primary'],
                                       font=('Poppins', 18, 'bold'), bd=0, 
                                       padx=50, pady=20, relief=tk.FLAT,
                                       activebackground='#c0392b')
        self.stop_timer_btn.pack(side=tk.LEFT)

    def browse_timer_sound(self):
        """Browse for custom timer sound"""
        file_path = filedialog.askopenfilename(
            title="Select Timer Sound File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg"), ("All Files", "*.*")]
        )
        if file_path:
            self.timer_sound_path = file_path
            self.timer_sound_var.set("Custom Sound")

    def test_timer_sound(self):
        """Test the selected timer sound"""
        try:
            pygame.mixer.music.set_volume(self.volume_var.get())
            sound_path = self.get_timer_sound_path(self.timer_sound_var.get())
            
            if sound_path and os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            else:
                self.create_beep_sound()
                pygame.mixer.music.play()
            
            messagebox.showinfo("Test", f"Playing timer sound: {self.timer_sound_var.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play timer sound: {str(e)}")

    def get_timer_sound_path(self, sound_name):
        """Get the file path for timer sound"""
        if sound_name == "Default Beep":
            return None
        elif sound_name == "Custom Sound":
            return self.timer_sound_path if hasattr(self, 'timer_sound_path') and self.timer_sound_path else None
        else:
            # Check if it's a Black Sheriff song
            for song in self.black_sheriff_songs:
                if song["title"] in sound_name:
                    return song["path"]
        return None

    def start_countdown_timer(self):
        """Start the countdown timer"""
        try:
            minutes = int(self.timer_minutes_var.get())
            seconds = int(self.timer_seconds_var.get())
            total_seconds = minutes * 60 + seconds
            
            if total_seconds <= 0:
                messagebox.showerror("Error", "Please set a valid duration")
                return
            
            self.countdown_time = total_seconds
            self.total_countdown_time = total_seconds
            self.timer_running = True
            
            # Update button states
            self.start_timer_btn.config(state='disabled', text="⏳ RUNNING...")
            self.pause_timer_btn.config(state='normal')
            self.timer_status_label.config(text="Timer Running", fg=self.colors['accent'])
            
            # Start countdown thread
            def countdown():
                while self.countdown_time > 0 and self.timer_running and self.running:
                    mins, secs = divmod(self.countdown_time, 60)
                    
                    # Update timer display
                    time_str = f"{mins:02d}:{secs:02d}"
                    self.timer_display.config(text=time_str)
                    
                    # Update circular progress
                    self.draw_timer_circle()
                    
                    time.sleep(1)
                    self.countdown_time -= 1
                
                # Timer finished
                if self.countdown_time <= 0 and self.timer_running and self.running:
                    self.timer_display.config(text="00:00")
                    self.timer_status_label.config(text="Time's Up!", fg=self.colors['danger'])
                    self.draw_timer_circle()
                    
                    # Play selected timer sound
                    sound_path = self.get_timer_sound_path(self.timer_sound_var.get())
                    self.play_alarm_sound(self.timer_sound_var.get(), sound_path or "")
                    
                    messagebox.showinfo("Timer", "Countdown timer finished!")
                    self.reset_timer()
            
            timer_thread = threading.Thread(target=countdown, daemon=True)
            timer_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def pause_timer(self):
        """Pause/Resume the timer"""
        if self.timer_running:
            self.timer_running = False
            self.pause_timer_btn.config(text="▶️ Resume")
            self.timer_status_label.config(text="Timer Paused", fg=self.colors['warning'])
        else:
            self.timer_running = True
            self.pause_timer_btn.config(text="⏸️ Pause")
            self.timer_status_label.config(text="Timer Running", fg=self.colors['accent'])
            # Resume the countdown thread without resetting the timer
            self.resume_countdown_timer()

    def reset_timer(self):
        """Reset the timer"""
        self.timer_running = False
        self.countdown_time = 0
        self.total_countdown_time = 0
        
        # Reset display
        self.timer_display.config(text="00:00")
        self.timer_status_label.config(text="Ready to start", fg=self.colors['text_secondary'])
        
        # Reset button states
        self.start_timer_btn.config(state='normal', text="🚀 START TIMER")
        self.pause_timer_btn.config(state='disabled', text="⏸️ Pause")
        
        # Clear circular timer
        self.draw_timer_circle()

    def resume_countdown_timer(self):
        """Resume the countdown timer from where it was paused."""
        def countdown():
            while self.countdown_time > 0 and self.timer_running and self.running:
                mins, secs = divmod(self.countdown_time, 60)
                
                # Update timer display
                time_str = f"{mins:02d}:{secs:02d}"
                self.timer_display.config(text=time_str)
                
                # Update circular progress
                self.draw_timer_circle()
                
                time.sleep(1)
                self.countdown_time -= 1
            
            # Timer finished
            if self.countdown_time <= 0 and self.timer_running and self.running:
                self.timer_display.config(text="00:00")
                self.timer_status_label.config(text="Time's Up!", fg=self.colors['danger'])
                self.draw_timer_circle()
                
                # Play selected timer sound
                sound_path = self.get_timer_sound_path(self.timer_sound_var.get())
                self.play_alarm_sound(self.timer_sound_var.get(), sound_path or "")
                
                messagebox.showinfo("Timer", "Countdown timer finished!")
                self.reset_timer()
        
        timer_thread = threading.Thread(target=countdown, daemon=True)
        timer_thread.start()

    def switch_view(self, view_name):
        # Hide all views
        for view in self.views.values():
            view.pack_forget()
        
        # Show selected view
        if view_name in self.views:
            self.views[view_name].pack(fill=tk.BOTH, expand=True)
        
        # Update navigation buttons
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.configure(bg=self.colors['hover'], fg=self.colors['text_primary'])
            else:
                btn.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
        
        # Refresh alarm list if switching to active alarms and update alarm count
        if view_name == "active":
            self.refresh_alarm_list()
        
        # Update alarm count on home view
        if view_name == "home":
            active_count = len([alarm for alarm in self.alarms if alarm['active']])
            self.alarm_count_label.config(text=f"{active_count} active alarm{'s' if active_count != 1 else ''}")

    def create_alarm_card(self, parent, alarm, index):
        """Create a professional alarm card with enhanced styling"""
        # Main card container with shadow effect
        card_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        card_container.pack(fill=tk.X, pady=8, padx=5)
        
        # Card with gradient-like effect using multiple frames
        card_shadow = tk.Frame(card_container, bg=self.colors['bg_secondary'], height=2)
        card_shadow.pack(fill=tk.X, pady=(0, 0))
        
        card = tk.Frame(card_container, bg=self.colors['card'], padx=25, pady=20, relief=tk.FLAT, bd=0)
        card.pack(fill=tk.X)
        
        # Status indicator bar
        status_color = self.colors['accent'] if alarm['active'] else self.colors['text_secondary']
        status_bar = tk.Frame(card, bg=status_color, height=3)
        status_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Main content frame
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.X)
        
        # Left side - Time and details
        left_frame = tk.Frame(content_frame, bg=self.colors['card'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Time display
        time_frame = tk.Frame(left_frame, bg=self.colors['card'])
        time_frame.pack(fill=tk.X)
        
        time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
        time_label = tk.Label(time_frame, text=time_str, 
                            font=('Poppins', 28, 'bold'), 
                            fg=self.colors['text_primary'], 
                            bg=self.colors['card'])
        time_label.pack(side=tk.LEFT)
        
        # AM/PM indicator (if needed)
        hour_24 = alarm['hour']
        am_pm = "AM" if hour_24 < 12 else "PM"
        am_pm_label = tk.Label(time_frame, text=am_pm, 
                             font=('Poppins', 12, 'bold'), 
                             fg=self.colors['text_secondary'], 
                             bg=self.colors['card'])
        am_pm_label.pack(side=tk.LEFT, anchor='n', padx=(5, 0), pady=(8, 0))
        
        # Details frame
        details_frame = tk.Frame(left_frame, bg=self.colors['card'])
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Alarm name with icon
        name_frame = tk.Frame(details_frame, bg=self.colors['card'])
        name_frame.pack(fill=tk.X)
        
        tk.Label(name_frame, text="⏰", 
                font=('Poppins', 14), 
                fg=self.colors['accent'], 
                bg=self.colors['card']).pack(side=tk.LEFT)
        
        tk.Label(name_frame, text=alarm['label'], 
                font=('Poppins', 16, 'bold'), 
                fg=self.colors['text_primary'], 
                bg=self.colors['card']).pack(side=tk.LEFT, padx=(8, 0))
        
        # Days and sound info
        info_frame = tk.Frame(details_frame, bg=self.colors['card'])
        info_frame.pack(fill=tk.X, pady=(8, 0))
        
        # Days
        days_str = ", ".join([day[:3] for day in alarm['days']])
        tk.Label(info_frame, text=f"📅 {days_str}", 
                font=('Poppins', 11), 
                fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(anchor='w')
        
        # Sound info
        sound_icon = "🎤" if any(song["title"] in alarm['sound'] for song in self.black_sheriff_songs) else "🔔"
        tk.Label(info_frame, text=f"{sound_icon} {alarm['sound']}", 
                font=('Poppins', 11), 
                fg=self.colors['text_secondary'], 
                bg=self.colors['card']).pack(anchor='w', pady=(2, 0))
        
        # Right side - Controls
        controls_frame = tk.Frame(content_frame, bg=self.colors['card'])
        controls_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Status indicator
        status_indicator = tk.Frame(controls_frame, bg=self.colors['card'])
        status_indicator.pack(pady=(0, 15))
        
        status_text = "ACTIVE" if alarm['active'] else "INACTIVE"
        status_label = tk.Label(status_indicator, text=status_text, 
                              font=('Poppins', 10, 'bold'), 
                              fg=status_color, 
                              bg=self.colors['card'])
        status_label.pack()
        
        # Control buttons container
        buttons_frame = tk.Frame(controls_frame, bg=self.colors['card'])
        buttons_frame.pack()
        
        # Toggle button
        toggle_bg = self.colors['accent'] if alarm['active'] else self.colors['bg_tertiary']
        toggle_text = "ON" if alarm['active'] else "OFF"
        
        toggle_btn = tk.Button(buttons_frame, text=toggle_text,
                              command=lambda: self.toggle_alarm_by_index(index),
                              bg=toggle_bg,
                              fg=self.colors['text_primary'],
                              font=('Poppins', 12, 'bold'), bd=0, 
                              padx=20, pady=8, relief=tk.FLAT,
                              activebackground='#1ed760' if alarm['active'] else self.colors['hover'])
        toggle_btn.pack(pady=(0, 8))
        
        # Delete button
        delete_btn = tk.Button(buttons_frame, text="🗑️ Delete",
                              command=lambda: self.delete_alarm_by_index(index),
                              bg=self.colors['danger'], 
                              fg=self.colors['text_primary'],
                              font=('Poppins', 10, 'bold'), bd=0, 
                              padx=15, pady=6, relief=tk.FLAT,
                              activebackground='#c0392b')
        delete_btn.pack()
        
        # Hover effects for the entire card
        def on_card_enter(event):
            card.config(bg=self.colors['card_hover'])
            for widget in [content_frame, left_frame, time_frame, details_frame, 
                          name_frame, info_frame, controls_frame, status_indicator, buttons_frame]:
                widget.config(bg=self.colors['card_hover'])
            # Keep text labels background updated
            for label in [time_label, am_pm_label, status_label]:
                label.config(bg=self.colors['card_hover'])
        
        def on_card_leave(event):
            card.config(bg=self.colors['card'])
            for widget in [content_frame, left_frame, time_frame, details_frame, 
                          name_frame, info_frame, controls_frame, status_indicator, buttons_frame]:
                widget.config(bg=self.colors['card'])
            # Keep text labels background updated
            for label in [time_label, am_pm_label, status_label]:
                label.config(bg=self.colors['card'])
        
        # Bind hover events to main card elements
        for widget in [card, content_frame, left_frame, time_frame, time_label]:
            widget.bind("<Enter>", on_card_enter)
            widget.bind("<Leave>", on_card_leave)

    def get_sound_path(self, sound_name):
        if sound_name == "Default Beep":
            return None
        elif sound_name == "Custom Sound":
            return self.sound_path if self.sound_path else None
        else:
            # Check if it's a Black Sheriff song
            for song in self.black_sheriff_songs:
                if song["title"] in sound_name:
                    return song["path"]
        return None

    def browse_sound_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg"), ("All Files", "*.*")]
        )
        if file_path:
            self.sound_path = file_path
            self.sound_var.set("Custom Sound")

    def test_sound(self):
        try:
            pygame.mixer.music.set_volume(self.volume_var.get())
            sound_path = self.get_sound_path(self.sound_var.get())
            
            if sound_path and os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            else:
                self.create_beep_sound()
                pygame.mixer.music.play()
            
            messagebox.showinfo("Test", f"Playing: {self.sound_var.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play sound: {str(e)}")

    def create_beep_sound(self):
        # Create a simple beep sound if it doesn't exist
        if not os.path.exists("beep.wav"):
            try:
                import numpy as np
                import wave
                
                sample_rate = 44100
                duration = 2.0
                frequency = 440.0
                
                t = np.linspace(0, duration, int(sample_rate * duration))
                audio_data = np.sin(2 * np.pi * frequency * t)
                audio_data = (audio_data * 32767).astype(np.int16)
                
                with wave.open("beep.wav", 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
            except ImportError:
                print("numpy not available, using pygame beep")
        
        if os.path.exists("beep.wav"):
            pygame.mixer.music.load("beep.wav")

    def create_alarm(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            label = self.label_var.get().strip()
            
            if not label:
                messagebox.showerror("Error", "Please enter a label for the alarm")
                return
            
            selected_days = [day for day, var in self.day_vars.items() if var.get()]
            
            if not selected_days:
                messagebox.showerror("Error", "Please select at least one day")
                return
            
            sound_path = self.get_sound_path(self.sound_var.get())
            
            alarm = {
                'id': len(self.alarms) + 1,
                'hour': hour,
                'minute': minute,
                'label': label,
                'days': selected_days,
                'active': True,
                'sound': self.sound_var.get(),
                'sound_path': sound_path or ""
            }
            
            self.alarms.append(alarm)
            self.save_alarms()
            
            messagebox.showinfo("Success", f"Alarm '{label}' created successfully!")
            
            # Reset form
            self.label_var.set("Wake Up")
            for var in self.day_vars.values():
                var.set(False)
            
            # Switch to active alarms view
            self.switch_view("active")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid time values")

    def toggle_alarm_by_index(self, index):
        if 0 <= index < len(self.alarms):
            self.alarms[index]['active'] = not self.alarms[index]['active']
            self.save_alarms()
            self.refresh_alarm_list()

    def delete_alarm_by_index(self, index):
        if 0 <= index < len(self.alarms):
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this alarm?"):
                del self.alarms[index]
                self.save_alarms()
                self.refresh_alarm_list()

    def refresh_alarm_list(self):
        # Clear existing cards
        for widget in self.alarm_cards_frame.winfo_children():
            widget.destroy()
        
        if not self.alarms:
            # Enhanced empty state
            empty_frame = tk.Frame(self.alarm_cards_frame, bg=self.colors['bg_primary'])
            empty_frame.pack(expand=True, fill=tk.BOTH, pady=100)
            
            tk.Label(empty_frame, text="⏰", 
                    font=('Poppins', 60), 
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_primary']).pack()
            
            tk.Label(empty_frame, text="No alarms set yet", 
                    font=('Poppins', 18, 'bold'), 
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_primary']).pack(pady=(10, 5))
            
            tk.Label(empty_frame, text="Create your first alarm to get started", 
                    font=('Poppins', 12), 
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_primary']).pack()
        else:
            for index, alarm in enumerate(self.alarms):
                self.create_alarm_card(self.alarm_cards_frame, alarm, index)

    def update_time(self):
        while self.running:
            self.current_time = datetime.datetime.now()
            time_str = self.current_time.strftime("%H:%M:%S")
            date_str = self.current_time.strftime("%A, %B %d, %Y")
            
            if hasattr(self, 'current_time_label'):
                self.current_time_label.config(text=time_str)
            if hasattr(self, 'current_date_label'):
                self.current_date_label.config(text=date_str)
            
            time.sleep(1)

    def check_alarms(self):
        while self.running:
            current_time = datetime.datetime.now()
            current_day = current_time.strftime("%A")
            current_hour = current_time.hour
            current_minute = current_time.minute
            
            for alarm in self.alarms:
                if (alarm['active'] and 
                    current_day in alarm['days'] and 
                    current_hour == alarm['hour'] and 
                    current_minute == alarm['minute'] and
                    current_time.second == 0):  # Only trigger once per minute
                    self.trigger_alarm(alarm)
            
            time.sleep(1)

    def trigger_alarm(self, alarm):
        def show_alarm():
            self.play_alarm_sound(alarm['sound'], alarm['sound_path'])
            
            alarm_window = tk.Toplevel(self.root)
            alarm_window.title("ALARM!")
            alarm_window.geometry("500x300")
            alarm_window.configure(bg=self.colors['bg_primary'])
            alarm_window.attributes('-topmost', True)
            
            # Center the window
            alarm_window.transient(self.root)
            alarm_window.grab_set()
            
            # Alarm content
            tk.Label(alarm_window, text="⏰", 
                    font=('Poppins', 60), 
                    fg=self.colors['accent'], 
                    bg=self.colors['bg_primary']).pack(pady=20)
            
            tk.Label(alarm_window, text="ALARM!", 
                    font=('Poppins', 24, 'bold'), 
                    fg=self.colors['text_primary'], 
                    bg=self.colors['bg_primary']).pack()
            
            tk.Label(alarm_window, text=alarm['label'], 
                    font=('Poppins', 18), 
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_primary']).pack(pady=10)
            
            time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
            tk.Label(alarm_window, text=f"Time: {time_str}", 
                    font=('Poppins', 14), 
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_primary']).pack()
            
            # Show sound name
            tk.Label(alarm_window, text=f"♪ {alarm['sound']}", 
                    font=('Poppins', 12), 
                    fg=self.colors['accent'], 
                    bg=self.colors['bg_primary']).pack(pady=5)
            
            def stop_alarm():
                pygame.mixer.music.stop()
                alarm_window.destroy()
            
            # Stop button
            stop_btn = tk.Button(alarm_window, text="Stop Alarm", 
                           command=stop_alarm, 
                           bg=self.colors['danger'], 
                           fg=self.colors['text_primary'], 
                           font=('Poppins', 16, 'bold'),
                           padx=30, pady=12, bd=0, relief=tk.FLAT,
                           activebackground='#c0392b')
            stop_btn.pack(pady=30)
            
            # Bind the close event to stop the alarm
            alarm_window.protocol("WM_DELETE_WINDOW", stop_alarm)
    
        # Run in main thread
        self.root.after(0, show_alarm)

    def play_alarm_sound(self, sound_type, sound_path):
        try:
            pygame.mixer.music.set_volume(self.volume_var.get())
            
            if sound_path and os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
            else:
                self.create_beep_sound()
            
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except Exception as e:
            print(f"Could not play alarm sound: {str(e)}")

    def save_alarms(self):
        try:
            with open(self.alarm_file, 'w') as f:
                json.dump(self.alarms, f, indent=2)
        except Exception as e:
            print(f"Could not save alarms: {str(e)}")

    def load_alarms(self):
        try:#We will load the saved alarms from a JSON file
            if os.path.exists(self.alarm_file):#check if the file exists (thus if the is a saved alarm schedule)
                with open(self.alarm_file, 'r') as f:
                    self.alarms = json.load(f)
        except Exception as e:
            print(f"Could not load alarms: {str(e)}")
            self.alarms = []

    def on_closing(self):
        self.running = False
        pygame.mixer.quit()
        self.root.destroy()

def main():
    # Check for required dependencies
    try:
        import pygame
    except ImportError:
        print("pygame is required for sound functionality.")
        print("Install it with: pip install pygame")
        return
    
    root = tk.Tk()
    
    # Set minimum window size
    root.minsize(1000, 700)
    
    # Try to set window icon
    try:
        root.iconbitmap("assets/icon.ico")
    except:
        pass
    
    app = GhanaStyleAlarmClock(root)
    root.mainloop()

if __name__ == "__main__":
    main()


# In[ ]:




