# lcmp - List Comparison Tool

## Table of Contents

1. [Description](#description)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [License](#license)
8. [For Beginners](#for-beginners)
9. [Examples](#examples)

## Description

**lcmp** is a lightweight tool designed to compare two lists and determine their differences. It allows you to find elements that are common to both lists, those that appear only in the first, and those that appear only in the second. This makes it useful for various applications, such as dataset analysis, user list management, or general list comparisons

Additionally, **lcmp** includes support for processing Instagram data, allowing users to analyze their followers and following lists. It can extract relevant data from downloaded Instagram files or directly from HTML\<div> elements

## Features

- Compare two lists and identify elements that:
  - Appear in both lists
  - Exist in the first list but not in the second
  - Exist in the second list but not in the first
- Process raw text files with one item per line
- Handle Instagram follower/following lists from downloaded data
- Extract user lists from `<div>` elements copied from Instagram’s web interface
- Display results in a structured format for easy analysis

## Requirements

- A **C compiler** (such as GCC, Clang, etc.). *(Tested with ****GCC 13.2.0****. Older versions may not work properly.)*
- `stb_ds.h` (already included in the project, no need to install separately)

This project uses [`stb_ds.h`](https://github.com/nothings/stb) by Sean Barrett, a public domain / MIT-licensed single-header library for dynamic arrays and hash maps in C

## Installation

To install and compile **lcmp**, follow these steps:

```sh
git clone https://github.com/mblucasm/lcmp.git
cd lcmp
gcc -O2 -o lcmp src/main.c src/arg.c src/buf.c src/method.c src/error.c src/slice.c
```

If you're new to programming or using a terminal, **don't worry!** I have a dedicated section: [For Beginners](#for-beginners). There, you'll find a detailed step-by-step guide explaining everything, from downloading the project to running it, in a way that's easy to follow—even if you've never used a terminal before

## Usage

To compare two lists, run:

```sh
./lcmp list1 list2
```

Where `list1` and `list2` contain the lists you want to compare. The program will output the differences between the two lists

### Instagram Data Processing

If you want to analyze your Instagram followers and following, you can specify the **Instagram data folder** directly:

```sh
./lcmp --instagram-folder=<path/to/folder>
```

Alternatively, if you have copied the `<div>` elements containing followers or following from the web interface, you can use those as input files

To get more details about the program's usage, run:
```sh
./lcmp --help
```

## License

Copyright © 2025 Lucas Martín  
Distributed under the MIT License. See the [LICENSE](./LICENSE) file for full details

## For Beginners

If you've never used a terminal or compiled a program before, this section will guide you step by step

### 1. **Opening the Terminal**

To run commands, you'll need to open the terminal:

- **Windows:** Open **PowerShell** or **CMD (Command Prompt)**
- **Mac:** Open **Terminal** from your applications or search bar

### 2. **Downloading the Project**

There are two ways to get lcmp:

- **Option 1: Using Git** (Recommended if you have Git installed)

  ```sh
  git clone https://github.com/mblucasm/lcmp.git
  ```

  This will create a folder named `lcmp` in your current directory

- **Option 2: Downloading as a ZIP file**

  - Visit the [GitHub repository](https://github.com/mblucasm/lcmp)
  - Click the green **"Code"** button and select **Download ZIP**
  - Extract the ZIP file into a folder

### 3. **Checking if You Already Have a Compiler Installed**

To check if you already have a compiler installed, open the terminal and type:

```sh
<compiler> --version
```

Replace `<compiler>` with `gcc`, `clang`, or another compiler name. If a version number appears, you already have a compiler installed. If not, follow the next step to install one

### 4. **Installing a Compiler**

A C compiler is required to compile the program. If you don't have one, follow these steps:

- **Windows:**

  - I personally recommend w64devkit because it's very easy to install and works out of the box
  - Download **w64devkit** from [this link](https://github.com/skeeto/w64devkit) → **Go to Releases** and download the `.exe` that suits your device (**x64** for 64-bit systems, **x86** for 32-bit systems)
  - Run the `.exe` file to extract w64devkit
  - w64devkit provides **gcc** and **cc** as compilers
  - To ensure the compiler is available in the terminal, [**add it to your system's PATH**](#41-adding-the-compiler-to-your-systems-path)

- **Mac:**

  - If `clang --version` didn't show a version, install Clang by running:
    ```sh
    xcode-select --install
    ```

#### 4.1 **Adding the Compiler to Your System's PATH**
The **PATH** is an environment variable that tells your operating system where to look for executable files. If a program is in a directory listed in the PATH, you can run it from any terminal window without specifying the full path

To add a program (e.g., `gcc` from w64devkit) to your PATH:

- **Windows:**
  1. Open **System Properties** (Win + R, type `sysdm.cpl`, press Enter)
  2. Go to the **Advanced** tab and click **Environment Variables**
  3. Under **System Variables**, find `Path` and click **Edit**
  4. Click **New** and add the path to the w64devkit `bin` folder
  5. Click **OK** and restart the terminal

### 5. **Navigating to the Project Folder**

Once you have the project downloaded and the compiler installed:

1. Open the terminal
2. Use the `cd` command to move into the project directory:
   ```sh
   cd <path/to/lcmp>
   ```
   
The `cd` command stands for "change directory". It is used to navigate to different folders in your file system. When you open the terminal, you start in your home directory. To go to another folder, you type `cd` followed by the path to the folder you want to go to

For example, if your project is in a folder named "lcmp" on your desktop, you would type `cd Desktop/lcmp`

### 6. **Compiling and Running the Program**

Now, compile the code into an executable program

For **GCC**:

```sh
gcc -O2 -o lcmp src/main.c src/arg.c src/buf.c src/method.c src/error.c src/slice.c
```

For **Clang (or other compilers)**, replace `gcc` with the name of your compiler:

```sh
<compiler> -O2 -o lcmp src/main.c src/arg.c src/buf.c src/method.c src/error.c src/slice.c
```

This will generate an executable file called `lcmp`, to see how to use it, read [Usage](#usage)

> That's it! You've successfully downloaded, compiled, and run the project. If you encounter any issues, there are many online tutorials and videos that explain how to set up and use compilers and terminals, so don't hesitate to check them out for more help

And that’s everything — enjoy using lcmp

Thanks for reading my beautifully written README  
(ChatGPT may or may not have had a hand in that)

Lucas M.