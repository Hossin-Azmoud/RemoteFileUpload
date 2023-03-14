# RFU - Remote file upload.

## Description

A Socket based file sharing program. if you know the password you can dump data to your server.

## Quick start

```bash	
    
    $ git clone https://github.com/Moody0101-X/RemoteFileUpload	
    $ cd RemoteFileUpload
    $ python -m venv venv	
    $ venv/Scripts/activate	 
    $ cd src
```

- Now after activating the env, you can execute the script as server using -s or as a client by -c but if it is a client instance u need to specify the host.

```bash
    $ python main.py -s (run as a server)
    $ python main.py -c -f <FILE_PATH_TO_SEND>(run as client)
```

### the defaults:

Port = 4000 (set with -p <NEWPORT>)
Host = yourHost (Localhost if not connected to any network, set with --host <IPHOST>)

### flags:
- `-s` run as server and listen for incoming connections.
- `-c`	run as client to connect to the server.
- `-p` Port

- `--host`:
    if you are using `-s` then this specify your host that you will be listening from. the default is localhost.
    if you are using `-c` then it is the host that is listening for files/commands in your other machine.

- `--progress` to log the progress of transmission.
- `--time` to log the time (How much it took to send/recv.)
- `-f` specify the file that you want to send.


#TODO:
[] Send Multiple files using wildcard.
[] Send directory using archives.
[] Add shell to the serving machine, to execute commands freely (I will just. use python to make a bootstrap around the command line.)












