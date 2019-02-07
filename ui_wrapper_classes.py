import tkinter as tk

import config as cfg


class Win:
    def __init__(self, window, window_title, maximize):
        self.window = window
        self.window.title(window_title)
        if maximize:
            self.window.state("zoomed")
        else:
            self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.window.destroy()


class WinText(Win):
    def __init__(self, window, window_title, widget, command, mycallback, text, width=120, state=tk.DISABLED):
        Win.__init__(self, window, window_title, False)

        self.widget = widget
        self.command = command
        self.function = mycallback
        widget.unbind(command)

        MyText(self.window, text, state, width, 30)
        self.window.mainloop()

    def quit(self):
        self.widget.bind(self.command, lambda event, c=self.command: self.function(event, c))
        Win.quit(self)


#
# Widget wrapper classes ===============================================================================================
#
class MySlider(object):
    init = False

    def __init__(self, my_parent, my_callback, name):
        self.name = name
        self.function = my_callback
        self.min = 1
        self.slider = tk.Scale(my_parent,
                               from_=self.min, to=cfg.opt_process[name + "_Max"],
                               label=cfg.opt_labels[name],
                               orient=tk.HORIZONTAL, length=300,
                               command=self.callback)

        if type(cfg.opt_process[name+ '_Max']) == float:
            self.slider.config(resolution=0.1)

        self.slider.pack()

        if cfg.opt_process[name] == self.min:
            self.init = True
        else:
            self.slider.set(cfg.opt_process[name])

    def get(self):
        return self.slider.get()

    def set(self, x):
        self.slider.set(x)

    def set_label(self, label):
        self.slider.config(label=label)

    def get_label(self):
        return self.slider.cget("label")

    def callback(self, x):
        if self.init:
            self.function(self.slider.get(), self.name)
        self.init = True

class MyText:
    def __init__(self, parent, text='', state='', width=120, height=None):
        self.scroll = tk.Scrollbar(parent)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.T = tk.Text(parent, width=width, yscrollcommand=self.scroll.set)

        self.T.delete(1.0, tk.END)
        self.T.insert(1.0, text)
        self.T.config(height = text.count('\n') - 1 if height is None else height)
        self.scroll.config(command=self.T.yview)
        self.T.pack(fill=tk.BOTH)

        if state == tk.DISABLED:
            self.T.config(state=state)

    def add(self, text):
        self.T.delete(1.0, tk.END)
        self.T.insert(1.0, text.rstrip('\n'))
        self.T.config(height=text.count('\n')+1)

    def remove_last_line(self):
        text = self.T.get(1.0, tk.END)
        value = text[text[:-1].rfind('\n')+1:-1]
        if not value == '---':
            text = text[:text[:-1].rfind('\n')]
            self.T.delete(1.0, tk.END)
            self.T.insert(1.0, text)
            self.T.config(height=self.T.cget('height') - 1)
            return value
        else:
            return None
