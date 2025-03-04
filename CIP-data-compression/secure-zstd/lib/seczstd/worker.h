#pragma once
#ifndef SECURE_ZSTD_WORKER_H_
#define SECURE_ZSTD_WORKER_H_

#include <stddef.h>
#include <sys/types.h>

struct worker_context {
    size_t buf_size;
    void *zstd_cctx;
    void *zstd_dctx;
    char *in_buf;
    char *out_buf;
    int comm_fd;
};

extern void worker_init(struct worker_context *ctx, const char *sock_path);
extern void worker_process_requests(struct worker_context *ctx);

#endif // !SECURE_ZSTD_WORKER_H_
