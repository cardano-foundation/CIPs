#include <errno.h>
#include <string.h>

#include <seccomp.h>

#include <zstd.h>
#include <zstd_errors.h>

#include "common.h"
#include "worker.h"

#define ZSTD_DEFAULT_COMPRESSION_LEVEL 9

static size_t compress(ZSTD_CCtx *cctx, void *const out, size_t max_out_sz, const void *in, size_t in_sz)
{
    size_t res = ZSTD_CCtx_reset(cctx, ZSTD_reset_session_only);
    if (ZSTD_isError(res))
        exit(EXIT_ZSTD_FAIL);
    const size_t out_sz = ZSTD_compress2(cctx, out, max_out_sz, in, in_sz);
    if (ZSTD_isError(out_sz))
        exit(EXIT_ZSTD_FAIL);
    return out_sz;
}

static size_t decompress(ZSTD_DCtx *dctx, void *const out, size_t max_out_sz, const void *in, size_t in_sz)
{
    size_t res = ZSTD_DCtx_reset(dctx, ZSTD_reset_session_only);
    if (ZSTD_isError(res))
        exit(EXIT_ZSTD_FAIL);
    const size_t out_sz = ZSTD_decompressDCtx(dctx, out, max_out_sz, in, in_sz);
    if (ZSTD_isError(out_sz))
        exit(EXIT_ZSTD_FAIL);
    return out_sz;
}

static int open_socket(const char *sock_path)
{
    int comm_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (comm_fd < 0)
        exit(EXIT_BAD_COMM_SOCKET);
    {
        struct sockaddr_un addr;
        memset(&addr, 0, sizeof(addr));
        addr.sun_family = AF_UNIX;
        const size_t sock_path_len = strlen(sock_path);
        if (sock_path_len + 1 > sizeof(addr.sun_path))
            exit(EXIT_BAD_COMM_SOCKET);
        memcpy(addr.sun_path, sock_path, sock_path_len + 1);
        if (connect(comm_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0)
            exit(EXIT_BAD_COMM_SOCKET);
    }
    return comm_fd;
}

static void close_stdio()
{
    for (int i = 0; i <= 2; ++i) {
        if (close(i) < 0)
            exit(EXIT_FILE_CLOSE_FAIL);
    }
}

static void create_cctx(struct worker_context *ctx)
{
    ctx->zstd_cctx = ZSTD_createCCtx();
    if (ctx->zstd_cctx == NULL)
        exit(EXIT_ZSTD_INIT_FAIL);
    {
        const size_t res = ZSTD_CCtx_setParameter(ctx->zstd_cctx, ZSTD_c_compressionLevel, ZSTD_DEFAULT_COMPRESSION_LEVEL);
        if (ZSTD_isError(res))
            exit(EXIT_ZSTD_INIT_FAIL);
    }
}

static void create_dctx(struct worker_context *ctx)
{
    ctx->zstd_dctx = ZSTD_createDCtx();
    if (ctx->zstd_dctx == NULL)
        exit(EXIT_ZSTD_INIT_FAIL);
}

static void allocate_bufs(struct worker_context *ctx)
{
    // These buffers are allocated for the whole duration of the program.
    // Therefore, there no need to explicitly free them.
    ctx->buf_size = MAX_DATA_SIZE;
    ctx->in_buf = (char *)malloc(ctx->buf_size);
    if (ctx->in_buf == NULL)
        exit(EXIT_MALLOC_FAIL);
    ctx->out_buf = (char *)malloc(ctx->buf_size);
    if (ctx->out_buf == NULL)
        exit(EXIT_MALLOC_FAIL);
}

static void preallocate_compression_buffers(struct worker_context *ctx)
{
    // run an end-to-end compression cycle on the full buffer to make ZSTD pre-allocate its buffers
    memset(ctx->in_buf, 0, ctx->buf_size);
    // compress from in_buf to out_buf
    const size_t c_sz = compress(ctx->zstd_cctx, ctx->out_buf, ctx->buf_size, ctx->in_buf, ctx->buf_size);
    // decompress from out_buf to in_buf, so in_buf has the result of the decompression!
    const size_t d_sz = decompress(ctx->zstd_dctx, ctx->in_buf, ctx->buf_size, ctx->out_buf, c_sz);
    if (d_sz != ctx->buf_size)
        exit(EXIT_ZSTD_FAIL);
    for (size_t i = 0; i < d_sz; ++i) {
        if (ctx->in_buf[i])
            exit(EXIT_ZSTD_FAIL);
    }
}

static void configure(struct worker_context *ctx, const char *sock_path)
{
    create_cctx(ctx);
    create_dctx(ctx);
    allocate_bufs(ctx);
    preallocate_compression_buffers(ctx);
    ctx->comm_fd = open_socket(sock_path);
    // close stdio the last to have a channel for a diagnostic output before the process is fully configured
    close_stdio();
}

// This effectively blocks all syscalls except for read, write and exit.
static void restrict_syscalls()
{
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
    if (ctx == NULL)
        exit(EXIT_SECCOMP_FAIL);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) != 0)
        exit(EXIT_SECCOMP_FAIL);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) != 0)
        exit(EXIT_SECCOMP_FAIL);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0) != 0)
        exit(EXIT_SECCOMP_FAIL);
    if (seccomp_load(ctx) != 0)
        exit(EXIT_SECCOMP_FAIL);
    // The seccomp context is created for the whole duration of the process.
    // So, there is no need to explicitly free it.
}

void worker_init(struct worker_context *ctx, const char *sock_path)
{
    configure(ctx, sock_path);
    restrict_syscalls();
}

void worker_process_requests(struct worker_context *ctx)
{
    for (;;) {
        // the child and the parent operate on the same host, so there is no need to convert data into the network byte order
        uint32_t hdr = 0;
        read_or_die(ctx->comm_fd, (char *)&hdr, sizeof(hdr));
        uint8_t cmd;
        uint32_t payload_sz;
        COMM_PARSE_HDR(hdr, cmd, payload_sz);
        if (payload_sz > ctx->buf_size)
            exit(EXIT_COMM_BAD_DATA);
        read_or_die(ctx->comm_fd, ctx->in_buf, payload_sz);
        switch (cmd) {
            case COMM_CMD_COMPRESS: {
                const uint32_t c_sz = compress(ctx->zstd_cctx, ctx->out_buf, ctx->buf_size, ctx->in_buf, payload_sz);
                write_or_die(ctx->comm_fd, &c_sz, sizeof(c_sz));
                write_or_die(ctx->comm_fd, ctx->out_buf, c_sz);
                break;
            }
            case COMM_CMD_DECOMPRESS: {
                const uint32_t d_sz = decompress(ctx->zstd_dctx, ctx->out_buf, ctx->buf_size, ctx->in_buf, payload_sz);
                write_or_die(ctx->comm_fd, &d_sz, sizeof(d_sz));
                write_or_die(ctx->comm_fd, ctx->out_buf, d_sz);
                break;
            }
            default: exit(EXIT_COMM_FAIL);
        }
    }
}
