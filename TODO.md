# TODO

## Synth

* Add event handler

* Add feature to export .wav files after every execution. Perhaps controlled by a CV gesture to start/stop recording?


## ST Implementation

* Create BLE abstraction (pygatt?)

* Parse incoming data

* Determine what parameters will control what portions of the synth


## CV Implementation

* Create gesture for changing the base, and default init base to 110Hz
    * If the final product will be screenless, the should it just re-assign the base to the lower or the higher octave?
    * Set base limits at 27.5Hz (A0) and 1760Hz (A6)

* Create gesture for changing the octave range
    * If the final product will be screenless, them should it add and subtract an octave to the range?
    * Set limits based on base so that the top note is 3520Hz (A7) at all times:
        * If base is at 27.5Hz (A0), then max octave range should be 7 octaves, so that the highest note remains at 3520Hz (A7)
        * If base is at 1760Hz (A6), then max octave range should be 1 octave, so that the highest note remains at 3520Hz (A7)
    * Adjust the octave range when base gets adjusted to not exceed 3520Hz (A7)

* Create gesture for changing scale
    * If the final product will be screenless, then should it just go to next/previous scale?
    
* Consider adding gestures for adding effects


## Secondary (Optional)

* Add a "Pause" functionality where the user can:
    * Allow changing chosen scales
    * View existing scales

* Add data visualization tools *Note that this would require the use of a screen.*

* Find a way to install Linux dependencies using `apt` or `apt-get` from a file.
