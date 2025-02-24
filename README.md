# epidemicTrack

This is an implementation for a Data Protection Technologies course assignment. The code is an extention based on **Peer-to-Peer Contact Tracing: Development of a Privacy-Preserving Smartphone App** with some additional security features.

## How to run the code

Firstly, run the following command to start a mysql docker container.

```bash
docker compose up -d # or docker-compose for some older versions, I think.
```

Then install required packages, initalize the database and start the server.

```bash
pip install -r requirements.txt
python init_db.py
python server.py
```

This will start a server in `127.0.0.1:5000`. 

Now start the client, which has few basic tests for the code.

```bash
python client.py
```

## What I did

### 1. Re-implemented the method from the paper



-  Anonymous and Decentralized Storage: Servers do not record users' personal information.
-  
- Blurred Time Representation: Each time step representing 30 minutes to prevent precise tracking.
- 
- Some Core Functions
  - Creation of new checkpoints
  - Check-in at a checkpoint
  - Local storage of visited places
  - Reporting an infection
  - Checking if a user has ever visited any risky location



### 2. Additional features that are not mentioned in the paper

**Some small security features that are not mentioned in the paper**

1. **Using random number to generate checkpoint ID.** It is independent of time and location (the authors only mentioned that they did not store GPS-related data). Therefore, it ensures minimal data retention on the server, as irrelevant information such as time and location is discarded—we only care about an anonymous checkpoint ID.

2. **Setting a rate limit when "Check Am I Safe".** This prevents attackers from forging their visited places and timestamps, and from using brute-force attempts to infer risky locations stored on the server.

3. **Removing "from home" and "to home" histories** when reporting or checking is the user safe.

**My main improvement to the code -- – Using Private Set Intersection (PSI)"**

While the server does not want to publicly disclose the list of high-risk locations, users may also be reluctant to expose their travel history to the server each time they check for infection risk. (This is different from the case where infected users *voluntarily* report their travel history to the server through a trusted institution.) 

**Private Set Intersection (PSI)** is a cryptographic technique that enables privacy-preserving risk assessment, ensuring that users and servers can exchange data safely without revealing their data to each other.

Doing this, the server and client each have a private key. (In my code, I just arbitrarily used `123456` for the server and `654321` for the client.) When checking if there is an intersection between **the user's visited locations** and **the server's high-risk locations**, the server first encrypts `(checkpoint, time)` using its private key. (This happens when an infected user reports their travel history. The encrypted data is saved to the database to avoid redundant computation.) 

The user then encrypts their **own travel history**. When the user requests the server to check whether they have been exposed, they upload their encrypted locations to the server. The server then **performs a second encryption** on the user's encrypted locations and returns the data and server's encrypted risk locations data to the user. The user then re-encryptsthe server’s encrypted data, and at this point, the user can compare the final encrypted values to determine if they have visited a high-risk location without revealing any sensitive location data to the server.

Mathematically:

If we use $E_s$  to represent encryption with the server's private key and $E_u$ to represent encryption with the user's private key.


- **Server Encryption**: $server\_data = [E_s(risky\_checkpoint\_id \| time), E_s(...), ...]$ 

  
- **User Encryption**: $client\_data = [E_u(visited\_checkpoint\_id \| time), E_u(...), ...]$ 

- **Server Re-encryption** :  $E_s ( client\_data) = [E_s(E_u(checkpoint, time)), ...]$
  
- **User Re-encryption** :  $E_u ( server\_data) = [E_u(E_s(checkpoint, time)), ...]$
  
I used `SHA-256` to encrypt data. Since this encryption is commutative, meaning that encrypting first with one key and then with another yields the same result regardless of the order. Thus user can compare doubly encrpted data from server and from local to determine if there is a match.

The core functionality of PSI has been tested in the `test_psi2` file.

There are also some demo code in the  `__main__` of `client.py`. Client 1 visited some place and report to be infected. Client 2 visited a place at the same time with Client 1 and then visited a place that Client 1 never been to. Client 3 visited that place. Then Client 2 should be in high risk and Client 3 should be in meduim risk. (align with the design from the paper)