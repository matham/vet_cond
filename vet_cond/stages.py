# -*- coding: utf-8 -*-
'''The stages of the experiment.
'''

from time import strftime
from os.path import isfile
from functools import partial

from moa.utils import ObjectStateTracker

from kivy.properties import (
    ObjectProperty, ListProperty, ConfigParserProperty, NumericProperty,
    BooleanProperty, StringProperty, OptionProperty, DictProperty)
from kivy.uix.behaviors.knspace import knspace

from cplcom.moa.device.ffplayer import FFPyPlayerDevice, FFPyWriterDevice
from cplcom.moa.device.barst_server import Server
from cplcom.moa.device.rtv import RTVChan
from cplcom.moa.stages import RootStageBase
from cplcom.moa.app import app_error

from vet_cond.devices import DAQOutDevice, DAQOutDeviceSim


class RootStage(RootStageBase):

    __settings_attrs__ = (
        'prehab', 'prerecord', 'posthab', 'postrecord', 'trial_opts',
        'video_name_pat', 'log_name_pat', 'record_video')

    server = ObjectProperty(None, allownone=True)

    mcdaq = ObjectProperty(None, allownone=True)

    rtv = ObjectProperty(None, allownone=True)

    ffwriter = None

    ffwriters = []

    video_name_pat = StringProperty(
        '{animal}_trial{trial}_%m-%d-%Y_%I-%M-%S_%p.avi')

    log_name_pat = StringProperty('{animal}_%m-%d-%Y_%I-%M-%S_%p.csv')

    prehab = NumericProperty(60)

    posthab = NumericProperty(60)

    prerecord = NumericProperty(5)

    postrecord = NumericProperty(5)

    record_video = BooleanProperty(True)

    trial_opts = ObjectProperty({
        'control': {'repeat': 3, 'shock': (0, 0), 'tone': (0, 0),
                    'duration': 15, 'iti': (45, 60)},
        'backward': {'repeat': 3, 'shock': (0, 3), 'tone': (5, 3),
                     'duration': 0, 'iti': (45, 60)},
        'condition': {'repeat': 3, 'shock': (2, 3), 'tone': (0, 3),
                      'duration': 0, 'iti': (45, 60)}})

    def on_trial_opts(self, *largs):
        for _, opts in self.trial_opts.items():
            opts['repeat'] = max(1, int(opts['repeat']))
            opts['duration'] = float(opts['duration'])
            opts['shock'] = float(opts['shock'][0]), float(opts['shock'][1])
            opts['tone'] = float(opts['tone'][0]), float(opts['tone'][1])
            opts['iti'] = float(opts['iti'][0]), float(opts['iti'][1])

    animal_id = StringProperty('')

    trial_type = StringProperty('')

    simulate = BooleanProperty(False)

    trial_repeat = NumericProperty(0)

    trial_duration = NumericProperty(0)

    shock_delay = NumericProperty(0)

    shock_duration = NumericProperty(0)

    tone_delay = NumericProperty(0)

    tone_duration = NumericProperty(0)

    iti_range = ObjectProperty((5, 10))

    tracker = None

    frame_ts = 0

    trial_stats = DictProperty({
        'shock_ts': -1, 'shock_te': -1, 'tone_ts': -1, 'tone_te': -1,
        'trial_ts': -1, 'trial_end': -1})

    _fd = None

    _log_filename = ''

    def get_config_classes(self):
        return {
            'barst_server': Server, 'switch_and_sense_8-8': DAQOutDevice,
            'rtv': RTVChan, 'rtv_simulate': FFPyPlayerDevice,
            'experiment': self, 'video_record': FFPyWriterDevice}

    def clear(self, recurse=False, loop=False, **kwargs):
        super(RootStage, self).clear(recurse=recurse, loop=loop, **kwargs)
        if not loop:
            self.tracker = self.server = self.mcdaq = self.rtv = None

    @app_error
    def init_devices(self):
        time_line = knspace.time_line
        time_line.clear_slices()
        elems = (
            (0, 'Init'), (self.prehab, 'Prehab'), (self.prerecord, 'Pre'),
            (self.trial_duration, 'Trial'), (self.postrecord, 'Post'),
            (max((d['iti'][1] for d in self.trial_opts.values())), 'ITI'),
            (self.posthab, 'Posthab'))
        for t, name in elems:
            time_line.add_slice(name=name, duration=t)
        time_line.smear_slices()

        sim = self.simulate = knspace.gui_simulate.state == 'down'
        tracker = self.tracker = ObjectStateTracker()
        settings = knspace.app.app_settings
        attr_map = {
            'shocker': knspace.gui_shocker, 'ir_leds': knspace.gui_ir_leds,
            'tone': knspace.gui_tone}

        if sim:
            daq = self.mcdaq = DAQOutDeviceSim(
                knsname='mcdaq', attr_map=attr_map)
            rtv = self.rtv = FFPyPlayerDevice(
                knsname='player', **settings['rtv_simulate'])
            devs = [daq, rtv]
        else:
            server = self.server = Server(
                knsname='barst_server', **settings['barst_server'])
            daq = self.mcdaq = DAQOutDevice(
                knsname='mcdaq', attr_map=attr_map, server=server,
                **settings['switch_and_sense_8-8'])
            rtv = self.rtv = RTVChan(knsname='player', server=server,
                                     **settings['rtv'])
            devs = [server, daq, rtv]

        rtv.fbind('on_data_update', self.video_callback)

        callbacks = [partial(d.activate, self) for d in devs[1:]]
        callbacks.append(knspace.exp_dev_init.step_stage)
        tracker.add_func_links(devs, callbacks, 'activation', 'active')
        devs[0].activate(self)

    @app_error
    def stop_devices(self):
        self.ffwriter = None
        if self._fd:
            self._fd.close()
            self._fd = None
        if self.rtv:
            self.rtv.funbind('on_data_update', self.video_callback)

        devs = [self.rtv, self.mcdaq, self.server] + self.ffwriters
        devs = [d for d in devs if d is not None]
        self.ffwriters = []

        if not devs:
            knspace.exp_dev_stop.step_stage()
            return

        tracker = self.tracker = ObjectStateTracker()
        callbacks = [partial(d.deactivate, self) for d in devs[1:]]
        callbacks.append(knspace.exp_dev_stop.step_stage)
        tracker.add_func_links(devs, callbacks, 'activation', 'inactive')
        devs[0].deactivate(self)

    @app_error
    def configure_animal_settings(self):
        animal_id = self.animal_id = knspace.gui_animal_id.text
        trial_type = self.trial_type = knspace.gui_trial_type.text
        opts = self.trial_opts[trial_type]

        fname = strftime(self.log_name_pat.format(**{'animal': animal_id}))
        filename = self._log_filename

        if filename != fname:
            fd = self._fd
            if fd is not None:
                fd.close()
                self._fd = None

            if fname:
                ex = isfile(fname)
                fd = self._fd = open(fname, 'a')
                if not ex:
                    fd.write('Date,ID,Type,Trial,TrialStart,TrialEnd,'
                             'ToneStart,ToneEnd,ShockStart,ShockEnd\n')

        self.trial_repeat = repeat = opts['repeat']
        self.trial_duration = opts['duration']
        self.shock_delay, self.shock_duration = opts['shock']
        self.tone_delay, self.tone_duration = opts['tone']
        self.iti_range = opts['iti']

        if self.record_video:
            ofmt = knspace.app.app_settings['video_record'].get('ofmt', '')
            rate = self.rtv.rate
            size = self.rtv.size
            ifmt = getattr(
                self.rtv,
                'display_img_fmt' if self.simulate else 'ff_output_img_fmt')

            w = []
            for i in range(repeat):
                fname = strftime(self.video_name_pat.format(**{
                    'trial': i, 'animal': animal_id}))
                writer = FFPyWriterDevice(
                    filename=fname, rate=rate, size=size, ifmt=ifmt, ofmt=ofmt)
                w.append(writer)
            self.ffwriters = w

            tracker = self.tracker = ObjectStateTracker()
            callbacks = [partial(d.activate, self) for d in w[1:]]
            callbacks.append(knspace.exp_animal_init.step_stage)
            tracker.add_func_links(w, callbacks, 'activation', 'active')
            w[0].activate(self)
        else:
            knspace.exp_animal_init.step_stage()

    def video_callback(self, *largs):
        pts, frame = self.rtv.last_img
        self.frame_ts = pts
        if self.ffwriter:
            self.ffwriter.add_frame(frame, pts)
        knspace.display.update_img(frame)

    def record_start(self):
        stats = self.trial_stats
        for k in stats:
            stats[k] = -1

        if not self.ffwriters:
            return
        self.ffwriter = self.ffwriters[knspace.exp_trial_root.count]

    def update_time(self, key):
        self.trial_stats[key] = self.frame_ts

    def record_stop(self):
        w = self.ffwriter
        if w:
            self.ffwriter = self.ffwriters[knspace.exp_trial_root.count] = None
            w.deactivate(self)

    @app_error
    def write_log(self):
        fd = self._fd
        if fd is None:
            return

        val = ('{},{},{},{},{trial_ts},{trial_te},{tone_ts},{tone_te},'
               '{shock_ts},{shock_te}\n'.format(
                strftime('%m/%d/%Y %I:%M:%S %p'), self.animal_id,
                self.trial_type, knspace.exp_trial_root.count,
                **self.trial_stats))
        fd.write(val)
        fd.flush()
