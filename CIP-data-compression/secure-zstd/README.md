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
