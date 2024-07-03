# AG_Oertel_software_emilio

## Description
This GitHub repository contains a collection of **Python tools** designed for the Oertel lab to streamline various processing steps for OCT, OCTA and pupillometry analysis. **Each tool is encapsulated within its own folder** and serves a specific purpose in the image analysis pipeline, offering functionalities tailored to different stages of the process. Additionally, there's a folder named **"Common_utils"** which contains scripts and general files utilized by the other tools.

A brief **overview of each tool** can be found **within each folder in the README.md file**


## Installation Prerequisites   
Before you proceed with using the tools in this repository, ensure that you have completed the following steps on your computer:

1. **Donwload this Repository**
You can download this repository as a ZIP file by clicking on the green "<> Code" button at the top right of the repository page. Once downloaded, extract the folders from the ZIP file to your desired location.

2. **Install Python 3+**
If you haven't already installed Python 3, you can download and install it from [here](https://www.python.org/downloads/).

3. **Install Python 3 Package Dependencies**
Navigate to the directory containing this repository's files (where `requirements.txt` is located) using the command prompt or Terminal. Then, install the required dependencies by running the following command: `pip install -r requirements.txt`


## How to use It
To utilize each tool within this repository, follow these steps:

1. **Navigate to the folder** corresponding to the **tool you want to use**. If you're not familiar with how to use the command prompt or Terminal, you can refer to the tutorial linked here: [Command Prompt or Terminal Window](https://github.com/emilio-lovarela/AG_Oertel_software_emilio/tree/main/Common_utils/CMD_tutorial)
2. Execute the `main.py` file within that folder using **Python** to open the **tool's interface** -> `python main.py`


### Main buttons and functionalities of the interface
Although the basic interface might vary across different tools depending on their utility, the general principles and functions remain the same. Below is the skeleton of the base interface for all tools, along with a brief explanation of the main buttons and their functionalities:

<table border="0">
 <tr>
    <td><b style="font-size:30px">Buttons</b></td>
    <td><b style="font-size:30px">Interface</b></td>
 </tr>
 <tr>
    <td>
       
1. **Select Folder**: This button allows you to select a folder from your system. Clicking on it opens a file dialog where you can navigate to the desired folder and select it.
       
2. **Run**: Clicking on this button executes the main functionality associated with the tool. It initiates the processing of the selected folder or files within it, based on the tool's purpose.

3. **Recursive Search**: This checkbox enables or disables recursive search functionality. When checked, the tool will search for files recursively within all subdirectories of the selected folder. If unchecked, it will only process files within the selected folder itself.

   </td>
   <td>
      <p align="center"> <img src="https://github.com/emilio-lovarela/AG_Oertel_software_emilio/blob/main/Common_utils/Tutorial_Images/interfaz.PNG?raw=true" alt="screenshot" width="700"></p>
   </td>
</tr>
</table>

These buttons and checkboxes provide users with the necessary controls to interact with the tool and perform the desired tasks.
