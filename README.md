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

```
	$ python main.py -s --host <host> -p <port> 
	$ python main.py -c --host <host> -p <port> -f <filepath> --chunked <feature still not quiet usefull, since it is slow>
```

## Issues
- No progress bar in the stable file sending protocol
- Problem in sending chunked data, because it sends incorrect things at a wrong order. (size; actual chunk)
- configuration mechanism still bad.
