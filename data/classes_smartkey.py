import tkinter as tk
from sqlalchemy import create_engine, Column, Integer, String, inspect, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine('sqlite:///smart_key.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    pin = Column(String, nullable=False)
    active = Column(Integer, nullable=False, default=1)

inspector = inspect(engine)
if not inspector.has_table(User.__tablename__):
    
    Base.metadata.create_all(engine)
    print('Table created successfully')

Session = sessionmaker(bind=engine)
session = Session()
users = [User(name='Pero Peric', pin='1234', active=True),
         User(name='Ana Anic', pin='5678', active=True),
         User(name='Marko Maric', pin='4321', active=False)]
session.add_all(users)
session.commit()

class SmartKey:
    def __init__(self, main_window):
        self.master = main_window
        main_window.title('SmartKey')
        main_window.geometry('600x600')

        self.bell_button = tk.Button(main_window, text='Pozvoniti', command=self.ring_bell)
        self.bell_button.pack(side=tk.TOP, padx=10, pady=10)
        self.unlock_button = tk.Button(main_window, text='Otključati', command=self.unlock_door)
        self.unlock_button.pack(side=tk.TOP, padx=10, pady=10)

        self.user_frame = tk.Frame(main_window)
        self.user_frame.pack(side=tk.TOP, padx=10, pady=10)
        
        self.pin_label = tk.Label(self.user_frame, text='PIN')
        self.pin_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pin_entry = tk.Entry(self.user_frame, show='*')
        self.pin_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.name_label = tk.Label(self.user_frame, text='Ime i prezime')
        self.name_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(self.user_frame)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.add_button = tk.Button(self.user_frame, text='Spremi', command=self.add_user)
        self.add_button.grid(row=3, column=0, padx=5, pady=5)
        
        self.cancel_button = tk.Button(self.user_frame, text='Odustani', command=self.cancel_user)
        self.cancel_button.grid(row=3, column=1, padx=5, pady=5)
        
        self.delete_button = tk.Button(self.user_frame, text='Izbriši', command=self.delete_user)
        self.delete_button.grid(row=3, column=2, padx=5, pady=5)

        self.pin_frame = tk.Frame(main_window)
        self.pin_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.pin_buttons = []
        for i in range(10):
            if i == 9:
                button_text = '0'
            else:
                button_text = str(i + 1)
            button = tk.Button(self.pin_frame,
                               text=button_text, 
                               command=lambda button_text=button_text: self.pin_entry.insert(tk.END, button_text))
            button.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.pin_buttons.append(button)

       
        lbl_display_element_var = tk.StringVar()
        lbl_display_element_var.set('Dobrodošli!')
        lbl_display_element = tk.Label(main_window,
                                textvariable=lbl_display_element_var,
                                font=('Vedrana', 18))
        lbl_display_element.pack(padx=10, pady=10,
                            fill=tk.BOTH)
        self.status = tk.Label(lbl_display_element,
                               text='Dobrodošli!', 
                               bd=2, 
                               relief=tk.SUNKEN, 
                               anchor=tk.W,
                               font=('Vedrana', 16))
        self.status.pack(side=tk.BOTTOM, fill='both')
    def delete_user(self):
        name = self.name_entry.get()
        with engine.begin() as conn:
            conn.execute(User.__table__.delete().where(User.name == name))
        self.status.config(text=f'Korisnik {name} je izbrisan iz baze podataka.')
        self.name_entry.delete(0, tk.END)
        self.pin_entry.delete(0, tk.END)
    def ring_bell(self):
            self.status.config(text='Zvono je aktivirano! Netko će uskoro doći i otvoriti vrata.')
    def lock_door(self):
        self.status.config(text='Vrata su zaključana.')
    def unlock_door(self):
        pin = self.pin_entry.get()
        name = self.get_name(pin)
        if name:
            self.status.config(text=f'Dobrodošao/la, {name}! Vrata su otključana.')
        else:
            self.status.config(text='Pogrešan PIN!')
    def add_user(self):
        name = self.name_entry.get()
        pin = self.pin_entry.get()
        if name and pin:
            try:
                Session = sessionmaker(bind=engine)
                session = Session()

                user = User(name=name, pin=pin, active=1)
                session.add(user)
                session.commit()

                self.status.config(text=f'Korisnik {name} je dodan u bazu podataka.')
            except SQLAlchemyError as e:
                self.status.config(text='Greška u bazi podataka: ' + str(e))
        else:
            self.status.config(text='Morate unijeti ime i PIN.')
    
    def cancel_user(self):
        self.name_entry.delete(0, tk.END)
        self.pin_entry.delete(0, tk.END)
        self.status.config(text='Unos otkazan.')
        

    def get_name(self, pin):
        with engine.connect() as conn:
            result = conn.execute(User.__table__.select().where(User.pin == pin, User.active == True))
            row = result.fetchone()
        return row[1] if row else None

