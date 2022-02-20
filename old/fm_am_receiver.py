#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FM/AM Receiver
# Author: Shawn Cresante
# Copyright: Public Domain
# Description: Works with SDRPlay
# GNU Radio version: 3.9.4.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



from gnuradio import qtgui

class fm_am_receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FM/AM Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FM/AM Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "fm_am_receiver")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 500000
        self.vol = vol = 1
        self.sel = sel = 0
        self.sdr_samp_rate = sdr_samp_rate = 4e6
        self.psth = psth = -30
        self.freq = freq = 127.85e6
        self.filter_taps = filter_taps = firdes.low_pass(1,samp_rate,100e3,1e3)
        self.fft_refresh = fft_refresh = 1/15
        self.amfm = amfm = 0

        ##################################################
        # Blocks
        ##################################################
        self._vol_range = Range(0, 1, 0.05, 1, 200)
        self._vol_win = RangeWidget(self._vol_range, self.set_vol, "volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._vol_win)
        if int == bool:
        	self._sel_choices = {'Pressed': bool(1), 'Released': bool(0)}
        elif int == str:
        	self._sel_choices = {'Pressed': "1".replace("'",""), 'Released': "0".replace("'","")}
        else:
        	self._sel_choices = {'Pressed': 1, 'Released': 0}

        _sel_toggle_button = qtgui.ToggleButton(self.set_sel, 'Squelch', self._sel_choices, False,"'value2'".replace("'",""))
        _sel_toggle_button.setColors("default","default","default","default")
        self.sel = _sel_toggle_button

        self.top_layout.addWidget(_sel_toggle_button)
        self._psth_range = Range(-70, 10, 1, -30, 200)
        self._psth_win = RangeWidget(self._psth_range, self.set_psth, "Power Threshold (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._psth_win)
        self._freq_range = Range(88.3e6, 148e6, 0.01e6, 127.85e6, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "RF Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        # Create the options list
        self._amfm_options = [0, 1]
        # Create the labels list
        self._amfm_labels = ['AM', 'FM']
        # Create the combo box
        # Create the radio buttons
        self._amfm_group_box = Qt.QGroupBox("AM/FM" + ": ")
        self._amfm_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._amfm_button_group = variable_chooser_button_group()
        self._amfm_group_box.setLayout(self._amfm_box)
        for i, _label in enumerate(self._amfm_labels):
            radio_button = Qt.QRadioButton(_label)
            self._amfm_box.addWidget(radio_button)
            self._amfm_button_group.addButton(radio_button, i)
        self._amfm_callback = lambda i: Qt.QMetaObject.invokeMethod(self._amfm_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._amfm_options.index(i)))
        self._amfm_callback(self.amfm)
        self._amfm_button_group.buttonClicked[int].connect(
            lambda i: self.set_amfm(self._amfm_options[i]))
        self.top_layout.addWidget(self._amfm_group_box)
        self.soapy_sdrplay_source_0_0 = None
        dev = 'driver=sdrplay'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_sdrplay_source_0_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_sdrplay_source_0_0.set_sample_rate(0, samp_rate)
        self.soapy_sdrplay_source_0_0.set_bandwidth(0, 0.0)
        self.soapy_sdrplay_source_0_0.set_antenna(0, 'Antenna A')
        self.soapy_sdrplay_source_0_0.set_gain_mode(0, False)
        self.soapy_sdrplay_source_0_0.set_frequency(0, freq)
        self.soapy_sdrplay_source_0_0.set_frequency_correction(0, 0)
        self.soapy_sdrplay_source_0_0.set_gain(0, min(max(--10, 0.0), 47.0))
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=50,
                decimation=48,
                taps=[],
                fractional_bw=0)
        self.qtgui_freq_sink_x_3_0_0_0_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_FLATTOP, #wintype
            0, #fc
            samp_rate, #bw
            'Demodulated AM', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_3_0_0_0_0.set_update_time(fft_refresh)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_3_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_3_0_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_3_0_0_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_3_0_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_3_0_0_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_3_0_0_0_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_3_0_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_3_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_3_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_3_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_3_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_3_0_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_3_0_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_3_0_0_0_0_win)
        self.qtgui_freq_sink_x_3_0_0_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_FLATTOP, #wintype
            0, #fc
            samp_rate, #bw
            'Demodulated FM', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_3_0_0_0.set_update_time(fft_refresh)
        self.qtgui_freq_sink_x_3_0_0_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_3_0_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_3_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_3_0_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_3_0_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_3_0_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_3_0_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_3_0_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_3_0_0_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_3_0_0_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_3_0_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_3_0_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_3_0_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_3_0_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_3_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_3_0_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_3_0_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_3_0_0_0_win)
        self.qtgui_freq_sink_x_3_0_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_FLATTOP, #wintype
            freq, #fc
            samp_rate, #bw
            'Filtered', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_3_0_0.set_update_time(fft_refresh)
        self.qtgui_freq_sink_x_3_0_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_3_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_3_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_3_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_3_0_0.enable_grid(False)
        self.qtgui_freq_sink_x_3_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_3_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_3_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_3_0_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_3_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_3_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_3_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_3_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_3_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_3_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_3_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_3_0_0_win)
        self.qtgui_freq_sink_x_3_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_FLATTOP, #wintype
            freq, #fc
            samp_rate, #bw
            'Resampled', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_3_0.set_update_time(fft_refresh)
        self.qtgui_freq_sink_x_3_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_3_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_3_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_3_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_3_0.enable_grid(False)
        self.qtgui_freq_sink_x_3_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_3_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_3_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_3_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_3_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_3_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_3_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_3_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_3_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_3_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_3_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_3_0_win)
        self.qtgui_freq_sink_x_3 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_FLATTOP, #wintype
            freq, #fc
            samp_rate, #bw
            'RF Input', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_3.set_update_time(fft_refresh)
        self.qtgui_freq_sink_x_3.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_3.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_3.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_3.enable_autoscale(False)
        self.qtgui_freq_sink_x_3.enable_grid(False)
        self.qtgui_freq_sink_x_3.set_fft_average(1.0)
        self.qtgui_freq_sink_x_3.enable_axis_labels(True)
        self.qtgui_freq_sink_x_3.enable_control_panel(False)
        self.qtgui_freq_sink_x_3.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_3.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_3.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_3.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_3.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_3.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_3_win = sip.wrapinstance(self.qtgui_freq_sink_x_3.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_3_win)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, filter_taps, 0, samp_rate)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_float*1,amfm,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,sel,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(vol)
        self.audio_sink_0_0 = audio.sink(48000, '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=samp_rate,
        	audio_decimation=10,
        )
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc(psth, 1e-4, 0, False)
        self.analog_am_demod_cf_0 = analog.am_demod_cf(
        	channel_rate=48e3,
        	audio_decim=10,
        	audio_pass=6000,
        	audio_stop=8000,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_am_demod_cf_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.analog_am_demod_cf_0, 0), (self.qtgui_freq_sink_x_3_0_0_0_0, 0))
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.analog_wfm_rcv_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.audio_sink_0_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_am_demod_cf_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_freq_sink_x_3_0_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_selector_0_0, 1))
        self.connect((self.rational_resampler_xxx_0, 0), (self.qtgui_freq_sink_x_3_0_0_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.qtgui_freq_sink_x_3_0, 0))
        self.connect((self.soapy_sdrplay_source_0_0, 0), (self.analog_pwr_squelch_xx_0, 0))
        self.connect((self.soapy_sdrplay_source_0_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.soapy_sdrplay_source_0_0, 0), (self.qtgui_freq_sink_x_3, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "fm_am_receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_filter_taps(firdes.low_pass(1,self.samp_rate,100e3,1e3))
        self.qtgui_freq_sink_x_3.set_frequency_range(self.freq, self.samp_rate)
        self.qtgui_freq_sink_x_3_0.set_frequency_range(self.freq, self.samp_rate)
        self.qtgui_freq_sink_x_3_0_0.set_frequency_range(self.freq, self.samp_rate)
        self.qtgui_freq_sink_x_3_0_0_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_frequency_range(0, self.samp_rate)
        self.soapy_sdrplay_source_0_0.set_sample_rate(0, self.samp_rate)

    def get_vol(self):
        return self.vol

    def set_vol(self, vol):
        self.vol = vol
        self.blocks_multiply_const_vxx_0_0.set_k(self.vol)

    def get_sel(self):
        return self.sel

    def set_sel(self, sel):
        self.sel = sel
        self.blocks_selector_0.set_input_index(self.sel)

    def get_sdr_samp_rate(self):
        return self.sdr_samp_rate

    def set_sdr_samp_rate(self, sdr_samp_rate):
        self.sdr_samp_rate = sdr_samp_rate

    def get_psth(self):
        return self.psth

    def set_psth(self, psth):
        self.psth = psth
        self.analog_pwr_squelch_xx_0.set_threshold(self.psth)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.qtgui_freq_sink_x_3.set_frequency_range(self.freq, self.samp_rate)
        self.qtgui_freq_sink_x_3_0.set_frequency_range(self.freq, self.samp_rate)
        self.qtgui_freq_sink_x_3_0_0.set_frequency_range(self.freq, self.samp_rate)
        self.soapy_sdrplay_source_0_0.set_frequency(0, self.freq)

    def get_filter_taps(self):
        return self.filter_taps

    def set_filter_taps(self, filter_taps):
        self.filter_taps = filter_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.filter_taps)

    def get_fft_refresh(self):
        return self.fft_refresh

    def set_fft_refresh(self, fft_refresh):
        self.fft_refresh = fft_refresh
        self.qtgui_freq_sink_x_3.set_update_time(self.fft_refresh)
        self.qtgui_freq_sink_x_3_0.set_update_time(self.fft_refresh)
        self.qtgui_freq_sink_x_3_0_0.set_update_time(self.fft_refresh)
        self.qtgui_freq_sink_x_3_0_0_0.set_update_time(self.fft_refresh)
        self.qtgui_freq_sink_x_3_0_0_0_0.set_update_time(self.fft_refresh)

    def get_amfm(self):
        return self.amfm

    def set_amfm(self, amfm):
        self.amfm = amfm
        self._amfm_callback(self.amfm)
        self.blocks_selector_0_0.set_input_index(self.amfm)




def main(top_block_cls=fm_am_receiver, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
