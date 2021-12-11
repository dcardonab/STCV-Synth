# TODO

## Jetson Nano

* Install and test `bleak` in Jetson Nano
* Verify automatic selection of `defualt` audio driver when initializing.
* Verify installation process.


## Documentation

* Verify installation instructions in README.
* Add user manual, including description and usage instructions.


## ST

* Implement 'Sustain' mode of operation. (Determine how to start and stop notes. Perhaps a tapping gesture?)
* Determine what ST parameters will control what portions of the synth.
* Add polyphonic control. (`Voice` class abstraction?)


## CV

* Connect GUI controls to the synth:
    * Scale selection.
    * Octave base.
    
* Reduce GUI buttons sensitivity

* Use the ST hand detection to only detect the other hand for polyphony, and the ST hand for GUI operation.
