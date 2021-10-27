# TODO

## Synth

* Add event handler.

* Add feature to export .wav files after every execution.

* Add modes of operation based on controllers detected upon launch.

* Calculate bases using multipliers

* Add base for each of the 12-tone system tonal centers


## ST Implementation

### BLE

* Create BLE abstraction

* Parse incoming BLE data

* Install and test `bleak` in Jetson Nano

* Verify installation instructions in README


### Synth

* Determine what ST parameters will control what portions of the synth.

* Decide which ST firmware to use.

* Figure out how to include/add the ST firmware, as well as what instructions the user needs in order to flash and install the firmware.


## CV Implementation

* Detect the number of fingers in the Field of View.

* Detect hand gestures (potentially ASL)    

* Add continuous control
    * Use sign language gestures to access parameters, and use continuous position motion/magnitude data to control the accessed parameter(s)


## Gestures

### Main

1. Inform the system of which hand is wearing the ST (potentially two different gestures).

2. Scales:
    * Next scale.
    * Previous scale.

3. Change base:
    * Higher frequency base, i.e., higher octave.
    * Lower frequency base, i.e., lower octave.
    * NOTES:
        * Default init base to 110Hz.
        * Set base multiplier limits at 27.5Hz (A0) and 1760Hz (A6).

4. Change musical subdivision:
    * Greater musical subdivision, i.e., increase the number of notes that play per beat.
    * Lesser musical subdivision, i.e., increase the number of notes that play per beat.

5. Change octave range:
    * Increase octave range.
    * Decrease octave range.
    * NOTES:
        * Set limits based on base so that the top note is 3520Hz (A7) at all times, e.g.:
            * If base is at 27.5Hz (A0), then max octave range should be 7 octaves, so that the highest note remains at 3520Hz (A7).
            * If base is at 1760Hz (A6), then max octave range should be 1 octave, so that the highest note remains at 3520Hz (A7).
        * Adjust the octave range when base gets adjusted to not exceed 3520Hz (A7). Take into account previous octave range so if the base returns to what it was, it can recall the same range.

6. Switch performance mode:
    * Sustain mode (sustain notes)
    * Pulsing mode (pulse notes at the given subdivision)
    * NOTES:
        * In both scenarios, the pitch of the notes will most likely be controlled via the ST.

7. Sustain mode:
    * Start and stop notes.

8. Pulsing mode and Clock:
    * Change BPM.
    * Change subdivision.
    * NOTES:
        * Even when in sustain mode, the clock may be used to control effects, in case things such as LFOs, Sample and Hold, and/or Delays are implemented.

9. Synth:
    * Modify loudness.
    * Modify pitch.
    * Additional potential parameters:
        * Modify waveform.

10. Pause menu:
    * Pause/Resume synth.
    * In the "Pause" menu, the user can:
        * View existing scales
        * Choose another scale
        * Choose BPM and Subdivision


### Additional Gestures (Optional)

1. Switch chord type, e.g., major, minor, suspended, augmented, diminished, etc. (this might be quite complicated because of how scales are being defined).

2. Switch chord inversion: assuming a C major chord (with notes C, E, and G), the chord is said to be in its fundamental position when the lowest note is C; it is said to be in first inversion if the bottom note is E (E, G, and C); and it is said to be in second inversion if the bottom note is G (G, C, and E).

3. Add/Remove effects.


## Secondary (Optional)

* Add data visualization tools (If video synth approach, potentially use PyOpenGL? If data analysis approach, potentially use MatPlotLib or Seaborn?) *Note that this would require the use of a screen.*
