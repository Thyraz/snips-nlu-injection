# snips-nlu-injection

copy nlu-inject.py to _/opt/snips-nlu-inject/_
start with `sudo python3 nlu-inject.py`

The script will listen to messages on the `hermes/asr/inject` topic
and inject the values to nlu. (_nlu_engine.json_ and _intent_parser.json_)
After that, the _snips-nlu.service_ gets restarted.

Injection has to be done again, after you update/install a new version of your assitant.
But this also applies to asr injection, so you should already be familier with that.

The script needs read write access to both files mentioned above.
