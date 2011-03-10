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
import sys
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
        self._logo = wx.StaticBitmap(self, id=wx.ID_ANY, bitmap=image)
        mainsizer.Add(self._logo, flag=wx.ALIGN_CENTER)

        bottomsizer = wx.GridBagSizer(vgap=10, hgap=10)

        self.bootbtn = wx.Button(self, label='boot image')
        self.Bind(wx.EVT_BUTTON, self.on_boot, self.bootbtn)
        bottomsizer.Add(self.bootbtn, pos=(0, 0))
        self.bootctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        bottomsizer.Add(self.bootctrl, pos=(0, 1))
        self.flashbootbtn = wx.Button(self, label='flash boot')
        self.Bind(wx.EVT_BUTTON, self.on_flashboot, self.flashbootbtn)
        bottomsizer.Add(self.flashbootbtn, pos=(0, 2))
        self.update_w_wipebtn = wx.Button(self,
                                          label='Complete update with wipe')
        self.Bind(wx.EVT_BUTTON, self.on_update_w_wipe, self.update_w_wipebtn)
        bottomsizer.Add(self.update_w_wipebtn, pos=(0, 3))

        self.systembtn = wx.Button(self, label='system image')
        bottomsizer.Add(self.systembtn, pos=(1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_system, self.systembtn)
        self.systemctrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        bottomsizer.Add(self.systemctrl, pos=(1, 1))
        self.flashsystembtn = wx.Button(self, label='flash system')
        self.Bind(wx.EVT_BUTTON, self.on_flashsystem, self.flashsystembtn)
        bottomsizer.Add(self.flashsystembtn, pos=(1, 2))
        self.update_wo_wipebtn = wx.Button(self,
                                           label='Complete update without wipe')
        self.Bind(wx.EVT_BUTTON, self.on_update_wo_wipe, self.update_wo_wipebtn)
        bottomsizer.Add(self.update_wo_wipebtn, pos=(1, 3))

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

        mainsizer.Add(bottomsizer, flag=wx.ALIGN_CENTER)

        self.SetSizerAndFit(mainsizer)

        self.Show()

    def on_about(self, event):
        '''About us?'''
        self._ok_dialog('A cross-platform, python-based, flasher'
                        + ' for the OpenEtna ROMs on the LG Eve'
                        + ' (GW 620)',
                        'About OpenEtna uniFlasher')

    def _ok_dialog(self, message, title, style=wx.OK):
        dlg = wx.MessageDialog(self, message, title, wx.OK | style)
        dlg.ShowModal()
        dlg.Destroy()

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
        self.bootimg = self._get_img_file(self.bootimg) or self.bootimg
        self.bootctrl.SetValue(self.bootimg)

    def on_system(self, event):
        '''Select system.img'''
        self.systemimg = self._get_img_file(self.systemimg) or self.systemimg
        self.systemctrl.SetValue(self.systemimg)

    def _get_img_file(self, default):
        '''Select and return an img file'''
        filename = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.lastdir,
                            defaultFile=default, wildcard='*.img',
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            self.lastdir = dlg.GetDirectory()
        dlg.Destroy()
        return filename and os.path.join(self.lastdir, filename) or ''

    def on_devices(self, event):
        '''check if some device is connected and found by adb'''
        self._devices()

    def _devices(self):
        '''check if some device is connected and found by adb'''
        # If adb doesn't find the device on a mac ->
        # http://www.zacpod.com/p/157
        # /System/Library/Extensions/IOUSBFamily.kext/Contents/PlugIns/IOUSBCompositeDriver.kext/Contents/
        result = do_and_log([self.adb, 'devices'])
        if result.find('recovery') >= 0:
            print >> sys.stderr, "The device is in recovery mode"
            found = True
        else:
            print >> sys.stderr, "No device in recovery mode"
            found = False
        self.ckbx_adb_ready.SetValue(found)
        return found

    def on_fbdevices(self, event):
        '''check if some device is connected and found by fastboot'''
        self._fbdevices()

    def _fbdevices(self):
        '''check if some device is connected and found by fastboot'''
        result = do_and_log([self.fastboot, 'devices'])
        if result.find('?\tfastboot\r\n') >= 0:
            print >> sys.stderr, "The device is in fastboot mode"
            found = True
        else:
            print >> sys.stderr, "No device in fastboot"
            found = False
        self.ckbx_fastb_ready.SetValue(found)
        return found

    def on_wipe(self, event):
        '''wipe device'''
        self._wipe()

    def _wipe(self):
        '''wipe device'''
        if self._fbdevices():
            return print_and_log([self.fastboot, '-w'])
        else:
            self._ok_dialog('You must put your phone in fastboot mode' +
                            'first', 'No device in fastboot',
                            wx.ICON_EXCLAMATION)
            return False

    def on_reboot(self, event):
        '''reboot adb device'''
        self._reboot()

    def _reboot(self):
        '''reboot device'''
        # TODO check if it works...
        return print_and_log([self.adb, 'reboot'])

    def on_flashboot(self, event):
        '''flash boot'''
        self._flash('boot', self.bootimg)
        if not self.bootimg:
            self.on_boot(event)
            self.bootimg and self._flash('boot', self.bootimg)

    def on_flashsystem(self, event):
        '''flash system'''
        self._flash('system', self.systemimg)
        if not self.systemimg:
            self.on_system(event)
            self.systemimg and self._flash('system', self.systemimg)

    def _flash(self, partition, imgfile):
        '''flash some image to the given partition on device'''
        if not imgfile:
            self._ok_dialog('You need to select a ' + partition +
                            ' image first',
                            'Missing '+ partition +'.img',
                            wx.ICON_EXCLAMATION)
            return False
        if self._fbdevices():
            return print_and_log([self.fastboot, 'flash', partition, imgfile],
                                 timeout=120)
        else:
            self._ok_dialog('You must put your phone in fastboot mode' +
                            'first', 'No device in fastboot',
                            wx.ICON_EXCLAMATION)
            return False

    def on_recovery(self, event):
        '''Launch recovery on device'''
        self._recovery()

    def _recovery(self):
        '''fastboot boot everarecovery.img'''
        if self._fbdevices():
            ok = print_and_log([self.fastboot, 'boot',
                                os.path.join('imgs', 'everarecovery.img')],
                               timeout=60)
            time.sleep(3)
            return ok
        else:
            self._ok_dialog('You must put your phone in fastboot mode' +
                            'first', 'No device in fastboot',
                            wx.ICON_EXCLAMATION)
            return False

    def on_update_w_wipe(self, event):
        '''Update boot and system with wipe'''
        self._flash_openetna()

    def _flash_openetna(self):
        '''very basic OpenEtna flash, adapted from OpenEtnaflash.bat'''
        return self._wipe() and \
                self._flash_openetna_wo_wipe()

    def on_update_wo_wipe(self, event):
        '''Update boot and system with wipe'''
        self._flash_openetna_wo_wipe()

    def _flash_openetna_wo_wipe(self):
        '''very basic OpenEtna flash without wipe'''
        return self._flash('boot', self.bootimg) and \
                self._flash('system', self.systemimg)

    def _wait_for_device(self):
        '''ask adb to wait for the device to be ready

        will not work for recovery, only "normal" device'''
        return print_and_log([self.adb, 'wait-for-device'])

    def on_backup(self, event):
        '''start backup on SDCard'''
        self._simple_backup()

    def _nandroid_backup(self):
        '''launch nandroid backup on device (#duration : about 160s)

        adb shell nandroid-mobile.sh -b --norecovery --nomisc --nosplash1
            --nosplash2 --defaultinput'''
        return print_and_log([self.adb, 'shell', 'nandroid-mobile.sh', '-b',
                              '--norecovery', '--nomisc', '--nosplash1',
                              '--nosplash2', '--defaultinput'], timeout=170)

    def on_restore(self, event):
        '''start restore from SDCard'''
        self._nandroid_restore()

    def _nandroid_restore(self):
        '''launch nandroid on device

        adb shell nandroid-mobile.sh -r --defaultinput'''
        return self._recovery() and \
                print_and_log([self.adb, 'shell', 'nandroid-mobile.sh',
                               '-r', '--defaultinput'], timeout=240)

    def _simple_backup(self):
        '''very basic backup, adapted from simplebackup.bat'''
        return self._recovery() and \
                self._nandroid_backup() and \
                self._reboot()

    def _gapps(self):
        '''push gapps to device'''
        if not self.gapps:
            print >> sys.stderr, "You need to select a zipped gapps file first"
            return
        return print_and_log([self.adb, 'remount']) and \
                print_and_log([self.abd, 'push', self.gapps,
                               '/sdcard/']) and \
                self._reboot()

    def _kill_server(self):
        return print_and_log([self.adb, 'kill-server'])

    def on_logcat(self, event):
        '''launch device logcat'''
        self._logcat()

    def _logcat(self):
        '''device logcat'''
        log = ''
        default=time.strftime('logcat_%Y%m%d%H%M%S.txt', time.localtime())
        dlg = wx.FileDialog(self, 'Choose a file to save the log output',
                            self.lastdir,
                            defaultFile=default,
                            wildcard='*.txt',
                            style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.lastdir = dlg.GetDirectory()
            logfile = os.path.join(self.lastdir, dlg.GetFilename())
            log = do_and_log([self.adb, 'logcat'], timeout=100)
            print >> sys.stderr, log
            try:
                logout = open(logfile, 'w')
                print >> logout, log
            finally:
                logout.close()
        dlg.Destroy()
        return log


def do_and_log(args, timeout=10, poll=0.1):
    '''print out a command, spawn a subprocess to execute it

    kill the subprocess after a given timeout (active poll)'''
    print >> sys.stderr, ' '.join(args)
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
            print >> sys.stderr, 'Error #', pipe.returncode
            return ''
        else:
            return output
    except OSError, error:
        # adb or fastboot not found
        print >> sys.stderr, 'Error :', error.strerror
        return ''

def print_and_log(*args, **kwargs):
    '''call do_and_log and print the returned process output'''
    output =  do_and_log(*args, **kwargs)
    if output:
        print >> sys.stderr, output
        return True
    else:
        return False

if __name__ == '__main__':
    # Create the app, don't redirect stdout/stderr.
    app = wx.App(False)
    frame = MainWindow()
    app.MainLoop()
