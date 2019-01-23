## pep.py - Modified for the osu! private server: Atoka

- Origin: https://git.zxq.co/ripple/pep.py
- Mirror: https://github.com/osuripple/pep.py

## Commands we borrowed (yoinked) from cmyui (thx dad) and added to FokaBot (Mirai)

* Linking your Discord from in-game (requires our discord bot.) (`!linkdiscord`)
* Scheduled Restrictions (`!erestrict, !eurestrict`)
* Instant Restart (`!ir`)
* Silent Restart (`!sr`)
* Allow Donors to change their own name in-game (`!c`)
* Change Username for Admins (`!changeusername`)
* Request a map to be ranked from in-game (`!request`)
* Modifed editMap, allows BATS to rank a map from in-game (`!map`)
* Announce to #announce (`!announce`)


This is Atoka's bancho server. It handles:
- Client login
- Online users listing and statuses
- Public and private chat
- Spectator
- Multiplayer
- Fokabot

## Requirements
- Python 3.5
- Cython
- C compiler
- MySQLdb (`mysqlclient`)
- Tornado
- Bcrypt
- Raven

## How to set up pep.py
First of all, initialize and update the submodules
```
$ git submodule init && git submodule update
```
afterwards, install the required dependencies with pip
```
$ pip install -r requirements.txt
```
then, compile all `*.pyx` files to `*.so` or `*.dll` files using `setup.py` (distutils file)
```
$ python3 setup.py build_ext --inplace
```
finally, run pep.py once to create the default config file and edit it
```
$ python3 pep.py
...
$ nano config.ini
```
you can run pep.py by typing
```
$ python3 pep.py
```

## License
All code in this repository is licensed under the GNU AGPL 3 License.  
See the "LICENSE" file for more information  
This project contains code taken by reference from [miniircd](https://github.com/jrosdahl/miniircd) by Joel Rosdahl.
