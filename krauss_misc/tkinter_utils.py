import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

def clear_text(widget):
   widget.delete("1.0","end")


def replace_text(widget, mystring):
    clear_text(widget)
    widget.insert('1.0', mystring)


class abstract_window(object):
    """I am mixing C and Python terminolgy here, but this is a class
    you mixin with other classes, you don't actually create an
    instance of this class."""
    ## def __init__(self, parent, title="Cool Toplevel Window", geometry='800x600'):
    ##     super().__init__(parent)
    ##     self.parent = parent
    ##     self.geometry(geometry)
    ##     self.title(title)
    ##     #self.make_widgets()


    def make_widgets(self):
        raise NotImplementedError("my_toplevel_window is intended to be an abstract class, you must override the make_widgets method")


    def make_label(self, text, root=None, attr=None):
        if root is None:
            root = self
        widget = ttk.Label(root, text=text)
        if attr is not None:
            # store widget to a parameter (attribute) of the class
            setattr(self, attr, widget)
        return widget


    def grid_label_sw(self, widget, row, col):
        widget.grid(row=row, column=col, sticky='SW', pady=(5,1), padx=10)


    def grid_widget(self, widget, row, col, padx=10, pady=5, **kwargs):
        widget.grid(row=row, column=col, padx=padx, pady=pady, **kwargs)


    def grid_box_nw(self, widget, row, col, **grid_opts):
        if 'sticky' in grid_opts:
            sticky = grid_opts['sticky']
        else:
            sticky = 'NW'
        widget.grid(row=row, column=col, sticky=sticky, pady=(1,5), padx=10)


    def make_label_and_grid_sw(self, text, row, col, root=None, attr=None):
        if root is None:
            root = self
        widget = self.make_label(text, root=root, attr=attr)
        self.grid_label_sw(widget, row, col)
        return widget


    def make_widget_and_var_grid_nw(self, basename, row, col, type="entry", root=None, **grid_opts):
        if root is None:
            root = self

        myvar = tk.StringVar()
        if type.lower() == 'entry':
            widget_class = ttk.Entry
            tail = '_entry'
        elif 'combo' in type.lower():
            widget_class = ttk.Combobox
            tail = '_combobox'

        mywidget = widget_class(root, textvariable=myvar)
        self.grid_box_nw(mywidget, row, col, **grid_opts)
        var_attr = basename + '_var'
        setattr(self, var_attr, myvar)
        widget_attr = basename + tail
        setattr(self, widget_attr, mywidget)
        return mywidget


    def make_text_box_and_grid_nw(self, row, col, width=50, height=10, \
                                  root=None, wrap='word', sticky='nw', \
                                  font=("Helvetica", 14), \
                                  ):
        if root is None:
            root = self

        widget = tk.Text(root, width=width, height=height, font=font)
        self.grid_box_nw(widget, row, col, sticky=sticky)
        return widget
        


    def _assign_widget_and_var_to_attrs(self, basename, tail, mywidget, myvar):
        var_attr = basename + '_var'
        setattr(self, var_attr, myvar)
        widget_attr = basename + tail
        setattr(self, widget_attr, mywidget)


    def make_listbox_and_var(self, basename, row, col, root=None, height=6, **grid_opts):
        if root is None:
            root = self

        myvar = tk.StringVar([])

        mywidget = tk.Listbox(root, \
                              listvariable=myvar, \
                              height=height, \
                              #selectmode='extended'
                              )
        self.grid_box_nw(mywidget, row, col, **grid_opts)
        tail = "_listbox"
        self._assign_widget_and_var_to_attrs(basename, tail, mywidget, myvar)
        return mywidget


    def make_entry_and_var_grid_nw(self, basename, row, col, root=None, **grid_opts):
        if root is None:
            root = self

        return self.make_widget_and_var_grid_nw(basename, row, col, type="entry", root=root, **grid_opts)
        ## myvar = tk.StringVar()
        ## myentry = ttk.Entry(self, textvariable=myvar)
        ## self.grid_box_nw(myentry, row, col)
        ## var_attr = basename + '_var'
        ## setattr(self, var_attr, myvar)
        ## entry_attr = basename + '_entry'
        ## setattr(self, entry_attr, myentry)


    def make_combo_and_var_grid_nw(self, basename, row, col, root=None):
        if root is None:
            root = self

        return self.make_widget_and_var_grid_nw(basename, row, col, type="combobox", root=root)        


    def make_button_and_grid(self, btn_text, row, col, command=None, root=None, sticky=None):
        if root is None:
            root = self

        kwargs = {}
        if command is not None:
            kwargs['command'] = command

        grid_opts = {}
        if sticky is not None:
            print("sticky = %s" % sticky)
            grid_opts['sticky'] = sticky

        mybutton = ttk.Button(root, text=btn_text, **kwargs)
        mybutton.grid(column=col, row=row, pady=10, padx=10, **grid_opts)
        return mybutton


