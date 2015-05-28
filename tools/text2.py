
'''
http://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
'''

import tkinter as tk
from util import MyUI

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, height=1, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, height=1, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) || 
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

class Text2(tk.Frame, MyUI):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.text = CustomText(self)
        self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.text)

        self.linenumbers.grid(column=0, row=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.add_widget_with_scrolls(self, self.text, True, True, column=1, row=0)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)
        self.text.bind("<Key-Tab>", self._on_tab)

        #self.text.insert("end", "one\ntwo\nthree\n")
        #self.text.insert("end", "four\n",("bigfont",))
        #self.text.insert("end", "five\n")

    def _on_tab(self, event, *args):
        try:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
        self.text.insert(tk.INSERT, " " * 4)
        return "break"

    def _on_change(self, event):
        self.linenumbers.redraw()
        if hasattr(self, 'text_change_cb'):
            self.text_change_cb()

if __name__ == "__main__":
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.grid(column=0, row=0, sticky=tk.NSEW)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    Text2(frame).grid(column=0, row=0, sticky=tk.NSEW)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    root.mainloop()

