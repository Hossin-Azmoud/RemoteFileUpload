exit(0)
# This File is not meant to be ran, just a script in which I can try things out!
# ---------------------- in client.----------------------------------
# solution One

{
    'size': 1024 + (),
    'amount': 1..15
}


with open(file) as f:
    HEADER = {}    
    size(b64encode(s)) => int
    byteObject = f.read(1024) #1KB
    size = b64encode(byteObject)
    HEADER['SIZE'] = size
    chunksAmount = os.stat(file).st_size // 1024












size = b64encode(fp.read(CHUNKSIZE))
rem = (File_Size % CHUNKSIZE)
amount = (File_Size // CHUNKSIZE) + (1 if rem > 0 else 0) 

m = ClientMessage(CHUNK, {
    'amount': amount,
    'size': size
})

bytes = Serializer.SerializeClientMessage(m)
send(bytes)

for i in chunks:
    if sent < amount:
        sendChunkNormally(i)
        continue
    if ...:
        sendRemainingChunkWithPadding(i, (size - rem) * ' ') # Second arg is the padding.

# --------------------------------------------------------------------
# ---------------------- in server.----------------------------------

m = Serializer.DeserializeClientMessage(bytes)
m.UnPackMessageData()

recv = 0
while m.amount > 0:
    buff += recv(m.size).strip()
    m.amount -= 1

ok()

# --------------------------------------------------------------------

# ---------------------- in client.----------------------------------
# solution Two


# --------------------------------------------------------------------
# ---------------------- in server.----------------------------------


# --------------------------------------------------------------------
