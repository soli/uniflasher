#!/usr/bin/env python
# Copyright admin@guimmer.co.cc, m.pluvinage@gmail.com,
# Tetsuo6995@gmail.com, Sylvain.Soliman@m4x.org
# License GPL v2.0

'''

A platform-independent automatic flasher for the OpenEtna images
for the LG Eve GW620
'''

import wx
import os, subprocess

class MainWindow(wx.Frame):
    '''Main window of the OpenEtna flasher

    Should be able to do:
    - select boot.img
    - select system.img
    - detection if a phone is connected and detect what is running
    (normal rom, recovery, fastboot)
    - wipe button
    - flash boot.img
    - flash system.img
    - update sequence with wipe
    - update sequence without wipe
    - launch recovery
    - launch backup if recovery launched
    - launch restore if recovery launched
    '''

    def __init__(self):
        '''Perform initialization and launch main window'''

        if os.name == 'nt':
            self.osname = 'Windows'
            self.toolspath = 'android-sdk-windows'
        else:
            # Linux on linux boxes Darwin on MacOS
            self.osname = os.uname()[0]
            self.toolspath = 'android-sdk-' \
                    + {'Darwin': 'mac', 'Linux': 'linux'}[self.osname] \
                    + '_x86'

        # FIXME can be platform-tools for ADB and fastboot can be
        # anywhere so... just use the SDK name?
        # self.toolspath = os.path.join(self.toolspath, 'tools')
        self.adb = os.path.join(self.toolspath, 'adb')
        self.fastboot = os.path.join(self.toolspath, 'fastboot')

        self.dirname=''

        self.bootimg=''
        self.systemimg=''

        wx.Frame.__init__(self, None, title='Hello ' + self.osname,
                          size=(300,200))

        # Setting up the menu.
        filemenu= wx.Menu()
        menuAbout= filemenu.Append(wx.ID_ABOUT, '&About',
                                   'Information about this program')
        menuQuit = filemenu.Append(wx.ID_EXIT, '&Quit',
                                   'Terminate the program')

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, '&File')
        self.SetMenuBar(menuBar)

        # Events.
        self.Bind(wx.EVT_MENU, self.on_quit, menuQuit)
        self.Bind(wx.EVT_MENU, self.on_about, menuAbout)

        # Window contents
        mainSizer = wx.GridBagSizer(wx.VERTICAL)

        self.bootbtn = wx.Button(self, label='boot image')
        self.Bind(wx.EVT_BUTTON, self.on_boot, self.bootbtn)
        mainSizer.Add(self.bootbtn, pos=(0, 0))
        self.bootctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainSizer.Add(self.bootctrl, pos=(0, 1))

        self.systembtn = wx.Button(self, label='system image')
        mainSizer.Add(self.systembtn, pos=(1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_system, self.systembtn)
        self.systemctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainSizer.Add(self.systemctrl, pos=(1, 1))

        self.devicesbtn = wx.Button(self, label='adb devices')
        self.Bind(wx.EVT_BUTTON, self.on_devices, self.devicesbtn)
        mainSizer.Add(self.devicesbtn, pos=(2, 0))

        self.wipebtn = wx.Button(self, label='wipe')
        self.Bind(wx.EVT_BUTTON, self.on_wipe, self.wipebtn)
        mainSizer.Add(self.wipebtn, pos=(2, 1))

        self.SetSizerAndFit(mainSizer)

        self.Show()

    def on_about(self,e):
        pass

    def on_quit(self,e):
        self.Close(True)

    def on_boot(self, event):
        '''Select boot.img'''
        self.bootimg = self.get_img_file() or self.bootimg
        self.bootctrl.SetValue(self.bootimg)

    def on_system(self, event):
        '''Select boot.img'''
        self.systemimg = self.get_img_file() or self.systemimg
        self.systemctrl.SetValue(self.systemimg)

    def get_img_file(self):
        '''Select and return an img file'''
        filename = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname,
                            defaultFile='', wildcard='*.img', style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
        dlg.Destroy()
        return filename or ''

    def on_devices(self, event):
        '''check if some device is connected and found by adb'''
        do_and_log([self.adb, 'devices'])

    def on_wipe(self, event):
        '''wipe device'''
        do_and_log([self.fastboot, '-w'])

def do_and_log(args):
    print ' '.join(args)
    print subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

if __name__ == '__main__':
    '''Create the app, don't redirect stdout/stderr.'''
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
