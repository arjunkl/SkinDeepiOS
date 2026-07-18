#include "framework/Common.h"

void SkinDeepIOS_RecordStartupBegin(void);
void SkinDeepIOS_RecordStartupSuccess(void);

int main(int argc, char **argv) {
    SkinDeepIOS_RecordStartupBegin();
    if (argc > 1) {
        common->Init(argc - 1, &argv[1]);
    } else {
        common->Init(0, nullptr);
    }
    SkinDeepIOS_RecordStartupSuccess();
    return 0;
}
