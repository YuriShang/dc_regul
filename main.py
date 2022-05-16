# Приложение "DC REGUL" написано на чистом энтузиазме без какого либо коммерческого интереса.
# Целью его создания являлась в первую очередь практика написания кода на Python. 
# Также есть вероятность, что приложение найдет применение на моем текущем месте работы 
# и принесет хотя бы небольшую пользу моим коллегам. 
# Основной функцией приложения "DC REGUL" является удаленное управление выпрямительными (AC/DC) модулями
# через протокл Modbus.

import time
from threading import Thread
import tkinter as tk
from tkinter.font import NORMAL
from tkinter.ttk import Combobox, Spinbox, Button
from tkinter import DISABLED, Toplevel, StringVar, Label, Frame
import configparser
import mobd_client

# Словарь для хранения стандартных настроек на случай утери или повреждения файла "settings.ini"
DEFAULT_SETTINGS = {
    'Comm':     {'port': 'COM10', 'baudrate': '9600', 'parity': 'N', 'stopbits': '1',},
    'Module 1': {'voltage_read': '04', 'voltage_write': '062', 'current_read': '07', 'current_write': '064',
                 'voltage_limit': '230', 'current_limit': '10', 'voltage_discret': '50'},
    'Module 2': {'voltage_read': '04', 'voltage_write': '062', 'current_read': '07', 'current_write': '064',
                 'voltage_limit': '230', 'current_limit': '10', 'voltage_discret': '50'},
}

# Проверка наличия файла настроек "settings.ini", при отсутствии будет создан новый 
# со стандартными настройками
config = configparser.ConfigParser()
if config.read('settings.ini'):
    config.read('settings.ini')
else:
    with open('settings.ini', 'w') as file:
        config.read_dict(DEFAULT_SETTINGS)
        config.write(file)
        print('File "settings.ini" not found, generating new one...', 'Default settings successfully aplied', sep='\n')


