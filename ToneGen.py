import time
import wx
from wx.lib import plot as wxplot
import numpy as np
import tones
import pyximport; pyximport.install()
import cshepard as shepard

import billiard as mp
mp.forking_enable(False)
import queue

import audio as audio



class AudioDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(AudioDialog, self).__init__(*args, **kw)

        #self.SetSize((300, 130))
        self.SetPosition((300,300))

        # Comboboxes
        self.device_choice = wx.Choice(self, choices=audio.device_names)
        self.device_choice.SetSelection(audio.device_indices.index(audio.default_device))

        self.samplerate_names = ['192000 Hz', '96000 Hz', '48000 Hz', '44100 Hz', '32000 Hz']
        self.samplerate_values = [192000, 96000, 48000, 44100, 32000]
        self.samplerate_choice = wx.Choice(self, choices=self.samplerate_names)
        self.samplerate_choice.SetSelection(self.samplerate_values.index(192000))

        self.closeButton = wx.Button(self, label='Done')

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.device_choice, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        self.sizer.Add(self.samplerate_choice, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        self.sizer.Add(self.closeButton, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, border=2)

        self.SetSizer(self.sizer)
        #self.device_choice.Bind(wx.EVT_CHOICE, self.OnChangeAudio)
        #self.samplerate_choice.Bind(wx.EVT_CHOICE, self.OnChangeAudio)
        self.closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        self.sizer.Fit(self)
        self.SetWindowStyleFlag(wx.STAY_ON_TOP|wx.SYSTEM_MENU)

    def get_sample_rate(self):
        return self.samplerate_values[self.samplerate_choice.GetSelection()]

    def get_device_index(self):
        print(audio.device_indices)
        return audio.device_indices[self.device_choice.GetSelection()]

    def OnClose(self, e):

        self.Close()




class Knob:
    """
    Knob - simple class with a "setKnob" method.
    A Knob instance is attached to a Param instance, e.g. param.attach(knob)
    Base class is for documentation purposes.
    """

    def setKnob(self, value):
        pass


class Param:
    """
    The idea of the "Param" class is that some parameter in the GUI may have
    several knobs that both control it and reflect the parameter's state, e.g.
    a slider, text, and dragging can all change the value of the frequency in
    the waveform of this example.
    The class allows a cleaner way to update/"feedback" to the other knobs when
    one is being changed.  Also, this class handles min/max constraints for all
    the knobs.
    Idea - knob list - in "set" method, knob object is passed as well
      - the other knobs in the knob list have a "set" method which gets
        called for the others.
    """

    def __init__(self, initialValue=None, minimum=0., maximum=1.):
        self.minimum = minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []

    def attach(self, knob):
        self.knobs += [knob]

    def set(self, value, knob=None):
        self.value = value
        self.value = self.constrain(value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value


class SliderGroupInt(Knob):
    def __init__(self, parent, label, param):
        self.sliderLabel = wx.StaticText(parent, label=label)
        self.sliderText = wx.TextCtrl(parent, -1, style=wx.TE_PROCESS_ENTER)
        self.slider = wx.Slider(parent, -1)
        self.slider.SetMax(param.maximum)
        self.setKnob(param.value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sliderLabel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.sliderText, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.slider, 1, wx.EXPAND)
        self.sizer = sizer

        self.slider.Bind(wx.EVT_SLIDER, self.sliderHandler)
        self.sliderText.Bind(wx.EVT_TEXT_ENTER, self.sliderTextHandler)

        self.param = param
        self.param.attach(self)

    def sliderHandler(self, evt):
        value = evt.GetInt()
        self.param.set(value)

    def sliderTextHandler(self, evt):
        value = float(self.sliderText.GetValue())
        self.param.set(value)

    def setKnob(self, value):
        self.sliderText.SetValue('%g' % value)
        self.slider.SetValue(value)


class SliderGroupFloat(Knob):
    def __init__(self, parent, label, param):
        self.sliderLabel = wx.StaticText(parent, label=label)
        self.sliderText = wx.TextCtrl(parent, -1, style=wx.TE_PROCESS_ENTER)
        self.slider = wx.Slider(parent, -1)
        self.slider.SetMin(param.minimum * 10)
        self.slider.SetMax(param.maximum*10)
        self.setKnob(param.value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sliderLabel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.sliderText, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.slider, 1, wx.EXPAND)
        self.sizer = sizer

        self.slider.Bind(wx.EVT_SLIDER, self.sliderHandler)
        self.sliderText.Bind(wx.EVT_TEXT_ENTER, self.sliderTextHandler)

        self.param = param
        self.param.attach(self)

    def sliderHandler(self, evt):
        value = evt.GetInt()/10
        self.param.set(value)

    def sliderTextHandler(self, evt):
        value = float(self.sliderText.GetValue())
        self.param.set(value)

    def setKnob(self, value):
        self.sliderText.SetValue('%g' % value)
        self.slider.SetValue(value*10)


class RootNoteSliderGroup(Knob):
    def __init__(self, parent, param):
        self.sliderLabel = wx.StaticText(parent, label="Root note:")
        self.sliderText = wx.TextCtrl(parent, -1, style=wx.TE_READONLY)
        self.slider = wx.Slider(parent, -1)
        self.slider.SetMax(param.maximum)
        self.setKnob(param.value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sliderLabel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.sliderText, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.slider, 1, wx.EXPAND)
        self.sizer = sizer

        self.slider.Bind(wx.EVT_SLIDER, self.sliderHandler)

        self.param = param
        self.param.attach(self)

    def sliderHandler(self, evt):
        value = evt.GetInt()
        self.param.set(value)

    def setKnob(self, value):
        self.sliderText.SetValue(tones.names[value])
        self.slider.SetValue(value)


class CutoffGroup(Knob):
    def __init__(self, parent, label, param):
        self.Label = wx.StaticText(parent, label=label)
        self.Text = wx.TextCtrl(parent, -1, style=wx.TE_PROCESS_ENTER)
        self.setKnob(param.value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.Label, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.Text, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        self.sizer = sizer

        self.Text.Bind(wx.EVT_TEXT_ENTER, self.TextHandler)

        self.param = param
        self.param.attach(self)

    def TextHandler(self, evt):
        value = float(self.Text.GetValue())
        self.param.set(value)

    def setKnob(self, value):
        self.Text.SetValue('%g' % value)



class FourierDemoFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        dialog = AudioDialog(None, title='Choose Sound Options')
        dialog.ShowModal()
        self.sample_rate = dialog.get_sample_rate()
        self.device_index = dialog.get_device_index()
        dialog.Destroy()


        self.SetPosition((300,300))

        self.plotpanel = PlotPanel(self)


        self.audio = audio.Audio(param_queue=self.plotpanel.param_queue, device_index=self.device_index, sample_rate=self.sample_rate)

        self.rootnoteSliderGroup = RootNoteSliderGroup(self, param=self.plotpanel.rootnoteindex)
        self.octaveSliderGroup = SliderGroupInt(self, label='Octave index:', \
                                                param=self.plotpanel.octaveindex)
        self.nSliderGroup = SliderGroupInt(self, label='Number of Octaves:', \
                                           param=self.plotpanel.n)
        self.envelopeshiftSliderGroup = SliderGroupFloat(self, label='Envelope shift:', \
                                                         param=self.plotpanel.dx0)
        self.envelopewidthSliderGroup = SliderGroupFloat(self, label='Envelope width:', \
                                                         param=self.plotpanel.width)
        self.volumeSliderGroup = SliderGroupFloat(self, label='Volume:', \
                                                         param=self.plotpanel.volume)

        # cutoffs
        self.lowcutoff = CutoffGroup(self, label='Low Frequency Cutoff:', \
                                                         param=self.plotpanel.lowcutoff)
        self.highcutoff = CutoffGroup(self, label='Low Frequency Cutoff:', \
                                                         param=self.plotpanel.highcutoff)
        self.cutoffsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cutoffsizer.Add(self.lowcutoff.sizer, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, border=2)
        self.cutoffsizer.Add(self.highcutoff.sizer, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, border=2)


        # Play Button
        self.playbutton =wx.ToggleButton(self, label="Play", size=(100, 30))

        self.bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomsizer.Add(self.playbutton, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, border=2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.plotpanel, 1, wx.EXPAND)
        sizer.Add(self.rootnoteSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.octaveSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.nSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.envelopeshiftSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.envelopewidthSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.volumeSliderGroup.sizer, 0, \
                  wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.cutoffsizer, 0, \
                  wx.SHAPED | wx.ALIGN_RIGHT | wx.ALL, border=5)
        sizer.Add(self.bottomsizer, 0, \
                  wx.SHAPED | wx.ALIGN_RIGHT | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle,self.playbutton)


    def OnToggle(self,event):
       state = event.GetEventObject().GetValue()
       if state == True:
          self.audio.on()
          self.nSliderGroup.slider.Enable(False)
          self.nSliderGroup.sliderText.Enable(False)
       else:
          self.audio.off()
          self.nSliderGroup.slider.Enable(True)
          self.nSliderGroup.sliderText.Enable(True)




class PlotPanel(wx.Panel, Knob):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.param_queue = mp.Queue()

        self.shepard = shepard.ShepardTone(tones.freqs[0]*2**5, 1, 100, 0, 0.5,20.0,100000.0)
        # starting_freq, n, envelope_width, envelope_x0, volume, low_cutoff, high_cutoff

        self.rootnoteindex = Param(0, minimum=0, maximum=len(tones.names)-1)
        self.octaveindex = Param(5, minimum=1, maximum=12)
        self.dx0 = Param(0.0, minimum=-10.0, maximum=10.)
        self.width = Param(5.0, minimum=1.0, maximum=20.)
        self.n = Param(1, minimum=1, maximum=32)
        self.volume = Param(0.5, minimum=0.0, maximum=1.)
        self.lowcutoff = Param(20.0, minimum=0.0, maximum=200.0)
        self.highcutoff = Param(100000, minimum=10000, maximum=200000)

        self.SetBackgroundColour("gray")

        # Not sure I like having two params attached to the same Knob,
        # but that is what we have here... it works but feels kludgy -
        # although maybe it's not too bad since the knob changes both params
        # at the same time (both f0 and A are affected during a drag)
        self.rootnoteindex.attach(self)
        self.octaveindex.attach(self)
        self.dx0.attach(self)
        self.width.attach(self)
        self.n.attach(self)
        self.volume.attach(self)
        self.lowcutoff.attach(self)
        self.highcutoff.attach(self)

        self.canvas1 = wxplot.PlotCanvas(self)
        self.canvas1.enableAntiAliasing = True
        #self.canvas1.enableHiRes = True
        self.canvas1.logScale = (True, False)


        self.canvas2 = wxplot.PlotCanvas(self)
        self.canvas2.enableAntiAliasing = True
        #self.canvas2.enableHiRes = True

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas1, 1, wx.EXPAND)
        sizer.Add(self.canvas2, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.draw()

    def draw(self):
        x1, y1, x2, y2 = self.compute(tones.freqs[self.rootnoteindex.value]*(2**int(self.octaveindex.value)), int(self.n.value),
                                      self.width.value, self.dx0.value, self.volume.value,self.lowcutoff.value,self.highcutoff.value)
        self.canvas1.Draw(self.getGraphics_freqs(x1,y1),yAxis=(0,1))
        #if len(x2) > 1:
        #    self.canvas1.Zoom((x1.mean(), 0.0), (1.2, 1.0))
        self.canvas2.Draw(self.getGraphics_waves(x2,y2))
        self.canvas2.Zoom((x2.mean(),y2.mean()),(1.0,1.2))


    def getGraphics_freqs(self,x_data,y_data):
        # most items require data as a list of (x, y) pairs:
        #    [[1x, y1], [x2, y2], [x3, y3], ..., [xn, yn]]
        xy_data = list(zip(x_data, y_data))

        # Create your Poly object(s).
        # Use keyword args to set display properties.
        markers = wxplot.PolyMarker(xy_data,
                                     colour='blue',
                                     marker='circle',
                                     size=1,
                                     )
        return wxplot.PlotGraphics([markers], xLabel = "frequency / Hz", yLabel = "amplitude",)

    def getGraphics_waves(self, x_data, y_data):
        # most items require data as a list of (x, y) pairs:
        #    [[1x, y1], [x2, y2], [x3, y3], ..., [xn, yn]]
        xy_data = list(zip(x_data, y_data))

        # Create your Poly object(s).
        # Use keyword args to set display properties.
        line = wxplot.PolySpline(
            xy_data,
            colour='blue',#wx.Colour(128, 128, 0),  # Color: olive
            width=3,
        )
        return wxplot.PlotGraphics([line], xLabel = "time / s", yLabel = "amplitude",)


    def compute(self, rootnote, n, env_x0, env_width, volume,lowcutoff, highcutoff):
        self.shepard.set(rootnote,n, env_x0, env_width, volume,lowcutoff, highcutoff)
        t = np.linspace(0,0.01,200,dtype=np.float32)
        y2 = self.shepard.get_waveform(t)
        #print(t)
        #x1,y1 = tones.calc_fft(x2,y2)
        #x1 = self.shepard.freqs
        #y1 = self.shepard.amps
        x1 = self.shepard.get_freqs()
        y1 = self.shepard.get_amps()
        return x1, y1, t, y2

    def setKnob(self, value):
        self.draw()
        try:
            #self.param_queue.put((self.shepard.starting_freq, self.shepard.n, self.shepard.envelope_width, self.shepard.envelope_x0, self.shepard.volume, self.shepard.low_cutoff, self.shepard.high_cutoff))
            self.param_queue.put((self.shepard.get_starting_freq(), self.shepard.get_n(), self.shepard.get_envelope_width(), self.shepard.get_envelope_x0(), self.shepard.get_volume(), self.shepard.get_low_cutoff(), self.shepard.get_high_cutoff()))
        except queue.Full:
            pass

class App(wx.App):
    def OnInit(self):
        self.frame1 = FourierDemoFrame(parent=None, title="Tone Generator", size=(700, 600))
        self.frame1.Show()
        return True


if __name__ == '__main__':
    mp.freeze_support()
    app = App()
    app.MainLoop()