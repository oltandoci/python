"""
figure module

plot utilities
"""

#Standard python
import matplotlib.pyplot as plt

class Plot:
    """
    Plot class
    """

    def __init__(self, num_fig = None, show_after = None):
        self.fig = plt
        self.show_after_cnt = 0
        if (num_fig != None):
            self.fig.figure(num_fig)
        if (show_after != None):
            self.show_after = show_after
        else:
            self.show_after = None
            
    def subplot(self, num, x, y, x_unit, y_unit, title):
        """
        new subplot
        """
        self.fig.subplot(num)
        self.set_fig_param(x, y, x_unit, y_unit, title)
        
    def plot(self, num, x, y, x_unit, y_unit, title):
        """
        new plot
        """
        self.fig.figure(num)
        self.set_fig_param(x, y, x_unit, y_unit, title)
        
    def set_fig_param(self, x, y, x_unit, y_unit, title):
        """
        set plot parameters
        """
        self.fig.plot(x, y)
        self.fig.xlabel(x_unit)
        self.fig.ylabel(y_unit)
        self.fig.title(title)
        if (self.show_after != None):
            self.show_after_cnt += 1
            if (self.show_after_cnt == self.show_after):
                self.show()
        
    def show(self):
        """
        show plot
        """
        #self.fig.savefig("fig.png")
        self.fig.show() #show method is blocking since it's processed into a loop inside a python thread
