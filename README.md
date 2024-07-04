## Description
This GitHub repository contains a collection of **Python tools** designed for the Oertel lab to streamline various processing steps for OCT, OCTA and pupillometry analysis. **Each tool is encapsulated within its own folder** and serves a specific purpose in the image analysis pipeline, offering functionalities tailored to different stages of the process. Additionally, there's a folder named **"Common_utils"** which contains scripts and general files utilized by the other tools.

A **brief overview of each tool** can be found in the **README.md file located in each tool's folder**. For example `Pupillometry_CSV_Format_Adapter` tool description can be localized -> [Pupillometry_CSV_Format_Adapter_README.md](https://github.com/emilio-lovarela/AG_Oertel_software_emilio/tree/main/Pupillometry_CSV_Format_Adapter)


## Installation Prerequisites   
Before you proceed with using the tools in this repository, ensure that you have completed the following steps on your computer:

1. **Donwload this Repository:**
You can download this repository as a ZIP file by clicking on the green "<> Code" button at the top right of the repository page. Once downloaded, extract the folders from the ZIP file to your desired location.

2. **Install Python 3+:**
If you haven't already installed Python 3, you can download and install it from [here](https://www.python.org/downloads/).

3. **Install Python 3 Package Dependencies:**
   1. Navigate to the **folder containing this repository**, which has the `requirements.txt` file, using the command prompt or Terminal. If you're not familiar with how to use the command prompt, you can check this brief tutorial: [Command Prompt or Terminal Window](https://github.com/emilio-lovarela/AG_Oertel_software_emilio/tree/main/Common_utils/CMD_tutorial).<br />
   **Note:** You can open a terminal directly in the desired folder in the following ways:
      - **Windows:** Go to your desired folder location and type `cmd` on the address bar
      - **Linux (Ubuntu):** Once in the folder location, right-click on an empty space in the file manager and then select `Open Terminal`
   2. Then, install the required dependencies by running the following command: `pip install -r requirements.txt`


## How to use It
To utilize each tool within this repository, follow these steps:

<table border="0">
 <tr>
    <td><b style="font-size:30px">Steps</b></td>
    <td><b style="font-size:30px">Example -> Pupillometry_CSV_Format_Adapter</b></td>
 </tr>
 <tr>
    <td>
       
1. **Open the terminal** or CMD. If you're not familiar with how to use the command prompt or Terminal, you can check this brief tutorial: [Command Prompt or Terminal Window](https://github.com/emilio-lovarela/AG_Oertel_software_emilio/tree/main/Common_utils/CMD_tutorial)

2. **Navigate to the folder** corresponding to the **tool you want to use**. To navigate to a specific path type `cd` **followed by the path** you want to go to: <br />
`cd Documents/AG_Oertel_software_emilio/Pupillometry_CSV_Format_Adapter`
      
3. **Execute** the `main.py` file within that folder using **Python** to open the **tool's interface** -> `python main.py`

   </td>
   <td>   
      <p align="center"> <img src="https://github.com/emilio-lovarela/AG_Oertel_software_emilio/blob/main/Common_utils/Tutorial_Images/cmd.png?raw=true" alt="screenshot" width="2600"></p>
   </td>
</tr>
</table>



#### Main buttons and functionalities of the interface
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
