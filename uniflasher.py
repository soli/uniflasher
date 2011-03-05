#!/usr/bin/env python
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
        self.bootimg=''
        self.systemimg=''

        wx.Frame.__init__(self, None, title='Hello ' + self.osname,
                          size=(300,200))

        # Setting up the menu.
        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, '&About',
                                   'Information about this program')
        menuExit = filemenu.Append(wx.ID_EXIT, 'E&xit',
                                   'Terminate the program')

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, '&File')
        self.SetMenuBar(menuBar)

        # Events.
        self.Bind(wx.EVT_MENU, self.on_exit, menuExit)
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)

        # Window contents
        mainSizer = wx.GridBagSizer(wx.VERTICAL)

        self.bootbtn = wx.Button(self, label="boot image")
        self.Bind(wx.EVT_BUTTON, self.on_click_boot, self.bootbtn)
        mainSizer.Add(self.bootbtn, pos=(0, 0))
        self.bootctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainSizer.Add(self.bootctrl, pos=(0, 1))

        self.systembtn = wx.Button(self, label="system image")
        mainSizer.Add(self.systembtn, pos=(1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_click_bsgystem, self.systembtn)
        self.systemctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainSizer.Add(self.systemctrl, pos=(1, 1))

        self.SetSizerAndFit(mainSizer)

        self.Show()

    def on_about(self,e):
        pass

    def on_exit(self,e):
        self.Close(True)

    def on_click_boot(self, event):
        '''Select boot.img'''
        self.bootimg = self.get_img_file() or self.bootimg
        self.bootctrl.SetValue(self.bootimg)

    def on_click_bsgystem(self, event):
        '''Select boot.img'''
        self.systemimg = self.get_img_file() or self.systemimg
        self.systemctrl.SetValue(self.systemimg)

    def get_img_file(self):
        '''Select and return an img file'''
        filename = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname,
                            defaultFile='', wildcard='*.*', style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
        dlg.Destroy()
        return filename or ''

if __name__ == '__main__':
    # Create a new app, don't redirect stdout/stderr to a window.
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
