import sqlite3
from sqlite3 import Error
from ttkthemes import themed_tk as tk
import tkinter as tk
from tkinter import *
from tkinter import font, Menu, colorchooser
from tkinter.filedialog import askopenfile
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from numpy import array
import configparser
import webbrowser
import subprocess
import validators
import shutil
import os
import re
class XY_Scroll(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pad_10x=int(root_width*0.01)#canvas left
        pad_20x=int(root_width*0.025)#hbar left
        pad_10y=int(root_height*0.04)#vbar top
        pad_20y=int(root_height*0.04)#vbar bottom
        Window_Color.set("#d4d4d4")
        self.canvas=tk.Canvas(self,border=3,relief="sunken",bg=Window_Color.get())
        scrollstyle = ttk.Style()
        scrollstyle.theme_use('classic')
        self.vbar=ttk.Scrollbar(self,orient=VERTICAL,command=self.canvas.yview)
        self.vbar.pack(side=RIGHT,fill=Y,padx=(2,2),pady=(pad_10y,pad_20y))                                        
        scrollstyle.configure("Horizontal.TScrollbar", background='#dfdfdf', bordercolor='#000000')
        self.hbar=ttk.Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
        self.hbar.pack(side=BOTTOM,fill=X,padx=(pad_20x,pad_10x),pady=(2,2))
        self.canvas.pack(side=TOP, anchor=NW, fill=BOTH, expand=True, padx=(pad_10x,0), pady=(0,0))
        self.data_window=tk.Frame(self.canvas,bg=Window_Color.get())
        self.data_window.pack(side=TOP,anchor=NW,fill=BOTH, expand=True, padx=(0,0), pady=(0,0))                     
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)                          
        self.canvas_window=self.canvas.create_window((0,0),window=self.data_window,anchor=NW, tags="self.data_window") 
        self.canvas.configure(bg=Window_Color.get())
        self.canvas.bind("<Key-Prior>", self.page_up)
        self.canvas.bind("<Key-Next>", self.page_down)
        self.canvas.bind("<Key-Up>", self.unit_up)
        self.canvas.bind("<Key-Down>", self.unit_down)        
        self.canvas.bind("<Key-Left>", self.unit_left)
        self.canvas.bind("<Key-Right>", self.unit_right)        
        self.data_window.bind("<Configure>", self.rst_frame)                       
        self.data_window.bind('<Enter>', self.inside_canvas)                                 
        self.data_window.bind('<Leave>', self.outside_canvas)
        self.rst_frame(None)
    def rst_frame(self, event):                                              
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))                 
    def unit_up(self, event):
        self.canvas.yview_scroll(-1, "unit")
        return "break"
    def unit_down(self, event):
        self.canvas.yview_scroll(1, "unit")
        return "break"
    def unit_left(self, event):
        self.canvas.xview_scroll(-1, "unit")
        return "break"
    def unit_right(self, event):
        self.canvas.xview_scroll(1, "unit")
        return "break"
    def page_up(self, event):
        self.canvas.yview_scroll(-1, "page")
        return "break"
    def page_down(self, event):
        self.canvas.yview_scroll(1, "page")
        return "break"
    def scroll_mousey(self, event):
        # Windows Mouse Wheel Scroll Y
        self.canvas.yview_scroll(int(-1* (event.delta/120)), 'units')
    def inside_canvas(self, event):                                                       
        self.canvas.focus_set()                                                 
        self.canvas.bind_all("<MouseWheel>", self.scroll_mousey)
    def outside_canvas(self, event):                                                       
        self.canvas.unbind_all("<MouseWheel>")
class Database_Ini:
    def __init__(self,funct,db_name,tbl_name=None,new_name=None,exist=None):
        Num_Rows.set(0)
        self.funct=funct
        self.db_name=db_name
        self.exist=exist
        self.table=tbl_name
        self.new_tbl_name=new_name
        self.file_name=str(f"{db_name}.ini")
        self.attach_folder=os.path.join(DB_Path.get(),"Attachments")# Attached Files Are Placed Here
        try:
            if not os.path.exists(self.attach_folder):
                os.makedirs(self.attach_folder) 
            if self.funct=='read' or self.funct=='write':
                self.ini_path=os.path.join(DB_Path.get(),self.file_name)
            config=configparser.ConfigParser()
            def read_ini_data():
                if self.table!=None:
                    if not os.path.exists(self.ini_path):
                        write_ini_data()
                    config.read(self.ini_path)
                    keys=["window_color","header_bg_color","header_font_color",
                            "entry_bg_color","entry_font_color","grid_color","grid_status"]
                    for key in keys:
                        try:
                            value=config.get(Active_Table.get().replace(" ","_"),key)# These Values Are Table Related
                            if key=="window_color":
                                Window_Color.set(value)
                                root.configure(bg=Window_Color.get()) # Set root backcolor
                                root.update()
                            elif key=="header_bg_color":Header_BG_Color.set(value)
                            elif key=="header_font_color":Header_Font_Color.set(value)
                            elif key=="entry_font_color":Entry_Font_Color.set(value)
                            elif key=="grid_color":Grid_Color.set(value)
                            elif key=="grid_status":
                                Grid_Status.set(int(value))
                                if value=='0':stat="on"
                                if value=='1':stat="off"
                                grid_menu.delete(0,END)
                                color_menu.delete(0,END)
                                populate_grid_menu(stat)
                                populate_color_menu()
                        except configparser.NoOptionError:
                            pass
            def write_ini_data():
                self.ini_path=os.path.join(DB_Path.get(),self.file_name)
                if not os.path.exists(self.ini_path):set_default_colors()
                config=configparser.ConfigParser()
                config.read(self.ini_path)
                if self.table!=None: 
                    try:
                        config.add_section(self.table)
                    except configparser.DuplicateSectionError:
                        pass
                    config.set(Active_Table.get(), "window_color", Window_Color.get())
                    config.set(Active_Table.get(), "header_bg_color", Header_BG_Color.get())
                    config.set(Active_Table.get(), "header_font_color", Header_Font_Color.get())
                    config.set(Active_Table.get(), "entry_font_color", Entry_Font_Color.get())
                    config.set(Active_Table.get(), "grid_color", Grid_Color.get())
                    config.set(Active_Table.get(), "grid_status", str(Grid_Status.get()))
                    with open(self.ini_path, 'w') as configfile:
                        config.write(configfile)
                    configfile.close()    
            def delete_section():
                self.ini_path=os.path.join(DB_Path.get(),self.file_name)
                if self.exist==None:
                    if not os.path.exists(self.ini_path):
                        return
                config=configparser.ConfigParser()
                config.read(self.ini_path)
                try:
                    with open(self.ini_path, 'r+') as configfile:
                        config.read_file(configfile)# File Position At End Of File)
                        config.remove_section(self.table)
                        configfile.seek(0)# Change File Position To Beginning Of File
                        config.write(configfile)
                        configfile.truncate()# Truncate Remaining Content After Written Position
                    configfile.close()
                except configparser.NoOptionError:
                    pass
            def rename_section():
                delete_section()
                self.table=self.new_tbl_name
                Active_Table.set(self.table)
                write_ini_data()
            def delete_ini():
                self.ini_path=os.path.join(DB_Path.get(),self.file_name)
                if self.exist==None:
                    if not os.path.exists(self.ini_path):
                        return
                os.remove(self.ini_path)
            if funct=='read':read_ini_data()        
            elif funct=='write':write_ini_data()
            elif funct=='delete section':delete_section()
            elif funct=='rename section':rename_section()
            elif funct=='delete ini':delete_ini()
        except Exception as ex:
            msg1=funct+ ' '+self.table+'\n'  
            if Language.get()=="Spanish":
                title='<Error de archivo INI '+funct+'>'
            else:
                title='<INI File Error '+funct+'>'
            msg2=f"\nError: '{ex}'"
            msg=msg1+msg2
            messagebox.showerror(title, msg)
