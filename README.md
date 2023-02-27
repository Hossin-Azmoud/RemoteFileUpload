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
	$ python main.py -s (Listen in port 4000)
	$ python main.py -c <host> <fileName to send to server instance>
```