class MainWin(tk.Tk, mobd_client.Client):
    def __init__(self):
        mobd_client.Client.__init__(self)
        super().__init__()
        
        # Инициализация главного окна
        self.title("DC REGUL")
        self.geometry("400x335")
        self.resizable(0, 0)
        
        try:
            self.iconbitmap('icon.ico')
        except:
            print('"icon.ico" is not defined')

        # Инициализация кнопок выбор модуля
        module_label = Label(text='Модуль')
        module_label.place(relx=.439, rely=.07)
        self.module_switch_first = Button(self, text="1", width=3)
        self.module_switch_first.place(relx=.408, rely=.135)
        self.module_switch_second = Button(self, text="2", width=3)
        self.module_switch_second.place(relx=.527, rely=.135)

        voltage_label = Label(text='Напряжение', width=15)
        voltage_label.place(relx=.08, rely=.07)
        current_label = Label(text='Ток', width=15)
        current_label.place(relx=.65, rely=.07)

        # Инициализация дисплеев для отображения тока и напряжения
        self.volt_string = StringVar()
        self.volt_string.set('- - -')
        voltage = Label(textvariable=self.volt_string, width=12, fg="#eee", bg="#333", font='"Calibri" 13 bold')
        voltage.place(relx=.07, rely=.135)
        self.current_string = StringVar()
        self.current_string.set('- - -')
        current = Label(textvariable=self.current_string, width=12, fg="#eee", bg="#333", font='"Calibri" 13 bold')
        current.place(relx=.65, rely=.135)

        # Инициализация кнопок дискретного изменения напряжения
        self.volt_down = Button(self, text="-", width = 5)
        self.volt_down.place(relx=.0685, rely=.23)
        self.volt_up = Button(self, text="+", width = 5)
        self.volt_up.place(relx=.257, rely=.23)

        # Инициализация кнопок дискретного изменения тока
        self.current_down = Button(self, text="-", width = 5)
        self.current_down.place(relx=.648, rely=.23)
        self.current_up = Button(self, text="+", width = 5)
        self.current_up.place(relx=.8365, rely=.23)

        # Инициализация спинбокса для установки шага изменения напряжения
        discret_label = Label(text='Шаг', width=15)
        discret_label.place(relx=.07, rely=.32)
        self.voltage_discret_string = StringVar()
        voltage_discret = Spinbox(width=7, from_=0, to=100, textvariable=self.voltage_discret_string)
        voltage_discret.place(relx=.0685, rely=.40)
        self.voltage_discret_accept = Button(self, text="Ок", width=5)
        self.voltage_discret_accept.place(relx=.258, rely=.391)

        # Инициализация спинбокса для задавания напряжения
        voltage_set_label = Label(text='Задать напряжение', width=15)
        voltage_set_label.place(relx=.07, rely=.50)
        self.voltage_set_string = StringVar()
        self.voltage_set_string.set('0.0')
        voltage_set = Spinbox(width=7, from_=0, to=230, textvariable=self.voltage_set_string)
        voltage_set.place(relx=.0685, rely=.59)
        self.voltage_set_accept = Button(self, text="Ок", width=5)
        self.voltage_set_accept.place(relx=.258, rely=.583)

        limit_label = Label(text='Ограничение', width=15)
        limit_label.place(relx=.36, rely=.69)

        # Инициализация спинбокса для задавания ограничения напряжения
        self.voltage_limit_string = StringVar()
        self.voltage_limit = Spinbox(width=7, from_=0, to=500, textvariable=self.voltage_limit_string)
        self.voltage_limit.place(relx=.0685, rely=.77)
        self.voltage_limit_accept = Button(self, text="Ок", width=5)
        self.voltage_limit_accept.place(relx=.258, rely=.7625)

        # Инициализация спинбокса для задавания ограничения тока
        self.current_limit_string = StringVar()
        self.current_limit = Spinbox(width=7, from_=0, to=25, textvariable=self.current_limit_string)
        self.current_limit.place(relx=.65, rely=.77)
        self.current_limit_accept = Button(self, text="Ок", width=5)
        self.current_limit_accept.place(relx=.839, rely=.761)

        # Инициализация кнопок на главном окне
        self.settings_butt = Button(self, text="Настройки", width = 17)
        self.settings_butt.place(relx=.03, rely=.90)
        self.run_butt = Button(self, text="Старт", width = 17)
        self.run_butt.place(relx=.36, rely=.90)
        self.soft_start_butt = Button(self, text="Плавный пуск", width = 17, state=DISABLED)
        self.soft_start_butt.place(relx=.69, rely=.90)

        # Инициализация счетчиков TX, Error
        fr = Frame(self)
        self.tx_string = StringVar()
        self.tx_string.set('TX: 0')
        tx_label = Label(fr, textvariable=self.tx_string, fg='gray')
        tx_label.pack(side=tk.LEFT, padx=0, pady=0)
        self.err_string = StringVar()
        self.err_string.set('Err: 0')
        err_label = Label(fr, textvariable=self.err_string, fg='gray')
        err_label.pack(side=tk.RIGHT, padx=1, pady=0)
        fr.place(relx=.061, rely=0)

        # Собсвтенно, тег автора данного проекта
        author_label = Label(text='(c) Yuri Sh.', font='"Calibri" 8', fg='gray')
        author_label.place(relx=.87, rely=0)

        self.settings_butt.configure(command=self.new_window)
        self.run_butt.configure(command=self.start)
        self.mod_num = 1 # При запуске программы по умолчанию активен первый модуль
        self.unit = 1
        self.client = False # Инициализация объекта клиента модбас
        self.soft_starter = False # Инициализация флага для плавного поднятия напряжения
        self.tx = 0
        self.err = 0
        self.delay = 0.6
        self.new_window() # Инициализация всех настроек
        self.settings.destroy()
        self.button_configurator() # Инициализация кнопок
        self.main_win_settings_set(self.mod_num) # Инициализация настроек в главном окне
        self.module_swither(self.mod_num) # Инициализация модуля по умолчанию

    def button_configurator(self):
        """
        Привязка команд к кнопкам. После изменения констант требуется переназначение команды, 
        в следствие этого и просиходит частый вызов данной функции
        """
        self.module_switch_first.configure(command=lambda: self.module_swither(1))
        self.module_switch_second.configure(command=lambda: self.module_swither(0))
        self.volt_up.configure(command=lambda: self.voltage_up_down(1, self.mod_num))
        self.volt_down.configure(command=lambda: self.voltage_up_down(0, self.mod_num))
        self.voltage_discret_accept.configure(command=lambda: self.voltage_discrete_limit_set(1, self.mod_num))
        self.voltage_set_accept.configure(command=lambda: self.voltage_set(self.mod_num))
        self.voltage_limit_accept.configure(command=lambda: self.voltage_discrete_limit_set(0, self.mod_num))
        self.current_up.configure(command=lambda: self.current_up_down(1, self.mod_num))
        self.current_down.configure(command=lambda: self.current_up_down(0, self.mod_num))
        self.current_limit_accept.configure(command=lambda: self.current_limit_set(self.mod_num))
    
    def main_win_settings_set(self, num):
        """
        Запись в данных в спинбоксы на главном окне
        """
        self.voltage_discret_string.set(config[f'Module {num}']['voltage_discret'])
        self.voltage_limit_string.set(config[f'Module {num}']['voltage_limit'])
        self.current_limit_string.set(config[f'Module {num}']['current_limit'])

    def module_swither(self, mod_num):
        """
        Выбор выпрямителя для работы. Всего их два
        """
        if mod_num:
            self.mod_num = 1
            self.unit = 1
            self.module_switch_first.configure(state = DISABLED)
            self.module_switch_second.configure(state = NORMAL)
        else:
            self.unit = 2
            self.mod_num = 2
            self.module_switch_second.configure(state = DISABLED)
            self.module_switch_first.configure(state = NORMAL)
        self.prepare_settings(self.mod_num)
        self.button_configurator()
        self.main_win_settings_set(self.mod_num)

    def new_window(self):
        """
        Диалогове окно с настройками соединения и назначением регистров для чтения и записи
        """
        self.settings = Toplevel(self)
        self.settings.geometry("270x310")
        self.settings.resizable(0, 0)
        self.settings.title("Настройки COM")
        self.ports = [f'COM{i + 1}' for i in range(32)]

        # Порт
        self.fr1 = Frame(self.settings)
        self.l1 = Label(self.fr1, text="Порт:")
        self.c1 = Combobox(self.fr1, values=self.ports, state='readonly')
        self.l1.pack(side=tk.LEFT, padx=0, pady=7)
        self.c1.pack(side=tk.RIGHT, padx=38, pady=7)
        self.fr1.place(relx=0.095, rely=.03)

        # Скорость
        self.speeds = ('1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200') 
        self.fr2 = Frame(self.settings)
        self.l2 = Label(self.fr2, text="Скорость:")
        self.c2 = Combobox(self.fr2, values=self.speeds, state='readonly')
        self.l2.pack(side=tk.LEFT, padx=0, pady=7)
        self.c2.pack(side=tk.RIGHT, padx=14, pady=7)
        self.fr2.place(relx=0.095, rely=.15)

        # Четность
        self.fr3 = Frame(self.settings)
        self.l3 = Label(self.fr3, text="Четность:")
        self.c3 = Combobox(self.fr3, values=('N', 'E'), state='readonly')
        self.l3.pack(side=tk.LEFT, padx=0, pady=7)
        self.c3.pack(side=tk.RIGHT, padx=16, pady=7)
        self.fr3.place(relx=0.095, rely=0.27)

        # Стопбиты
        self.fr4 = Frame(self.settings)
        self.l4 = Label(self.fr4, text="Стоп биты:")
        self.c4 = Combobox(self.fr4, values=('1', '2'), state='readonly')
        self.l4.pack(side=tk.LEFT, padx=0, pady=7)
        self.c4.pack(side=tk.RIGHT, padx=8.2, pady=7)
        self.fr4.place(relx=0.095, rely=0.39)

        # Изменение регистров для чтения и записи
        self.fr5 = Frame(self.settings)
        self.registers_setting_label = Label(self.fr5, text="Регистры для чтения и записи")
        self.registers_setting_label.pack(side=tk.LEFT, padx=0, pady=7)
        self.fr5.place(relx=0.16, rely=0.51)

        # Регистры для чтения и записи напряжения 
        self.fr6 = Frame(self.settings)
        self.read_Vregs_label = Label(self.fr6, text="Напр. r/w:")
        self.wr_Vregs = Spinbox(self.fr6, width=7, from_=0, to=255)
        self.wr_Vregs.pack(side=tk.RIGHT, padx=8, pady=7)
        self.read_Vregs = Spinbox(self.fr6, width=7, from_=0, to=255)
        self.read_Vregs_label.pack(side=tk.LEFT, padx=0, pady=7)
        self.read_Vregs.pack(side=tk.RIGHT, padx=13, pady=7)
        self.fr6.place(relx=.095, rely=.63)

        # Регистры для чтения и записи тока 
        self.fr8 = Frame(self.settings)
        self.read_Iregs_label = Label(self.fr8, text="Ток r/w:")
        self.wr_Iregs = Spinbox(self.fr8, width=7, from_=0, to=255)
        self.wr_Iregs.pack(side=tk.RIGHT, padx=0, pady=7)
        self.read_Iregs = Spinbox(self.fr8, width=7, from_=0, to=255)
        self.read_Iregs_label.pack(side=tk.LEFT, padx=1, pady=7)
        self.read_Iregs.pack(side=tk.RIGHT, padx=24, pady=7)
        self.fr8.place(relx=.088, rely=.758)

        ok_butt = Button(self.settings, text="Ок", width=12, command=lambda: self.settings_save(self.mod_num))
        ok_butt.place(relx=0.13, rely=0.9)
        cancel_butt = Button(self.settings, text="Отмена", width=12, command=self.settings.destroy)
        cancel_butt.place(relx=0.57, rely=0.9)
        self.settings_apply(self.mod_num)
    
        if self.client:
            self.stop()
 
    def settings_apply(self, num):
        """
        Запись выбранных параметров в комбобоксы и спинбоксы.
        Реализована отдельная функция, т.к. приходится часто обращаться к данным методам
        """
        self.c1.current(list(self.c1['values']).index(config['Comm']["port"]))
        self.c2.current(list(self.c2['values']).index(config['Comm']["baudrate"]))
        self.c3.current(list(self.c3['values']).index(config['Comm']["parity"]))
        self.c4.current(list(self.c4['values']).index(config['Comm']["stopbits"]))
        self.read_Vregs.insert(1, int(config[f'Module {num}']["voltage_read"]))
        self.wr_Vregs.insert(1, int(config[f'Module {num}']["voltage_write"]))
        self.read_Iregs.insert(1, int(config[f'Module {num}']["current_read"]))
        self.wr_Iregs.insert(1, int(config[f'Module {num}']["current_write"]))
        self.options = self.c1.get(), self.c2.get(), self.c3.get(), self.c4.get(),
        self.rw_registers = self.read_Vregs.get(), self.wr_Vregs.get(), self.read_Iregs.get(), self.wr_Iregs.get()

    def settings_save(self, num):
        """
        Выбор настроек для записи в файл settings.ini. 
        Настройки берутся с комбо- и спинбоксов
        """
        config['Comm']["port"] = self.c1.get()
        config['Comm']["baudrate"] = self.c2.get()
        config['Comm']["parity"] = self.c3.get()
        config['Comm']["stopbits"] = self.c4.get()
        config[f'Module {num}']["voltage_read"] = self.read_Vregs.get()
        config[f'Module {num}']["voltage_write"] = self.wr_Vregs.get()
        config[f'Module {num}']["current_read"] = self.read_Iregs.get()
        config[f'Module {num}']["current_write"] = self.wr_Iregs.get()
        self.settings_apply(num)
        self.settings.destroy()
        self.setting_write()

    def setting_write(self):
        """
        Запись настроек в файл. Также выведена в отдельную функцию в связи частым вызовом
        """
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    def prepare_settings(self, num):
        """
        Подготовка необходимых параметров для предстоящего подключения к устройству
        """
        self.options = (config['Comm']["port"],
                        config['Comm']["baudrate"],
                        config['Comm']["parity"],
                        config['Comm']["stopbits"],)
        self.r_registers = (int(config[f'Module {num}']["voltage_read"]), 
                            int(config[f'Module {num}']["current_read"]),)
        self.voltage_write_reg, self.current_write_reg = (int(config[f'Module {num}']["voltage_write"]),
                                                          int(config[f'Module {num}']["current_write"]),)

    def start(self):
        """
        Помщение функции, который выполняет чтение/запись данных, в поток и ее запуск 
        """
        self.prepare_settings(self.mod_num)
        self.thr = Thread(target=self.indicators)
        if not self.client:
            self.soft_start_butt.configure(text="Плавный пуск", width=17, command=self.soft_start_init)
            self.activ_inactiv_buttons(True)
            self.init_client(*self.options)
            print(f'New settings {self.options} has been applied')
            self.thr.start()
            self.run_butt.configure(text="Стоп", command=self.stop)
            self.soft_start_butt.configure(state=NORMAL)

    def write_registers(self, reg, value):
        """
        Функция прокладка. Необходима для создания условия при записи данных в устройство
        """
        if self.client and not self.error:
            self.writer(reg, value, self.unit)

    def stop(self):
        """
        Останов чтения данных
        """
        self.client.close() # Пока не переопределишь объект клиента, COM порт будет занят
        self.client = False
        self.run_butt.configure(text="Старт", command=self.start)
        self.soft_start_butt.configure(state=DISABLED)
        if self.soft_starter:
            self.soft_start_stop()

    def indicators(self):
        """
        Функция в бесконечном цикле выполняет обращение к основной функции считывания данных по 
        протоклу модбас. В качестве аргументов передает регистры для чтения напряжения и тока, а также
        адрес устройства. Считанные данные помещает в соответсвующе окна (напряжение, ток)
        """
        self.error = True
        while True:
            if not self.client:
                print('STOPPED')
                break
            if self.client:
                time.sleep(self.delay)
                voltage, current = self.runner(*self.r_registers, self.unit)
            if voltage != 'error':
                self.tx += 1
                self.tx_string.set(f'TX: {self.tx}')
                self.volt_string.set(voltage)
                self.current_string.set(current)
                self.error = False
            elif self.client:
                self.err += 1
                self.err_string.set(f'Err: {self.err}')
                self.tx += 1
                self.tx_string.set(f'TX: {self.tx}')
            if self.soft_starter is True:
                self.delay = 0.08
                self.soft_start(self.mod_num)
    
    def soft_start_init(self):
        """
        Инициализатор функции плавного поднятия напряжения.
        Задает начальный уровень напряжения и флаг-триггер для запуска
        самой функции
        """
        if self.client and not self.error:
            self.voltage_to_write = float(self.volt_string.get())
            self.soft_starter = True
            self.soft_discret = 18

    def soft_start(self, num):
        """
        Функция плавно поднимает напряжение до уровня ограничения
        """
        if not self.error:
            self.soft_start_butt.configure(text="Отмена", width = 17, command=self.soft_start_stop)
            self.activ_inactiv_buttons(False)
            limit = float(self.voltage_limit.get())
            if self.client and self.soft_starter:
                if not self.soft_starter or float(self.current_string.get()) >= float(config[f'Module {num}']['current_limit']):
                    self.soft_start_stop()
                else:
                    self.voltage_to_write += self.soft_discret
                if self.voltage_to_write >= limit - self.soft_discret * 3:
                    self.soft_discret /= 2
                if self.voltage_to_write >= limit - 1:
                    self.voltage_to_write = limit
                    self.soft_start_stop()
                self.write_registers(self.voltage_write_reg, self.voltage_to_write)

    def soft_start_stop(self):
        """
        Останов функции плавного поднятия напряжения
        """
        self.activ_inactiv_buttons(True)
        self.soft_start_butt.configure(text="Плавный пуск", width = 17, command=self.soft_start_init)
        self.soft_starter = False
        self.delay = 0.6
        
    def voltage_up_down(self, flag, num):
        """
        Функция для поднятия либо снижения напряжения на заданный шаг по нажатию соответсвующей кнопки(-, +).
        """
        if self.client and not self.error:
            voltage = float(self.volt_string.get().replace(',', '.'))
            discret = float(config[f'Module {num}']['voltage_discret'])
            limit = float(config[f'Module {num}']['voltage_limit'])
            if flag:
                if voltage + discret > limit:
                    voltage = limit
                else:
                    voltage += discret
            else:
                if voltage - discret < 0:
                    voltage = 0
                else:
                    voltage -= discret
            self.writer(self.voltage_write_reg, voltage, self.unit)

    def current_up_down(self, flag, num):
        """
        Функция для поднятия либо снижения ограничения тока на 1 А
        по нажатию соответсвующей кнопки(-, +).
        """
        current = float(self.current_limit_string.get().replace(',', '.'))
        if flag:
            current += 1
        else:
            current -= 1
        if current >= 25:
            current = 25.0
        if current <= 1:
            current = 1.0
        self.current_limit_string.set(str(current))
        config[f'Module {num}']['current_limit'] = str(current)
        self.write_registers(self.current_write_reg, current)
        self.setting_write()
        
    def current_limit_set(self, num):
        """
        Установка ограничения тока от 0 до 25 А. 
        """
        current = float(self.current_limit_string.get().replace(',', '.'))
        if current > 25:
            current = 25
            self.current_limit_string.set('25')
        self.write_registers(self.current_write_reg, current)
        config[f'Module {num}']['current_limit'] = self.current_limit_string.get()
        self.setting_write()

    def voltage_discrete_limit_set(self, flag, num):
        """
        Установка шага изменения напряжения от 0 до 100 В для функции voltage_up_down
        """
        discret = float(self.voltage_discret_string.get().replace(',', '.'))
        limit = float(self.voltage_limit_string.get().replace(',', '.'))
        if flag:
            if discret > 100:
                self.voltage_discret_string.set('100')
                config[f'Module {num}']['voltage_discret'] = '100'
            else:
                config[f'Module {num}']['voltage_discret'] = str(discret)
        else:
            if limit > 500:
                self.voltage_limit_string.set('500')
                config[f'Module {num}']['voltage_limit'] = '500'
            else:
                config[f'Module {num}']['voltage_limit'] = str(limit)
            if self.client and float(self.volt_string.get()) > limit:
                self.write_registers(self.voltage_write_reg, limit)
        self.setting_write()
    
    def voltage_set(self, num):
        """
        Установка уровня напряжения от 0 до 500 В либо до уровня ограничения
        """
        voltage = float(self.voltage_set_string.get().replace(',', '.'))
        limit = float(config[f'Module {num}']['voltage_limit'])
        if voltage > 500:
            voltage = 500
            self.voltage_set_string.set('500')
        if voltage > limit:
            voltage = limit
        self.write_registers(self.voltage_write_reg, voltage)

    def activ_inactiv_buttons(self, idx):
        """
        Функция для временной деактивации всех кнопок при плавном наборе напряжения
        """
        buttons = (self.volt_up, self.volt_down, self.current_up, self.current_down, self.current_limit_accept, 
                   self.voltage_discret_accept, self.voltage_limit_accept, self.voltage_set_accept)
        state = [DISABLED, NORMAL][idx]
        for button in buttons:
            button.configure(state=state)

if __name__ == '__main__':
    app = MainWin()
    app.mainloop()
