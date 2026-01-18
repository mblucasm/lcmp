<h1>
    <img src="assets/logo.svg" alt="lcmp logo" height="80" style="vertical-align: middle; margin-right: 8px;">
    lcmp
</h1>

#### Instagram followers & following list comparison tool

`lcmp` is a small utility to compare **Instagram followers & following** lists from one or two data exports

You can easily see:

* Who you follow but doesn’t follow you back
* Who follows you but you don’t follow back
* Mutual followers
* Who started or stopped following between two dates
* Overlap and differences between two different accounts

Everything is handled through a simple **drag & drop** interface  
Clicking on a username in the results list opens that user’s Instagram profile in your **default browser**

## Table of Contents

- [Using the App](#using-the-app)
    - [1. Download the program](#1-download-the-program)
    - [2. Download your Instagram information](#2-download-your-instagram-information)
    - [3. Drag & drop Instagram folders](#3-drag--drop-instagram-folders)
    - [4. Select one folder or two folders](#4-select-one-folder-or-two-folders)
    - [5. Open profiles in your browser](#5-open-profiles-in-your-browser)
- [Privacy and Data Safety](#privacy-and-data-safety)
- [Important note about Instagram export accuracy](#important-note-about-instagram-export-accuracy)
- [License](#license)

## Using the App

### 1. Download the program

To download the program, go to [Releases](https://github.com/mblucasm/lcmp/releases) and download the `.zip` file for your device. As of right now:

* lcmp_v1.0.0_Windows_x64.zip

### 2. Download your Instagram information

On Instagram, go to:

> **Settings → Accounts Center → Your information and permissions → Export your information → Create export → Export to device**

Then:

1. Select **Customize information**
2. Clear **ALL** checkboxes from **ALL** sections
3. Only check the **Followers and Following** box inside the **Connections** section

*`lcmp` will still work if you keep other boxes checked, but it will ignore the extra data. Leaving them enabled only wastes disk space and makes the export larger and slower to download*

Make sure the following options are set:

* **Date range**: **All time**
* **Format**: **HTML** (default)
* **Media quality**: **Lower quality**

  * *`lcmp` doesn’t use any media, so higher quality only increases disk usage and export time for no benefit*

Once the export is ready, download it, unzip it, and you’re ready to drag the folder into `lcmp`

### 3. Drag & drop Instagram folders

Run `lcmp`. At first, you’ll see a **“Drag & Drop”** message  
Drag & drop your Instagram export folder (the extracted folder, not the .zip file) into the window

The folder name **must follow this pattern** (this is the default Instagram export format):

* `instagram-USERNAME-YYYY-MM-DD-UUID`

If valid, it will appear in the left list as:

* `USERNAME YYYY-MM-DD`

You may drop multiple folders

### 4. Select one folder or two folders

Select one or two folders from the left panel:

* With **one folder selected**, you can see who you follow but doesn’t follow you back, who follows you but you don’t follow back, and mutual followers
* With **two folders selected**, you can see who followed or unfollowed you, who you followed or unfollowed, and who remained the same between the two dates

### 5. Open profiles in your browser

When results are shown (the list of usernames in the main panel), you can:

* **Click any username** in the results list
* `lcmp` will open your **default web browser** at that profile

This makes it easy to quickly inspect specific accounts directly on Instagram

## Privacy and Data Safety

`lcmp` works **entirely offline**  
It depends on a trusted Python library named `pygame`  
Absolutely nothing is uploaded, sent, or shared anywhere. All data is read locally

That said:

> As with anything on the internet, **never trust blindly**  
> Don’t take my word for it, or anyone else’s  
> If you care about your privacy, always inspect the tools you use, check the source code, and make sure they do what they claim

*I know it does, since I wrote the program myself, but verifying things yourself is always a good idea*

### Important note about Instagram export accuracy

For some reason, the data downloaded from Instagram is often inaccurate, and users may appear in lists even though they shouldn’t

Always double-check `lcmp`’s output  
If you see accounts that don’t make sense, this is caused by Instagram’s export errors, not by the program itself

## License

Copyright © 2025 Lucas Martín  
Distributed under the MIT License. See the [LICENSE](./LICENSE) file for full details

---

That’s everything  
Lucas M.