class Database():
    def validate_integer(string):
        regex=re.compile(r'[(0-9)/d]*$') # Allow
        result=regex.match(string)
        return (string == "" or result is not None) 
    def on_validate_integer(P):
        return Database.validate_integer(P) 
    def validate_entries(string):
        regex=re.compile(r'[(0-9)(a-zA-Z)( )]*$') # Allow
        result=regex.match(string)
        return (string == "" 
        # Prevent duplicates
        or (string.count("'") == 0
            and string.count("(") == 0
            and string.count(")") == 0
            and result is not None
            and result.group(0) != ""))
    def on_validate_entries(P):
        return Database.validate_entries(P) 
    def get_rowid(col_name,var):
        conn=sqlite3.connect(Active_DB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT rowid FROM "+Active_Table.get()+" WHERE column_name = "+col_name, (var,))
        rowid=cursor.fetchone()[0]
        return rowid           
    def database_exist(db_name):
        try:
            sqlite3.connect('file:'+db_name+'?mode=ro', uri=True)
            return True
        except:
            return False
    def create_connection(db_file):
        conn=None
        try:
            conn=sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as er:
            if Language.get()=="Spanish":msg1='Error Conectándose a '+db_file+'\n'
            else:msg1='Error Connecting To '+db_file+'\n'    
            msg2=f"\nError: '{er}'"
            messagebox.showerror("<"+db_file+ "Connection>", msg1+msg2)
    def create_new_database():
        Database.destroy_widgets()
        if Language.get()=="Spanish": 
            title='Estás aquí → Crear Nueva Base de Datos'
            msg='Ingrese un Nombre para esta Nuevo Base de Datos, luego haga clic en OK.'
        else:        
            title=str("You Are Here → Create New Database")
            msg='Enter a Name For This New Database, Then Click OK.'
        new_db=my_askstring(title, msg)
        if new_db=="" or new_db==None:return
        new_db=new_db.replace(" ","_")
        DB_Name.set(new_db)
        tbl_menu.delete(0,END)
        Active_Table.set("")
        db_file=os.path.join(DB_Path.get(), str(new_db+".db"))
        if not Database.database_exist(db_file):
            try:
                conn=Database.create_connection(db_file)
                if Language.get()=="Spanish":
                    title1='<Crear Nueva Base de Datos>'
                    msg=new_db+' Creado con éxito!'
                    title2='Estás aquí → Nueva Base de Datos Creada → '+new_db
                else:    
                    title1='<Create New Database> '
                    msg=new_db+' Created Successfully!\n'
                    title2="You Are Here → New Database Created → "+new_db
                messagebox.showinfo(title1+" "+new_db, msg)
                Active_DB.set(db_file)
                conn.close()
                root.title(title2)
                root.update()
                populate_db_menu()
                config_menu(None)
            except sqlite3.Error as e:
                if Language.get()=="Spanish":
                    title='<Crear Nueva Base de Datos> '
                    msg1='¡'+new_db+' No Fue Creado!\n'
                else:
                    title='<Create New Database> '
                    msg1=new_db+' Was Not Created!\n'
                msg2=f"Error: '{e}'"
                messagebox.showerror(title+ new_db, msg1+msg2)
                return
            finally:
                if conn:conn.close()
        else:        
            if Language.get()=="Spanish":
                title='<Crear Nueva Base de Datos> '+ new_db
                msg='¡La Base de Datos ' +new_db+ ' ya existe!'
            else:    
                title='<Create New Database> '+ new_db
                msg=new_db+' Database Already Exist!'
            messagebox.showinfo(title, msg)
    def populate_tbl_menu(db_path,db_name):
        Database.destroy_widgets()
        set_default_colors() 
        change_colors("all")
        DB_Path.set(db_path)
        Active_DB.set(os.path.join(db_path, db_name))
        DB_Name.set(os.path.splitext(db_name)[0])# Remove File Extension
        if DB_Name.get()!="":  
            Database_Ini('read',DB_Name.get(),None,None,None)
        Active_Table.set('')
        if Language.get()=="Spanish":title='ESTÁ AQUÍ → '+DB_Name.get()+' de Base de Datos → Seleccione una Tabla'
        else:title="You Are Here → Database "+DB_Name.get() +" → Select A Table"    
        root.title(title)
        root.update()
        tbl_menu.delete(0, END)
        tbls=Database.fetch_tables()
        num_tbls=0
        for name in tbls:
            if name[0]!="sqlite_sequence":
                tbl_menu.add_command(label=name[0],command=lambda a=name[0]:Database.exec_tbl_item(a))
                tbl_menu.add_separator()
                num_tbls+=1
        if num_tbls==0:
            if Language.get()=="English":
                menubar.entryconfig("     Select Table     ", state="disabled")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
            elif Language.get()=="Spanish":    
                menubar.entryconfig("     Seleccionar Tabla     ", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
        else:
            if Language.get()=="English":
                menubar.entryconfig("     Select Table     ", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
            elif Language.get()=="Spanish":    
                menubar.entryconfig("     Seleccionar Tabla     ", state="normal")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
        config_menu('db_selected')
    def delete_selected_db(db_name):
        try:
            db_file=os.path.join(DB_Path.get(), db_name)
            if os.path.exists(db_file):os.remove(db_file)# Delete The Database File
            db_name=db_name.split(".")[0]# Remove The File Extension
            Database_Ini("delete ini",db_name,None,None)# Delete ini File Associated With Deleted Database
            if db_file==Active_DB.get():
                Active_DB.set("")
                DB_Name.set("")
                Active_Table.set("")
            populate_db_menu()
            tbl_menu.delete(0,"end")
            config_menu('db_deleted')
            if Language.get()=="Spanish":
                title='<Eliminar la base de datos> '+db_name
                msg=db_name+' eliminado con éxito!'
            else:
                title='<Delete Database> '+db_name
                msg=db_name+' Deleted Successfully!'   
            messagebox.showinfo(title, msg)
        except Exception as ex:
            if Language.get()=="Spanish":
                title='<Eliminar la Base de Datos Seleccionada> '+db_name
                msg1='Error de eliminar la Base de Datos '+ db_name
            else:
                title='<Delete Selected Database> '+db_name
                msg1=db_name+' Error Deleting Database '+db_name+'\n'  
            msg2=f"\nError: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def set_language(lang):
        pgm_ini_file=os.path.join(DB_Path.get(), "My_Database.ini")
        config=configparser.ConfigParser()
        config.read(pgm_ini_file)
        try:
            config.add_section("Language")
            config.set("Language", "language", lang)# Language Is Database Related
            with open(pgm_ini_file, 'w') as configfile:
                config.write(configfile)
            configfile.close()
            Language.set(lang)
            populate_menus()
            set_menu_defaults()
            color_menu.delete(0,END)
            populate_color_menu()
            if Grid_Status.get()==0:populate_grid_menu('on')
            elif Grid_Status.get()==1:populate_grid_menu('off')
        except configparser.DuplicateSectionError:
            pass
    def select_language():
        pgm_ini_file=os.path.join(DB_Path.get(), "My_Database.ini")
        if not os.path.exists(pgm_ini_file):
            languages=["English","Spanish"]
            title="You Are Here → Select Program Language"
            msg='Please Select The Desired Program Language.'
            selected=my_askstring(title, msg, languages)
            if selected=="" or selected==None:return
            else: Database.set_language(selected)
        else:# Set Language
            config=configparser.ConfigParser()
            config.read(pgm_ini_file)
            try:
                lang=config.get("Language","language")# Language Is Database Related
                Language.set(lang)
                populate_menus()
                set_menu_defaults()
                color_menu.delete(0,END)
                populate_color_menu()
                if Grid_Status.get()==0:populate_grid_menu('on')
                elif Grid_Status.get()==1:populate_grid_menu('off')
            except configparser.NoOptionError:
                pass
    def import_database():
        try:
            if Language.get()=="English":txt="Sqlite Database Files"
            else:txt="Archivos de Base de Datos Sqlite"
            types=[(txt, DB_Extensions)]
            path=askopenfile(mode='r',initialdir="C:/",defaultextension="*.*",filetypes=types)
            if path is None:return
            file_name=os.path.basename(path.name)
            file_ext=os.path.splitext(file_name)[1]
            if file_ext not in DB_Extensions:
                if Language.get()=="English":
                    title="<Import Database>"
                    msg1="The File Extension Is Not Recognized By "+sqlite3.sqlite_version+"."
                    msg2="The Database File May Not Be Compatable!"
                    msg3="To Continue Press OK Or Cancel To Exit Import."
                else:    
                    title="<Importar Base de Datos>"
                    msg1="La extensión de archivo no es reconocida por "+sqlite3.sqlite_version+"."
                    msg2="¡Es posible que el Archivo de la Base de Datos no sea Compatible!"
                    msg3="Para Continuar, presione OK o Cancel para Salir de la Importación."
                msg=msg1+msg2+msg3     
                messagebox.askokcancel(title, msg)
            if os.path.isfile(path.name):
                src=path.name
                dst_path=str(Path(__file__).parent.absolute())
                dst=os.path.join( dst_path,file_name)
            if not os.path.isfile(dst):# Copy File To Database Directory
                shutil.copy(src, dst)
                file_name=os.path.splitext(dst)[0]
                new_path=file_name+".db"
                Active_DB.set(new_path)
                new_file_name=os.path.basename(new_path)
                new_name=os.path.splitext(new_file_name)[0]
                DB_Name.set(new_name)
                os.rename(dst, new_path)
                DB_Path.set(dst_path)
            if Language.get()=="Spanish":
                title='<Importar Base de Datos>'
                msg='"La Importación de la Base de Datos se realizó Correctamente'
            else:
                title="<Import Database>"
                msg="Import Database Succeeded."
            messagebox.showinfo(title, msg)
            Active_Table.set("")
            populate_db_menu()
            set_default_colors()
            change_colors("all")
            tbls=Database.fetch_tables()
            for name in tbls:# Write Table .ini Sections
                Active_Table.set(name[0])
                if name[0]!="sqlite_sequence":Database_Ini('write',DB_Name.get(),name[0],None,None)
            Active_Table.set("")    
            return
        except Exception as ex:
            pass    
    def delete_database():
        Database.destroy_widgets() 
        db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
        if len(db_files)==0:
            if Language.get()=="Spanish":
                title='<Eliminar la Base de Datos>'
                msg='¡No se Encuentran Archivos de Base de Datos!'
            else:
                title="<Delete Database>"
                msg="No Database Files Found!"
            messagebox.showerror(title, msg)
            return
        if Language.get()=="Spanish":
            title='Estás aquí → Eliminar Base de Datos → '
            msg='Seleccione la Base de Datos para Eliminar, luego haga clic en OK.'
        else:
            title="You Are Here → Delete Database →"
            msg='Select The Database To Delete, Then Click OK.'
        root.title(title)
        root.update()
        selected=my_askstring(title, msg, db_files)
        if selected=="" or selected==None:return
        else: Database.delete_selected_db(selected)
    def cancel_new_table(item):
        Database.destroy_widgets()
        Edit_Definitions.set(False)
        if Language.get()=="Spanish":title='Estás Aquí → '+DB_Name.get()+' de Base de Ddatos → Crear Nueva Tabla Cancelada'
        else:title="You Are Here → Database "+DB_Name.get()+" → Create New Table Cancelled"
        root.title(title)
        root.update()
        if Active_Table.get()!="":
            Database.exec_tbl_item(Active_Table.get())# Populate Table With New Entry
            enable_menubar("all")
        config_menu(None)
    def fetchone_row(id):
        try:
            conn = sqlite3.connect(Active_DB.get())
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM "+Active_Table.get()+" WHERE id = "+id)
            row=cursor.fetchone()
            colm_data=list(row)
            conn.commit()    
            conn.close()
            return colm_data
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Recuperar Fila de Tabla>'
                msg1='¡No se pudo recuperar la Fila de la Tabla!'
            else:
                title="<Fetch Table Row>"
                msg1="Failed to Retrieve Table Row!\n"    
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def create_new_table(tbl_name=None):
        if Active_DB.get()=="":
            if Language.get()=="Spanish":
                title='<No se selecciona la Base de Datos>'
                msg='Se debe seleccionar una Base de Datos para continuar.\n¡Seleccione una Base de Datos y vuelva a intentarlo!'
            else:
                title='<No Database Selected>'
                msg='A Database Must Be Selected To Continue.\nPlease Select A Database And Try Again!'
            messagebox.showerror(title, msg)
            return
        colm_names=[]
        colm_data=[]
        colm_widths=[]
        colm_defs=[]
        if Edit_Definitions.get()==False:
            if Language.get()=="Spanish":
                title='Base de datos '+DB_Name.get()+' <Nuevo Nombre de la Tabla>'
                msg='Ingrese un Nombre para la Nueva Tabla y Luego haga Clic en OK Cuando esté Listo.'
            else:
                title="Database "+DB_Name.get()+" <New Table Name>"
                msg='Enter A Name For The New Table Then Click OK When Ready.'
            new_tbl=my_askstring(title, msg)
            if new_tbl=="" or new_tbl==None:return
            tbl_name=new_tbl
            new_tbl=new_tbl.replace(" ","_")
            tables=Database.fetch_tables()
            for name in tables:# Check For Table Already Exist
                if name[0]==new_tbl:
                    if Language.get()=="Spanish":
                        title='<Tabla existe>'
                        msg='Tabla '+tbl_name+' ¡Ya existe!\nCancelando Crear nueva Tabla!'
                    else:
                        title="<Table Exist>"    
                        msg='Table ' + tbl_name+ ' Already Exist!\nCancelling Create New Table!'
                    messagebox.showerror(title, msg)
                    return
            if Language.get()=="Spanish":
                title=tbl_name+" Número de Columnas"
                msg1="Ingrese el Número de Columnas para la Nueva Tabla '"+tbl_name+"'.\n"
                msg2='Nota: Las Columnas de Fila e ID se incluyen Automáticamente.'
            else:    
                title=tbl_name+" Number Of Columns"
                msg1="Enter The Number Of Columns For New Table '"+tbl_name+"'.\n"
                msg2="Note: Row And ID Columns Are Included Automatically."
            msg=msg1+msg2
            num_colms=my_askinteger(title, msg, 5, 2, 100)# Initial Value. Min Value, Max Value
            if num_colms!=None:num_colms+=2# Add Row And ID Columns
            else:return
            for c in range(num_colms):
                if c==0:
                    if Language.get()=="Spanish":txt="Fila"
                    else:txt='Row'
                    colm_names.append(txt)
                    colm_data.append(1)
                elif c==1:    
                    colm_names.append("ID")
                    colm_data.append(1)
                else:    
                    if Language.get()=="Spanish":txt="Nombre de Columna "+str(c-1) 
                    else:txt="Column Name "+str(c-1)
                    colm_names.append(txt)
                    if Language.get()=="Spanish":entry_txt="Entrada "+ str(c-1)
                    else:entry_txt="Entry "+str(c-1)    
                    colm_data.append(entry_txt)
        else:
            num_colms=Num_Columns.get()
            colm_names,colm_defs=Database.get_table_schema()# Doesn't Return "Row" Which Isn't In Schema
            colm_data=Database.fetchone_row("1")
            colm_data.insert(0,1)
            if Language.get()=="Spanish":txt="Fila"
            else:txt='Row'
            colm_names.insert(0,txt)
            colm_defs.insert(0,"INTEGER PRIMARY KEY AUTOINCREMENT")
            for c in range(num_colms):
                colm_names[c]=colm_names[c].replace("_"," ")
            new_tbl=Active_Table.get()
        for c in range(num_colms):
            if c==0:colm_widths.append(5)
            elif c==1:colm_widths.append(5)
            else:colm_widths.append(25)
        Database.destroy_widgets()
        tk.Frame.scroll.canvas.configure(bg='#dddddd')
        tk.Frame.scroll.data_window.configure(bg='#dddddd')
        tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
        tk.Frame.scroll.canvas.yview_moveto(0)
        root.update()
        try:
            if num_colms==None:return
            global Column_Widgets
            Column_Widgets={}# Used To Destroy Entries And Change Color
            global Column_Names
            Column_Names=[]# StringVars
            name=[]
            entry_count=0
            row=0
            c=2
            # ROW # ********** Column Names **********
            row_entry=Entry(tk.Frame.scroll.data_window,bg='#dddddd',fg=Entry_Font_Color.get(), 
                font=root.font,width=colm_widths[0],highlightthickness=1,justify='center',relief='sunken') 
            row_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            row_entry.insert(0,colm_names[0])
            Column_Widgets[entry_count]=row_entry
            row_entry.grid(row=row, column=0, columnspan=1)
            if Edit_Definitions.get()==True:row_entry.config(state='disabled')
            txt_var=tk.StringVar()
            Column_Names.append(txt_var)
            name.append(0) # ID
            name[0]=Entry(tk.Frame.scroll.data_window,bg='#dddddd',textvariable=Column_Names[0],fg=Entry_Font_Color.get(), 
                font=root.font,width=colm_widths[1],highlightthickness=1,justify='center',relief='sunken')
            name[0].configure(highlightbackground='#000000', highlightcolor='#000000')
            name[0].insert(0,colm_names[1])
            entry_count+=1
            Column_Widgets[entry_count]=name[0]
            name[0].grid(row=row, column=1, columnspan=1)
            if Edit_Definitions.get()==True:name[0].config(state='disabled')
            for c, columns in enumerate(colm_names[2:],start=2):#  Column Names
                txt_var=tk.StringVar()
                Column_Names.append(txt_var)
                name.append(c-1)
                name[c-1]=Entry(tk.Frame.scroll.data_window,font=root.font,textvariable=Column_Names[c-1],
                    width=colm_widths[c],highlightthickness=1,bg='#c8ffff', fg='#000000',justify='center',relief='flat') 
                name[c-1].insert(0,columns)
                name[c-1]['validatecommand']=(name[c-1].register(Database.validate_entries),'%P','%d')
                val_cmd=(name[c-1].register(Database.on_validate_entries), '%P')
                name[c-1].config(validate="key", validatecommand=val_cmd)
                name[c-1].configure(highlightbackground='#000000', highlightcolor='#000000')
                entry_count+=1
                Column_Widgets[entry_count]=name[c-1]
                name[c-1].grid(row=row, column=c, columnspan=1)
                if Edit_Definitions.get()==True:name[c-1].config(state='disabled')
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
        except Exception as ex:
            if Language.get()=="Spanish":
                title="<Crear Nueva Tabla>"
                msg1="¡Crear Nueva Tabla Falló!\n"
                msg2=f"Error: '{ex}'"
            else:
                title='<Create New Table>'    
                msg1='Create New Table Failed!\n'
                msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            return
        root.update()
        try:
            global Widgets# Used To Destroy Entries And Change Color
            Widgets={}
            new_entries=[]
            append_buttons=[]
            if Language.get()=="Spanish":
                def_zero="Tipo de Dato"
            else:def_zero="Data Type"    
            definitions=[def_zero,"BLOB","BLOB NOT NULL","INTEGER","INTEGER NOT NULL",
                         "NUMERIC","NUMERIC NOT NULL","REAL","REAL NOT NULL","TEXT","TEXT NOT NULL"]
            define_cbo=[]
            global Column_Data
            Column_Data=[]# StringVars
            global Column_Defines
            Column_Defines=[]
            entry_count=0
            if Language.get()=="Spanish":
                btn_text="Adjuntar"
            else:btn_text="Attach"    
            row=1
            # Row, Row 1, Column 0 # ********** Column Data Row 1 **********    
            row_entry=Entry(tk.Frame.scroll.data_window,bg='#dddddd',fg=Entry_Font_Color.get(), 
                font=root.font,width=colm_widths[0],highlightthickness=1,justify='center',relief='sunken') 
            row_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            row_entry.insert(0,colm_data[0])
            Widgets[entry_count]=row_entry
            row_entry.grid(row=row, column=0, columnspan=1)
            if Edit_Definitions.get()==True:row_entry.config(state='disabled')
            # ID, ROW 1, Column 1    
            id_entry=Entry(tk.Frame.scroll.data_window,bg='#dddddd',fg=Entry_Font_Color.get(), 
                font=root.font,width=colm_widths[1],highlightthickness=1,justify='center',relief='sunken')
            id_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            id_entry.insert(0,colm_data[1])
            entry_count+=1
            Widgets[entry_count]=id_entry
            id_entry.grid(row=row, column=1, columnspan=1)
            if Edit_Definitions.get()==True:id_entry.config(state='disabled')
            # Data Entry Fields, Row 1, Columns 2 - num_colms    
            for c, columns in enumerate(colm_data[2:],start=2):#  Column Names
                row=1
                txt_var=tk.StringVar()
                Column_Data.append(txt_var)
                new_entries.append(c-2)
                new_entries[c-2]=Entry(tk.Frame.scroll.data_window,textvariable=Column_Data[c-2],bg='#c8ffff',fg='#000000', 
                    font=root.font,width=colm_widths[c],highlightthickness=1,justify='center',relief='sunken')
                new_entries[c-2].configure(highlightbackground='#000000', highlightcolor='#000000')
                new_entries[c-2].insert(0,columns)
                new_entries[c-2].grid(row=row, column=c, columnspan=1)
                if Edit_Definitions.get()==True:new_entries[c-2].config(state='disabled')
                entry_count+=1
                Widgets[entry_count]=new_entries[c-2]
                root.update()
                row=2 # Column Definitions 
                cbo_var=tk.StringVar()
                Column_Defines.append(cbo_var)
                define_cbo.append(c-2)
                define_cbo[c-2]=ttk.Combobox(tk.Frame.scroll.data_window,textvariable=Column_Defines[c-2],
                                             state = "readonly",justify="center",font=root.font)
                define_cbo[c-2]['values']=definitions
                if Edit_Definitions.get()==False:define_cbo[c-2].current(0)
                else:define_cbo[c-2].set(colm_defs[c])
                define_cbo[c-2].grid(row=row, pady=(5,0),column=c, columnspan=1)
                entry_count+=1
                Widgets[entry_count]=define_cbo[c-2]
                row=3 # Attach File Buttons
                if Edit_Definitions.get()==False:
                    append_buttons.append(c-2)
                    append_buttons[c-2]=Button(tk.Frame.scroll.data_window, text=btn_text,font=root.font,fg='#000000',bg='#dcdcdc',
                                                command=lambda a=Column_Data[c-2],b=Column_Defines[c-2]:Database.append_file_to_entry(a,b))
                    append_buttons[c-2].grid(row=row, pady=(5,0),column=c, columnspan=1)
                    entry_count+=1
                    Widgets[entry_count]=append_buttons[c-2]
                    row=4
                    if c==2:
                        row_space=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                                bg= '#dddddd',anchor="w",justify='left')
                        row_space.grid_rowconfigure(row, minsize=100)
                        row_space.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
                        entry_count+=1
                        Widgets[entry_count]=row_space
                    row=5
            row_space1=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                       bg= '#dddddd',anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space1
            if Edit_Definitions.get()==False:
                if Language.get()=="Spanish":title="Usted está aquí → Base de Datos "+DB_Name.get()+ " → Crear Nueva Tabla → "+new_tbl
                else:title=str("You Are Here → Database "+DB_Name.get()+" → Create New Table → "+new_tbl) 
                root.title(title)
                config_menu(None)
                root.update()
                if Language.get()=="Spanish":
                    msg1="Reemplace el Nombre de Columna y los campos de Entrada anteriores con sus datos.\n"
                    msg2="Asegúrese de seleccionar el tipo de datos para cada columna. Puede adjuntar archivos como\n"
                    msg3="música, video, foto, documentos de texto y archivos PDF. Al hacer doble clic en la ruta\n" 
                    msg4="del campo adjunto en la vista de tabla, se intentará abrir el archivo. Cuando haya terminado,\n" 
                    msg5="haga clic en Cancelar o Guardar tabla. Notas: Al ejecutar archivos adjuntos con el tipo\n"
                    msg6="de texto de datos seleccionado, solo se ejecuta el archivo en su ubicación actual. Archivos\n"
                    msg7="adjuntos con tipo de datos BLOB Copia el archivoen el directorio de la base de datos en\n"
                    msg8="la carpeta 'Archivos adjuntos' y luego ejecuta esa copia."
                    msg=msg1+msg2+msg3+msg4+msg5+msg6+msg7+msg8
                elif Language.get()=="English":
                    msg1="Replace The Column Names And Entry Fields Above With Your Data. Make Sure To Select\n"
                    msg2="The Data Type For Each Column First. You Can Attach File Paths Such As Music, Video, Photo,\n"
                    msg3="Text Document And PDF File. Double Clicking The Attached Field Name In Table View Will\n" 
                    msg4="Attempt To Open The File. When Finished, Click Cancel Or Save Table.\n"
                    msg5="Notes: Executing Attached Files With Data Type Text Selected Only Executes The File In\n"
                    msg6="It's Present Location. Attached Files With Data Type BLOB Copies The File To The Database\n"
                    msg7="Directory In Folder 'Attachments' And Then Executes That Copy."
                    msg=msg1+msg2+msg3+msg4+msg5+msg6+msg7
            else:
                if Language.get()=="Spanish":title="Usted está aquí → Base de Datos "+DB_Name.get()+ " → Editar Definiciones de Columna → "+new_tbl
                else:title=str("You Are Here → Database "+DB_Name.get()+" → Edit Column Definitions → "+new_tbl) 
                root.title(title)
                config_menu(None)
                root.update()
                if Language.get()=="Spanish":
                    msg1="Cambie las Definiciones de Columna como desee, luego presione Guardar para continuar o Cancelar.\n"
                    msg2="Nota: Se Muestran las Definiciones de las Columnas Actuales."
                elif Language.get()=="English":
                    msg1="Change The Column Definitions As Desired, Then Press Save To Continue Or Cancel.\n"
                    msg2="Note: Present Column Definitions Are Shown."
                msg=msg1+msg2  
            row=6
            lbl1=Label(tk.Frame.scroll.data_window,text=msg,font=root.font,fg=Entry_Font_Color.get(),
                       bg='#dddddd',anchor="w",justify='left')
            lbl1.grid_rowconfigure(row, minsize=100)
            lbl1.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=lbl1
            row=7
            root.update()
            row_space2=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                       bg='#dddddd',anchor="w",justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=2, columnspan=num_colms,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space2
            if Language.get()=="Spanish":
                txt='Cancelar'
            else:txt="Cancel"
            row=11    
            cancel=Button(tk.Frame.scroll.data_window, text=txt,font=root.font,fg='#000000',bg='#dcdcdc',
                    command=lambda:Database.cancel_new_table("Cancel Table"))
            cancel.grid_rowconfigure(row, minsize=10)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=cancel
            if Language.get()=="Spanish":
                txt="Guardar"
            else:txt="Save"    
            save=Button(tk.Frame.scroll.data_window, text=txt,font=root.font,fg='#000000', bg='#dcdcdc',
                command=lambda:Database.save_new_table(new_tbl))
            save.grid_rowconfigure(row, minsize=10)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=save
            Num_Columns.set(num_colms)# Includes Row And ID Column.
            disable_menubar("all")
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(1)
        except Exception as ex:
            if Language.get()=="Spanish":
                title="<Crear Nueva Tabla>"
                msg1="¡Crear Nueva Tabla Falló!\n"
                msg2=f"Error: '{ex}'"
            else:
                title='<Create New Table>'    
                msg1='Create New Table Failed!\n'
                msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            Num_Columns.set(0)
            enable_menubar("all")
            config_menu(None)
    def delete_selected_tbl(tbl):
        try:
            conn=Database.create_connection(Active_DB.get())            
            cursor=conn.cursor()
            cursor.execute("DROP TABLE "+tbl)
            tbl_menu.delete(0, END)
            tbls=Database.fetch_tables()
            for name in tbls:
                if name[0]!="sqlite_sequence":
                    tbl_menu.add_command(label=name[0],command=lambda a=name[0]:Database.exec_tbl_item(a))
                    tbl_menu.add_separator()
            conn.commit()
            if DB_Name.get()!="" and tbl!="":  
                Database_Ini('delete section',DB_Name.get(),tbl,None,None)
            if tbl==Active_Table.get():
                Database.destroy_widgets()
                Active_Table.set("")
            if Language.get()=="Spanish":
                msg='¡Tabla '+tbl+' eliminada con éxito!'
                title1='<Eliminar tabla> '+tbl
                title2='Estás Aquí → '+DB_Name.get()+' de Base de Datos → '+'Eliminar tabla '+tbl
            else:
                msg=tbl+' Table Deleted Successfully!'
                title1='<Delete Table> '+tbl
                title2="You Are Here → Database "+DB_Name.get()+" → Delete Table "+tbl    
            messagebox.showinfo(title1, msg)
            root.title(title2)
            root.update()
            config_menu(None)
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                msg1='Error de eliminación de la Tabla '+tbl+'\n'
                title='<Eliminar tabla seleccionada> '+tbl
            else:
                msg1='Error Deleting Table '+tbl+'\n'
                title='<Delete Selected Table> '+tbl
            msg2=f"\nError: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def delete_table():
        try:# Retrieve The Tables And Populate Combobox With Choices
            num_tbls=Database.get_num_tbls()
            if num_tbls==0:return
            conn=Database.create_connection(Active_DB.get())            
            cursor=conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables=[]
            for name in sorted(cursor.fetchall()):
                if name[0]!="sqlite_sequence":tables.append(name[0])
            active_tbl=Active_Table.get()    
            for i,t in enumerate(tables):
                if Active_Table.get()!="":
                    if t==active_tbl:
                        current=i
                        break
                else:current=0
            conn.commit()    
            conn.close()
            if len(tables)==0:return
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Eliminar tabla>'
                msg1='¡No se pudo recuperar los nombres de las Tabla!'
            else:
                title="<Delete Table>"
                msg1="Failed to retrieve Table Names!\n"    
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
        if Language.get()=="Spanish":
            title='Estás Aquí → '+DB_Name.get()+' de Base de Datos → Eliminar tabla → '
            msg='Seleccione la Tabla que desea Eliminar, luego haga clic en OK.'
        else:
            title="You Are Here → Database "+DB_Name.get()+" → Delete Table →"
            msg='Select The Table You Wish To Delete, Then Click OK.'    
        selected=my_askstring(title, msg, tables)
        if selected=="" or selected==None:return
        else: Database.delete_selected_tbl(selected)
    def rename_table():
        if Active_Table.get()=="":
            if Language.get()=="Spanish":
                title='<'+DB_Name.get()+' / sin tabla seleccionada>'
                msg1='Se debe seleccionar una tabla para continuar.'
                msg2='¡Seleccione una tabla y vuelva a intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        else:
            old_name=Active_Table.get().replace("_"," ")
            if Language.get()=="Spanish":
                title='Estás aquí → '+DB_Name.get()+' de Base de Datos → Cambiar el Nombre de la Tabla → '+old_name
                ask_title='<Cambiar la Tabla '+old_name+'>'
                ask_prompt="Introduzca un Nuevo Nombre para "+old_name+"."
            else:
                title="You Are Here → Database "+DB_Name.get()+" → Rename Table → "+old_name
                ask_title="<Rename Table "+ old_name+">"
                ask_prompt="Enter A New Name For "+old_name+"."
            root.title(title)
            root.update()
            new_name=my_askstring(ask_title, ask_prompt)
            if new_name=="" or new_name==None:return
        try:
            new_name=new_name.replace(" ","_")    
            conn=Database.create_connection(Active_DB.get())            
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM sqlite_master")
            tables=cursor.fetchall()
            if len(tables)!=0:
                cursor.execute("ALTER TABLE "+ Active_Table.get()+ " RENAME TO " + new_name)# Rename Table In Database
                conn.commit()
                conn.close()
            else:
                conn.close()
                return
            if DB_Name.get()!="" and Active_Table.get()!="":  
                Database_Ini("rename section",DB_Name.get(),Active_Table.get(),new_name,None)# Rename Table Section In .ini File
                Active_Table.set(new_name)
                Database.populate_tbl_menu(DB_Path.get(),DB_Name.get()+".db")                
                Database.exec_tbl_item(new_name)# Populate Table With New Entry
            if Language.get()=="Spanish":
                title='<Renombrar Tabla> '+Active_Table.get()
                msg='Cambiar el Nombre a '+Active_Table.get()+' Exitoso'
            else:
                title='<Rename Table> '+Active_Table.get()
                msg="Rename To "+Active_Table.get()+' Successful'
            messagebox.showinfo(title, msg)
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Renombrar Tabla> '+Active_Table.get()
                msg1='No se pudo cambiar el Nombre de '+Active_Table.get()
            else:
                title='<Rename Table> '+Active_Table.get()
                msg1="Failed To Rename "+Active_Table.get()+'\n'    
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def fetch_tables():
        try:
            conn=Database.create_connection(Active_DB.get())            
            cursor=conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return sorted(cursor.fetchall())
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Tablas de busca>'
                msg1='No se pudo recuperar tablas de '+DB_Name.get()+'\n'
            else:
                title='<Fetch Tables>'
                msg1="Failed To Retrieve "+DB_Name.get()+" Tables\n"  
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
    def get_all_ids():
        id_list=[]# Get All IDs 
        try:
            conn=Database.create_connection(Active_DB.get())
            data=conn.execute(f'SELECT * FROM {Active_Table.get()}').fetchall()
            for r in range(len(data)):
                id=str(data[r][:1]).replace("(","").replace(")","").replace(",","")
                id_list.append(id)# Insert ID's To List
            if conn:conn.close()
            return  id_list
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Recuperar Entradas de Tabla>'
                msg1='No se pudo Recuperar los Datos de '+Active_Table.get()+'\n'
            else:    
                title='<Retrieve Table Entries>'
                msg1="Failed To Retrieve "+Active_Table.get()+" Data\n"
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def delete_selected_entry(id):
        try:
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute("DELETE FROM "+ Active_Table.get()+" WHERE id="+id)
            conn.commit()
            conn.close()
            Database.exec_tbl_item(Active_Table.get())# Populate Table With New Entry
            if Language.get()=="Spanish":
                title='<Eliminar '+Active_Table.get()+', ID = '+id+">"
                msg1=DB_Name.get()+' de base de datos, Tabla '+Active_Table.get()+', ID='+id+'\n'
                msg2='Entrada de Tabla '+Active_Table.get()+' ID = '+id+' eliminado correctamente!'
            else:    
                title="<Delete "+Active_Table.get()+', ID = '+id+">"
                msg1='Database '+DB_Name.get()+', Table '+Active_Table.get()+', ID='+id+'\n'
                msg2='Table Entry '+Active_Table.get()+' ID = '+id+' Deleted Successfully!'
            messagebox.showinfo(title, msg1+msg2)
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Deleccionar entrada seleccionada>'
                msg1='No se pudo eliminar el '+DB_Name.get()+' ID = '+id+'\n'
            else:    
                title='<Delect Selected Entry>'
                msg1='Failed to Delete '+DB_Name.get()+' ID = '+id+'\n'
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def delete_tbl_row():
        if Active_Table.get()=="" or Num_Columns.get()==0:
            if Language.get()=="Spanish":
                title='<Eliminar Fila de Tabla>'
                msg1='Se debe seleccionar una Tabla para continuar.'
                msg2='¡Seleccione una Tabla y vuelva a intentarlo!'
            else:    
                title='<Delete Table Row>'
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        else:
            all_ids=Database.get_all_ids()
            if Language.get()=="Spanish":
                title='Eliminar Fila de Tabla Seleccionada'
                msg1="Seleccione el 'ID' Asociado con la Fila que desea Eliminar.\n"
                msg2='Luego haga Clic en OK para Continuar.'
            else:    
                title="Delete Selected Table Row"
                msg1="Select The 'ID' Associated With The Row To Delete.\n"
                msg2='Then Click OK To Continue.'
            msg=msg1+msg2    
            id=my_askstring(title, msg, all_ids)
            if id==None or id=="":return
            Database.delete_selected_entry(id)
    def save_new_column(name,data,define,id):
        if Language.get()=="Spanish":
            if name=="":
                msg1="¡Nombre de la Columna No Puede Estar en Blanco!\n"
                msg2="¡Por Favor, Inténtelo de Nuevo!"
                msg=msg1+msg2
                messagebox.showerror("Falta Nombre de la Columna", msg)
                return
            if define=="Tipo de Dato":
                msg1="¡Nombre de la Columna "+name+" Tipo de Datos No Está Seleccionado!\n"
                msg2="¡Por Favor, Inténtelo de Nuevo!"
                msg=msg1+msg2
                messagebox.showerror("Tipo de Datos Faltante "+name, msg)
                return
        else:# English        
            if name=="":
                msg="Column Name Cannot Be Blank. Please Try Again!"
                messagebox.showerror("Missing Column Name "+name, msg)
                return
            if define=="Data Type":
                msg="Column Name "+name+" Data Type Is Not Selected. Please Try Again!"
                messagebox.showerror("Missing Data Type "+name, msg)
                return
        try:
            if data=="":data="None"
            name=name.replace(" ","_")
            colm_defined=name+" "+define
            conn = sqlite3.connect(Active_DB.get())
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE "+Active_Table.get()+ " ADD COLUMN "+ colm_defined)
            conn.commit()
            query="UPDATE "+Active_Table.get()+" SET "+name+" = ? Where id = ?"
            colm_data=(data, id)
            cursor.execute(query, colm_data)
            conn.commit()
            conn.close()
            Database.exec_tbl_item(Active_Table.get())# Populate Table With New Entry
            tk.Frame.scroll.canvas.xview_moveto(1.0)# Position Scrollbar To max x
            tk.Frame.scroll.canvas.yview_moveto(0)
            if Language.get()=="English":messagebox.showinfo("Add New Column", "New Column Created Sucessfully.")
            else:messagebox.showinfo("Crear nueva columna", "Nueva columna creada con éxito.")
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Agregar nueva columna>'
                msg1='Error al agregar la columna '+DB_Name.get()+' ID = '+id+'\n'
            else:    
                title='<Add New Column>'
                msg1='Failed to Add Column '+DB_Name.get()+' ID = '+id+'\n'
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
            return
        finally:
            if conn:conn.close()
    def add_new_column():
        if Language.get()=="Spanish":
            txt=", Nueva Columna"
            msg1="La Nueva Columna se agregará al final de "+Active_Table.get()+"."
            msg2=" Haga clic en OK para continuar o en Cancel para salir de la Nueva Columna."
        else:
            txt=", New Column"
            msg1="The New Column Will Be Added To The End Of "+Active_Table.get()+"."
            msg2=" Click OK To Continue Or Cancel To Exit New Column."
        msg=msg1+msg2    
        status=messagebox.askokcancel("Database "+DB_Name.get()+", Table "+Active_Table.get()+txt, msg)
        if not status:return
        tk.Frame.scroll.canvas.configure(bg='#dddddd')
        tk.Frame.scroll.data_window.configure(bg='#dddddd')
        Database.destroy_widgets()
        root.update()
        # ******************** Column Names ********************
        all_rows=Database.retrieve_table_entries()
        num_columns=all_rows.shape[1]-1# Dont include ID
        if Language.get()=="Spanish":colm_name="Columna "+str(num_columns)+" Nombre"
        else:colm_name="Column "+str(num_columns)+" Name"
        tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
        tk.Frame.scroll.canvas.yview_moveto(0)
        global Column_Widgets
        Column_Widgets={}# Used To Destroy Entries And Change Color
        entry_count=0
        row=0
        try:
            # Row
            row_entry=Entry(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                font=root.font,width=5,highlightthickness=1,justify='center',relief='sunken') 
            row_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            if Language.get()=="Spanish":txt="Fila"
            else:txt='Row'    
            row_entry.insert(0,txt)
            Column_Widgets[entry_count]=row_entry
            row_entry.grid(row=row, column=0, columnspan=1)
            # ID
            id=Entry(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                font=root.font,width=5,highlightthickness=1,justify='center',relief='sunken')
            id.configure(highlightbackground='#000000', highlightcolor='#000000')
            id.insert(0,"ID")
            entry_count+=1
            Column_Widgets[entry_count]=id
            id.grid(row=row, column=1, columnspan=1)
            # New Column Name
            name=Entry(tk.Frame.scroll.data_window,font=root.font,
                width=30,highlightthickness=1,bg='#c8ffff', fg='#000000',justify='center',relief='flat') 
            name.insert(0,colm_name)
            name.configure(highlightbackground='#000000', highlightcolor='#000000')
            entry_count+=1
            Column_Widgets[entry_count]=name
            name.grid(row=row, column=2, columnspan=1)
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
        except Exception as ex:
            if Language.get()=="Spanish":
                title="<Crear Nueva Tabla>"
                msg1=Active_Table.get()+" ¡Crear Nueva Tabla Falló!\n"
                msg2=f"Error: '{ex}'"
            else:
                title='<Create New Table>'    
                msg1=Active_Table.get()+' Create New Table Failed!\n'
                msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            Active_Table.set("")
            return
        try:
            global Widgets# Used To Destroy Entries And Change Color
            Widgets={}
            if Language.get()=="Spanish":
                definitions=["Tipo de Dato","BLOB","INTEGER","NUMERIC","REAL","TEXT"]
            else:    
                definitions=["Data Type","BLOB","INTEGER","NUMERIC","REAL","TEXT"]
            if Language.get()=="Spanish":
                colm_txt="Columna "+str(num_columns)+" Ancho"
                entry_txt="Entrada "+str(num_columns)
            else:
                colm_txt=str("Column "+str(num_columns)+" Width")
                entry_txt="Entry "+str(num_columns)    
            entry_count=0
            if Language.get()=="Spanish":
                btn_text="Adjuntar"
            else:btn_text="Attach"    
            row=1
            # ******************** Data Entry Fields ********************
            # Row    
            row_entry=Entry(tk.Frame.scroll.data_window,bg='#dddddd',fg=Entry_Font_Color.get(), 
                font=root.font,width=5,highlightthickness=1,justify='center',relief='sunken') 
            row_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            row_entry.insert(0,"1")
            Widgets[entry_count]=row_entry
            row_entry.grid(row=row, column=0, columnspan=1)
            # ID
            id_entry=Entry(tk.Frame.scroll.data_window,bg='#dddddd',fg=Entry_Font_Color.get(), 
                font=root.font,width=5,highlightthickness=1,justify='center',relief='sunken')
            id_entry.configure(highlightbackground='#000000', highlightcolor='#000000')
            id=str(Database.get_all_ids()[0])
            id_entry.insert(0,id)
            entry_count+=1
            Widgets[entry_count]=id_entry
            id_entry.grid(row=row, column=1, columnspan=1)
            # New Column Data
            txt_var=tk.StringVar()
            data=Entry(tk.Frame.scroll.data_window,textvariable=txt_var,bg='#c8ffff',fg='#000000', 
                font=root.font,width=30,highlightthickness=1,justify='center',relief='sunken')
            data.configure(highlightbackground='#000000', highlightcolor='#000000')
            data.insert(0,entry_txt)
            data.grid(row=row, column=2, columnspan=1)
            entry_count+=1
            Widgets[entry_count]=data
            # New Column Definition    
            row=2
            cbo_var=tk.StringVar()
            defined=ttk.Combobox(tk.Frame.scroll.data_window,textvariable=cbo_var,state = "readonly",justify="center",font=root.font)
            defined['values']=definitions
            if Language.get()=="English":defined.set("Data Type")
            else:defined.set("Tipo de Dato")
            defined.grid(row=row, pady=(5,0),column=2, columnspan=1)
            entry_count+=1
            Widgets[entry_count]=defined
            # ******************** Attach File Buttons ********************    
            row=3
            attach_btn=Button(tk.Frame.scroll.data_window, text=btn_text,font=root.font,fg='#000000',bg='#dcdcdc',
                                        command=lambda a=txt_var,b=cbo_var:Database.append_file_to_entry(a,b))
            attach_btn.grid(row=row, pady=(5,0),column=2, columnspan=1)
            entry_count+=1
            Widgets[entry_count]=attach_btn
            row=4
            row_space=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                    bg= '#dddddd',anchor="w",justify='left')
            row_space.grid_rowconfigure(row, minsize=100)
            row_space.grid(row=row, column=2, columnspan=5,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space
            row=5
            row_space1=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                       bg= '#dddddd',anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=1, columnspan=5,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space1
            if Language.get()=="Spanish":title="Usted está aquí → Base de Datos "+DB_Name.get()+" → Tabla "+Active_Table.get()+" → Agregar Nueva Columna"
            else:title=str("You Are Here → Database "+DB_Name.get()+" → Table "+Active_Table.get()+ " → Add New Column")
            root.title(title)
            config_menu(None)
            if Language.get()=="Spanish":
                txt='Cancelar'
            else:txt="Cancel"
            row=6  
            cancel=Button(tk.Frame.scroll.data_window, text=txt,font=root.font,fg='#000000',bg='#dcdcdc',
                    command=lambda:Database.cancel_new_table("Cancel Table"))
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(40,0), columnspan=1,sticky=SW)
            entry_count+=1
            Widgets[entry_count]=cancel
            if Language.get()=="Spanish":
                txt="Guardar"
            else:txt="Save"
            save=Button(tk.Frame.scroll.data_window, text=txt,font=root.font,fg='#000000', bg='#dcdcdc',
                command=lambda:Database.save_new_column(name.get(),data.get(),defined.get(),id))
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=2, padx=(0,40), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=save
            disable_menubar("all")
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(1)
            root.update()
        except Exception as ex:
            if Language.get()=="Spanish":
                title="<Agregar Nueva Columna>"
                msg1=Active_Table.get()+" ¡Crear Nueva Columna Falló!\n"
                msg2=f"Error: '{ex}'"
            else:
                title='<Add New Column>'    
                msg1=Active_Table.get()+' Add New Column Failed!\n'
                msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            enable_menubar("all")
            config_menu(None)
    def drop_column():
        colm_names,colm_definitions=Database.get_table_schema()# Doesn't Return "Row" Which Isn't In Schema
        colm_names.pop(0)# Remove ID, Cannot Be Renamed
        colm_names=[s.replace('_', ' ') for s in colm_names]
        if Language.get()=="Spanish":    
            title="Eliminar Columna"
            msg1='Seleccione el Nombre de la Columna que desea Eliminar.\n'
            msg2='Haga clic en OK para Continuar.'
        else:
            title="Delete Table Column"
            msg1='Select The Column Name Of The Column You Wish To Delete.\n'
            msg2='Then Click OK To Continue.'
        msg=msg1+msg2
        name=my_askstring(title, msg, colm_names)
        if name==None or name=="":return
        name=name.replace(" ","_")
        try:
            conn=sqlite3.connect(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute("ALTER TABLE "+Active_Table.get()+" DROP COLUMN "+name)
            conn.commit()
            conn:conn.close()
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Eliminar Columna>'
                msg1='¡Error en la Eliminación de Columnas!'
            else:    
                title='<Delete Table Column>'
                msg1='Delete Table Column Failed!\n'
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
        Database.exec_tbl_item(Active_Table.get())# Populate Table With New Entry
        tk.Frame.scroll.canvas.xview_moveto(1.0)# Position Scrollbar To max x
        tk.Frame.scroll.canvas.yview_moveto(0)
        if Language.get()=="English":messagebox.showinfo("Delete Table Column", "Column Deletion Sucessfully.")
        else:messagebox.showinfo("Eliminar Columna", "Eliminación de Columnas con éxito.")
    def rename_column():
        colm_names,colm_definitions=Database.get_table_schema()# Doesn't Return "Row" Which Isn't In Schema
        colm_names.pop(0)# Remove ID, Cannot Be Renamed
        colm_names=[s.replace('_', ' ') for s in colm_names]
        if Language.get()=="Spanish":    
            title="Cambiar el Nombre de la Columna"
            msg1='Seleccione el Nombre de la Columna a la que desea Cambiar el Nombre.\n'
            msg2='Haga clic en OK para continuar.'
        else:
            title="Rename Table Column"
            msg1='Select The Name Of The Column You Wish To Rename\n'
            msg2='Then Click OK To Continue.'
        msg=msg1+msg2
        name=my_askstring(title, msg, colm_names)
        if name==None or name=="":return
        old_name=name.replace(" ","_")
        if Language.get()=="Spanish":    
            title="Cambiar el Nnombre de la Columna"
            msg1='Introduzca un Nuevo Nombre de Columna para esta Columna.\n'
            msg2='Haga clic en OK para continuar.'
        else:
            title="Rename Table Column"
            msg1='Enter A New Column Name For This Column.\n'
            msg2='Click OK To Continue.'
        msg=msg1+msg2
        new_name=my_askstring(title, msg)
        if new_name==None or new_name=="":return
        new_name=new_name.replace(" ","_")
        try:
            conn=sqlite3.connect(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute("ALTER TABLE "+Active_Table.get()+" RENAME COLUMN "+old_name+" TO "+new_name)
            conn.commit()
            conn:conn.close()
            Database.exec_tbl_item(Active_Table.get())# Populate Table With New Entry
            if Language.get()=="Spanish":messagebox.showinfo("Cambiar el Nombre de la Columna", "¡El cambio de Nombre de Columna se ha realizado correctamente!")
            else:messagebox.showinfo("Rename Table Column", "Column Rename Successful!")
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Cambiar el Nombre de la Columna>'
                msg1='¡Error al cambiar el nombre de la columna!'
            else:    
                title='<Rename Table Column>'
                msg1='Rename Table Column Failed!\n'
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
        finally:
            if conn:conn.close()
    def insert_into_table(tbl_name):
        if tbl_name=="":
            if Language.get()=="Spanish":
                title='<'+DB_Name.get()+' / sin Tabla seleccionada>'
                msg1='Se debe seleccionar una Tabla para continuar.'
                msg2='¡Seleccione una Tabla y vuelva a intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        tbl_name=tbl_name.replace(' ','_')
        if Column_Data[0].get()=="" and Column_Data[1].get()=="":
            if Language.get()=="Spanish":
                title='Insertar en la Tabla '+Active_Table.get()
                msg1='Columna 1 y Columna 2\n'
                msg2='¡Debe completarse para continuar!\n'
                msg3='¡Complete los campos faltantes!'
            else:    
                title='Insert Into '+Active_Table.get()+' Table'
                msg1='Column 1 and Column 2\n'
                msg2='Must Be Filled Out To Continue!\n'
                msg3='Please Fill Out The Missing Fields!'
            messagebox.showerror(title, msg1+msg2+msg3)
            return
        Num_Columns.set(Num_Columns.get()-1)
        colm_names=Database.retrieve_column_names()# Also Returns "Row" Which Isn't In Schema
        header=[]
        for c in range(2,len(colm_names)):
            name=str(colm_names[c]).replace(" ","_") 
            header.append(name)
        data=[]
        for d in range(Num_Columns.get()-1):
            if Column_Data[d].get()=="":Column_Data[d].set("None") 
            data.append(Column_Data[d].get())
        try:
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            names=""
            values=""
            for s in range(Num_Columns.get()-1):
                if s==1:
                    names+=header[s]+", "
                    values+='?, '
                elif s==Num_Columns.get()-2:
                    names+=header[s]
                    values+='?'
                else:    
                    values+='?, '
                    names+=header[s]+", "
            values=values.replace("'","")    
            cursor.execute("INSERT INTO " + tbl_name + " ("+names+") VALUES("+values+")",(data))
            conn.commit()
            conn.close()
            Active_Table.set(tbl_name)
            tbl_menu.delete(0,END)
            Database.populate_tbl_menu(DB_Path.get(),DB_Name.get()+".db")                
            Database.exec_tbl_item(tbl_name)# Populate Table With New Entry
            if Language.get()=="Spanish":
                title='<Agregar Nueva Fila>'
                msg1='Tabla de '+DB_Name.get()+' de Base de Datos '+tbl_name+'\n'
                msg2='¡Nueva Fila de Tabla creada con éxito!.'
            else:    
                title='<Add New Row>'
                msg1='Database '+DB_Name.get()+' Table '+tbl_name+'\n'
                msg2='New Row Created Successfully!.'
            messagebox.showinfo(title, msg1+msg2)
            enable_menubar("all")
            config_menu(None)
            return
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Agregar Nueva Fila>'
                msg1='Table = '+tbl_name+'\n'
                msg2='¡Crear Nueva Fila de Tabla Falló!\n'
            else:    
                title='<Add New Row>'
                msg1='Table = '+tbl_name+'\n'
                msg2='Add New Row Failed!\n'
            msg3=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def save_new_table(tbl_name):
        # Check For Missing Fields, Data Types
        if Language.get()=="Spanish":
            for c in range(Num_Columns.get()-2):
                if Column_Names[c].get()=="":
                    msg1="¡Nombre de la Columna "+str(c+1)+" No Puede Estar en Blanco!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Falta Nombre de la Columna "+str(c+1), msg)
                    return
                if Column_Defines[c].get()=="Tipo de Dato":
                    msg1="¡Nombre de la Columna "+str(c+1)+" Tipo de Datos No Está Seleccionado!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Tipo de Datos Faltante "+str(c+1), msg)
                    return
                if "NOT NULL" in Column_Defines[c].get() and Column_Data[c].get()=="":
                    msg1="¡Datos de Columna "+str(c+1)+" No puede estar en blanco!\n"
                    msg2="¡Por Favor, Inténtelo de Nuevo!"
                    msg=msg1+msg2
                    messagebox.showerror("Tipo de Datos Seleccionado "+Column_Defines[c].get(), msg)
                    return
        else:# English        
            for c in range(Num_Columns.get()-2):
                if Column_Names[c].get()=="":
                    msg="Column Name "+str(c+1)+" Cannot Be Blank. Please Try Again!"
                    messagebox.showerror("Missing Column Name "+str(c+1), msg)
                    return
                if Column_Defines[c].get()=="Data Type":
                    msg="Column Name "+str(c+1)+" Data Type Is Not Selected. Please Try Again!"
                    messagebox.showerror("Missing Data Type "+str(c+1), msg)
                    return
                if "NOT NULL" in Column_Defines[c].get() and Column_Data[c].get()=="":
                    msg="Column Data "+str(c+1)+" Cannot Be Blank. Please Try Again!"
                    messagebox.showerror("Selected Data Type "+Column_Defines[c].get(), msg)
                    return
        Num_Columns.set(Num_Columns.get()-1)
        defined_types=""
        colm_names=""
        queries=""
        null_queries=""
        header=[]
        data=[]
        header.append(Column_Names[0].get().replace(" ","_"))# ID
        for c in range(1,Num_Columns.get()):
            if Column_Data[c-1].get()=="":Column_Data[c-1].set("None") 
            data.append(Column_Data[c-1].get())
            if Column_Names[c].get()=="":Column_Names[c].set("None") 
            header.append(Column_Names[c].get().replace(" ","_"))#Spaces Not Allowed In Column Names
            if c==1:
                colm_names+=header[c]+", "
                queries+='?, '
                null_queries+='NULL, '
            elif c==Num_Columns.get()-1:
                colm_names+=header[c]
                queries+='?'
                null_queries+='NULL'
            else:    
                queries+='?, '
                null_queries+='NULL, '
                colm_names+=header[c]+", "
            if c==Num_Columns.get()-1:defined_types+=header[c]+" "+Column_Defines[c-1].get() 
            else:defined_types+=header[c]+" "+Column_Defines[c-1].get()+", "
        queries=queries.replace("'","")    
        null_queries=null_queries.replace("'","")    
        tbl_name=tbl_name.replace(' ','_')
        defined_types="ID INTEGER PRIMARY KEY AUTOINCREMENT, "+defined_types# Define Column 1
        try:
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({defined_types})")
            if Edit_Definitions.get()==False:
                cursor.execute(f"INSERT OR REPLACE INTO {tbl_name} ({colm_names}) VALUES({queries})", data)
                conn.commit()
                conn.close()
                Active_Table.set(tbl_name)
                tbl_menu.delete(0,END)
                set_default_colors()
                change_colors("all")
                if DB_Name.get()!="" and tbl_name!="":  
                    Database_Ini('write',DB_Name.get(),tbl_name,None,None)
                    Database.populate_tbl_menu(DB_Path.get(),DB_Name.get()+".db")                
                    Database.exec_tbl_item(tbl_name)# Populate Table With New Entry
                if Language.get()=="Spanish":
                    title='<Guardar nueva tabla>'
                    msg1='Tabla de '+DB_Name.get()+' de Base de Datos '+tbl_name+'\n'
                    msg2='¡Nueva Tabla Creada con éxito!.'
                else:    
                    title='<Save New Table>'
                    msg1='Database '+DB_Name.get()+' Table '+tbl_name+'\n'
                    msg2='New Table Created Successfully!.'
                messagebox.showinfo(title, msg1+msg2)
                enable_menubar("all")
                config_menu(None)
            else:# Edit Table Definitions
                # This Section will rename our 'original' table to old_table. 
                # Then recreate a new 'original' table with the new datatypes.
                # Delete Row 1 Which Is Only Used To Create New Table. Gets Reinserted Next Step.
                # Then insert all of the data from the old_table into the new 'original' table.
                # Then delete the old_table once verified ok.
                conn=sqlite3.connect(Active_DB.get())
                conn.execute("PRAGMA foreign_keys = OFF")
                cursor=conn.cursor()
                cursor.execute(f"ALTER TABLE {tbl_name} RENAME TO old_table")
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {tbl_name} ({defined_types})")
                cursor.execute(f"INSERT OR REPLACE INTO {tbl_name} ({colm_names}) VALUES({queries})", data)
                cursor.execute(f"DELETE FROM {tbl_name} WHERE id=1")
                cursor.execute(f"INSERT OR IGNORE INTO {tbl_name} SELECT * FROM old_table")
                cursor.execute("DROP TABLE old_table")
                conn.execute("PRAGMA foreign_keys = ON")
                conn.commit()
                conn.close()
                Edit_Definitions.set(False)    
                if DB_Name.get()!="" and tbl_name!="":  
                    Database_Ini('write',DB_Name.get(),tbl_name,None,None)
                    Database.populate_tbl_menu(DB_Path.get(),DB_Name.get()+".db")                
                    Database.exec_tbl_item(tbl_name)# Populate Table With New Entry
                if Language.get()=="English":
                    title='<Edit Column Definitions>'
                    msg='Editing Column Definitions Succeeded!'
                else:    
                    title='<Editar Definiciones de Columna>'
                    msg='¡La Edición de Definiciones de Columna se realizó Correctamente!'
                messagebox.showinfo(title, msg)
            return
        except sqlite3.Error as error:
            if Language.get()=="Spanish":
                title='<Guardar Nueva Tabla>'
                msg1='Tabla = '+tbl_name+'\n'
                msg2='¡Falló la Creación o Guardado de la Nueva Tabla!'
            else:    
                title='<Save New Table>'
                msg1='Table = '+tbl_name+'\n'
                msg2='Creating or Saving New Table Failed.\n'
            msg3=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def add_new_row():
        if Active_Table.get()=="":
            if Language.get()=="Spanish":
                title='<'+DB_Name.get()+' / Sin Tabla Seleccionada>'
                msg1='Se debe Seleccionar una Tabla para Continuar.'
                msg2='¡Seleccione una Tabla y Vuelva a Intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        try:
            if Language.get()=='Spanish':
                menubar.entryconfig('     Crear/Modificar Tabla     ', state="disabled")
                menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="normal")
                btn_txt='Adjuntar'
                save_txt='Guardar'
                cancel_txt='Cancelar'
            else:    
                menubar.entryconfig('     Create/Modify Table     ', state="disabled")
                menubar.entryconfig('     Create/Modify Table Entry     ', state="normal")
                btn_txt='Attach'
                save_txt='Save'
                cancel_txt='Cancel'
            colms=Num_Columns.get()
            row=Num_Rows.get()+1
            new_entries=[]# Widgets
            append_buttons=[]
            colm_names=Database.retrieve_column_names()# Also Returns "Row" Which Isn't In Schema
            Database.destroy_widgets() # Clear window For New Table
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(0)
            Num_Columns.set(len(colm_names))
            global Column_Widgets
            Column_Widgets={}# Used To Destroy Entries And Change Color
            name=[]
            wid=[]
            wid_items=["www.","https://","@",":/"]
            ids=Database.get_all_ids()
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM "+ Active_Table.get()+" WHERE id="+ids[0])
            id_entry=cursor.fetchall()
            new_list=['Row']# 
            for item in id_entry:new_list.extend(list(item))# Add 1 Element 'Row' To Array Inside List And Convert To List
            for c, columns in enumerate(new_list):# Define Column Widths Depending On Text
                if c==0:
                    _wid=int(Column_Widths[c]*1.2)# @ Difference Between Label And Entry Widths 
                    wid.append(_wid)# Label Widths Of The Same Value Are Larger Than Entry Widths (??)
                else:    
                    for item in wid_items:
                        if item in str(id_entry[0][c-1]):
                            _wid=int(Column_Widths[c]*2)
                            break
                        else:_wid=int(Column_Widths[c]*1.2)
                    wid.append(_wid)
            for c, columns in enumerate(colm_names):# Default Names
                name.append(c)
                name[c]=Entry(tk.Frame.scroll.data_window,font=root.font,width=wid[c],highlightthickness=Grid_Status.get(),
                    bg=Header_BG_Color.get(), fg=Header_Font_Color.get(),justify='center',relief='flat') 
                name[c].delete(0,END)
                name[c].insert(0,columns)
                name[c].configure(highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                Column_Widgets[c]=name[c]
                name[c].grid(row=0, column=c, columnspan=1)
                name[c].config(state= "disabled")
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            root.update()
            global Column_Defines
            Column_Defines=[]
            colm_names,colm_definitions=Database.get_table_schema()# Doesn't Return "Row" Which Isn't In Schema
            for c, defines in enumerate(colm_definitions):
                define_var=tk.StringVar()
                Column_Defines.append(define_var)
                define_var.set(defines)                
            global Column_Data
            Column_Data=[]# StringVars
            entry_count=len(Widgets)
            for c in range(colms-1):
                txt_var=tk.StringVar()
                Column_Data.append(txt_var)
                if c==0:
                    row_entry=Entry(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                        font=root.font,width=wid[c],borderwidth=1,justify='center',relief='sunken') 
                    row_entry.delete(0,END)
                    row_entry.insert(0,str(row))
                    Widgets[entry_count]=row_entry
                    row_entry.grid(row=row, column=c, columnspan=1)
                    row_entry.config(state= "disabled")
                    id_entry=Entry(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                        font=root.font,width=wid[c+1],borderwidth=1,justify='center',relief='sunken')
                    id_entry.delete(0,END)
                    id_entry.insert(0,"?")
                    entry_count+=1
                    Widgets[entry_count]=id_entry
                    id_entry.grid(row=row, column=c+1, columnspan=1)
                    id_entry.config(state= "disabled")
                else:
                    new_entries.append(c-1)
                    new_entries[c-1]=Entry(tk.Frame.scroll.data_window,textvariable=Column_Data[c-1],bg= '#c8ffff',fg='#000000', 
                        font=root.font,width=wid[c+1],highlightthickness=1,justify='center',relief='sunken')
                    new_entries[c-1].configure(highlightbackground='red', highlightcolor='red')
                    new_entries[c-1].grid(row=row, column=c+1, columnspan=1)
                    entry_count+=1
                    Widgets[entry_count]=new_entries[c-1]
                    append_buttons.append(c-1)
                    append_buttons[c-1]=Button(tk.Frame.scroll.data_window, text=btn_txt,font=root.font,fg='#000000',bg='#dcdcdc',
                                               command=lambda a=Column_Data[c-1],b=Column_Defines[c-1]:Database.append_file_to_entry(a,b))
                    append_buttons[c-1].grid(row=row+1, pady=(5,0),column=c+1, columnspan=1)
                    entry_count+=1
                    Widgets[entry_count]=append_buttons[c-1]
            row+=2
            row_space1=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                       bg= Window_Color.get(),anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=Num_Columns.get(),sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space1
            row+=1
            row_space2=Label(tk.Frame.scroll.data_window, text="",fg=Entry_Font_Color.get(),bg= Window_Color.get(),justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=0, columnspan=Num_Columns.get(),sticky=SW)
            entry_count+=1
            Widgets[entry_count]=row_space2
            row+=1
            cancel=Button(tk.Frame.scroll.data_window, text=cancel_txt,font=root.font,fg='#000000',bg='#dcdcdc',
                    command=lambda:Database.exec_tbl_item(Active_Table.get()))
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=cancel
            save=Button(tk.Frame.scroll.data_window, text=save_txt,font=root.font,fg='#000000', bg='#dcdcdc',
                command=lambda:Database.insert_into_table(Active_Table.get()))
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=save
            if Language.get()=="Spanish":
                title1='Estás Aquí → '+DB_Name.get()+' de Base de Datos → Nueva Entrada de Tabla → '+ Active_Table.get()
                title='<Nueva Entrada de Tabla>'
                msg1='Complete los Campos de Entrada que faltan y luego\n'
                msg2='Seleccione Guardar Entrada o Cancelar Entrada.'
            else:    
                title1="You Are Here → Database "+DB_Name.get()+" → New Table Entry → "+ Active_Table.get()
                title='<New Table Entry>'
                msg1='Fill In The Missing Entry Fields And Then\n'
                msg2='Select Save Entry Or Cancel Entry.'
            root.title(title1)
            root.update()
            new_entries[0].focus_force()
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(1)
            messagebox.showinfo(title, msg1+msg2)
            disable_menubar("all")
        except Exception as ex:
            if Language.get()=="Spanish":
                title='<Nuevas Entradas de Tabla>'
                msg1='¡Falló la Nueva Entrada de la Tabla '+Active_Table.get()+'!\n'
            else:    
                title='<New Table Entries>'
                msg1=Active_Table.get()+' New Table Entry Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
            enable_menubar("all")
            config_menu(None)
    def edit_tbl_row():
        if Active_Table.get()=="":
            if Language.get()=="Spanish":
                title='<'+DB_Name.get()+' / sin Tabla Seleccionada>'
                msg1='Se debe Seleccionar una Tabla para Continuar.\n'
                msg2='¡Seleccione una Tabla y Vuelva a Intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
            messagebox.showerror(title, msg1+msg2)
            return
        all_ids=Database.get_all_ids()
        if Language.get()=="Spanish":
            title='Editar Fila de Tabla'
            msg1='Seleccione el Número de ID Asociado a la Fila de la Tabla que Desea Editar.\n'
            msg2='A Continuación, haga Clic en OK para Continuar.'
        else:    
            title="Edit Table Row"
            msg1="Select The ID Number Associated With The Table Row To Edit.\n"
            msg2="Then Click OK To Continue."
        msg=msg1+msg2    
        num_rows=Database.retrieve_table_rowcount()
        if num_rows>1:
            id=my_askstring(title, msg, all_ids)
            if id==None or id=="":return
        else:id=all_ids[0]           
        try:
            id=str(id)
            # Get Selected ID Row Data
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute("SELECT * FROM "+ Active_Table.get()+" WHERE id="+id)
            id_entry=cursor.fetchall()
            colms=Num_Columns.get()
            global Column_Defines
            Column_Defines=[]
            colm_names,colm_definitions=Database.get_table_schema()# Doesn't Return "Row" Which Isn't In Schema
            for c, defines in enumerate(colm_definitions):
                define_var=tk.StringVar()
                Column_Defines.append(define_var)
                define_var.set(defines)                
            global Column_Data
            Column_Data=[]
            for c in range(Num_Columns.get()-1): 
                txt_var=tk.StringVar()
                Column_Data.append(txt_var)
                Column_Data[c].set(id_entry[0][c])
            colm_names=Database.retrieve_column_names()# Also Returns "Row" Which Isn't In Schema
            Database.destroy_widgets() # Clear window For New Table
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(0)
            Num_Columns.set(len(colm_names))# Row Not Part Of Database
            global Column_Widgets
            Column_Widgets={}# Used To Destroy Entries And Change Color
            name=[]
            wid_items=["www.","https://","@",":/"]
            wid=[]
            for c, columns in enumerate(colm_names):# Define Column Widths Depending On Text
                if c==0:
                    _wid=int(Column_Widths[c]*1.2)# @ Difference Between Label And Entry Widths 
                    wid.append(_wid)# Label Widths Of The Same Value Are Larger Than Entry Widths (??)
                else:    
                    for item in wid_items:
                        if item in Column_Data[c-1].get():
                            _wid=int(Column_Widths[c]*2)
                            break
                        else:_wid=int(Column_Widths[c]*1.2)
                    wid.append(_wid)
            for c, columns in enumerate(colm_names):
                name.append(c)
                name[c]=Entry(tk.Frame.scroll.data_window,font=root.font,width=wid[c],highlightthickness=Grid_Status.get(),
                    bg=Header_BG_Color.get(), fg=Header_Font_Color.get(),justify='center',relief='flat') 
                name[c].delete(0,END)
                name[c].insert(0,columns)
                name[c].configure(highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                Column_Widgets[c]=name[c]
                name[c].grid(row=0, column=c, columnspan=1)
                name[c].config(state= "disabled")
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            root.update()
            global Widgets# Used To Destroy Entries And Change Color
            Widgets={}
            new_entries=[]
            append_buttons=[]
            row=1
            entry_count=len(Widgets)
            if Language.get()=='Spanish':
                btn_txt='Adjuntar'
                save_txt='Guardar'
                cancel_txt='Cancelar'
            else:    
                btn_txt='Attach'
                save_txt='Save'
                cancel_txt='Cancel'
            for c in range(colms-1):
                if c==0:
                    row_entry=Label(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                        font=root.font,width=wid[c],borderwidth=1,justify='center',relief='sunken') 
                    row_entry.configure(text="")
                    Widgets[entry_count]=row_entry
                    row_entry.grid(row=row, column=c, columnspan=1)
                    id_entry=Label(tk.Frame.scroll.data_window,bg= Window_Color.get(),fg=Entry_Font_Color.get(), 
                        font=root.font,width=wid[c+1],borderwidth=1,justify='center',relief='sunken')
                    id_entry.configure(text=Column_Data[0].get())
                    entry_count+=1
                    Widgets[entry_count]=id_entry
                    id_entry.grid(row=row, column=c+1, columnspan=1)
                else:
                    new_entries.append(c-1)    
                    new_entries[c-1]=Entry(tk.Frame.scroll.data_window,textvariable=Column_Data[c],bg= '#c8ffff',fg='#000000', 
                        font=root.font,width=wid[c+1],highlightthickness=1,justify='center',relief='sunken')
                    new_entries[c-1].configure(highlightbackground=Grid_Color.get(),highlightcolor=Grid_Color.get())
                    new_entries[c-1].grid(row=row, column=c+1, columnspan=1)
                    entry_count+=1
                    Widgets[entry_count]=new_entries[c-1]
                    append_buttons.append(c-1)
                    append_buttons[c-1]=Button(tk.Frame.scroll.data_window,text=btn_txt,font=root.font,fg='#000000',bg='#dcdcdc',
                                               command=lambda a=Column_Data[c],b=Column_Defines[c]:Database.append_file_to_entry(a,b))
                    append_buttons[c-1].grid(row=row+1, pady=(5,0),column=c+1, columnspan=1)
                    entry_count+=1
                    Widgets[entry_count]=append_buttons[c-1]
            row+=2
            row_space1=Label(tk.Frame.scroll.data_window,text="",font=root.font,fg=Entry_Font_Color.get(),
                       bg= Window_Color.get(),anchor="w",justify='left')
            row_space1.grid_rowconfigure(row, minsize=100)
            row_space1.grid(row=row, column=2, columnspan=Num_Columns.get(),sticky=SW)
            entry_count+=1
            row+=1
            Widgets[entry_count]=row_space1
            Num_Columns.set(Num_Columns.get()-2)# Remove Row And ID Column
            row_space2=Label(tk.Frame.scroll.data_window, text="",fg=Entry_Font_Color.get(),bg= Window_Color.get(),justify='left')
            row_space2.grid_rowconfigure(row, minsize=100)
            row_space2.grid(row=row, column=0, columnspan=Num_Columns.get(),sticky=SW)
            entry_count+=1
            row+=1
            Widgets[entry_count]=row_space2
            cancel=Button(tk.Frame.scroll.data_window, text=cancel_txt,font=root.font,fg='#000000',bg='#dcdcdc',
                    command=lambda:Database.exec_tbl_item(Active_Table.get()))
            cancel.grid_rowconfigure(row, minsize=100)
            cancel.grid(row=row, column=2, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=cancel
            save=Button(tk.Frame.scroll.data_window, text=save_txt,font=root.font,fg='#000000', bg='#dcdcdc',
                command=lambda a='Save Edited Table Entry':Database.save_edited_entry())
            save.grid_rowconfigure(row, minsize=100)
            save.grid(row=row, column=3, padx=(0,5), columnspan=1,sticky=SE)
            entry_count+=1
            Widgets[entry_count]=save
            root.title(title)
            disable_menubar("all")
            root.update()
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Editar Fila de la Tabla>'
                msg1='Tabla = '+Active_Table.get()+'\n'
                msg2='¡Obtenga la ID de Entrada de la Tabla = '+id+' Falló!\n'
            else:    
                title='<Edit Table Row>'
                msg1='Table = '+Active_Table.get()+'\n'
                msg2='Get Table Entry ID = '+id+' Failed!\n'
            msg3=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def save_edited_entry():
        if Active_Table.get()=="":
            if Language.get()=='Spanish':
                title='<'+DB_Name.get()+' / sin Tabla Seleccionada>'
                msg1='Se debe Seleccionar una Tabla para Continuar.'
                msg2='¡Seleccione una Tabla y Vuelva a Intentarlo!'
            else:    
                title="<"+DB_Name.get()+" / No Table Selected>"
                msg1='A Table Must Be Selected To Continue.\n'
                msg2='Please Select A Table And Try Again!'
                messagebox.showerror(title, msg1+msg2)
                return
        try:
            colm_names=Database.retrieve_column_names()# Also Returns "Row" Which Isn't In Schema
            names=[]
            conn=Database.create_connection(Active_DB.get())
            cursor=conn.cursor()
            for c in range(len(colm_names)):# Restore Underscores
                names.append(colm_names[c].replace(" ","_"))
                if c>=2:
                    query="UPDATE "+Active_Table.get()+" SET "+names[c]+" = ? Where id = ?"
                    data=(Column_Data[c-1].get(), Column_Data[0].get())
                    cursor.execute(query, data)
            conn.commit()
            conn.close()
            Database.exec_tbl_item(Active_Table.get())# Populate Table With New Edited Entries
            if Language.get()=='Spanish':
                title='<Guardar Entrada Editada>'
                msg='¡Cambios de Entrada Editados Guardados!'
            else:    
                title='<Save Edited Entry>'
                msg="Edited Entry Changes Saved!"
            messagebox.showinfo(title, msg)
            enable_menubar("all")
            config_menu(None)
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Guardar Entrada Eeditada>'
                msg1='Tabla = '+Active_Table.get()+'\n'
                msg2='¡Guardar ID de Entrada Editado = '+Column_Data[0].get()+' Falló!\n'
            else:    
                title='<Save Edited Entry>'
                msg1='Table = '+Active_Table.get()+'\n'
                msg2='Save Edited Entry ID = '+Column_Data[0].get()+' Failed!\n'
            msg3=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2+msg3)
            enable_menubar("all")
            config_menu(None)
        finally:
            if conn:conn.close()
    def destroy_widgets():# Destroys Database Column And Row Widgets
        try:
            for c in range(len(Column_Widgets)):
                    Column_Widgets[c].destroy()
            for e in range(len(Widgets)):
                Widgets[e].destroy()
            Num_Rows.set(0)
        except Exception as ex:
            pass
    def retrieve_table_rowcount():
        try:
            conn=Database.create_connection(Active_DB.get())
            num_rows=len(conn.execute(f'SELECT * FROM {Active_Table.get()}').fetchall())
            if conn:conn.close()
            return num_rows
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Recuperar el Recuento de Filas de la Tabla>'
                msg1='No se pudo Recuperar los Datos de '+Active_Table.get()+'\n'
            else:    
                title='<Retrieve Table Row Count>'
                msg1="Failed To Retrieve "+Active_Table.get()+" Data\n"
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
            return "break"
    def get_num_tbls():
        tbls=Database.fetch_tables()
        num_tbls=0
        for name in tbls:
            if name[0]!="sqlite_sequence":
                num_tbls+=1
        return num_tbls        
    def retrieve_table_entries():
        # Row Column Is Not Part Of Database
        # Row Data Is Inserted Into Each Row Tuple At Index 0
        try:
            conn=Database.create_connection(Active_DB.get())
            row_data=conn.execute(f'SELECT * FROM {Active_Table.get()}').fetchall()
            for r in range(len(row_data)):
                row_data[r]=row_data[r][:0]+(r+1,)+row_data[r][0:]# Insert Row Data To Tuples
            row_data=array(row_data)
            if conn:conn.close()
            return  row_data
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Recuperar Entradas de Tabla>'
                msg1='No se pudo Recuperar los Datos de '+Active_Table.get()+'\n'
            else:    
                title='<Retrieve Table Entries>'
                msg1="Failed To Retrieve "+Active_Table.get()+" Data\n"
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
            return "break"
    def populate_table_entries(table_data):
        try:
            nr=Database.retrieve_table_rowcount()
            Num_Rows.set(nr)
            colms, rows=(Num_Columns.get(), Num_Rows.get())
            entry=[]
            global Widgets# Used For Widget Destruction
            Widgets={}
            entry_count=0
            for r, rows in enumerate(table_data):
                for c in range(colms):
                    entry.append(entry_count)    
                    entry[entry_count]=Label(tk.Frame.scroll.data_window,bg=Window_Color.get(),fg=Entry_Font_Color.get(), 
                        font=root.font,width=Column_Widths[c],highlightthickness=Grid_Status.get(),justify='center',relief='flat')
                    if str(rows[c])!="":
                        if "https://" in str(rows[c]):entry[entry_count].bind('<Double-Button-1>', lambda event, url=str(rows[c]):Database.open_url(url)) 
                        elif '.' in str(rows[c]):# Check For Email, Image, Text
                            result=Database.check_for_email(str(rows[c]))# Check For Email Extension
                            if result:
                                entry[entry_count].bind('<Double-Button-1>', lambda event, address=str(rows[c]):Database.validate_email(address))
                            else:
                                result=Database.check_for_image(str(rows[c]))# Check For Image Extension
                                if result:entry[entry_count].bind('<Double-Button-1>', lambda event, image=str(rows[c]):Database.open_image(image))
                                else:
                                    result=Database.check_for_video(str(rows[c]))# Check For Video Extension
                                    if result:entry[entry_count].bind('<Double-Button-1>', lambda event, video=str(rows[c]):Database.open_video(video))
                                    else:
                                        result=Database.check_for_text(str(rows[c]))# Check For Document Extension
                                        if result:entry[entry_count].bind('<Double-Button-1>', lambda event, text=str(rows[c]):Database.open_text(text))
                                        else:
                                            result=Database.check_for_music(str(rows[c]))# Check For Sound Extension
                                            if result:entry[entry_count].bind('<Double-Button-1>', lambda event, music=str(rows[c]):Database.open_music(music))
                        txt=str(rows[c])# basename Does Not Work Correctly If Last Charactersis Is / Or \
                        while txt[-1]=="/" or txt[-1]==r'"\"':# Remove / And \ From Path End
                            txt=txt[:-1]
                        text=os.path.splitext(txt)[0]# Remove File Extension    
                        text=os.path.basename(text)# Display File Name Only
                        entry[entry_count].configure(text=text) 
                    else:
                        entry[entry_count].configure(text="None")
                    entry[entry_count].configure(bg=Window_Color.get(),highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                    Widgets[entry_count]=entry[entry_count]
                    entry[entry_count].grid(row=r+1, column=c, columnspan=1)
                    entry_count+=1
            root.update()            
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(0)
            tk.Frame.scroll.update()
        except Exception as ex:
            if Language.get()=='Spanish':
                title='<Entradas de Tabla de Población>'
                msg1='¡Fallaron las Entradas de la Tabla de Población de A '+Active_Table.get()+'!\n'
            else:    
                title='<Populate Table Entries>'
                msg1=Active_Table.get()+' Populating Table Entries Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def exec_tbl_item(item):
        if Edit_Definitions.get()==True:return
        Active_Table.set(item)
        Database.destroy_widgets()
        if Language.get()=="English":title=str("You Are Here → Database "+DB_Name.get()+" → Execute Table "+Active_Table.get())  
        else:title=str("Usted está aquí → Base de Datos "+DB_Name.get()+" → Ejecutar Tabla "+Active_Table.get()) 
        root.title(title)
        root.update()
        if DB_Name.get()!="" and item!="":  
            Database_Ini('read',DB_Name.get(),item,None,None)
        tk.Frame.scroll.canvas.configure(bg=Window_Color.get())
        tk.Frame.scroll.data_window.configure(bg=Window_Color.get())
        if Language.get()=="English":
            menubar.entryconfig('     Create/Modify Table     ', state="normal")
            menubar.entryconfig('     Create/Modify Table Entry     ', state="normal")
        else:    
            menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
            menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="normal")
        tbl_data=Database.retrieve_table_entries()
        colm_names=Database.retrieve_column_names()# Also Returns "Row" Which Isn't In Schema
        Database.set_colm_widths(colm_names,tbl_data)
        Database.populate_column_names(colm_names)
        Database.populate_table_entries(tbl_data)
        enable_menubar("all")
        config_menu(None)
        root.update()
    def retrieve_column_names():# Also Returns "Row" Which Isn't In Schema
        try:
            conn=Database.create_connection(Active_DB.get())            
            colm_names=[]
            # Row Column Is Not Part Of Database
            # Append To Column Names At Position 0
            if Language.get()=="Spanish":colm_names.append("Fila")
            else:colm_names.append("Row")    
            colm_data=conn.execute(f'PRAGMA table_info({Active_Table.get()});').fetchall()
            for c in range(len(colm_data)):
                name=str(colm_data[c][1]).replace("_"," ")
                colm_names.append(name)
            if conn:conn.close()
            return colm_names
        except sqlite3.Error as error:
            if Language.get()=='Spanish':
                title='<Recuperar Nombres de Columna>'
                msg1='No se pudo Recuperar los Nombres de la Columna '+Active_Table.get()+'\n'
            else:    
                title='<Retrieve Column Names>'
                msg1="Failed To Retrieve "+Active_Table.get()+" Column Names\n"
            msg2=f"Error: '{error}'"
            messagebox.showerror(title, msg1+msg2)
            return "break"
    def set_colm_widths(colm_names,colm_data):
        # Get The Required Width For Columns. Compare Column Names To Data Fields.
        # Use Whichever Width Is Greated For That Column. Dummy Labels Are Used Just To Obtain Required Widths.
        global Column_Widths
        Column_Widths=[]
        num_rows=Database.retrieve_table_rowcount()
        data_wid=[]
        for c in range(len(colm_names)):# Columns
            dummy_1=tk.Label(root, text=colm_names[c], font=root.font)# Dummy Label
            root.update()
            pixel_width=dummy_1.winfo_reqwidth()# Required Width For Text In Pixels
            char_width=root.font.measure("0")# 1 Character Width
            colm_wid=int(pixel_width/char_width)
            for d in range(num_rows):
                # Purge / \ From Text. basename Does Not Like
                txt=str(colm_data[d][c])
                while txt[-1]=="/" or txt[-1]==r'"\"':# Remove / And \ From Path End
                    txt=txt[:-1]
                text=os.path.splitext(txt)[0]# Remove File Extension    
                text=os.path.basename(str(text))# Display File Name Only
                dummy_2=tk.Label(root, text=text, font=root.font)# Dummy Label
                root.update()
                pixel_width=dummy_2.winfo_reqwidth()# Required Width For Text In Pixels
                char_width=root.font.measure("0")# 1 Character Width
                data_wid.append(int(pixel_width/char_width))
            list_max=max(data_wid)
            if colm_wid>list_max:width=colm_wid
            else:width=list_max
            Column_Widths.append(width)
            data_wid.clear()
        dummy_1.destroy()
        dummy_2.destroy()    
    def populate_column_names(list_of_names):
        try:
            Database.destroy_widgets() # Clear window For New Table
            tk.Frame.scroll.canvas.xview_moveto(0)# Position Scrollbar To Position 0 For New Table
            tk.Frame.scroll.canvas.yview_moveto(0)
            colms=(len(list_of_names))
            Num_Columns.set(colms)# Row Not Part Of Database
            global Column_Widgets
            Column_Widgets={}# Used To Destroy Entries And Change Color
            name=[]
            for c, columns in enumerate(list_of_names):# Default Names
                name.append(c)
                name[c]=Label(tk.Frame.scroll.data_window,font=root.font,width=Column_Widths[c],highlightthickness=Grid_Status.get(),
                    bg=Header_BG_Color.get(), fg=Header_Font_Color.get(),justify='center',relief='flat') 
                name[c].configure(text=columns)
                name[c].configure(highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                Column_Widgets[c]=name[c]
                name[c].grid(row=0, column=c, columnspan=1)
                if c>1:name[c].bind("<Button-1>", lambda event, a=columns:Database.colm_agg(event,a))
            tk.Frame.scroll.pack(side="top", fill="both", expand=True)
        except Exception as ex:
            if Language.get()=='Spanish':
                title='<Completar Nombres de Columnas>'
                msg1='No se pudo Completar los Nombres de la Columnas '+Active_Table.get()+'\n'
            else:    
                title='<Populate Column Names>'
                msg1="Failed To Populate "+Active_Table.get()+" Column Names\n"
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def get_column_max(column_name):
        conn=sqlite3.connect(Active_DB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT MAX(CAST("+column_name+" AS FLOAT)) FROM "+Active_Table.get())
        return round(cursor.fetchone()[0],4)
    def get_column_min(column_name):
        conn=sqlite3.connect(Active_DB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT MIN(CAST("+column_name+" AS FLOAT)) FROM "+Active_Table.get())
        return round(cursor.fetchone()[0],4)
    def get_column_avg(column_name):
        conn=sqlite3.connect(Active_DB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT AVG(CAST("+column_name+" AS FLOAT)) FROM "+Active_Table.get())
        return round(cursor.fetchone()[0],4)
    def get_column_total(column_name):
        conn=sqlite3.connect(Active_DB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT TOTAL(CAST("+column_name+" AS FLOAT)) FROM "+Active_Table.get())
        return round(cursor.fetchone()[0],4)
    def colm_agg(event,name):
        colm_name=str(name).replace(" ","_")
        colm_max=Database.get_column_max(colm_name)
        colm_min=Database.get_column_min(colm_name)
        colm_avg=Database.get_column_avg(colm_name)
        colm_total=Database.get_column_total(colm_name)
        if colm_total!=0.0:
            if Language.get()=="Spanish":
                title="<Columna "+name+" Información>"
                msg1=name+" Valor Mínimo = "+str(colm_min)+"\n"
                msg2=name+" Valor Máximo = "+str(colm_max)+"\n"
                msg3=name+" Valor Medio = "+str(colm_avg)+"\n"
                msg4=name+" Valor Total = "+str(colm_total)
            elif Language.get()=="English":
                title="<Columna "+name+" Information>"
                msg1=name+" Minimum Value = "+str(colm_min)+"\n"
                msg2=name+" Maximum Value = "+str(colm_max)+"\n"
                msg3=name+" Average Value = "+str(colm_avg)+"\n"
                msg4=name+" Total Value = "+str(colm_total)
            msg=msg1+msg2+msg3+msg4
            messagebox.showinfo(title, msg)
    def copy_table1_to_table2(from_tbl,to_tbl,drop):
        try:
            conn=sqlite3.connect(Active_DB.get())
            cursor=conn.cursor()
            # Copy the data from table1 to table2
            cursor.execute("INSERT OR IGNORE INTO  "+ to_tbl + " SELECT * FROM "+ from_tbl)
            conn.commit()
            if drop:
                cursor.execute("DROP TABLE "+from_tbl)
                conn.commit()
            conn.close()
        except sqlite3.Error as error:
            if Language.get()=="English":messagebox.showerror("<Copy Table Data>", error)
            else:messagebox.showerror("<Copiar Datos de Tabla>", error)
        finally:
            if conn:conn.close()
    def edit_table_definitions():
        Edit_Definitions.set(True)
        Database.create_new_table(Active_Table.get())
    def get_table_schema():# Doesn't Return "Row" Which Isn't In Schema
        try:
            colm_names=[]
            colm_definitions=[]
            conn=sqlite3.connect(Active_DB.get())
            cursor=conn.cursor()
            cursor.execute(f"PRAGMA table_info({Active_Table.get()})")
            columns=cursor.fetchall()
            for column in columns:
                colm_names.append(column[1])
                if column[3]==1:colm_definitions.append(column[2]+" NOT NULL")
                else:colm_definitions.append(column[2])
            conn.close()        
            return colm_names,colm_definitions
        except sqlite3.Error as error:
            if Language.get()=="English":messagebox.showerror("<Get Table Schema>", error)
            else:messagebox.showerror("<Obtener Esquema de tabla>", error)
        finally:
            if conn:conn.close()
    def append_file_to_entry(txt_var,define_var):
        if define_var.get()=="Data Type":# Nothing Selected
            if Language.get()=="Spanish":
                title="Se debe Seleccionar un Tipo de Datos"
                msg1=" Se debe seleccionar un tipo de datos antes de que"
                msg2=" se pueda adjuntar un archivo. Si se selecciona el"
                msg3=" tipo 'BLOB', El archivo se copiará en el directorio"
                msg4=" de la base de datos en la carpeta 'Archivos adjuntos'."
                msg5=" Si se selecciona el tipo 'TEXTO', el archivo no se copia."
                msg6=" En la vista de tabla, el archivo se ejecuta desde su"
                msg7=" ubicación original o desde la ubicación copiada, según"
                msg8=" el texto o el BLOB, respectivamente."
                msg=msg1+msg2+msg3+msg4+msg5+msg6+msg7+msg8
            else:
                title="A Data Type Must Be Selected"
                msg1="A Data Type Must Be Selected Before A File Can"
                msg2=" Be Attached! If 'BLOB' Type Is Selected, The"
                msg3=" File Will Be Copied To The Database Directory"
                msg4=" In Folder 'Attachments'. If 'TEXT' Type Is Selected,"
                msg5=" The File Is Not Copied. In Table View, The File Is"
                msg6=" Executed From It's Original Location Or From The"
                msg7=" Copied Location Depending On 'Text Or 'BLOB' Respectively."
                msg=msg1+msg2+msg3+msg4+msg5+msg6+msg7
            messagebox.showinfo(title, msg)
            return
        file_extensions=['.txt','.rtf','.odt','.docx','.pdf','.wav','.mp3','.3gp','.wma','.aac','.ogg','.flac','.alac','.aiff',
                '.av1','.mpg','.mpeg','.m1v','.mp2','.mp2v','.mp4','.mp4v','.mov','.wmv','.rm','.swf','.webm','.mkv',
                '.flv','.vob','.3gp','.avchd','.html5','.jpg','.jpeg','.jpe','.jif','.jfif','.jfi','.png','.gif','.webp',
                '.tiff','.tif','.psd','.bmp','.dib','.heif','.heic','.svg','.svgz']
        if Language.get()=="English":txt="Text, Music, Photo and Video Files"
        else:txt="Archivos de Texto, Música, Fotos y Videos"
        types=[(txt, file_extensions)]
        user_dir=Path.home()
        root.update_idletasks()
        path=askopenfile(mode='r',initialdir=user_dir,defaultextension="*.*",filetypes=types)
        if path is None:return
        if define_var.get()!="BLOB" and define_var.get()!="BLOB NOT NULL":
            txt_var.set(path.name)
            return
        else:
            file_name=os.path.basename(path.name)
            if os.path.isfile(path.name):
                src=path.name
                dst_path=os.path.join(DB_Path.get(),"Attachments")
                dst=os.path.join( dst_path,file_name)
            if not os.path.isfile(dst):# Copy File To Database Directory
                shutil.copy(src, dst)
            txt_var.set(dst)
        return
    def set_grid(status):
        try:
            l=len(Column_Widgets)# Create Exception if not exist
            if status=='off' or status=="0":
                Grid_Status.set(0)
                stat='on'
            elif status=='on' or status=="1":
                Grid_Status.set(1)
                stat='off'
                for c in range(len(Column_Widgets)):
                    Column_Widgets[c].configure(highlightthickness=Grid_Status.get())
                for e in range(len(Widgets)):
                    Widgets[e].configure(highlightthickness=Grid_Status.get())
            if DB_Name.get()!="" and Active_Table.get()!="":  
                Database_Ini('write',DB_Name.get(),Active_Table.get(),None,None)
            if Active_Table.get()!="":Database.exec_tbl_item(Active_Table.get())        
            tk.Frame.scroll.data_window.update()
            grid_menu.delete(0,END)
            populate_grid_menu(stat)
        except Exception as ex:
            pass
    def create_default_db():
        set_default_colors()
        db_file=os.path.join(DB_Path.get(), "Example"+".db")
        Active_DB.set(db_file)
        Num_Columns.set(7)
        column_title=["ID","Name","Birthday","Cellular","City_State","Email","Website"]
        DB_Name.set("Example")
        if not Database.database_exist(db_file):# Create The Default Database "Example"
            default_tbl='Example_Table'
            default_entries=[("Johnny Doe","July 17","356-560-8347","Dallas Tx.","JohnDoe@gmail.com","https://www.stratofortress.org"),
                            ("Jane Doe","August 31","333-660-9861","Saint Louis Mo.","JaneDoe@Outlook.com","https://www.belk.com")]
            try:
                conn=Database.create_connection(db_file)
                conn.close()
                populate_db_menu()
            except Error as e:
                msg1="Database Example Was Not Created!\n"
                msg2=f"Error: '{e}'"
                messagebox.showerror('<Create Default Database>', msg1+msg2)
                return
            try:# Populate The Database With Default Values
                conn=Database.create_connection(Active_DB.get())
                cursor=conn.cursor()
                for row in range(0,2): 
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + default_tbl + " ("+column_title[0]+" INTEGER PRIMARY KEY AUTOINCREMENT, "+column_title[1]+" TEXT, "+column_title[2]+" TEXT, "+column_title[3]+" TEXT, "+column_title[4]+" TEXT, "+column_title[5]+" TEXT, "+column_title[6]+" TEXT)")
                    cursor.execute("INSERT INTO " + default_tbl + " ("+column_title[1]+", "+column_title[2]+", "+column_title[3]+", "+column_title[4]+", "+column_title[5]+", "+column_title[6]+") VALUES(?, ?, ?, ?, ?, ?)", 
                                (default_entries[row][0], default_entries[row][1],default_entries[row][2],default_entries[row][3],default_entries[row][4],default_entries[row][5]))
                    conn.commit()
                conn.close()
                Active_Table.set(default_tbl)
                if DB_Name.get()!="" and Active_Table.get()!="":  
                    Database_Ini('write',DB_Name.get(),default_tbl,None,None)
                Active_Table.set("")    
            except sqlite3.Error as error:
                msg1='Table = '+default_tbl+'\n'
                msg2='Create Default Table Failed.\n'
                msg3=f"Error: '{error}'"
                messagebox.showerror("<"+default_tbl+">", msg1+msg2+msg3)
            finally:
                if conn:conn.close()
    def open_music(music):# 
        try:
            exist=os.path.exists(music)
            if exist:webbrowser.open(music)
            else:
                if Language.get()=='Spanish':
                    title='<Archivo de música abierto>'
                    msg='Abriendo el archivo de música E:/Music/All My People.mp3 ¡No se encuentra!'
                else:    
                    title='<Open Music File>'
                    msg='Opening Music File '+music+' Not Found!\n'
                messagebox.showinfo(title, msg)
        except Exception as ex:
            if Language.get()=='Spanish':
                title='<Archivo de Música Abierto>'
                msg1='¡Apertura de Archivo de Música '+music+' Falló!\n'
            else:
                title='<Open Music File>'
                msg1='Opening Music File '+music+' Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def check_for_music(name):
        music_exts=['.wav','.mp3','.3gp','.wma','.aac','.ogg','.flac','.alac','.aiff']
        file_name=os.path.basename(name)
        for i in range(len(music_exts)):
            if music_exts[i] in file_name:
                result=True
                return result
            else:
                result=False
        return result
    def open_text(text):#
        try:
            exist=os.path.exists(text)
            if exist:
                subprocess.Popen([text], shell=True)
            else:

                if Language.get()=='Spanish':
                    title='<Abrir archivo de texto>'
                    msg='¡Abra el archivo '+text+' no encontrado!'
                else:    
                    title='<Open Text File>'
                    msg='Opening Text File '+text+' Not Found!'
                messagebox.showinfo(title, msg)
        except Exception as ex:

            if Language.get()=='Spanish':
                title='<Abrir archivo de texto>'
                msg1='¡Falló el archivo de apertura que '+text+'!\n'
            else:    
                title='<Open Text File>'
                msg1='Opening Text File '+text+' Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def check_for_text(name):
        text_exts=['.txt','.rtf','.odt','.docx','.pdf']
        file_name=os.path.basename(name)
        for i in range(len(text_exts)):
            if text_exts[i] in file_name:
                result=True
                return result
            else:
                result=False
        return result
    def check_for_video(name):
        video_exts=['.av1','.mpg','.mpeg','.m1v','.mp2','.mp2v','.mp4','.mp4v','.mov','.wmv','.rm','.swf',
                    '.webm','.mkv','.flv','.vob','.3gp','.avchd','.html5']
        file_name=os.path.basename(name)
        for v in range(len(video_exts)):
            if video_exts[v] in file_name:
                result=True
                return result
            else:
                result=False
        return result
    def open_video(video):#
        try:
            exist=os.path.exists(video)
            if exist:
                subprocess.Popen([video], shell=True)
            else:
                if Language.get()=='Spanish':
                    title='<Abrir archivo de imagen>'
                    msg='¡Abra el archivo de imagen '+video+' no encontrado!'
                else:    
                    title='<Open Image File>'
                    msg='Opening Image File '+video+' Not Found!'
                messagebox.showinfo(title, msg)
        except Exception as ex:
            if Language.get()=='Spanish':
                title='<Abrir archivo de imagen>'
                msg1='¡Falló el archivo de imagen de la imagen que '+video+'!\n'
            else:    
                title='<Open Image File>'
                msg1='Opening Image File '+video+' Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def open_image(image):# 
        try:
            exist=os.path.exists(image)
            if exist:
                subprocess.Popen([image], shell=True)
            else:
                if Language.get()=='Spanish':
                    title='<Abrir archivo de imagen>'
                    msg='¡Abra el archivo de imagen '+image+' no encontrado!'
                else:    
                    title='<Open Image File>'
                    msg='Opening Image File '+image+' Not Found!'
                messagebox.showinfo(title, msg)
        except Exception as ex:
            title='<Open Image File>'
            msg1='Opening Image File '+image+' Failed!\n'
            msg2=f"Error: '{ex}'"
            messagebox.showerror(title, msg1+msg2)
    def check_for_image(name):
        image_exts=['.jpg','.jpeg','.jpe','.jif','.jfif','.jfi','.png','.gif','.webp','.tiff','.tif',
                    '.psd','.bmp','.dib','.heif','.heic','.svg','.svgz']
        file_name=os.path.basename(name)
        for i in range(len(image_exts)):
            if image_exts[i] in file_name:
                result=True
                return result
            else:
                result=False
        return result
    def open_url(url):
        if url!="":
            valid=validators.url(url)
            if valid:webbrowser.open(url, new=2)
            else:messagebox.showerror("<Open URL>", "The Website Is Not A Valid Site!")
    def check_for_email(email):#  Check For Characters In List
        email_exts=[".com",".net",".co",".org",".info",".mobi",".travel",".int",".edu",".gov",".mil",".lnc", 
                    ".is",".dev",".travel",".info",".biz",".email",".build",".agency",".zone",".bid",".condos",
                    ".dating",".events",".maison",".partners",".properties",".productions",".social",".reviews"]
        for i in range(len(email_exts)):
            if email_exts[i] in email:
                result=True
                return result
            else:
                result=False
        return result
    def validate_email(address):
        if address!="":
            if "www" in address:# Maybe Facebook Site, Tweeter, etc...
                Database.open_url(address)
                return
            try:
                address=address.lower()
                email_status=re.compile(r"[^@]+@[^@]+\.[^@]+")# Check Email Format
                if email_status.match(address):
                    webbrowser.open('mailto:'+address, new=1)
                else:    
                    if Language.get()=='Spanish':
                        title='<Validar Correo Electrónico>'
                        msg1='¡Falló la dirección de Correo Electrónico!\n'
                    else:    
                        title='<Validate Email>'
                        msg1='Email Address Format Incorrect!\n'
                    messagebox.showerror(title, msg1)
            except Exception as ex:
                if Language.get()=='Spanish':
                    title='<Validar Correo Electrónico>'
                    msg1='¡Falló la dirección de Correo Electrónico!\n'
                else:    
                    title='<Validate Email>'
                    msg1='Email Address Failed!\n'
                msg2= repr(ex)
                messagebox.showerror(title, msg1+msg2)
def my_askinteger(title,prompt,init_val,min_val,max_val):
    d=My_IntegerDialog(title, prompt ,init_val,min_val,max_val)
    answer=d.result
    root.update_idletasks()
    return answer  
class My_IntegerDialog(tk.simpledialog._QueryInteger):
    def body(self, master):
        self.attributes("-toolwindow", True)# Remove Min/Max Buttons
        self.bind('<KP_Enter>', self.ok)
        self.bind('<Return>', self.ok)
        pt=tk.Label(master, text=self.prompt, justify="left", font=root.font)
        pad=int((pt.winfo_reqwidth()/2)/2)
        pt.grid(row=2, padx=(5,5),pady=(5,5), sticky=W+E)
        self.entry=tk.Entry(master, name="entry", justify='center', bg="#d6ffff", font=root.font)
        self.entry.grid(row=3, padx=(pad,pad), sticky=W+E)
        self.entry.bind('<Map>', self.on_map)
        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)
        root.update_idletasks()
        return self.entry
    def on_map(self, event):
        self.entry.focus_force()    
def my_askstring(title, prompt, init_val=None):
    d=My_StringDialog(title, prompt , init_val)
    answer=d.result
    root.update_idletasks()
    return answer  
class My_StringDialog(tk.simpledialog._QueryString):
    def body(self, master):# initialvalue May Be List, String Or None
        self.attributes("-toolwindow", True)# Remove Min/Max Buttons
        self.bind('<KP_Enter>', self.ok)
        self.bind('<Return>', self.ok)
        pt=tk.Label(master, text=self.prompt, justify="left", font=root.font)
        pad=int((pt.winfo_reqwidth()/2)/2)
        pt.grid(row=2, padx=(5,5),pady=(5,5), sticky=W+E)
        if self.initialvalue is not None:
            if type(self.initialvalue)==list:# List
                self.entry=ttk.Combobox(master, name="entry", state = "readonly",justify="center",font=root.font)
                self.entry['values']=self.initialvalue
                self.entry.current(0)
            else:# String
                self.entry=tk.Entry(master, name="entry", justify='center', bg="#d6ffff", font=root.font)
                self.entry.insert(0, self.initialvalue)
                self.entry.select_range(0, END)
        else:# None
            self.entry=tk.Entry(master, name="entry", justify='center', bg="#d6ffff", font=root.font)
            self.entry.insert(0, "")
            self.entry.select_range(0, END)
        self.entry.grid(row=3, padx=(pad,pad), sticky=W+E)
        self.entry.bind('<Map>', self.on_map)
        root.update_idletasks()
        return self.entry
    def on_map(self, event):
        self.entry.focus_force()    
def about():
    if Language.get()=="Spanish":
        title="Mi SQLite3 de Base de Datos Creador/Navegador"
        msg1="Creador del programa: Ross Waters\nDirección de correo electrónico: rosswatersjr@gmail.com\nPlataformas: Windows 10/11\n"
        msg2="Lenguaje de programación: Python 3.12.0 64 bits\nRevisión: 3.2\nÚltima revisión: 02/12/2023"
    elif Language.get()=="English":
        title="My SQLite3 Database Creator/Browser"
        msg1="Program Creator: Ross Waters\nEmail Address: rosswatersjr@gmail.com\nPlatforms: Windows 10/11\n"
        msg2="Programming Language: Python 3.12.0 64-bit\nRevision: 3.2\nLatest Revision: 12/02/2023"
    msg=msg1+msg2
    messagebox.showinfo(title, msg)
def destroy():
    try:# X Icon Was Clicked
        if DB_Name.get()!="" and Active_Table.get()!="":  
            Database_Ini('write',DB_Name.get(),Active_Table.get(),None,'keep')
        Database.destroy_widgets()# Destroys Database Column And Row Widgets
        for widget in root.winfo_children():# Destroys Menu Bars, Frame, Canvas And Scroll Bars
            if isinstance(widget, tk.Canvas):widget.destroy()
            else:widget.destroy()
        os._exit(0)
    except Exception as ex:
        pass
        os._exit(0)
def change_colors(which):
    try:
        if which=='window' or which=="all":        
            if which=='window':
                if Language.get()=='Spanish':
                    title='Color de Ventana Principal'
                else:    
                    title="Main Window Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Window_Color.get())
                if color_code[1]==None:return
                Window_Color.set(color_code[1])
                root.configure(background=Window_Color.get()) # Set root backcolor
                root.update()
                tk.Frame.scroll.data_window.configure(bg=Window_Color.get())
                tk.Frame.scroll.canvas.configure(bg=Window_Color.get())
                for e in range(len(Widgets)):
                    Widgets[e].configure(bg=color_code[1])
            elif which=="all":        
                root.configure(background=Window_Color.get()) # Set root backcolor
                root.update()
                tk.Frame.scroll.data_window.configure(bg=Window_Color.get())
                tk.Frame.scroll.canvas.configure(bg=Window_Color.get())
                for e in range(len(Widgets)):
                    Widgets[e].configure(bg=color_code[1])
        elif which=='header_bg' or which=="all":
            if which=='header_bg':
                if Language.get()=='Spanish':
                    title='Nombres de Columna Color de Fondo'
                else:    
                    title="Column Names Background Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Header_BG_Color.get())
                if color_code[1]==None:return
                Header_BG_Color.set(color_code[1])
                if Column_Widgets:        
                    for c in range(len(Column_Widgets)):
                        Column_Widgets[c].configure(bg=Header_BG_Color.get()) 
            elif which=="all":        
                if Column_Widgets:        
                    for c in range(len(Column_Widgets)):
                        Column_Widgets[c].configure(bg=Header_BG_Color.get()) 
        elif which=='header_font' or which=="all":
            if which=='header_font':
                if Language.get()=='Spanish':
                    title='Nombres de Columna Color de Texto'
                else:    
                    title="Column Names Text Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Header_Font_Color.get())
                if color_code[1]==None:return
                Header_Font_Color.set(color_code[1])
                if Column_Widgets:        
                    for c in range(len(Column_Widgets)):
                        Column_Widgets[c].configure(fg=Header_Font_Color.get())
                if Language.get()=='Spanish':
                    title='Entradas de Tabla Color de Texto'
                else:    
                    title="Table Entries Text Color"
            elif which=="all":        
                if Column_Widgets:        
                    for c in range(len(Column_Widgets)):
                        Column_Widgets[c].configure(fg=Header_Font_Color.get())
                if Language.get()=='Spanish':
                    title='Entradas de Tabla Color de Texto'
                else:    
                    title="Table Entries Text Color"
        elif which=='entry_font' or which=="all":
            if which=='entry_font':
                color_code=colorchooser.askcolor(title=title,initialcolor=Entry_Font_Color.get())
                if color_code[1]==None:return
                Entry_Font_Color.set(color_code[1])
                for e in range(len(Widgets)):
                    Widgets[e].configure(fg=Entry_Font_Color.get())
            elif which=="all":        
                for e in range(len(Widgets)):
                    Widgets[e].configure(fg=Entry_Font_Color.get())
        elif which=='grid_color' or which=="all":
            if which=='grid_color':
                if Language.get()=='Spanish':
                    title='Color de la Línea de la Cuadrícula'
                else:    
                    title="Grid Line Color"
                color_code=colorchooser.askcolor(title=title,initialcolor=Grid_Color.get())
                if color_code[1]==None:return
                Grid_Color.set(color_code[1])
                for c in range(len(Column_Widgets)):
                    Column_Widgets[c].configure(highlightthickness=Grid_Status.get(),highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                for e in range(len(Widgets)):
                    Widgets[e].configure(highlightthickness=Grid_Status.get(),highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
            elif which=="all":        
                for c in range(len(Column_Widgets)):
                    Column_Widgets[c].configure(highlightthickness=Grid_Status.get(),highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
                for e in range(len(Widgets)):
                    Widgets[e].configure(highlightthickness=Grid_Status.get(),highlightbackground=Grid_Color.get(), highlightcolor=Grid_Color.get())
        if DB_Name.get()!="" and Active_Table.get()!="":  
            Database_Ini('write',DB_Name.get(),Active_Table.get(),None,None)
    except Exception as ex:
        pass
def disable_menubar(which):
    if Language.get()=="English":
        if which=="database" or which=="all":
            menubar.entryconfig('     Create/Select Database     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig("     Select Table     ", state="disabled")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Create/Modify Table     ', state="disabled")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Create/Modify Table Entry     ', state="disabled")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Table Colors     ', state="disabled")
        if which=="Grid" or which=="all":
            menubar.entryconfig('     Set Grid     ', state="disabled")
    elif Language.get()=="Spanish":        
        if which=="database" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig("     Seleccionar Tabla     ", state="disabled")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Crear/Modificar Tabla     ', state="disabled")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="disabled")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colores de la Tabla     ', state="disabled")
        if which=="Grid":
            menubar.entryconfig('     Establecer líneas     ', state="disabled")
def enable_menubar(which):
    if Language.get()=="English":                    
        if which=="database" or which=="all":
            menubar.entryconfig('     Create/Select Database     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig("     Select Table     ", state="normal")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Create/Modify Table     ', state="normal")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Create/Modify Table Entry     ', state="normal")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Table Colors     ', state="normal")
        if which=="Grid" or which=="all":
            menubar.entryconfig('     Set Grid     ', state="normal")
    elif Language.get()=="Spanish":        
        if which=="database" or which=="all":
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="disabled")
        if which=="tbl_menu" or which=="all":
            menubar.entryconfig("     Seleccionar Tabla     ", state="normal")
        if which=="modify_tbl_menu" or which=="all":
            menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
        if which=="modify_entry_menu" or which=="all":        
            menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="normal")
        if which=="Edit Colors" or which=="all":
            menubar.entryconfig('     Colores de la Tabla     ', state="normal")
        if which=="Grid" or which=="all":
            menubar.entryconfig('     Establecer líneas     ', state="normal")
def set_menu_defaults():
    disable_menubar("tbl_menu")
    disable_menubar("modify_tbl_menu")
    disable_menubar("modify_entry_menu")
    disable_menubar("Edit Colors")
    disable_menubar("Grid")
    if Language.get()=="English":
        modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
        modify_tbl_menu.entryconfig("Delete Table", state="disabled")
        modify_tbl_menu.entryconfig("Rename Table", state="disabled")
    elif Language.get()=="Spanish":    
        modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
        modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
        modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
def config_menu(selected=None):
    if Language.get()=="English":
        if selected=='db_selected':    
            menubar.entryconfig("     Select Table     ", state="normal")
            menubar.entryconfig('     Create/Modify Table     ', state="normal")
            menubar.entryconfig('     Create/Modify Table Entry     ', state="disabled")
            modify_tbl_menu.entryconfig("Create New Table", state="normal")
            menubar.entryconfig('     Table Colors     ', state="disabled")
            menubar.entryconfig('     Set Grid     ', state="disabled")
            num_tbls=Database.get_num_tbls()
            if num_tbls==0:
                menubar.entryconfig("     Select Table     ", state="disabled")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
            else:
                menubar.entryconfig("     Select Table     ", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
            modify_tbl_menu.entryconfig("Rename Table", state="disabled")
        elif selected=='db_deleted':
            db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
            if len(db_files)==0:
                menubar.entryconfig('     Create/Select Database     ', state="normal")
                db_menu.entryconfig('Delete Database', state="disabled")
                db_menu.entryconfig('Create New Database', state="normal")
                menubar.entryconfig("     Select Table     ", state="disabled")
                menubar.entryconfig('     Create/Modify Table     ', state="disabled")
                menubar.entryconfig('     Create/Modify Table Entry     ', state="disabled")
                menubar.entryconfig('     Table Colors     ', state="disabled")
                menubar.entryconfig('     Set Grid     ', state="disabled")
            else:    
                menubar.entryconfig('     Create/Select Database     ', state="normal")
                db_menu.entryconfig('Create New Database', state="normal")
                db_menu.entryconfig('Delete Database', state="normal")
        elif selected==None:
            menubar.entryconfig('     Create/Select Database     ', state="normal")
            menubar.entryconfig('     Create/Modify Table     ', state="normal")
            num_tbls=Database.get_num_tbls()
            if num_tbls==0:# No Tables Exist
                menubar.entryconfig("     Select Table     ", state="disabled")
                menubar.entryconfig('     Create/Modify Table     ', state="normal")
                menubar.entryconfig('     Create/Modify Table Entry     ', state="disabled")
                menubar.entryconfig('     Table Colors     ', state="disabled")
                menubar.entryconfig('     Set Grid     ', state="disabled")
                modify_tbl_menu.entryconfig("Create New Table", state="normal")
                modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
                modify_tbl_menu.entryconfig("Delete Table", state="disabled")
                modify_tbl_menu.entryconfig("Rename Table", state="disabled")
                modify_entry_menu.entryconfig("Add New Row", state="disabled")
                modify_entry_menu.entryconfig("Edit Table Row", state="disabled")
                modify_entry_menu.entryconfig("Delete Table Row", state="disabled")
                modify_entry_menu.entryconfig("Add New Column", state="disabled")
                modify_entry_menu.entryconfig("Delete Table Column", state="disabled")
                modify_entry_menu.entryconfig("Rename Table Column", state="disabled")
            else:# Tables Exist
                menubar.entryconfig("     Select Table     ", state="normal")
                menubar.entryconfig('     Create/Modify Table     ', state="normal")
                menubar.entryconfig('     Create/Modify Table Entry     ', state="normal")
                modify_tbl_menu.entryconfig("Create New Table", state="normal")
                if Active_Table.get()=="":
                    modify_tbl_menu.entryconfig("Edit Table Definitions", state="disabled")
                    modify_tbl_menu.entryconfig("Rename Table", state="disabled")
                else:    
                    modify_tbl_menu.entryconfig("Edit Table Definitions", state="normal")
                    modify_tbl_menu.entryconfig("Rename Table", state="normal")
                modify_tbl_menu.entryconfig("Delete Table", state="normal")
                modify_entry_menu.entryconfig("Add New Row", state="normal")
                modify_entry_menu.entryconfig("Edit Table Row", state="normal")
                modify_entry_menu.entryconfig("Delete Table Row", state="normal")
                modify_entry_menu.entryconfig("Add New Column", state="normal")
                modify_entry_menu.entryconfig("Delete Table Column", state="normal")
                modify_entry_menu.entryconfig("Rename Table Column", state="normal")
    elif Language.get()=="Spanish":            
        if selected=='db_selected':    
            menubar.entryconfig("     Seleccionar Tabla     ", state="normal")
            menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
            menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="disabled")
            modify_tbl_menu.entryconfig("Crear Nueva Tabla", state="normal")
            menubar.entryconfig('     Colores de la Tabla     ', state="disabled")
            menubar.entryconfig('     Establecer líneas     ', state="disabled")
            num_tbls=Database.get_num_tbls()
            if num_tbls==0:
                menubar.entryconfig("     Seleccionar Tabla     ", state="disabled")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
            else:
                menubar.entryconfig("     Seleccionar Tabla     ", state="normal")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
            modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
        elif selected=='db_deleted':
            db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
            if len(db_files)==0:
                menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
                db_menu.entryconfig('Eliminar Base de Datos', state="disabled")
                db_menu.entryconfig('Crear Nueva Base de Datos', state="normal")
                menubar.entryconfig("     Seleccionar Tabla     ", state="disabled")
                menubar.entryconfig('     Crear/Modificar Tabla     ', state="disabled")
                menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="disabled")
                menubar.entryconfig('     Colores de la Tabla     ', state="disabled")
                menubar.entryconfig('     Establecer líneas     ', state="disabled")
            else:    
                menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
                db_menu.entryconfig('Crear Nueva Base de Datos', state="normal")
                db_menu.entryconfig('Eliminar Base de Datos', state="normal")
        elif selected==None:
            menubar.entryconfig('     Crear/Seleccionar Base de Datos     ', state="normal")
            menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
            num_tbls=Database.get_num_tbls()
            if num_tbls==0:# No Tables Exist
                menubar.entryconfig("     Seleccionar Tabla     ", state="disabled")
                menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
                menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="disabled")
                menubar.entryconfig('     Colores de la Tabla     ', state="disabled")
                menubar.entryconfig('     Establecer líneas     ', state="disabled")
                modify_tbl_menu.entryconfig("Crear Nueva Tabla", state="normal")
                modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="disabled")
                modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
                modify_entry_menu.entryconfig("Agregar Nueva Fila", state="disabled")
                modify_entry_menu.entryconfig("Editar Fila de Tabla", state="disabled")
                modify_entry_menu.entryconfig("Eliminar Fila de Tabla", state="disabled")
                modify_entry_menu.entryconfig("Agregar Nueva Columna", state="disabled")
                modify_entry_menu.entryconfig("Eliminar Columna", state="disabled")
                modify_entry_menu.entryconfig("Cambiar Nombre de Columna", state="disabled")
            else:# Tables Exist
                menubar.entryconfig("     Seleccionar Tabla     ", state="normal")
                menubar.entryconfig('     Crear/Modificar Tabla     ', state="normal")
                menubar.entryconfig('     Crear/Modificar Entrada de Tabla     ', state="normal")
                modify_tbl_menu.entryconfig("Crear Nueva Tabla", state="normal")
                if Active_Table.get()=="":
                    modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="disabled")
                    modify_tbl_menu.entryconfig("Renombrar Tabla", state="disabled")
                else:    
                    modify_tbl_menu.entryconfig("Editar Definiciones de Tabla", state="normal")
                    modify_tbl_menu.entryconfig("Renombrar Tabla", state="normal")
                modify_tbl_menu.entryconfig("Eliminar Tabla", state="normal")
                modify_entry_menu.entryconfig("Agregar Nueva Fila", state="normal")
                modify_entry_menu.entryconfig("Editar Fila de Tabla", state="normal")
                modify_entry_menu.entryconfig("Eliminar Fila de Tabla", state="normal")
                modify_entry_menu.entryconfig("Agregar Nueva Columna", state="normal")
                modify_entry_menu.entryconfig("Eliminar Columna", state="normal")
                modify_entry_menu.entryconfig("Cambiar Nombre de Columna", state="normal")
