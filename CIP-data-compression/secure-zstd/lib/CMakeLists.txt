find_library(ZSTD zstd REQUIRED)
find_library(SECCOMP seccomp REQUIRED)

add_library(seczstd OBJECT seczstd/common.c seczstd/caller.c seczstd/worker.c)
target_include_directories(seczstd PUBLIC .)
target_link_libraries(seczstd PUBLIC ${ZSTD} ${SECCOMP})