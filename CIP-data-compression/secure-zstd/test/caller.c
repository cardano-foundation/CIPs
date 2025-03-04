#include <stdio.h>
#include <time.h>

#include <dirent.h>
#include <fcntl.h>

#include <seczstd/common.h>
#include <seczstd/caller.h>

static void run_test(struct caller_context *ctx, const char *sample_dir)
{
    char *in_buf = malloc(MAX_DATA_SIZE);
    if (!in_buf)
        die("A malloc call failed!");
    char *out_buf = malloc(MAX_DATA_SIZE);
    if (!out_buf)
        die("A malloc call failed!");

    for (;;) {
        DIR *dir = opendir(sample_dir);
        if (dir == NULL)
            die(sample_dir);
        struct dirent *dir_entry;
        while ((dir_entry = readdir(dir)) != NULL) {
            if (dir_entry->d_type != DT_REG)
                continue;
            char path[PATH_MAX];
            if (snprintf(path, sizeof(path), "%s/%s", sample_dir, dir_entry->d_name) < 0)
                die("The sample_dir's pathname is too long!");
            const size_t file_sz = read_file(in_buf, MAX_DATA_SIZE, path);

            struct timespec start, stop;
            if (clock_gettime(CLOCK_MONOTONIC, &start) < 0)
                die("A clock_gettime call failed!");
            const size_t d_size = caller_decompress_reliably(ctx, out_buf, MAX_DATA_SIZE, in_buf, file_sz);
            if (clock_gettime(CLOCK_MONOTONIC, &stop) < 0)
                die("A clock_gettime call failed!");
            double duration = ((stop.tv_sec - start.tv_sec) * 1e6 + (stop.tv_nsec - start.tv_nsec) / 1e3) / 1e3;
            double speed = (double)d_size / 1e6 / (duration / 1e3);
            fprintf(stderr, "%s ratio: %0.3f time: %0.3f ms speed: %0.3f MB/sec\n", path, (double)d_size / file_sz, duration, speed);
        }
        if (closedir(dir) < 0)
            die("A closedir call failed!");
    }
}

int main(int argc, const char **argv)
{
    if (argc < 4) {
        printf("Usage: zstd-parent <worker-bin> <sock-path> <zstd-sample-dir>\n");
        return 1;
    }
    struct caller_context ctx;
    caller_init(&ctx, argv[1], argv[2]);
    run_test(&ctx, argv[3]);
    return 0;
}