class my_toplevel_window(tk.Toplevel, abstract_window):
    def __init__(self, parent, title="Cool Toplevel Window", geometry='800x600'):
        super().__init__(parent)
        self.parent = parent
        self.geometry(geometry)
        self.title(title)
        #self.make_widgets()


    ## def make_widgets(self):
    ##     raise NotImplementedError("my_toplevel_window is intended to be an abstract class, you must override the make_widgets method")


    ## def make_label(self, text, root=None, attr=None):
    ##     if root is None:
    ##         root = self
    ##     widget = ttk.Label(root, text=text)
    ##     if attr is not None:
    ##         # store widget to a parameter (attribute) of the class
    ##         setattr(self, attr, widget)
    ##     return widget


    ## def grid_label_sw(self, widget, row, col):
    ##     widget.grid(row=row, column=col, sticky='SW', pady=(5,1), padx=10)


    ## def grid_widget(self, widget, row, col, padx=10, pady=5, **kwargs):
    ##     widget.grid(row=row, column=col, padx=padx, pady=pady, **kwargs)


    ## def grid_box_nw(self, widget, row, col, **grid_opts):
    ##     if 'sticky' in grid_opts:
    ##         sticky = grid_opts['sticky']
    ##     else:
    ##         sticky = 'NW'
    ##     widget.grid(row=row, column=col, sticky=sticky, pady=(1,5), padx=10)


    ## def make_label_and_grid_sw(self, text, row, col, root=None, attr=None):
    ##     if root is None:
    ##         root = self
    ##     widget = self.make_label(text, root=root, attr=attr)
    ##     self.grid_label_sw(widget, row, col)
    ##     return widget


    ## def make_widget_and_var_grid_nw(self, basename, row, col, type="entry", root=None):
    ##     if root is None:
    ##         root = self

    ##     myvar = tk.StringVar()
    ##     if type.lower() == 'entry':
    ##         widget_class = ttk.Entry
    ##         tail = '_entry'
    ##     elif 'combo' in type.lower():
    ##         widget_class = ttk.Combobox
    ##         tail = '_combobox'

    ##     mywidget = widget_class(root, textvariable=myvar)
    ##     self.grid_box_nw(mywidget, row, col)
    ##     var_attr = basename + '_var'
    ##     setattr(self, var_attr, myvar)
    ##     widget_attr = basename + tail
    ##     setattr(self, widget_attr, mywidget)
    ##     return mywidget


    ## def _assign_widget_and_var_to_attrs(self, basename, tail, mywidget, myvar):
    ##     var_attr = basename + '_var'
    ##     setattr(self, var_attr, myvar)
    ##     widget_attr = basename + tail
    ##     setattr(self, widget_attr, mywidget)


    ## def make_listbox_and_var(self, basename, row, col, root=None, height=6, grid_opts={}):
    ##     if root is None:
    ##         root = self

    ##     myvar = tk.StringVar([])

    ##     mywidget = tk.Listbox(root, \
    ##                           listvariable=myvar, \
    ##                           height=height, \
    ##                           #selectmode='extended'
    ##                           )
    ##     self.grid_box_nw(mywidget, row, col, **grid_opts)
    ##     tail = "_listbox"
    ##     self._assign_widget_and_var_to_attrs(basename, tail, mywidget, myvar)
    ##     return mywidget


    ## def make_entry_and_var_grid_nw(self, basename, row, col, root=None):
    ##     if root is None:
    ##         root = self

    ##     return self.make_widget_and_var_grid_nw(basename, row, col, type="entry", root=root)
    ##     ## myvar = tk.StringVar()
    ##     ## myentry = ttk.Entry(self, textvariable=myvar)
    ##     ## self.grid_box_nw(myentry, row, col)
    ##     ## var_attr = basename + '_var'
    ##     ## setattr(self, var_attr, myvar)
    ##     ## entry_attr = basename + '_entry'
    ##     ## setattr(self, entry_attr, myentry)


    ## def make_combo_and_var_grid_nw(self, basename, row, col, root=None):
    ##     if root is None:
    ##         root = self

    ##     return self.make_widget_and_var_grid_nw(basename, row, col, type="combobox", root=root)        


    ## def make_button_and_grid(self, btn_text, row, col, command=None, root=None, sticky=None):
    ##     if root is None:
    ##         root = self

    ##     kwargs = {}
    ##     if command is not None:
    ##         kwargs['command'] = command

    ##     grid_opts = {}
    ##     if sticky is not None:
    ##         print("sticky = %s" % sticky)
    ##         grid_opts['sticky'] = sticky

    ##     mybutton = ttk.Button(root, text=btn_text, **kwargs)
    ##     mybutton.grid(column=col, row=row, pady=10, padx=10, **grid_opts)
    ##     return mybutton
