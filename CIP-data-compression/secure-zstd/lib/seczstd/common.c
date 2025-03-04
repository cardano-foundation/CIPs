#include <errno.h>
#include <stdio.h>

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>

#include "common.h"

void die(const char *msg)
{
    fprintf(stderr, "%s errno: %d, strerror: %s\n", msg, errno, strerror(errno));
    exit(1);
}

void logerr(const char *msg)
{
    fprintf(stderr, "%s\n", msg);
}

size_t read_file(void *out, const size_t out_max_sz, const char *path)
{
    const int fd = open(path, O_RDONLY);
    if (fd < 0)
        die(path);
    const off_t file_sz = lseek(fd, 0, SEEK_END);
    if (file_sz < 0)
        die("An lseek call failed");
    if ((size_t)file_sz > out_max_sz)
        die("At least one sample file is too big!");
    if (lseek(fd, 0, SEEK_SET) < 0)
        die("An lseek call failed");
    read_or_die(fd, out, file_sz);
    if (close(fd) < 0)
        die("A close call failed!");
    return file_sz;
}

int read_reliably(int fd, void *ptr, const size_t size)
{
    char *buf = (char*)ptr;
    for (size_t done = 0; done < size;) {
        const ssize_t nread = read(fd, &buf[done], size - done);
        if (nread <= 0) {
            if (errno == EAGAIN || errno == EINTR)
                continue;
            return -1;
        }
        done += (size_t)nread;
    }
    return 0;
}

int write_reliably(int fd, const void *ptr, const size_t size)
{
    const char *buf = (char*)ptr;
    for (size_t done = 0; done < size;) {
        const ssize_t nwritten = write(fd, &buf[done], size - done);
        if (nwritten <= 0) {
            if (errno == EAGAIN || errno == EINTR)
                continue;
            return -1;
        }
        done += (size_t)nwritten;
    }
    return 0;
}

void read_or_die(int fd, void *buf, const size_t size)
{
    if (read_reliably(fd, buf, size) < 0)
        exit(EXIT_COMM_FAIL);
}

void write_or_die(int fd, const void *buf, const size_t size)
{
    if (write_reliably(fd, buf, size) < 0)
        exit(EXIT_COMM_FAIL);
}