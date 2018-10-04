# Item Catalog

## About
This an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.
## TO Run
### requirements
* python 3 
* vagrant
* virtualbox

### Setup

### Install VirtualBox

VirtualBox is the software that actually runs the virtual machine
you can download it [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.
you can download it [here](https://www.vagrantup.com/downloads.html)

### Download the VM configuration

download and unzip this file:[FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)
you will end up with a new directory containing the VM files. Change to this directory in your terminal with cd. Inside, you will find another directory called vagrant. Change directory to the vagrant directory

### Start the virtual machine

From your terminal, inside the vagrant subdirectory, run the command
`vagrant up`
This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.
then run command
`vagrant ssh`
to log in to installed Linux VM.

### Download the data

Download and unzip this [file](https://github.com/kady153/Item-catalog)
The file inside is called `Item-catalog-master`. Put this file into the vagrant directory, which is shared with your virtual machine.
To load the data, `cd` into the vagrant directory and then `cd` into the `Item-catalog-master`


### Run the project 

run command `python catalog.py`
if it doesn't work try `python3 catalog.py`

Access the application by visiting [http://localhost:8080](http://localhost:8080).

## JSON Endpoints

`/items/JSON` - Displays all items with it's details.
`/item/<int:id>/JSON` -Displays one item by it's id .


## License

Copyright (c) [2018] [amr elkady]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

#### if you need help with something or have any suggestions don't hesitate to contact me at _amr.elkady153@gmail.com_
