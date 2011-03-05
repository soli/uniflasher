#!/usr/bin/env VERSIONER_PYTHON_PREFER_32_BIT=yes python
# Copyright blah blah
# License blah blah (GPL v2 ?)

'''

A platform-independent automatic flasher for the OpenEtna images
for the LG Eve GW620
'''

import wx
import os

class MainWindow(wx.Frame):
    def __init__(self):
        '''Perform initialization and launch main window'''

        if os.name == 'nt':
            self.osname = 'Windows'
        else:
            # Linux on linux boxes Darwin on MacOS
            self.osname = os.uname()[0]

        self.dirname=''
        wx.Frame.__init__(self, None, title='Hello ' + self.osname,
                          size=(300,200))

        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        self.Show()

    def OnAbout(self,e):
        pass

    def OnExit(self,e):
        self.Close(True)

    def OnOpen(self, event):
        ''' Open a file'''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname,
                            defaultFile='', wildcard='*.*', style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.control.SetValue(self.filename)
        dlg.Destroy()

if __name__ == '__main__':
    # Create a new app, don't redirect stdout/stderr to a window.
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
