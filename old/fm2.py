#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: fm2
# Author: shawn
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

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



from gnuradio import qtgui

class fm2(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "fm2", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("fm2")
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

        self.settings = Qt.QSettings("GNU Radio", "fm2")

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
        self.freq_def = freq_def = 91100000
        self.samp_rate = samp_rate = 2000000
        self.quad = quad = 192000
        self.freq = freq = freq_def
        self.decimation2 = decimation2 = 2
        self.decimation1 = decimation1 = 8
        self.cutoff = cutoff = 100000

        ##################################################
        # Blocks
        ##################################################
        self._quad_range = Range(10000, 800000, 50000, 192000, 500)
        self._quad_win = RangeWidget(self._quad_range, self.set_quad, "quadrature rate", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._quad_win)
        self._freq_range = Range(87000000, 108000000, 100000, freq_def, 600)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "freq", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self._cutoff_range = Range(1000, 200000, 25000, 100000, 200)
        self._cutoff_win = RangeWidget(self._cutoff_range, self.set_cutoff, "cutoff", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._cutoff_win)
        self.soapy_sdrplay_source_0 = None
        dev = 'driver=sdrplay'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_sdrplay_source_0 = soapy.source(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_sdrplay_source_0.set_sample_rate(0, samp_rate)
        self.soapy_sdrplay_source_0.set_bandwidth(0, 0.0)
        self.soapy_sdrplay_source_0.set_antenna(0, 'Antenna A')
        self.soapy_sdrplay_source_0.set_gain_mode(0, False)
        self.soapy_sdrplay_source_0.set_frequency(0, freq)
        self.soapy_sdrplay_source_0.set_frequency_correction(0, 0)
        self.soapy_sdrplay_source_0.set_gain(0, min(max(--20, 0.0), 47.0))
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=8,
                taps=[],
                fractional_bw=0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                cutoff,
                1000000,
                window.WIN_HAMMING,
                6.76))
        self._decimation2_range = Range(1, 12, 1, 2, 200)
        self._decimation2_win = RangeWidget(self._decimation2_range, self.set_decimation2, "decimation rx", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._decimation2_win)
        self._decimation1_range = Range(1, 12, 1, 8, 200)
        self._decimation1_win = RangeWidget(self._decimation1_range, self.set_decimation1, "decimation resampler", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._decimation1_win)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(.5)
        self.audio_sink_0 = audio.sink(44100, '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=quad,
        	audio_decimation=6,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_wfm_rcv_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.soapy_sdrplay_source_0, 0), (self.rational_resampler_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "fm2")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_freq_def(self):
        return self.freq_def

    def set_freq_def(self, freq_def):
        self.freq_def = freq_def
        self.set_freq(self.freq_def)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, 1000000, window.WIN_HAMMING, 6.76))
        self.soapy_sdrplay_source_0.set_sample_rate(0, self.samp_rate)

    def get_quad(self):
        return self.quad

    def set_quad(self, quad):
        self.quad = quad

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.soapy_sdrplay_source_0.set_frequency(0, self.freq)

    def get_decimation2(self):
        return self.decimation2

    def set_decimation2(self, decimation2):
        self.decimation2 = decimation2

    def get_decimation1(self):
        return self.decimation1

    def set_decimation1(self, decimation1):
        self.decimation1 = decimation1

    def get_cutoff(self):
        return self.cutoff

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.cutoff, 1000000, window.WIN_HAMMING, 6.76))




def main(top_block_cls=fm2, options=None):

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
