#!/usr/bin/env python

import Tkinter
import tkMessageBox

class myWindow:
    def close(self, *args, **kwargs):
        #print('got close event')
        self.mw.destroy()
        
        
    def __init__(self, msg="Message", title="Message"):
        self.msg = msg
        self.title = title
        self.mw = Tkinter.Tk()
        self.mw.option_add("*font", ("Arial", 15, "normal"))
        self.mw.geometry("+100+100")
        ## self.var = Tkinter.StringVar()
        ## entry = Tkinter.Entry(self.mw, textvariable=self.var)
        ## entry.focus_set()
        ## entry.pack()
        ## #entry.bind("<KP_Enter>", self.close)
        ## entry.bind("<Return>", self.close)
        self.mw.title(title)
        self.label = Tkinter.Label(self.mw, text=msg, justify='left')
        self.label.pack()
        ## self.btn2 = Tkinter.Button(self.mw,
        ##                            text = "Exit",
        ##                            command = self.mw.destroy)
        ## self.btn2.pack()

        self.mw.mainloop()


##     def btnClick(self):

##         self.answer = tkMessageBox.askyesno(title = "Your Choice", message = 'Please click either "Yes" or "No".')

##         if self.answer:
##             tkMessageBox.showinfo(title = "Yes", message = "Your choice was: Yes.")
##         else:
##             tkMessageBox.showinfo(title = "No", message = "Your choice was: No.")

if __name__ == "__main__":
   app = myWindow("Please anchor floating selection.")
