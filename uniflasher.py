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
import time
import webbrowser

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

        if __file__:
            curpath = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
        else:
            curpath = os.getcwd()

        sdkpath = os.path.join(curpath, sdkpath)
        imgpath = os.path.join(curpath, 'imgs')

        self.adb = os.path.join(sdkpath, 'adb')
        self.fastboot = os.path.join(sdkpath, 'fastboot')

        self.lastdir = ''

        self.bootimg = ''
        self.systemimg = ''
        self.gapps = ''

        wx.Frame.__init__(self, None, title='Hello ' + self.osname,
                          size=(500, 300))

        # Setting up the menu.
        filemenu = wx.Menu()
        menuquit = filemenu.Append(wx.ID_EXIT, '&Quit',
                                   'Terminate the program')
        helpmenu = wx.Menu()
        menuabout = helpmenu.Append(wx.ID_ABOUT, '&About',
                                   'Information about this program')
        if os.name != 'Darwin':
            helpmenu.AppendSeparator()

        menuoe = helpmenu.Append(wx.ID_ANY, '&OpenEtna website',
                                 'Open the OpenEtna website in a browser')
        menuforum = helpmenu.Append(wx.ID_ANY, '&Search forum',
                                    'Search the OpenEtna users\' forum')

        # Creating the menubar.
        menubar = wx.MenuBar()
        menubar.Append(filemenu, '&File')
        menubar.Append(helpmenu, '&Help')
        self.SetMenuBar(menubar)

        # Events.
        self.Bind(wx.EVT_MENU, self.on_quit, menuquit)
        self.Bind(wx.EVT_MENU, self.on_about, menuabout)
        self.Bind(wx.EVT_MENU, self.on_oe, menuoe)
        self.Bind(wx.EVT_MENU, self.on_forum, menuforum)

        # Window contents
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        image = wx.Bitmap(os.path.join(imgpath, 'openetna_logo.png'))
        self._logo = wx.StaticBitmap(self,
                                     id=wx.ID_ANY,
                                     bitmap=image)
        mainsizer.Add(self._logo)

        bottomsizer = wx.GridBagSizer(wx.VERTICAL)

        self.bootbtn = wx.Button(self, label='boot image')
        self.Bind(wx.EVT_BUTTON, self.on_boot, self.bootbtn)
        bottomsizer.Add(self.bootbtn, pos=(0, 0))
        self.bootctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        bottomsizer.Add(self.bootctrl, pos=(0, 1))
        self.flashbootbtn = wx.Button(self, label='flash boot')
        self.Bind(wx.EVT_BUTTON, self.on_flashboot, self.flashbootbtn)
        bottomsizer.Add(self.flashbootbtn, pos=(0, 2))

        self.systembtn = wx.Button(self, label='system image')
        bottomsizer.Add(self.systembtn, pos=(1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_system, self.systembtn)
        self.systemctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        bottomsizer.Add(self.systemctrl, pos=(1, 1))
        self.flashsystembtn = wx.Button(self, label='flash system')
        self.Bind(wx.EVT_BUTTON, self.on_flashsystem, self.flashsystembtn)
        bottomsizer.Add(self.flashsystembtn, pos=(1, 2))

        self.devicesbtn = wx.Button(self, label='adb devices')
        self.Bind(wx.EVT_BUTTON, self.on_devices, self.devicesbtn)
        bottomsizer.Add(self.devicesbtn, pos=(3, 0))
        self.ckbx_adb_ready = wx.CheckBox(self, label='recovery adb ready')
        bottomsizer.Add(self.ckbx_adb_ready, pos=(3, 1))

        self.wipebtn = wx.Button(self, label='wipe')
        self.Bind(wx.EVT_BUTTON, self.on_wipe, self.wipebtn)
        bottomsizer.Add(self.wipebtn, pos=(2, 0))

        self.fbdevicesbtn = wx.Button(self, label='fastboot devices')
        self.Bind(wx.EVT_BUTTON, self.on_fbdevices, self.fbdevicesbtn)
        bottomsizer.Add(self.fbdevicesbtn, pos=(4, 0))
        self.ckbx_fastb_ready = wx.CheckBox(self, label='fastboot ready')
        bottomsizer.Add(self.ckbx_fastb_ready, pos=(4, 1))

        self.rebootbtn = wx.Button(self, label='reboot adb device')
        self.Bind(wx.EVT_BUTTON, self.on_reboot, self.rebootbtn)
        bottomsizer.Add(self.rebootbtn, pos=(5, 0))

        self.recoverybtn = wx.Button(self, label='Launch Recovery')
        self.Bind(wx.EVT_BUTTON, self.on_recovery, self.recoverybtn)
        bottomsizer.Add(self.recoverybtn, pos=(6, 0))

        self.backupbtn = wx.Button(self, label='Backup Phone')
        self.Bind(wx.EVT_BUTTON, self.on_backup, self.backupbtn)
        bottomsizer.Add(self.backupbtn, pos=(7, 0))

        self.retorebtn = wx.Button(self, label='Restore last backup')
        self.Bind(wx.EVT_BUTTON, self.on_restore, self.retorebtn)
        bottomsizer.Add(self.retorebtn, pos=(7, 1))

        self.logcatbtn = wx.Button(self, label='ADB Logcat')
        self.Bind(wx.EVT_BUTTON, self.on_logcat, self.logcatbtn)
        bottomsizer.Add(self.logcatbtn, pos=(8, 0))

        mainsizer.Add(bottomsizer)

        self.SetSizerAndFit(mainsizer)

        self.Show()

    def on_about(self, event):
        '''About us?'''
        dlg = wx.MessageDialog(self,
                               'A cross-platform, python-based, flasher'
                               + ' for the OpenEtna ROMs on the LG Eve'
                               + ' (GW 620)',
                               'About OpenEtna uniFlasher', wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def on_quit(self, event):
        '''Quit nicely'''
        self._kill_server()
        self.Close(True)

    def on_oe(self, event):
        '''Open the OpenEtna web site in a browser'''
        webbrowser.open('http://openetna.com/openetna/')

    def on_forum(self, event):
        '''Open the OpenEtna users\'s forum in a browser'''
        webbrowser.open('http://forum.openetna.com/index.php?action=search')

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
        result = do_and_log([self.adb, 'devices'])
        if result.find('recovery') >= 0:
            print "The device is in recovery mode"
            self.ckbx_adb_ready.SetValue(True)
        else:
            print "No device in recovery mode"
            self.ckbx_fastb_ready.SetValue(False)

    def on_fbdevices(self, event):
        '''check if some device is connected and found by fastboot'''
        result = do_and_log([self.fastboot, 'devices'])
        if result.find('?\tfastboot\r\n') >= 0:
            print "The device is in fastboot mode"
            self.ckbx_fastb_ready.SetValue(True)
        else:
            print "No device in fastboot"
            self.ckbx_fastb_ready.SetValue(False)

    def on_wipe(self, event):
        '''wipe device'''
        self._wipe()

    def _wipe(self):
        '''wipe device'''
        print_and_log([self.fastboot, '-w'])

    def on_reboot(self, event):
        '''reboot adb device'''
        self._reboot()

    def _reboot(self):
        '''reboot device'''
        print_and_log([self.adb, 'reboot'])

    def on_flashboot(self, event):
        '''flash boot'''
        self._flash('boot',self.bootimg)

    def on_flashsystem(self, event):
        '''flash system'''
        self._flash('system',self.systemimg)

    def _flash(self, partition, imgfile):
        '''flash some image to the given partition on device'''
        print_and_log([self.fastboot, 'flash', partition, imgfile],
                      timeout=120)

    def on_recovery(self, event):
        '''Launch recovery on device'''
        self._recovery()

    def _recovery(self):
        '''fastboot boot everarecovery.img'''
        print_and_log([self.fastboot, 'boot',
                    os.path.join('imgs', 'everarecovery.img')], timeout=60)

    def _flash_openetna(self):
        '''very basic OpenEtna flash, adapted from OpenEtnaflash.bat'''
        if not self.bootimg:
            print "You need to select a boot image first"
            return
        if not self.systemimg:
            print "You need to select a system image first"
            return
        self._wipe()
        self._flash('boot', self.bootimg)
        self._flash('system', self.systemimg)

    def _wait_for_device(self):
        '''ask adb to wait for the device to be ready'''
        print_and_log([self.adb, 'wait-for-device'])

    def on_backup(self, event):
        '''start backup on SDCard'''
        self._nandroid_backup()

    def _nandroid_backup(self):
        '''launch nandroid backup on device (#duration : about 160s)

        adb shell nandroid-mobile.sh -b --norecovery --nomisc --nosplash1
            --nosplash2 --defaultinput'''
        print_and_log([self.adb, 'shell', 'nandroid-mobile.sh', '-b',
                       '--norecovery', '--nomisc', '--nosplash1',
                       '--nosplash2', '--defaultinput'], timeout=170)

    def on_restore(self, event):
        '''start restore from SDCard'''
        self._nandroid_restore()

    def _nandroid_restore(self):
        '''launch nandroid on device

        adb shell sbin/nandroid-mobile.sh -r --defaultinput'''
        print_and_log([self.adb, 'shell', 'nandroid-mobile.sh', '-r',
                       '--defaultinput'], timeout=240)

    def _simple_backup(self):
        '''very basic backup, adapted from simplebackup.bat'''
        self._recovery()
        self._wait_for_device()
        self._nandroid_backup()
        self._reboot()

    def _gapps(self):
        '''push gapps to device'''
        if not self.gapps:
            print "You need to select a zipped gapps file first"
            return
        print_and_log([self.adb, 'remount'])
        print_and_log([self.abd, 'push', self.gapps, '/sdcard/'])
        self._reboot()

    def _kill_server(self):
        print_and_log([self.adb, 'kill-server'])

    def on_logcat(self, event):
        '''launch device logcat'''
        self._logcat()

    def _logcat(self):
        '''device logcat'''
        print_and_log([self.adb, 'logcat'], timeout=100)


def do_and_log(args, timeout=10, poll=0.1):
    '''print out a command, spawn a subprocess to execute it

    kill the subprocess after a given timeout (active poll)'''
    print ' '.join(args)
    elapsed = 0.0
    try:
        pipe = subprocess.Popen(args, stdout=subprocess.PIPE)
        while pipe.poll() is None:
            time.sleep(poll)
            elapsed += poll
            if elapsed > timeout:
                pipe.terminate()
        output =  pipe.communicate()[0]
        if pipe.returncode != 0:
            print pipe.returncode
            return ''
        else:
            return output
    except OSError, error:
        # adb or fastboot not found
        print error.strerror
        return ''

def print_and_log(*args, **kwargs):
    '''call do_and_log and print the returned process output'''
    print do_and_log(*args, **kwargs)

if __name__ == '__main__':
    # Create the app, don't redirect stdout/stderr.
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
