''' Devices used in the experiment.
'''

from moa.device.digital import ButtonPort

from kivy.properties import (
    ConfigParserProperty, BooleanProperty, ListProperty, ObjectProperty,
    NumericProperty, StringProperty)

from cplcom.moa.device.mcdaq import MCDAQDevice


class DAQOutDeviceBase(object):

    shocker = BooleanProperty(False, allownone=True)

    ir_leds = BooleanProperty(False, allownone=True)

    tone = BooleanProperty(False, allownone=True)


class DAQOutDeviceSim(DAQOutDeviceBase, ButtonPort):
    '''Device used when simulating the Switch & Sense 8/8 output device.
    '''
    pass


class DAQOutDevice(DAQOutDeviceBase, MCDAQDevice):
    '''Device used when using the barst Switch & Sense 8/8 output devices.
    '''
    __settings_attrs__ = ('shocker_pin', 'ir_leds_pin', 'tone_pin')

    def __init__(self, **kwargs):
        super(DAQOutDevice, self).__init__(direction='o', **kwargs)
        self.dev_map = {
            'shocker': self.shocker_pin, 'ir_leds': self.ir_leds_pin,
            'tone': self.tone_pin}

    shocker_pin = NumericProperty(4)

    ir_leds_pin = NumericProperty(6)

    tone_pin = NumericProperty(5)
