Miner code:
We ended up creating 3 running modes for the miner.

0. Normal mode: Each client starts with a given difficulty level that does not change. They mine normally. This is the default mode.
1. Average block age time mode: Each client has a target seconds value x and he tries to adjust his difficulty level so that blocks on the chain are spaced on average x seconds apart.
2. Equal blocks for clients mode: Each client will adjust his difficulty level so that he has as many blocks on the block chain as other clients.

Modes 1 and 2 are not meant to represent any real life scenario, just a fun way to play with the block chain and mining.

Implementation issue: When a client detects that he is out of sync with the block chain (he is working on a block with counter = n and he receives a block with counter = n + 2) the client will abandon his block chain and request a fresh copy of the block chain from some other client. This is of course not realistic since the block chain will grow to be huge, but it was a simplification we decided to have. It causes issues described below.

Known issues:
1. Difficulty levels were restricted to range 10-23. Above there is more than 30 min of waiting between blocks and below the speed is so great it creates a race condition where a client might neve receive a full block chain because he is constantly out of sync and while he fetches a new block chain from another client some other client has found too many blocks so that the newly fetched block chain is already outdated.
2. In mode 'Equal blocks for clients', since we are dumping the entire block chain and restoring it when a client is out of sync it can happen that a new client enters that needs to start fetching a big block chain from a client. While that happens a 3rd client can continue mining and by the time the new client gets the block chain it might already be too old so the new client is stuck in a loop of trying to fetch a block chain.

Graphs:
We did not fully implement the graphs requested but we DID create a single graph showing number of forks per min for 2 and 3 clients and the max fork length for each difficulty leve.
Here is the graph.

Commands to run the code:
Run the following commands from the folder '12-09' in source. They all assume 3 clients so just skip the last 1 or 2 lines if less clients are needed. Also note that the first command
starts a central register where the clients register themselves and receive a list of all clients in respnse.

# Normal mode
python Central_Register.py localhost 10550
python Working_Client.py ClientName1 localhost 10501 127.0.0.1 10550 18 # Last parameter is difficulty level
python Working_Client.py ClientName2 localhost 10502 127.0.0.1 10550 18
python Working_Client.py ClientName3 localhost 10503 127.0.0.1 10550 18

# Average block age time mode
python Central_Register.py localhost 10550
python Working_Client.py ClientName1 localhost 10501 127.0.0.1 10550 21 1 10 # Last 3 parameters are (starting_difficulty_lvl, mode, target_seconds_between_blocks)
python Working_Client.py ClientName2 localhost 10502 127.0.0.1 10550 21 1 10
python Working_Client.py ClientName3 localhost 10503 127.0.0.1 10550 21 1 10

# Equal blocks for clients mode
python Central_Register.py localhost 10550
python Working_Client.py ClientName1 localhost 10501 127.0.0.1 10550 21 2 # Last 2 parameters are (starting_difficulty_lvl, mode)
python Working_Client.py ClientName2 localhost 10502 127.0.0.1 10550 21 2
python Working_Client.py ClientName3 localhost 10503 127.0.0.1 10550 21 2