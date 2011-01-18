#!/usr/bin/env python

import Tkinter
import tkMessageBox
import rwkmisc, rwkos, os, glob

from Tkinter import StringVar, IntVar, DoubleVar

pklpath = '/home/ryan/pygimp_lecturerc.pkl'

class myWindow:
    def close(self, *args, **kwargs):
        #print('got close event')
        self.mw.destroy()
        
        
    def __init__(self, title="Enter Quiz #"):

        self.mw = Tkinter.Tk()
        self.mw.option_add("*font", ("Arial", 15, "normal"))
        self.mw.geometry("+250+200")
        self.var = Tkinter.StringVar()
        entry = Tkinter.Entry(self.mw, textvariable=self.var)
        entry.focus_set()
        entry.pack()
        #entry.bind("<KP_Enter>", self.close)
        entry.bind("<Return>", self.close)
        self.mw.title(title)

        self.btn2 = Tkinter.Button(self.mw,
                                   text = "Exit",
                                   command = self.mw.destroy)
        self.btn2.pack()

        self.mw.mainloop()



class width_and_dpi_dialog:#(tkSimpleDialog.Dialog):
    def close(self, *args, **kwargs):
        #print('got close event')
        self.width_float = float(self.width_string.get())
        self.result = self.width_float, self.dpi_int.get()
        print('result = %f, %i' % self.result)
        self.mw.destroy()


    def __init__(self, title="Width and DPI Dialog"):
        self.result = None
        self.mw = Tkinter.Tk()
        self.mw.option_add("*font", ("Arial", 15, "normal"))
        self.mw.geometry("+250+200")
        Tkinter.Label(self.mw, text="Width (in.):").grid(row=0)
        Tkinter.Label(self.mw, text="dpi:").grid(row=1)
        
        self.width_string = Tkinter.StringVar()#Tkinter.DoubleVar()
        self.dpi_int = Tkinter.IntVar()
        width_entry = Tkinter.Entry(self.mw, textvariable=self.width_string)
        width_entry.grid(row=0, column=1)
        dpi_entry = Tkinter.Entry(self.mw, textvariable=self.dpi_int)
        dpi_entry.grid(row=1, column=1)
        self.dpi_int.set(300)
        self.width_string.set('')
        #self.width_float.set(3.0)
        #entry.pack()
        #entry.bind("<KP_Enter>", self.close)
        width_entry.bind("<Return>", self.close)
        self.mw.title(title)

        self.exit_btn = Tkinter.Button(self.mw,
                                       text = "Exit",
                                       command = self.mw.destroy)
        self.exit_btn.grid(row=2, column=0)

        self.go_btn = Tkinter.Button(self.mw,
                                     text = "Go",
                                     command = self.close)
        self.go_btn.grid(row=2, column=1)

        width_entry.focus_set()
        self.mw.mainloop()

    ## def body(self, master):

    ##     Label(master, text="First:").grid(row=0)
    ##     Label(master, text="Second:").grid(row=1)

    ##     self.e1 = Entry(master)
    ##     self.e2 = Entry(master)

    ##     self.e1.grid(row=0, column=1)
    ##     self.e2.grid(row=1, column=1)
    ##     return self.e1 # initial focus

    ## def apply(self):
    ##     first = string.atoi(self.e1.get())
    ##     second = string.atoi(self.e2.get())
    ##     self.result = first, second
    ##     print first, second # or something



##     def btnClick(self):

##         self.answer = tkMessageBox.askyesno(title = "Your Choice", message = 'Please click either "Yes" or "No".')

##         if self.answer:
##             tkMessageBox.showinfo(title = "Yes", message = "Your choice was: Yes.")
##         else:
##             tkMessageBox.showinfo(title = "No", message = "Your choice was: No.")


class pickle_entry(object):
    def __init__(self, parent, mw, label, key, row, \
                 varclass=None):
        if varclass is None:
            varclass = StringVar
        self.var = varclass()
        self.parent = parent
        self.mw = mw
        self.label = label
        self.key = key
        self.row = row
        curtext = label + ":"
        Tkinter.Label(mw, text=curtext).grid(row=row, column=0, sticky='e')
        self.entry = Tkinter.Entry(mw, textvariable=self.var, \
                                   width=75)  
        self.entry.grid(row=row, column=1)


    def get(self):
        return self.key, self.var.get()


    def load_pickle(self):
        value = self.parent.pickle[self.key]
        self.var.set(value)
        

