/* This file is part of Daedalus Turbo project: https://github.com/sierkov/daedalus-turbo/
 * Copyright (c) 2022-2023 Alex Sierkov (alex dot sierkov at gmail dot com)
 * Copyright (c) 2024-2025 R2 Rationality OÜ (info at r2rationality dot com)
 * This code is distributed under the license specified in:
 * https://github.com/sierkov/daedalus-turbo/blob/main/LICENSE */

 #include <seczstd/common.h>
 #include <seczstd/caller.h>
 #include <seczstd/worker.h>

static struct caller_context c_ctx;
static void *out_buf = NULL;

static pid_t worker_start(const char *sock_path, const void *worker_arg)
{
    // silence the compiler warning about an unused argument
    (void)worker_arg;
    
    const pid_t worker_pid = fork();
    if (worker_pid < 0)
        die("A fork failed");
    if (worker_pid == 0) {
        struct worker_context w_ctx;
        worker_init(&w_ctx, sock_path);
        worker_process_requests(&w_ctx);
        die("A worker process has failed!");
    }
    logerr("A fork was successful");
    return worker_pid;
}

static void ensure_initialized(void)
{
    if (!out_buf) {
        caller_init_custom(&c_ctx, "./seczstd-fuzz.sock", worker_start, NULL);
        out_buf = malloc(MAX_DATA_SIZE);
        if (!out_buf)
            die("A malloc call failed!");
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data, const size_t size)
{
    ensure_initialized();
    return caller_decompress(&c_ctx, out_buf, MAX_DATA_SIZE, (const char *)data, size);
}
