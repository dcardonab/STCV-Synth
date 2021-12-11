# TODO

## Jetson Nano

* Install and test `bleak` in Jetson Nano.

* Verify automatic selection of `defualt` audio driver when initializing. --> Difficult due to Pyo's `pa_list_devices()` function only printing the list of devices to the screen as opposed to returning the list. GitHub issue has been opened for this, and depending on the answer, it might be necessary to implement a function that queries PortAudio.

* Verify installation process.


## Documentation

* Verify installation instructions in README.

* Add user manual, including description and usage instructions.


## ST

* Implement 'Sustain' mode of operation. (Determine how to start and stop notes. Perhaps a tapping gesture?)

* Add polyphonic control. (`Voice` class abstraction?)


## CV

* Improve performance

* Use the ST wearing hand menu to only detect the other hand for polyphony, and the ST hand for GUI operation.


## GUI

* Connect octave base GUI control to the synth.

* Reduce GUI buttons sensitivity.

* Gray out plus and minus buttons when the current value is equal to the minimum or maximum.
