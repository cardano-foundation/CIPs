#pragma once
#ifndef SECURE_ZSTD_CALLER_H_
#define SECURE_ZSTD_CALLER_H_

#include <stddef.h>
#include <sys/types.h>

typedef pid_t (*caller_start_worker_fn)(const char *sock_path, const void *worker_arg);

struct caller_context {
    const void *worker_arg;
    const char *sock_path;
    int bind_fd;
    int comm_fd;
    pid_t pid;
    int num_deaths;
    caller_start_worker_fn start_worker_fn;
};

// Worker initialization through a custom binary is the recommended way to start a worker process.
// There reason is that it does not require the worker to clean up parent's resources after a fork.
extern void caller_init(struct caller_context *ctx, const char *worker_path, const char *sock_path);

// For use in a fuzzer or other test-related activities.
extern void caller_init_custom(struct caller_context *ctx, const char *sock_path, caller_start_worker_fn worker_fn, const void *worker_arg);

// A negative returned value by caller_decompress means an error and the need for a worker restart
extern ssize_t caller_decompress(struct caller_context *ctx, void *const out, const size_t max_out_sz, const char *const in, const size_t in_sz);

// caller_decompress_reliably automatically restarts the worker upon failures
extern size_t caller_decompress_reliably(struct caller_context *ctx, void *const out, const size_t max_out_sz, const char *const in, const size_t in_sz);

#endif // !SECURE_ZSTD_CALLER_H_
