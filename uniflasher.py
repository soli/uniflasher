#!/usr/bin/env python
# Copyright admin@guimmer.co.cc, m.pluvinage@gmail.com,
# Tetsuo6995@gmail.com, Sylvain.Soliman@m4x.org
# License GPL v2.0

'''

A platform-independent automatic flasher for the OpenEtna images
for the LG Eve GW620
'''

import wx
import os
import subprocess


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
            sdkpath = 'android-sdk-windows'
        else:
            # Linux on linux boxes Darwin on MacOS
            self.osname = os.uname()[0]
            sdkpath = 'android-sdk-' \
                    + {'Darwin': 'mac', 'Linux': 'linux'}[self.osname] \
                    + '_x86'

        self.adb = os.path.join(sdkpath, 'adb')
        self.fastboot = os.path.join(sdkpath, 'fastboot')

        self.lastdir = ''

        self.bootimg = ''
        self.systemimg = ''

        wx.Frame.__init__(self, None, title='Hello ' + self.osname,
                          size=(300, 200))

        # Setting up the menu.
        filemenu = wx.Menu()
        menuabout = filemenu.Append(wx.ID_ABOUT, '&About',
                                   'Information about this program')
        menuquit = filemenu.Append(wx.ID_EXIT, '&Quit',
                                   'Terminate the program')

        # Creating the menubar.
        menubar = wx.MenuBar()
        menubar.Append(filemenu, '&File')
        self.SetMenuBar(menubar)

        # Events.
        self.Bind(wx.EVT_MENU, self.on_quit, menuquit)
        self.Bind(wx.EVT_MENU, self.on_about, menuabout)

        # Window contents
        mainsizer = wx.GridBagSizer(wx.VERTICAL)

        self.bootbtn = wx.Button(self, label='boot image')
        self.Bind(wx.EVT_BUTTON, self.on_boot, self.bootbtn)
        mainsizer.Add(self.bootbtn, pos=(0, 0))
        self.bootctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainsizer.Add(self.bootctrl, pos=(0, 1))

        self.systembtn = wx.Button(self, label='system image')
        mainsizer.Add(self.systembtn, pos=(1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_system, self.systembtn)
        self.systemctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        mainsizer.Add(self.systemctrl, pos=(1, 1))

        self.devicesbtn = wx.Button(self, label='adb devices')
        self.Bind(wx.EVT_BUTTON, self.on_devices, self.devicesbtn)
        mainsizer.Add(self.devicesbtn, pos=(2, 0))

        self.wipebtn = wx.Button(self, label='wipe')
        self.Bind(wx.EVT_BUTTON, self.on_wipe, self.wipebtn)
        mainsizer.Add(self.wipebtn, pos=(2, 1))

        self.SetSizerAndFit(mainsizer)

        self.Show()

    def on_about(self, event):
        '''About us?'''
        pass

    def on_quit(self, event):
        '''Quit nicely'''
        self.Close(True)

    def on_boot(self, event):
        '''Select boot.img'''
        self.bootimg = self._get_img_file() or self.bootimg
        self.bootctrl.SetValue(self.bootimg)

    def on_system(self, event):
        '''Select boot.img'''
        self.systemimg = self._get_img_file() or self.systemimg
        self.systemctrl.SetValue(self.systemimg)

    def _get_img_file(self):
        '''Select and return an img file'''
        filename = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.lastdir,
                            defaultFile='', wildcard='*.img', style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            self.lastdir = dlg.GetDirectory()
        dlg.Destroy()
        return filename and os.path.join(self.lastdir, filename) or ''

    def on_devices(self, event):
        '''check if some device is connected and found by adb'''
        do_and_log([self.adb, 'devices'])

    def on_wipe(self, event):
        '''wipe device'''
        do_and_log([self.fastboot, '-w'])


def do_and_log(args):
    '''print out a command, spawn a subprocess to execute it and print
    the result'''
    print ' '.join(args)
    print subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

if __name__ == '__main__':
    # Create the app, don't redirect stdout/stderr.
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
