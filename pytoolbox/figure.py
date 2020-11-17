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
        self.fig.plot(x, y)
        self.set_fig_param(x_unit, y_unit, title)
        
    def plot(self, num, x, y, x_unit, y_unit, title):
        """
        new plot
        """
        self.fig.figure(num)
        self.fig.plot(x, y)
        self.set_fig_param(x_unit, y_unit, title)
        
    def multiplot(self, num, plotlist, x_unit, y_unit, title):
        """
        multiple plots
        """
        self.fig.figure(num)
        
        if (len(plotlist)/4 == 2):
            self.fig.plot(plotlist[0], plotlist[1], plotlist[2], plotlist[3], plotlist[4], plotlist[5])
            plt.legend((plotlist[6], plotlist[7]), loc='upper right')
        elif (len(plotlist)/4 == 3):
            self.fig.plot(plotlist[0], plotlist[1], plotlist[2], plotlist[3], plotlist[4], plotlist[5], plotlist[6], plotlist[7], plotlist[8])
            plt.legend((plotlist[9], plotlist[10], plotlist[11]), loc='upper right')
        elif (len(plotlist)/4 == 4):
            self.fig.plot(plotlist[0], plotlist[1], plotlist[2], plotlist[3], plotlist[4], plotlist[5], plotlist[6], plotlist[7], plotlist[8], plotlist[9], plotlist[10], plotlist[11])
            plt.legend((plotlist[12], plotlist[13], plotlist[14], plotlist[15]), loc='upper right')
        else:
            print("Must plot only 2, 3 or 4 curves at maximum!")
        
        self.set_fig_param(x_unit, y_unit, title)
        
    def set_fig_param(self, x_unit, y_unit, title):
        """
        set plot parameters
        """
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
