#pragma once
#ifndef SECURE_ZSTD_COMMON_H_
#define SECURE_ZSTD_COMMON_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

#define MAX_DATA_SIZE (128 << 20)
#define COMM_MAKE_HDR(cmd, payload_sz) ((uint32_t)(((cmd & 0xF) << 28) | (payload_sz & ((1 << 28) - 1))))
#define COMM_PARSE_HDR(hdr, cmd, payload_sz) do { cmd = (hdr >> 28) & 0xF; payload_sz = hdr & ((1 << 28) - 1); } while(0)

enum COMM_CMD {
    COMM_CMD_COMPRESS = 0,
    COMM_CMD_DECOMPRESS = 1
};

enum EXIT_STATUS {
    EXIT_OK = 0,
    EXIT_BAD_ARGUMENTS = 1,
    EXIT_ZSTD_INIT_FAIL = 2,
    EXIT_MALLOC_FAIL = 3,
    EXIT_BAD_COMM_SOCKET = 4,
    EXIT_FILE_CLOSE_FAIL = 5,
    EXIT_ZSTD_FAIL = 6,
    EXIT_COMM_FAIL = 7,
    EXIT_SECCOMP_FAIL = 8,
    EXIT_COMM_BAD_DATA = 9
};

extern void die(const char *msg);
extern void logerr(const char *msg);

extern size_t read_file(void *out, const size_t out_max_sz, const char *path);

extern int read_reliably(int fd, void *buf, const size_t size);
extern void read_or_die(int fd, void *buf, const size_t size);

extern int write_reliably(int fd, const void *buf, const size_t size);
extern void write_or_die(int fd, const void *buf, const size_t size);

#endif // !defined(SECURE_ZSTD_COMMON_H_)
