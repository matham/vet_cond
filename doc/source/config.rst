vet_cond Config
===============

:app:

`inspect`: False
 Enables GUI inspection. If True, it is activated by hitting ctrl-e in
 the GUI.
 

:barst_server:

`server_path`: 
 The full path to the Barst executable. Could be empty if the server
 is already started, on remote computer, or if it's in the typical
 `Program Files` path or came installed with the wheel. If the server is not
 running, this executable is needed to launch the server.
 
 Defaults to `''`.
 
`server_pipe`: 
 The full path to the pipe name (to be) used by the server. Examples are
 ``\remote_name\pipe\pipe_name``, where ``remote_name`` is the name of
 the remote computer, or a period (`.`) if the server is local, and
 ``pipe_name`` is the name of the pipe used to create the server.
 
 Defaults to `''`.
 

:experiment:

`log_name_pat`: {animal}_%m-%d-%Y_%I-%M-%S_%p.csv
 The pattern that will be used to generate the log filenames for each
 trial. It is generated as follows::
 
     strftime(log_name_pat.format(**{'animal': animal_id}))
 
 Which basically means that all instances of ``{animal}`` is replaced by the
 animal name given in the GUI. Then, it's is passed to `strftime` that
 formats any time parameters to get the log name used for that animal.
 
 If the filename matches an existing file, the new data will be appended to
 that file.
 
`posthab`: 60
 The amount of time to wait before finishing for the animal after the
 end of trials.
 
`postrecord`: 5
 The amount of time after each trial which video should continue to be
 recorded. It is in addition to any ITI.
 
`prehab`: 60
 The amount of time to wait habituating the animal before the start of
 trials.
 
`prerecord`: 5
 The amount of time before each trial when video should be started
 being recorded. It is in addition to any ITI.
 
`record_video`: True
 Whether video should be recorded for this experiment.
     
 
`trial_opts`: {'control': {'duration': 15, 'repeat': 3, 'tone': (0, 0), 'shock': (0, 0), 'iti': (45, 60)}, 'backward': {'duration': 0, 'repeat': 3, 'tone': (5, 3), 'shock': (0, 3), 'iti': (45, 60)}, 'condition': {'duration': 0, 'repeat': 3, 'tone': (0, 3), 'shock': (2, 3), 'iti': (45, 60)}}
 A dictionary that describes the available experiments, which will be
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
 
`video_name_pat`: {animal}_trial{trial}_%m-%d-%Y_%I-%M-%S_%p.avi
 The pattern that will be used to generate the video filenames for each
 trial. It is generated as follows::
 
     name = strftime(video_name_pat.format(**{'trial': trial_number,
                     'animal': animal_id}))
 
 Which basically means that all instances of ``{trial}`` is replaced by
 the current trial number and ``{animal}`` is replaced by the animal
 name given in the GUI. Then, it's is passed to `strftime` that formats
 any time parameters to get the name used for that trial/animal.
 
 If the filename already exists an error will be raised.
 

:rtv:

`output_img_fmt`: gray
 The desired output image format that the rtv device should send us.
 It can be one of `'rgb16', 'gray', 'rgb15', 'rgb24', 'rgb32'`.
 
 Defaults to `'gray'`.
 
`output_video_fmt`: full_NTSC
 The desired output image size that the rtv device should send us.
 It can be one of
 `'full_NTSC', 'full_PAL', 'CIF_NTSC', 'CIF_PAL', 'QCIF_NTSC', 'QCIF_PAL'`
 and its corresponding size is listed in :attr:`img_sizes`.
 
`port`: 0
 The port number on the RTV card of camera to use.
     
 

:rtv_simulate:

`filename`: Wildlife.mp4
 The full filename to the video file or video stream.
     
 
`output_img_fmt`: 
 The image pixel format from :attr:`ffpyplayer.tools.pix_fmts` that is to
 be used for the images output to us by the player. Defaults to `''` and
 must be set.
 

:switch_and_sense_8-8:

`SAS_chan`: 0
 The channel number of the Switch & Sense 8/8 as configured in InstaCal.
 
 Defaults to zero.
 
`ir_leds_pin`: 6
 The pin number on the Switch and Sense 8/8 that is connected to and
 controls the IR LEDs.
 
`shocker_pin`: 4
 The pin number on the Switch and Sense 8/8 that is connected to and
 controls the shocker.
 
`tone_pin`: 5
 The pin number on the Switch and Sense 8/8 that is connected to and
 controls the tone.
 

:video_record:

`filename`: 
 The filename of the video to create.
     
 
`ofmt`: 
 The pixel format from :attr:`ffpyplayer.tools.pix_fmts` in which
 the images will be written to disk. If not empty and different than
 :attr:`ifmt`, the input format, the images will be internally converted to
 this format before writing to disk.
 
