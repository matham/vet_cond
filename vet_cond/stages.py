# -*- coding: utf-8 -*-
'''Stages
===========

The stages of the experiment.
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
from cplcom.moa.stages import ConfigStageBase
from cplcom.moa.app import app_error

from vet_cond.devices import DAQOutDevice, DAQOutDeviceSim

__all__ = ('RootStage', )


class RootStage(ConfigStageBase):
    '''The root stage of the experiment.
    '''

    __settings_attrs__ = (
        'prehab', 'prerecord', 'posthab', 'postrecord', 'trial_opts',
        'video_name_pat', 'log_name_pat', 'record_video')

    server = ObjectProperty(None, allownone=True)
    '''The Barst server instance,
    :class:`~cplcom.moa.device.barst_server.Server`, or None when
    :attr:`simulate`.
    '''

    mcdaq = ObjectProperty(None, allownone=True)
    '''The Switch and Sense device, :class:`~vet_cond.devices.DAQOutDevice`
    when using actual hardware, or a
    :class:`~vet_cond.devices.DAQOutDeviceSim` when :attr:`simulate` the
    hardware.
    '''

    rtv = ObjectProperty(None, allownone=True)
    '''The RTV video acquisition device
    :class:`~cplcom.moa.device.rtv.RTVChan` when using actual hardware, or a
    :class:`~cplcom.moa.device.ffplayer.FFPyPlayerDevice` when
    :attr:`simulate` the hardware.
    '''

    ffwriter = None
    '''The :attr:`ffwriters` instance used in the current trial.
    '''

    ffwriters = []
    '''A list of :class:`~cplcom.moa.device.ffplayer.FFPyWriterDevice`
    instances equal to the number of trials, with each instance being a writer
    for the corresponding trial. They are all created at once at the start of
    running the subject.
    '''

    video_name_pat = StringProperty(
        '{animal}_trial{trial}_%m-%d-%Y_%I-%M-%S_%p.avi')
    '''The pattern that will be used to generate the video filenames for each
    trial. It is generated as follows::

        name = strftime(video_name_pat.format(**{'trial': trial_number,
                        'animal': animal_id}))

    Which basically means that all instances of ``{trial}`` is replaced by
    the current trial number and ``{animal}`` is replaced by the animal
    name given in the GUI. Then, it's is passed to `strftime` that formats
    any time parameters to get the name used for that trial/animal.

    If the filename already exists an error will be raised.
    '''

    log_name_pat = StringProperty('{animal}_%m-%d-%Y_%I-%M-%S_%p.csv')
    '''The pattern that will be used to generate the log filenames for each
    trial. It is generated as follows::

        strftime(log_name_pat.format(**{'animal': animal_id}))

    Which basically means that all instances of ``{animal}`` is replaced by the
    animal name given in the GUI. Then, it's is passed to `strftime` that
    formats any time parameters to get the log name used for that animal.

    If the filename matches an existing file, the new data will be appended to
    that file.
    '''

    prehab = NumericProperty(60)
    '''The amount of time to wait habituating the animal before the start of
    trials.
    '''

    posthab = NumericProperty(60)
    '''The amount of time to wait before finishing for the animal after the
    end of trials.
    '''

    prerecord = NumericProperty(5)
    '''The amount of time before each trial when video should be started
    being recorded. It is in addition to any ITI.
    '''

    postrecord = NumericProperty(5)
    '''The amount of time after each trial which video should continue to be
    recorded. It is in addition to any ITI.
    '''

    record_video = BooleanProperty(True)
    '''Whether video should be recorded for this experiment.
    '''

    trial_opts = ObjectProperty({
        'control': {'repeat': 3, 'shock': (0, 0), 'tone': (0, 0),
                    'duration': 15, 'iti': (45, 60)},
        'backward': {'repeat': 3, 'shock': (0, 3), 'tone': (5, 3),
                     'duration': 0, 'iti': (45, 60)},
        'condition': {'repeat': 3, 'shock': (2, 3), 'tone': (0, 3),
                      'duration': 0, 'iti': (45, 60)}})
    '''A dictionary that describes the available experiments, which will be
    available from the GUI to choose from.

    The keys are name of the experiment types and its values are dictionaries
    describing the structure of each experiment type.

    The structure dictionaries each has the following keys:

        `repeat`: int
            The number of trials for that experiment.
        `shock`: 2-tuple of floats
            The first element is the delay from the start of the trial until
            the shock start. The second element is the duration of the shock
            after that delay. A duration of zero will disable the shock.
        `tone`: 2-tuple of floats
            The first element is the delay from the start of the trial until
            the tone starts. The second element is the duration of the tone
            after that delay. A duration of zero will disable the tone.
        `iti`: 2-tuple of floats
            The minimum and maximum duration of the ITI. A value will be chosen
            uniformly at random from that range.
        `duration`: float
            The duration of the trial.
    '''

    def on_trial_opts(self, *largs):
        for _, opts in self.trial_opts.items():
            opts['repeat'] = max(1, int(opts['repeat']))
            opts['duration'] = float(opts['duration'])
            opts['shock'] = float(opts['shock'][0]), float(opts['shock'][1])
            opts['tone'] = float(opts['tone'][0]), float(opts['tone'][1])
            opts['iti'] = float(opts['iti'][0]), float(opts['iti'][1])

    animal_id = StringProperty('')
    '''The animal name acquired form the GUI.
    '''

    trial_type = StringProperty('')
    '''The experiment type from :attr:`trial_opts` for this animal.
    '''

    simulate = BooleanProperty(False)
    '''Whether the user has chosen to simulate the experiment. When ``True``,
    no actual hardware is required and all the hardware will be emulated
    by software and virtual devices. E.g. a video player for the video
    acquisition system.
    '''

    trial_repeat = NumericProperty(0)
    '''The number of trials from :attr:`trial_opts` for this animal.
    '''

    trial_duration = NumericProperty(0)
    '''The trial duration from :attr:`trial_opts` for this animal.
    '''

    shock_delay = NumericProperty(0)
    '''The shock delay from :attr:`trial_opts` for this animal.
    '''

    shock_duration = NumericProperty(0)
    '''The shock duration from :attr:`trial_opts` for this animal.
    '''

    tone_delay = NumericProperty(0)
    '''The tone delay from :attr:`trial_opts` for this animal.
    '''

    tone_duration = NumericProperty(0)
    '''The tone duration from :attr:`trial_opts` for this animal.
    '''

    iti_range = ObjectProperty((5, 10))
    '''The ITI range from :attr:`trial_opts` for this animal.
    '''

    tracker = None
    '''The :class:`~moa.utils.ObjectStateTracker` instance used to
    process the device activation and deactivation during startup and
    shutdown.
    '''

    frame_ts = 0
    '''The video time at the most recent frame.
    '''

    trial_stats = DictProperty({
        'shock_ts': -1, 'shock_te': -1, 'tone_ts': -1, 'tone_te': -1,
        'trial_ts': -1, 'trial_end': -1})
    '''Trials stats of the tone, shock, and trial start and end times in video
    time use for the log.
    '''

    _fd = None
    '''The log file handle.
    '''

    _log_filename = ''
    '''The filename of the current log file.
    '''

    _shutting_down_devs = False
    '''Whether we have or ere currently shutting down the devs.
    '''

    @classmethod
    def get_config_classes(cls):
        d = {
            'barst_server': Server, 'switch_and_sense_8-8': DAQOutDevice,
            'rtv': RTVChan, 'rtv_simulate': FFPyPlayerDevice,
            'experiment': RootStage, 'video_record': FFPyWriterDevice}
        d.update(ConfigStageBase.get_config_classes())
        return d

    def clear(self, recurse=False, loop=False, **kwargs):
        super(RootStage, self).clear(recurse=recurse, loop=loop, **kwargs)
        self._shutting_down_devs = False
        if not loop:
            self.tracker = self.server = self.mcdaq = self.rtv = None
            self.ffwriters = []
            self.ffwriter = None

    @app_error
    def init_devices(self):
        '''Called to start the devices during the init stage.
        '''
        settings = knspace.app.app_settings
        for k, v in settings['experiment'].items():
            setattr(self, k, v)

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
        callbacks.append(knspace.exp_dev_init.ask_step_stage)
        tracker.add_func_links(devs, callbacks, 'activation', 'active')
        devs[0].activate(self)

    def step_stage(self, source=None, **kwargs):
        if not self.started or (source is not None and source != self) or \
                self._shutting_down_devs:
            return super(RootStage, self).step_stage(source=source, **kwargs)

        self._shutting_down_devs = True
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
            return super(RootStage, self).step_stage(source=source, **kwargs)

        tracker = self.tracker = ObjectStateTracker()
        callbacks = [partial(d.deactivate, self, clear=True) for d in devs[1:]]
        callbacks.append(partial(self.ask_step_stage, source=source, **kwargs))
        tracker.add_func_links(devs, callbacks, 'activation', 'inactive',
                               timeout=5.)
        devs[0].deactivate(self, clear=True)
        return False

    @app_error
    def configure_animal_settings(self):
        '''Called to setup the experiment for the current animal before
        the animal is started.
        '''
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
            callbacks.append(knspace.exp_animal_init.ask_step_stage)
            tracker.add_func_links(w, callbacks, 'activation', 'active')
            w[0].activate(self)
        else:
            knspace.exp_animal_init.ask_step_stage()

    def video_callback(self, *largs):
        '''Called for each frame read from the viceo device.
        '''
        pts, frame = self.rtv.last_img
        self.frame_ts = pts
        if self.ffwriter:
            self.ffwriter.add_frame(frame, pts)
        knspace.display.update_img(frame)

    def record_start(self):
        '''Called at the start of each recording to init the recorders.
        '''
        stats = self.trial_stats
        for k in stats:
            stats[k] = -1

        if not self.ffwriters:
            return
        self.ffwriter = self.ffwriters[knspace.exp_trial_root.count]

    def update_time(self, key):
        '''Updates trial stats when an event occurs.
        '''
        self.trial_stats[key] = self.frame_ts

    def record_stop(self):
        '''Called at the end of each recording to stop the recorders.
        '''
        w = self.ffwriter
        if w:
            self.ffwriter = self.ffwriters[knspace.exp_trial_root.count] = None
            w.deactivate(self)

    @app_error
    def write_log(self):
        '''Called after each trial to dump the trial stats to the log.
        '''
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
