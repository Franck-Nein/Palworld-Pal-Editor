# Palworld Pal Editor

<p align="center">
   <strong>English</strong> | <a href="/README.cn.md">简体中文</a>
</p>

<p align='center'>
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/KrisCris/Palworld-Pal-Editor?style=for-the-badge">&nbsp;&nbsp;
<img alt="Python" src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">&nbsp;&nbsp;
<img alt="Vue.js" src="https://img.shields.io/badge/Vue%20js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D">&nbsp;&nbsp;
</p>

## What is this?

### A Palworld Pal Editor developed by _connlost with ❤️

 ~~(yeah i am just too lazy to change github username)~~

***I've only tested this tool on my save, it may not work properly for you.***

***Always backup your save in case corruption happens. (The tool does backup files for you.)***

***LET ME KNOW IF ANY BUG PRESENTS.***

<img width="720" alt="Screenshot 2024-03-03 at 1 39 32 PM" src="https://github.com/KrisCris/Palworld-Pal-Editor/assets/38860226/b6259622-707a-4634-abea-c280dc7060d4">

---

- [Palworld Pal Editor](#palworld-pal-editor)
  - [What is this?](#what-is-this)
    - [A Palworld Pal Editor developed by \_connlost with ❤️](#a-palworld-pal-editor-developed-by-_connlost-with-️)
  - [What This Tool Can Do](#what-this-tool-can-do)
  - [Usage](#usage)
    - [1. Directly Run the Code](#1-directly-run-the-code)
    - [2. Use Pre-Built Binary](#2-use-pre-built-binary)
    - [3. Docker Container](#3-docker-container)
    - [Config File](#config-file)
      - [Note: Command Line Arguments Override Config](#note-command-line-arguments-override-config)
  - [Videos](#videos)
  - [Possible Roadmap? (NO ETA)](#possible-roadmap-no-eta)
  - [Contribution](#contribution)
  - [Sponsor](#sponsor)
  - [Thanks](#thanks)
  - [Why?](#why)

---

## What This Tool Can Do

- [x] Unlock Viewing Cage for Selected player (multiplayer server)
- [x] List Players and Pals
- [x] Inspect Pal Stats
- [x] Change Pal Gender
- [x] Toggle BOSS / Rare / Tower
- [x] Change Pal NickName
- [x] Add / Remove Pal Learned Attacks
- [x] Add / Remove Pal Equipped Attacks
- [x] Change Pal Level / Exp
- [x] Change Pal Condenser Level
- [x] Change Pal Soul Levels
- [x] Change CharacterID (Pal Species)
- [x] Change Pal Passive Skills
- [x] Change Pal IV
- [x] Calculate MaxHP
- [x] Remove Pal Sicks
- [x] Revive Pals
- [x] Edit Food Buff Timer (Only if the pal has food buff, and cli only)

## Usage

### 1. Directly Run the Code

1. Install Python 3.11+
2. Clone / Download the code
3. In the project directory, run `setup_and_run.ps1` for Windows Powershell, or `setup_and_run.sh` on Unix-like OS.
4. Optional Params:
   - `--password yourPW` Login Auth, you may want this if you are running web mode.
   - `--mode <gui | web | cli>` You can launch the program in either `gui`, `web` or `cli` mode.
   - `--path /path/to/save/folder` Provide the path to the folder containing Level.sav.
   - `--port 8080` Port for web mode.
   - `--lang <zh-CN | en>` Currently supporting `zh-CN` and `en`. (Currrently hardcoded UI texts are English only.)
   - `--i` for enable interactive mode, you may want to use with `cli` mode.
5. You can change language in `cli` mode by calling `lang($LANG_CODE)`.

### 2. Use Pre-Built Binary

1. Download from GitHub Release Page, may not be bundled with the latest code.
2. Also support command line arguments mentioned above.

### 3. Docker Container

1. Clone the code.
2. You may want to take a look at `./docker/docker-compose.yml`, and do some modification.
3. Run `./build_and_run_docker.sh`, or just manually run the commends if you are using Windows.

### Config File

#### Note: Command Line Arguments Override Config

Default:

```json
// config.json
{
    "i18n": "en",
    "mode": "web",
    "port": 58080,
    "debug": false,
    "path": null,
    "password": null,
    "JWT_SECRET_KEY": "X2Nvbm5sb3N0"
}
```

Custom:

```json
// config.json
{
    "i18n": "zh-CN",
    "mode": "gui",
    "port": 12345,
    "debug": false,
    "path": "/path/to/save/folder",
    "password": "YOUR PASSWORD",
    "JWT_SECRET_KEY": "YOUR SECRETS"
}
```

## Videos

- DOCKER

https://github.com/KrisCris/Palworld-Pal-Editor/assets/38860226/d7008b22-a2ff-4a2c-8903-32bab0922b32

- GUI / WEB
  

https://github.com/KrisCris/Palworld-Pal-Editor/assets/38860226/66f3cb1e-f1fc-401e-b8a1-987ac3e6b02d

- CLI: (old, but you get the idea)

https://github.com/KrisCris/Palworld-Pal-Editor/assets/38860226/02284dda-f1d7-40af-b12d-6b4ae11d4113

## Possible Roadmap? (NO ETA)

- [ ] Improve WebUI (I am bad at frontend dev, sorry! Contribution appreciated.)
- [ ] Real GUI, or maybe just a Terminal GUI using [Textual](https://textualize.io/).
- [ ] Add / Remove Pal (I mean, you can just catch a pal and set it to something else.)
- [ ] Move Pal to Different Slots? Change owner? IDK...
- [ ] More Stuff...

## Contribution

1. If you found a bug, or want a feature, please check [Issues](https://github.com/KrisCris/Palworld-Pal-Editor/issues) first.
2. If you want to contribute code, please checkout the latest branch.
3. Open a PR so everyone knows what you are going to contribute.

## Sponsor

THANK YOU ❤️, BUT THIS IS YET TBD.

## Thanks

- Fast game save loading code by [MagicBear](https://github.com/magicbear).
- Save conversion between GVAS and `.sav` by [palworld-save-tools](https://github.com/cheahjs/palworld-save-tools).
- Inspired by [MagicBear](https://github.com/magicbear)'s awesome [Palworld-Server-Toolkit](https://github.com/magicbear/palworld-server-toolkit).
- Inspired by [EternalWraith](https://github.com/EternalWraith)'s [PalEdit](https://github.com/EternalWraith/PalEdit).

## Why?

1. I made the tool for my friends who spent time playing this game with me ❤.
2. For practicing my 2-year untouched Python skills.
3. Fun, I am just too boring these days.
4. This guy had a really bad time fixing both his corrupted game save, and bugs of a similar tool.