class lecture_pickle_dialog:#(tkSimpleDialog.Dialog):
    def close(self, *args, **kwargs):
        print('got close event')
        #self.width_float = float(self.width_string.get())
        #self.result = self.width_float, self.dpi_int.get()
        #print('result = %f, %i' % self.result)
        self.set_pickle()
        self.save_pickle()
        self.mw.destroy()


    def load_pickle(self):
        for entry in self.entries:
            entry.load_pickle()

    def set_pickle(self):
        for entry in self.entries:
            key, val = entry.get()
            self.pickle[key] = val


    def save_pickle(self):
        rwkmisc.SavePickle(self.pickle, pklpath)
        

    def __init__(self, title="Lecture Pickle Dialog"):
        self.pickle = rwkmisc.LoadPickle(pklpath)        
        self.result = None
        self.mw = Tkinter.Tk()
        self.mw.option_add("*font", ("Arial", 15, "normal"))
        self.mw.geometry("+600+300")
        self.labels = ['Lecture Path', 'Course Num.', \
                       'Search Pattern', 'Date Stamp', \
                       'Pat', 'Current Slide', \
                       'Outline Slide']

        self.keys = ['lecture_path', 'course_num', \
                     'search_pat', 'date_stamp' , \
                     'pat', 'current_slide', 'outline_slide']

        self.data = [('Lecture Path', 'lecture_path', StringVar), \
                     ('Course Num.', 'course_num', StringVar), \
                     ('Search Pattern', 'search_pat', StringVar), \
                     ('Date Stamp', 'date_stamp', StringVar), \
                     ('Pat', 'pat', StringVar), \
                     ('Current Slide', 'current_slide', IntVar), \
                     ('Outline Slide', 'outline_slide', IntVar), \
                      ]

        self.entries = []
        
        for i, tup in enumerate(self.data):
            label = tup[0]
            key = tup[1]
            varclass = tup[2]
            pickle = pickle_entry(self, self.mw, \
                                  label=label, \
                                  key=key, \
                                  row=i, \
                                  varclass=varclass)
            self.entries.append(pickle)
            
        N = len(self.data)
        
        self.mw.title('Pickle Editor')

        self.exit_btn = Tkinter.Button(self.mw,
                                       text = "Exit",
                                       command = self.mw.destroy)
        self.exit_btn.grid(row=N, column=0)

        self.go_btn = Tkinter.Button(self.mw,
                                     text = "Go",
                                     command = self.close)
        self.go_btn.grid(row=N, column=1)
        self.load_pickle()
        self.mw.mainloop()


class reset_lecture_dialog:#(tkSimpleDialog.Dialog):
    def close(self, *args, **kwargs):
        print('got close event')
        self.pickle['current_slide'] = 0
        #self.width_float = float(self.width_string.get())
        #self.result = self.width_float, self.dpi_int.get()
        #print('result = %f, %i' % self.result)
        if self.var1.get():
            print('reseting outline slide')
            self.reset_outline()
        if self.var2.get():
            print('deleting existing slides')
            self.delete_existing_slides()
        rwkmisc.SavePickle(self.pickle, pklpath)
        self.mw.destroy()


    def reset_outline(self):
        self.pickle['outline_slide'] = 0


    def _build_pat(self, end='*'):
        lp = self.pickle['lecture_path']
        pat = self.pickle['search_pat'] + end
        return os.path.join(lp, pat)


    def build_xcf_pat(self):
        self.xcf_pat = self._build_pat(end='*.xcf')


    def build_delete_pat(self):
        self.delete_pat = self._build_pat(end='*')


    def delete_existing_slides(self):
        self.build_delete_pat()
        rwkos.delete_from_glob_pat(self.delete_pat)
        

    def __init__(self, title="Reset Lecture Dialog"):
        self.result = None
        self.mw = Tkinter.Tk()
        self.mw.option_add("*font", ("Arial", 15, "normal"))
        self.mw.geometry("+300+300")

        self.pickle = rwkmisc.LoadPickle(pklpath)

        #Need to display the number of existing slides and the
        #current outline slide number

        label1 = Tkinter.Label(self.mw, \
                               text='Number of existing slides')
        label1.grid(row=0, column=0, sticky='w')
        self.num_slides = IntVar()
        self.entry1 = Tkinter.Entry(self.mw, \
                                    textvariable=self.num_slides, \
                                    width=5)
        self.entry1.grid(row=0, column=1)

        self.build_xcf_pat()
        self.existing_slides = glob.glob(self.xcf_pat)
        self.num_slides.set(len(self.existing_slides))


        label2 = Tkinter.Label(self.mw, \
                               text='Outline Slide')
        label2.grid(row=1, column=0, sticky='w')

        self.outline_slide = IntVar()
        self.entry2 = Tkinter.Entry(self.mw, \
                                    textvariable=self.outline_slide, \
                                    width=5)
        self.entry2.grid(row=1, column=1)
        
        self.outline_slide.set(self.pickle['outline_slide'])
        
        
        self.var1 = IntVar()
        check1 = Tkinter.Checkbutton(self.mw, \
                                     text="Reset outline slide", \
                                     variable=self.var1)
        check1.var = self.var1
        check1.grid(row=2, sticky='w')


        self.var2 = IntVar()
        check2 = Tkinter.Checkbutton(self.mw, \
                                     text="Delete existing slides", \
                                     variable=self.var2)
        check2.var = self.var2
        check2.grid(row=3, sticky='w')

        self.go_btn = Tkinter.Button(self.mw,
                                     text = "Go",
                                     command = self.close)
        self.go_btn.bind("<Return>", self.close)
        self.go_btn.grid(row=4)
        self.go_btn.focus_set()
        self.mw.title(title)
        self.mw.mainloop()


if __name__ == "__main__":
   #app = myWindow()
   #app = width_and_dpi_dialog()
   #app = lecture_pickle_dialog()
   app = reset_lecture_dialog()
