from cgitb import text
from email.mime import application
from inspect import Parameter
from logging.config import valid_ident
from tkinter import *
from tkinter import ttk
import sqlite3


# Crea una clase Python para definir el interfaz de usuario de
# la aplicación. Cuando se cree un objeto del tipo 'Aplicacion'
# se ejecutará automáticamente el método __init__() qué 
# construye y muestra la ventana con todos sus widgets: 


class Product:

    db_name = "database.db"

    def __init__(self,window):
        self.wind = window
        self.wind.title("Products Application")

        # Crear a Frame Container
        frame = LabelFrame(self.wind, text= "Register a New Product")
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Name Input
        Label(frame, text= "Name: ").grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()  #Permite que al abrir el curso aparezca dentro de la caja de texto Name
        self.name.grid(row=1,column=1)

        # Price Input
        Label(frame, text= "Price: ").grid(row=2, column=0)
        self.price = Entry(frame)
        self.price.grid(row=2,column=1)

        # Button Save
        ttk.Button(frame, text= "Save Product", command = self.add_products).grid(row=3, column=0, columnspan=2, sticky= W + E)

        # Output Messages
        self.message = Label(text="", fg = 'red')
        self.message.grid(row=3, column=2, columnspan=2, sticky= W+E)

        # Table
        self.tree = ttk.Treeview(height=10, columns=2)
        self.tree.grid(row=4 , column=2, columnspan=2)
        self.tree.heading('#0', text= "Name", anchor=CENTER)
        self.tree.heading('#1', text= "Price", anchor=CENTER)

        #Buttons
        ttk.Button(text= "EDIT", command = self.edit_product).grid(row=5, column=2, sticky= W + E)
        ttk.Button(text= "DELETE", command = self.confirm_change).grid(row=5, column=3, sticky= W + E)



        # FIlling the rows
        self.get_products()
        
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_products(self):
        
        #cleaning table
        records = self.tree.get_children() # Me permite obtener todos los datos existentes en la tabla (luego los recorro y los limpio)
        for element in records:
            self.tree.delete(element)

        #query database
        query = 'SELECT * FROM product ORDER BY name DESC'
        db_rows = self.run_query(query)
        
        #filling data
        for row in db_rows:
            self.tree.insert("",0, text = row[1], values= row[2])

    # Creo una función que me permite validar que los dos datos tienen valor
    def validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0
    
    def add_products(self):
        if self.validation():
            query = "INSERT INTO product VALUES(NULL, ?,?)"
            parameters = (self.name.get(), self.price.get())
            self.run_query(query, parameters)
            self.message["text"] = "Product {} added Succesfully".format(self.name.get())
            self.name.delete(0,END)
            self.price.delete(0,END)
        else:    
            self.message["text"] = "No ha cargado nada"
        
        self.get_products() # Para actualizar la tabla

    # Borar procutos
    def delete_products(self, name):
        query = "DELETE FROM product WHERE name = ?"
        self.run_query(query, (name, ))
        self.quit_delete()
        self.get_products()

    def edit_product(self):
        #Limpio el mensaje de texto
        self.message['text']=""

        # Verifico que haya seleccionado algún item
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = "Please Select a Record"
            return

        name = self.tree.item(self.tree.selection())['text']
        old_price = self.tree.item(self.tree.selection())['values'][0]   

        self.edit_wind = Toplevel()
        self.edit_wind.title = "Edit Product"

        #Nombre Viejo
        Label(self.edit_wind, text= "Nombre Viejo: ").grid(row=0,column=1)
        Entry(self.edit_wind, textvariable= StringVar(self.edit_wind, value=name), state= 'readonly').grid(row=0, column=2)

        #Nombre Nuevo
        Label(self.edit_wind, text= "Nombre Nuevo: ").grid(row=1,column=1)
        new_name = Entry(self.edit_wind)
        new_name.grid(row=1, column=2)

        #Precio Viejo
        Label(self.edit_wind, text= "Precio Viejo: ").grid(row = 2, column = 1)
        Entry(self.edit_wind, textvariable= StringVar(self.edit_wind, value = old_price), state= 'readonly').grid(row=2, column=2)
        
        #Precio Viejo
        Label(self.edit_wind, text= "Precio Nuevo: ").grid(row=3, column=1)
        new_price = Entry(self.edit_wind)
        new_price.grid(row=3, column=2)

        #Boton
        Button(self.edit_wind, text= 'Actualizar', command = lambda: self.edit_records(new_name.get(), name, new_price.get(), 
        old_price)).grid(row=4, column=1, sticky=W+E)

        #Boton Cancel
        Button(self.edit_wind, text= 'Cancel', command = self.quit_edit).grid(row=4, column=2, sticky=W+E)


    def edit_records(self, new_name, name, new_price, old_price):
        query = "UPDATE product SET name = ?, price = ? WHERE name=? AND price=?"
        parameters = (new_name, new_price, name, old_price)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = "Se ha actualizado el valor de {}".format(new_name)
        self.get_products()


    def confirm_change(self):
        #Limpio el mensaje de texto
        self.message['text']=""

        # Verifico que haya seleccionado algún item
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = "Please Select a Record"
            return

        name = self.tree.item(self.tree.selection())['text']
        old_price = self.tree.item(self.tree.selection())['values'][0]   

        self.delete_wind = Toplevel()
        self.delete_wind.title = "Confirm Change Product"

        #Nombre Viejo
        Label(self.delete_wind, text= "Nombre Viejo: ").grid(row=0,column=1)
        Entry(self.delete_wind, textvariable= StringVar(self.delete_wind, value=name), state= 'readonly').grid(row=0, column=2)

        #Precio Viejo
        Label(self.delete_wind, text= "Precio Viejo: ").grid(row = 2, column = 1)
        Entry(self.delete_wind, textvariable= StringVar(self.delete_wind, value = old_price), state= 'readonly').grid(row=2, column=2)
        
        #Boton Confirm
        Button(self.delete_wind, text= 'Delete', command = lambda: self.delete_products(name)).grid(row=4, column=1, sticky=W+E)
        
        #Boton Cancel
        Button(self.delete_wind, text= 'Cancel', command = self.quit_delete).grid(row=4, column=2, sticky=W+E)

    def quit_delete(self):
       self.delete_wind.destroy()
    
    def quit_edit(self):
       self.edit_wind.destroy()

# Define la función main() que es en realidad la que indica 
# el comienzo del programa. Dentro de ella se crea el objeto 
# aplicación 'mi_app' basado en la clase 'Aplicación':

#def main():
#    mi_app = Aplicacion()
#    return 0

# Mediante el atributo __name__ tenemos acceso al nombre de un
# un módulo. Python utiliza este atributo cuando se ejecuta
# un programa para conocer si el módulo es ejecutado de forma
# independiente (en ese caso __name__ = '__main__') o es 
# importado:

if __name__ == '__main__':
    window = Tk()
    application = Product(window)
    window.mainloop()