<h1>
  <img src="assets/logo.svg" alt="lcmp logo" height="80" style="vertical-align: middle; margin-right: 8px;">
  LCMP
</h1>

#### Instagram followers / following list comparison tool

`lcmp` is a program designed to compare **Instagram followers / following** lists between one or two data exports

You can see:

- Who you follow but doesn't follow you back
- Who follows you but you don't follow back
- Mutual followers
- Who started / stopped following between two dates
- Overlap and differences between two different accounts

All of this is done with a simple **drag & drop** interface  
Additionally, when you click on a username in the results list, `lcmp` opens your **default browser** with that user's Instagram profile

## Table of Contents

1. [What lcmp Does](#what-lcmp-does)
2. [Privacy and Data Safety](#privacy-and-data-safety)
3. [Requirements](#requirements)
4. [Quick Start](#quick-start)
5. [Using the App](#using-the-app)  
    - [0. Download your Instagram's information](#0-download-your-instagrams-information)
    - [1. Drag & drop Instagram folders](#1-drag--drop-instagram-folders)  
    - [2.a Select one folder](#2a-select-one-folder)  
    - [2.b Select two folders](#2b-select-two-folders)  
    - [3. Switch method](#3-switch-method)  
    - [4. Switch followers / following](#4-switch-followers--following)  
    - [5. Open profile in browser](#5-open-profile-in-browser)
6. [Expected Instagram Export Format](#expected-instagram-export-format)
7. [License](#license)

## What lcmp Does

`lcmp` reads the **HTML export** from Instagram's "Download Your Information" feature and compares the user lists it finds there

You use it to:

- Compare **followers vs following** for a single account  
- Compare **two exports of the same account** (different dates) to see:
  - who started following you
  - who stopped following you
  - who kept following you
- Compare **two different accounts** to see:
  - who follows A but not B
  - who follows B but not A
  - who follows both

Everything is shown as a simple numbered list of usernames

## Privacy and Data Safety

`lcmp` works **100% offline**  
Absolutely nothing is uploaded, sent, or shared anywhere. Your Instagram export stays on **your machine**, is read locally, shown on screen, and that's the end of the story

I know this because **I wrote the program**, and there is literally no code inside it capable of sending anything to anyone, not even by accident  
It couldn't leak your data even if it tried (and it doesn't try)

That said:

>  As with anything on the internet, **never trust blindly**  
>  Don't take my word for it, or anyone's  
>  If you care about your privacy, always inspect the tools you use, check the source code, and make sure it does what it claims

So `lcmp` is safe, private, and offline  
As I said, **I know it is** but checking things by yourself is always a good idea

## Requirements

- **Python 3**

You don't need to install anything else manually  
When you run `launcher.py` for the first time, it will:

- create a local virtual environment (`.venv`)
- install the only required package (`pygame`) inside it  

All of this happens automatically and only once

## Quick Start

1. [Download and Install Python 3](https://www.python.org/downloads/)
2. Download this project (Git or ZIP and extract it)
3. Run `launcher.py` (only `launcher.py` , `lcmp.py` is **NOT** supposed to be run directly)

For example, from a terminal:

```
python launcher.py
```

(Or use whatever double-click / launcher setup you prefer on your system)

## Using the App

### 0. Download your Instagram's information
On Instagram, go to:

> **Settings → Accounts Center → Your information and permissions → Export your information → Create export → Export to device**

Then:
1. Select **Customize information**  
2. Clear **ALL** checkboxes from **ALL** sections  
3. Only check the **Followers and Following** box inside the **Connections** section  

`lcmp` will still work if you keep other boxes checked, but it will ignore that extra data. Leaving them enabled just:

- wastes disk space  
- makes the export larger and slower to download  

Now make sure:

- **Date range** is set to **All time**  
- **Format** is set to **HTML** (default)  
- **Media quality** is set to **Lower quality**  
  - `lcmp` doesn't use any media, so a higher quality only means more disk space and slower export for no benefit

Once the export is ready, download it, unzip it, and you're ready to drag the folders into `lcmp`

### 1. Drag & drop Instagram folders

At first you'll see a **"Drag & Drop"** message  
Drag your Instagram export folder (the extracted folder, not the ZIP) into the window

The folder name **must follow this pattern** (this is the pattern folders will naturally follow):

- `instagram-USERNAME-YYYY-MM-DD-UUID`

If valid, it appears on the left list as:

- `USERNAME YYYY-MM-DD`

You may drop multiple folders

### 2.a Select one folder

Click one of the folders that appeared within the `lcmp` window

This shows comparisons between **followers** and **following** within that export:

- People you follow but don't follow you back  
- People who follow you but you don't follow them  
- Mutual follows  

You'll also see the total count  
You can use the mouse wheel to scroll both the folder list and the users list

### 2.b Select two folders

Select two entries (max 2)

**If both belong to the same user (different dates):**

- See who started following  
- Who stopped following  
- Who kept following  

**If they belong to different users:**

- People who follow A but not B  
- People who follow B but not A  
- People who follow both  

The top of the results panel always explains what you're currently viewing in plain language

### 3. Switch method

A red button lets you switch between the three comparison methods:

- **XA**
- **AX**
- **AA**

The selected method is always visible in the **"Method used"** box and reflected in the explanatory text above the results list

### 4. Switch followers / following

When two folders are selected, a blue button appears:

- **"Click to compare following instead"**  
  or  
- **"Click to compare followers instead"**

Clicking this button toggles the mode between **followers** and **following** comparisons  
The current mode ("Followers" or "Following") is shown in the **"Comparing"** box

### 5. Open profile in browser

When results are shown (the list of usernames in the main panel), you can:

- **Click any username** in the results list  
- `lcmp` will open your **default web browser** at:

  - `https://www.instagram.com/USERNAME/`

This makes it easy to quickly inspect specific accounts directly on Instagram

## Expected Instagram Export Format

Inside each folder, `lcmp` expects this structure:

```
connections/
  followers_and_following/
    followers_1.html
    following.html
```

These HTML files contain links like:

```html
<a href="https://www.instagram.com/USERNAME/">
```

`lcmp` extracts the USERNAME from those links and uses them in the comparisons

### ⚠️ Important note about Instagram export accuracy

For some reason, the data you download from Instagram is often inaccurate, and users may appear in the lists even though they shouldn't  

Always double-check `lcmp`'s output: if you see accounts that don't make sense, this is caused by Instagram's export errors, not by the program itself

### ⚠️ Important note about big accounts and multiple followers_*.html files

While writing this README I discovered that, for **large Instagram accounts**, the followers export may include **multiple files**:

```
followers_1.html
followers_2.html
followers_3.html
```

**lcmp currently uses only `followers_1.html`**, because I didn't know Instagram split the data this way until now and the program is already finished

I have **no intention of changing this behavior for now**, although it might be improved in the future

If your account has many followers, be aware that results will not include users found in `followers_2.html`, `followers_3.html`, etc

If the folder name is invalid, an error message appears in the terminal, and the folder is not added to the list  
If the folder structure is invalid, `lcmp` will safely crash when trying to open the required files

## License

Copyright © 2025 Lucas Martín  
Distributed under the MIT License. See the [LICENSE](./LICENSE) file for full details

--- 

Finally, I'd like to give ChatGPT credit for writing 99% of this README  

That's everything  
Lucas M.
