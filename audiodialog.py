#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ZetCode wxPython tutorial

In this code example, we create a
custom dialog.

author: Jan Bodnar
website: www.zetcode.com
last modified: April 2018
'''

import wx
import audio2 as audio



class Example(wx.Frame):

    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.InitUI()


    def InitUI(self):

        tb = self.CreateToolBar()
        tb.AddTool(1, '', wx.EmptyBitmap(20,20))
        tb.Realize()

        tb.Bind(wx.EVT_TOOL, self.OnChangeDepth)

        self.SetSize((350, 250))
        self.SetTitle('Custom dialog')
        self.Centre()

    def OnChangeDepth(self, e):

        cdDialog = AudioDialog(None,
                               title='Change Color Depth')
        cdDialog.ShowModal()
        print(cdDialog.samplerate_choice.GetSelection())
        cdDialog.Destroy()


def main():

    app = wx.App()
    ex = Example(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()