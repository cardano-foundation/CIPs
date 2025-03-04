#include <stdlib.h>

#include <seczstd/common.h>
#include <seczstd/worker.h>

int main(int argc, const char **argv)
{
    if (argc != 2)
        exit(EXIT_BAD_ARGUMENTS);
    struct worker_context ctx;
    worker_init(&ctx, argv[1]);
    worker_process_requests(&ctx);
    return 0;
}
