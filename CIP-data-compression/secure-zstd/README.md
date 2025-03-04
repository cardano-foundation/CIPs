# Secure Integration of ZStandard Library using Isolation via IPC

This directory provides a minimal example implementation of a secure integration of the **ZStandard** library using the **Isolation via IPC** technique, extended with Linux's ```seccomp``` feature. This imlementation supports a [Cardano Improvement Proposal for Block Data Compression](https://github.com/sierkov/data-compression-CIP), demonstrating the simplicity and advantages of this approach.

Currently, it has only been tested on **Ubuntu Linux 24.04 LTS**.

## Build Instructions

Install the necessary dependencies:
```sh
sudo apt update
sudo apt install -y build-essential cmake zstd libseccomp-dev libzstd-dev
```

Build the code:
```sh
cmake -B build-gcc-rel
cmake --build build-gcc-rel
```

## Test Instructions

### Standard Functionality Test

Launch the caller and worker processes to continuously decompress all files in a user-supplied directory. This helps monitor stability, memory usage, and other performance characteristics. Replace ```<data-directory>``` with the path to a directory containing **ZStandard-compressed files** (can be with the ```zstd``` command line utility):
```
./build-gcc-rel/caller ./build-gcc-rel/worker ./build-gcc-rel/worker.sock <zstd-data-directory>
```

### Malicious Input Test
To test behavior on **non-ZStandard data** (e.g., potential attack scenarios), use a directory containing unrelated files, such as ```/usr/bin```:
```
./build-gcc-rel/caller ./build-gcc-rel/worker ./build-gcc-rel/worker.sock <non-zstd-data-directory>
```

## How It Works
1. The managing (caller) process creates a Unix socket.
2. A new worker process is started, which communicates exclusively with the parent process through this socket.
3. The worker process pre-initializes the ZStandard library by running a compressor and decompressor on a statically defined dataset. This eliminates the need for further dynamic memory allocations.
4. The worker process closes all open file descriptors except for the Unix socket.
5. The worker process applies a ```seccomp``` profile to restrict system calls to only ```read```, ```write```, and ```exit```.
6. The worker process is then ready to handle compression and decompression requests from the caller process.

An attacker can still send malicious data to the Cardano Node. However, in such cases, the worker process will immediately crash, and the caller process will receive a corresponding notification. 

Given the high quality of the ZStandard library, such a crash is likely indicative of an attack attempt, warranting an appropriate response:
- **Block the malicious peer** to prevent further communication and mitigate potential Denial-of-Service attacks.
- **Restart the worker process** to continue handling requests from a safe state.

The provided implementation is compact—approximately **200 lines of code** for [the worker process](./lib/seczstd/worker.c) and **100 lines of code** for [the caller](./lib/seczstd/caller.c). This allows for **easy security audits** compared to auditing the full ZStandard decompression library, which consists of about **15,000** lines of code.

Furthermore, the **Isolation via IPC** approach, extended with ```seccomp```, can be similarly applied to other untrusted data-processing tasks, such as newer but less-tested cryptographic libraries (e.g., potential Plutus builtins) and other use cases.