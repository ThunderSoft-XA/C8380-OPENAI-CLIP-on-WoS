## 1. Overview
This document details how to set up and run the demo environment, as well as how to use the demo program.

## 2. Installing Python and Configuring the Python Environment
Download and install Python Release Python 3.8.10, and configure an independent Python environment using the following commands:
```powershell
mkdir -p C:\Users\HCKTest\source\venvs
cd C:\Users\HCKTest\source\venvs
C:\Users\HCKTest\AppData\Local\Programs\Python\Python38\python.exe -m venv qai_3.8.10
& "C:\Users\HCKTest\source\venvs\qai_3.8.10\Scripts\Activate.ps1"
python.exe -m pip install --upgrade pip
```

## 3. Installing Python Software Packages Required by the Demo
To run the demo, you need to install the following software packages: numpy, torch, diffusers, accelerate, opencv, transformers, and torchvision. Use the following commands to install them:
```powershell
pip install wheel setuptools pybind11
pip install numpy torch diffusers accelerate opencv-python transformers torchvision
```
​
## 4. Installing the QNN SDK (AI Engine Direct)
Download and install QNN SDK v2.23.0.240531, and configure the environment using the following commands:
```powershell
& "C:\Qualcomm\AIStack\QAIRT\2.23.0.240531\bin\envsetup.ps1"
```
Manually copy the library files libqnnhtpv73.cat and libQnnHtpV73Skel.so from the directory C:\Qualcomm\AIStack\QAIRT\2.23.0.240531\lib\hexagon-v73\unsigned to C:\Qualcomm\AIStack\QAIRT\2.23.0.240531\lib\arm64x-windows-msvc. For convenience, you can execute the command notepad.exe $PROFILE to open the PowerShell configuration document and add the following two lines at the end:
```powershell
& "C:\Users\HCKTest\source\venvs\qai_3.8.10\Scripts\Activate.ps1"
& "C:\Qualcomm\AIStack\QAIRT\2.23.0.240531\bin\envsetup.ps1"
```
​
## 5. Downloading the Source Code and Compiling and Installing qai_appbuilder
Download the qai_appbuilder source code, compile it to generate the Python installation package, and install it using the following commands:
```powershell
mkdir -p C:\Users\HCKTest\source\repos
cd C:\Users\HCKTest\source\repos
git clone https://github.com/quic/ai-engine-direct-helper.git
cd C:\Users\HCKTest\source\repos\ai-engine-direct-helper\pybind
Remove-Item -Force pybind11
git clone https://github.com/pybind/pybind11.git
cd C:\Users\HCKTest\source\repos\ai-engine-direct-helper
python .\setup.py bdist_wheel
pip install dist\qai_appbuilder-2.24.0-cp38-cp38-qnn-2.23-win_amd64.whl
```
​
## 6. Running the Demo Program to Repair the Specified Image
The demo program source code aotgan.py defines one global variables: QNN_SDK_PATH. QNN_SDK_PATH points to the actual installation path of the QNN SDK. You can modify them as needed. You should download the large model files from the corresponding release and save them into the folder named models before run the demo program. To run the demo program, use the following command:
```powershell
cd C:\Users\HCKTest\source\repos\QCS8380-OPENAI-CLIP-on-WoS
python ./clip_search_images_qt.py
```
​
The demo program source code clip_search_images_ui.py designs a UI interface for receiving user inputs and displaying processing results. Before searching, you need to specify the path of the images, and then wait for the scan to complete. After the scan is complete, you can enter a text description to search.