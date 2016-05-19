'''Devices
===========

Defines some of the devices that are used in the experiment.
'''

from moa.device.digital import ButtonPort

from kivy.properties import (
    ConfigParserProperty, BooleanProperty, ListProperty, ObjectProperty,
    NumericProperty, StringProperty)

from cplcom.moa.device.mcdaq import MCDAQDevice

__all__ = ('DAQOutDeviceBase', 'DAQOutDeviceSim', 'DAQOutDevice')


class DAQOutDeviceBase(object):
    '''Base class that defines the properties which control the hardware
    devices connected to the Switch and Sense.
    '''

    shocker = BooleanProperty(False, allownone=True)
    '''Boolean property that controls the shocker.
    '''

    ir_leds = BooleanProperty(False, allownone=True)
    '''Boolean property that controls the IR LEDs.
    '''

    tone = BooleanProperty(False, allownone=True)
    '''Boolean property that controls the tone generator.
    '''


class DAQOutDeviceSim(DAQOutDeviceBase, ButtonPort):
    '''Device used when simulating a Switch & Sense 8/8 output device,
    but when none is connected.
    '''
    pass


class DAQOutDevice(DAQOutDeviceBase, MCDAQDevice):
    '''Device used when using the Barst Switch & Sense 8/8 output device.
    '''
    __settings_attrs__ = ('shocker_pin', 'ir_leds_pin', 'tone_pin')

    def __init__(self, **kwargs):
        super(DAQOutDevice, self).__init__(direction='o', **kwargs)
        self.dev_map = {
            'shocker': self.shocker_pin, 'ir_leds': self.ir_leds_pin,
            'tone': self.tone_pin}

    shocker_pin = NumericProperty(4)
    '''The pin number on the Switch and Sense 8/8 that is connected to and
    controls the shocker.
    '''

    ir_leds_pin = NumericProperty(6)
    '''The pin number on the Switch and Sense 8/8 that is connected to and
    controls the IR LEDs.
    '''

    tone_pin = NumericProperty(5)
    '''The pin number on the Switch and Sense 8/8 that is connected to and
    controls the tone.
    '''
