#include <errno.h>
#include <stdio.h>

#include <sys/wait.h>

#include "common.h"
#include "caller.h"

static pid_t caller_default_start_worker(const char *sock_path, const void *worker_arg)
{
    const char *worker_path = (const char *)worker_arg;
    const pid_t worker_pid = fork();
    if (worker_pid < 0)
        die("A fork failed");
    if (worker_pid == 0) {
        execl(worker_path, worker_path, sock_path, NULL);
        die(worker_path);
    }
    logerr("A fork was successful");
    return worker_pid;
}

static void wait_for_worker_process(struct caller_context *ctx)
{
    ctx->pid = ctx->start_worker_fn(ctx->sock_path, ctx->worker_arg);
    for (size_t retry_no = 0; retry_no < 5; ++retry_no) {
        ctx->comm_fd = accept(ctx->bind_fd, NULL, NULL);
        if (ctx->comm_fd < 0) {
            if (errno == EAGAIN || errno == EINTR)
                continue;
            die("accept failed");
        }
        break;
    }
    logerr("An accept was successful");
}

static void open_listening_socket(struct caller_context *ctx)
{
    ctx->bind_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (ctx->bind_fd < 0)
        die("Unable to create a socket!");

    if (remove(ctx->sock_path) < 0 && errno != ENOENT) {
        die("The socket path already exits and its removal failed!");
    }

    struct sockaddr_un addr;
    addr.sun_family = AF_UNIX;
    if (snprintf(addr.sun_path, sizeof(addr.sun_path), "%s", ctx->sock_path) < 0)
        die("The socket path is too long!");

    if (bind(ctx->bind_fd, (struct sockaddr *)&addr, sizeof(addr)) < -0) {
        die("A bind failed");
    }

    logerr("A bind was successful");

    if (listen(ctx->bind_fd, 0) < 0) {
        die("A listen failed");
    }

    logerr("A listen was successful");
}

void caller_init_custom(struct caller_context *ctx, const char *sock_path, caller_start_worker_fn worker_fn, const void *worker_arg)
{
    ctx->worker_arg = worker_arg;
    ctx->start_worker_fn = worker_fn;
    ctx->sock_path = sock_path;
    ctx->num_deaths = 0;
    open_listening_socket(ctx);
    wait_for_worker_process(ctx);
}


void caller_init(struct caller_context *ctx, const char *worker_path, const char *sock_path)
{
    caller_init_custom(ctx, sock_path, caller_default_start_worker, worker_path);
}

static void restart_worker_process(struct caller_context *ctx)
{
    if (++ctx->num_deaths >= 5)
        die("The worker has died too many times!");
    close(ctx->comm_fd);
    wait_for_worker_process(ctx);
}

static bool worker_is_dead(struct caller_context *ctx)
{
    int status;
    pid_t res = waitpid(ctx->pid, &status, WNOHANG);
    if (res < 0)
        die("A waitpid failed");    
    if (res > 0)
        return true;
    return false;
}

ssize_t caller_decompress(struct caller_context *ctx, void *const out, const size_t max_out_sz, const char *const data, const size_t sz)
{
    if (sz > MAX_DATA_SIZE)
        die("The compressed data is too big!");
    uint32_t hdr = COMM_MAKE_HDR(COMM_CMD_DECOMPRESS, sz);
    if (write_reliably(ctx->comm_fd, (char *)&hdr, sizeof(hdr)) < 0)
        return -1;
    if (write_reliably(ctx->comm_fd, data, sz) < 0)
        return -1;

    uint32_t payload_sz;
    if (read_reliably(ctx->comm_fd, (char *)&payload_sz, sizeof(payload_sz)) < 0)
        return -1;
    if (payload_sz > max_out_sz)
        return -1;
    if (read_reliably(ctx->comm_fd, out, payload_sz) < 0)
        return -1;
    return payload_sz;
}

size_t caller_decompress_reliably(struct caller_context *ctx, void *const out, const size_t max_out_sz, const char *const in, const size_t in_sz)
{
    for (size_t retry_no = 0; retry_no < 3; ++retry_no) {
        const ssize_t d_sz = caller_decompress(ctx, out, max_out_sz, in, in_sz);
        if (d_sz >= 0)
            return d_sz;
        if (worker_is_dead(ctx)) {
            fprintf(stderr, "A worker with pid %d has died!\n", ctx->pid);
            restart_worker_process(ctx);
        }
    }
    die("The worker has failed to provide an output repeatedly on the same input!");
    // The line is never reached but is here to silence compiler warnings
    return 0;
}