def change_language():
    if Language.get()=="Spanish":
        msg="¡El Idioma se puede Cambiar después de que se cierre este Programa y luego se vuelva a abrir!"
        messagebox.showinfo("Cambiar Idioma", msg)
    else:
        msg="The Language Can Be Changed After This Program Is Closed Then Reopened!"
        messagebox.showinfo("Change Language", msg)
    pgm_ini_file=os.path.join(DB_Path.get(), "My_Database.ini")
    if os.path.exists(pgm_ini_file):os.remove(pgm_ini_file)
def set_default_colors():# If No INI FILE Exist, Setup With tk Variables And Create File
    Window_Color.set('#e2eef8')
    Header_BG_Color.set('#f9ff99')
    Header_Font_Color.set('#072663')
    Entry_Font_Color.set('#000000')
    Grid_Color.set('#7b7b7b')
    Grid_Status.set(1)
def populate_db_menu():
    db_menu.delete(0,"end")
    if Language.get()=="English":
        db_menu.add_command(label='Create New Database',command=Database.create_new_database)
        db_menu.add_command(label='Import Database',command=Database.import_database)
        db_menu.add_command(label='Delete Database',command=Database.delete_database)
    elif Language.get()=="Spanish":    
        db_menu.add_command(label='Crear Nueva Base de Datos',command=Database.create_new_database)
        db_menu.add_command(label='Importar Base de Datos',command=Database.import_database)
        db_menu.add_command(label='Eliminar Base de Datos',command=Database.delete_database)
    db_menu.add_separator()
    db_files=[file for file in os.listdir(DB_Path.get()) if os.path.splitext(file)[1] in DB_Extensions]# Retrieve All Databases In Folder
    db_files=sorted(db_files)
    for i in range(len(db_files)):# Populate db_menu
        lbl_name=db_files[i]
        db_menu.add_command(label=lbl_name,command=lambda a=DB_Path.get(),b=db_files[i]:Database.populate_tbl_menu(a,b))
        db_menu.add_separator()
