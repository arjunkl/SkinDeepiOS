#include "framework/Common.h"

// This executable is a device-ABI link gate. Runtime startup is enabled only
// after every platform and third-party dependency is represented honestly.
int main(int argc, char **argv) {
    if (argc > 1) {
        common->Init(argc - 1, &argv[1]);
    } else {
        common->Init(0, nullptr);
    }
    return 0;
}