def populate_menus():
    if Language.get()=="English":
        menubar.add_cascade(label='    File     ',menu=file_menu)
        file_menu.add_command(label='Change Language',command=lambda:change_language())
        file_menu.add_separator()
        file_menu.add_command(label='About',command=lambda:about())
        file_menu.add_separator()
        file_menu.add_command(label='Exit',command=lambda:destroy())
        menubar.add_cascade(label='     Create/Select Database     ',menu=db_menu)
        populate_db_menu()
        menubar.add_cascade(label='     Select Table     ',menu=tbl_menu)
        menubar.add_cascade(label='     Create/Modify Table     ',menu=modify_tbl_menu)
        modify_tbl_menu.add_command(label='Create New Table',command=Database.create_new_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Edit Table Definitions',command=Database.edit_table_definitions)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Rename Table',command=Database.rename_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Delete Table',command=Database.delete_table)
        modify_tbl_menu.add_separator()
        menubar.add_cascade(label='     Create/Modify Table Entry     ',menu=modify_entry_menu)
        modify_entry_menu.add_command(label='Add New Row',command=Database.add_new_row)
        modify_entry_menu.add_command(label='Edit Table Row',command=Database.edit_tbl_row)
        modify_entry_menu.add_command(label='Delete Table Row',command=Database.delete_tbl_row)
        modify_entry_menu.add_separator()
        modify_entry_menu.add_command(label='Add New Column',command=Database.add_new_column)
        modify_entry_menu.add_command(label='Rename Table Column',command=Database.rename_column)
        modify_entry_menu.add_command(label='Delete Table Column',command=Database.drop_column)
        modify_entry_menu.add_separator()
        menubar.add_cascade(label='     Table Colors     ',menu=color_menu)
        menubar.entryconfig('     Create/Modify Table     ', state="disabled")
        menubar.add_cascade(label='     Set Grid     ',menu=grid_menu)
    elif Language.get()=="Spanish":    
        menubar.add_cascade(label='    Archivo     ',menu=file_menu)
        file_menu.add_command(label='Cambiar Idioma',command=lambda:change_language())
        file_menu.add_separator()
        file_menu.add_command(label='Acerca de',command=lambda:about())
        file_menu.add_separator()
        file_menu.add_command(label='Salida',command=lambda:destroy())
        menubar.add_cascade(label='     Crear/Seleccionar Base de Datos     ',menu=db_menu)
        populate_db_menu()
        menubar.add_cascade(label='     Seleccionar Tabla     ',menu=tbl_menu)
        menubar.add_cascade(label='     Crear/Modificar Tabla     ',menu=modify_tbl_menu)
        modify_tbl_menu.add_command(label='Crear Nueva Tabla',command=Database.create_new_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Editar Definiciones de Tabla',command=Database.edit_table_definitions)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Renombrar Tabla',command=Database.rename_table)
        modify_tbl_menu.add_separator()
        modify_tbl_menu.add_command(label='Eliminar Tabla',command=Database.delete_table)
        modify_tbl_menu.add_separator()
        menubar.add_cascade(label='     Crear/Modificar Entrada de Tabla     ',menu=modify_entry_menu)
        modify_entry_menu.add_command(label='Agregar Nueva Fila',command=Database.add_new_row)
        modify_entry_menu.add_command(label='Editar Fila de Tabla',command=Database.edit_tbl_row)
        modify_entry_menu.add_command(label='Eliminar Fila de Tabla',command=Database.delete_tbl_row)
        modify_entry_menu.add_separator()
        modify_entry_menu.add_command(label='Agregar Nueva Columna',command=Database.add_new_column)
        modify_entry_menu.add_command(label='Cambiar Nombre de Columna',command=Database.rename_column)
        modify_entry_menu.add_command(label='Eliminar Columna',command=Database.drop_column)
        modify_entry_menu.add_separator()
        menubar.add_cascade(label='     Colores de la Tabla     ',menu=color_menu)
        menubar.entryconfig('     Crear/Modificar Tabla     ', state="disabled")
        menubar.add_cascade(label='     Establecer líneas     ',menu=grid_menu)
def populate_color_menu():
    if Language.get()=="English":
        color_menu.add_command(label='Main Window Color',command=lambda:change_colors('window'))
        color_menu.add_separator()
        color_menu.add_command(label='Column Names Background Color',command=lambda:change_colors('header_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Column Names Text Color',command=lambda:change_colors('header_font'))
        color_menu.add_separator()
        color_menu.add_command(label='Table Entries Text Color',command=lambda:change_colors('entry_font'))
        color_menu.add_separator()
        color_menu.add_command(label='Grid Color',command=lambda:change_colors('grid_color'))
    elif Language.get()=="Spanish":    
        color_menu.add_command(label='Color de la Ventana Principal',command=lambda:change_colors('window'))
        color_menu.add_separator()
        color_menu.add_command(label='Color de Fondo de los Nombres de las Columnas',command=lambda:change_colors('header_bg'))
        color_menu.add_separator()
        color_menu.add_command(label='Nombres de Columnas Color del Texto',command=lambda:change_colors('header_font'))
        color_menu.add_separator()
        color_menu.add_command(label='Color del Texto de las Entradas de la Tabla',command=lambda:change_colors('entry_font'))
        color_menu.add_separator()
        color_menu.add_command(label='Color de las Lineas de Cuadricula',command=lambda:change_colors('grid_color'))
def populate_grid_menu(stat):
    if Language.get()=="English":
        if stat=='off':lbl='Turn Grid Off'
        if stat=='on':lbl='Turn Grid On'
    elif Language.get()=="Spanish":    
        if stat=='off':lbl='Desactivar las Lineas de la Cuadricula'
        if stat=='on':lbl='Activar Lineas de Cuadricula'
    grid_menu.add_command(label=lbl,command=lambda:Database.set_grid(stat))
if __name__ == '__main__':
    root=tk.Tk()
    style=ttk.Style()
    style.theme_use('classic')
    style.map('TCombobox', background=[('readonly','#0b5394')])# Down Arrow
    style.map('TCombobox', fieldbackground=[('readonly','#d4f2f2')])
    style.map('TCombobox', selectbackground=[('readonly','#0b5394')])
    style.map('TCombobox', selectforeground=[('readonly', '#ffffff')])
    screen_width=root.winfo_screenwidth() # Width of the screen
    screen_height=root.winfo_screenheight() # Height of the screen
    root_width=screen_width/1.6
    root_height=screen_height/1.8
    x=(screen_width/2)-(root_width/2)
    y=(screen_height/2)-(root_height/1.8)
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y, ))
    root.font=font.Font(family='Times New Romans', size=10, weight='bold', slant='italic')
    root.title("My SQLite3 Database Creator/Browser")
    root.protocol("WM_DELETE_WINDOW", destroy)
    DB_Path=StringVar()
    DB_Path.set(Path(__file__).parent.absolute())
    filename='Database.ico' # Program icon
    ico_path=os.path.join(DB_Path.get(), filename)
    root.iconbitmap(default=ico_path) # root and children
    DB_Extensions=[".db",".db2",".db3",".sl2",".sl3",".sdb",".s2db",".sqlite",".sqlite2",".sqlite3"]
    Language=StringVar()
    Window_Color=StringVar()
    Header_BG_Color=StringVar()
    Header_Font_Color=StringVar()
    Entry_Font_Color=StringVar()
    Grid_Color=StringVar()
    Grid_Status=IntVar()# 1=On, 0=Off
    DB_Name=StringVar()# Name Of Database Without Exts Or Spaces
    Active_DB=StringVar()# Complete Address Of Database File With Exts Without Spaces
    Active_Table=StringVar()
    Edit_Definitions=BooleanVar()
    Num_Rows=IntVar()
    Num_Columns=IntVar()
    Edit_Definitions.set(False)
    menubar=Menu(root)# Create Menubar
    file_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    db_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    tbl_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    modify_tbl_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    modify_entry_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    color_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    grid_menu=Menu(menubar,background='#d7fdfd',foreground='black',tearoff=0,font=root.font)# File Menu and commands
    root.config(menu=menubar)
    big_font=font.Font(family='Times New Romans', size=12, weight='bold', slant='italic')
    tk.Frame.scroll=XY_Scroll(root) # Vertical/Horizontal Scrollbars
    Database.create_default_db()
    root.after(500, Database.select_language)
    root.mainloop()

