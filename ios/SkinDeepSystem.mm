#import <Foundation/Foundation.h>

#include <sys/param.h>

#include "framework/Common.h"
#include "idlib/Str.h"
#include "sys/posix/posix_public.h"
#include "sys/sys_public.h"

static NSURL *SDApplicationSupportURL(void) {
    NSFileManager *files = NSFileManager.defaultManager;
    NSURL *root = [files URLsForDirectory:NSApplicationSupportDirectory
                                inDomains:NSUserDomainMask].firstObject;
    NSURL *url = [root URLByAppendingPathComponent:@"SkinDeep" isDirectory:YES];
    [files createDirectoryAtURL:url
    withIntermediateDirectories:YES
                     attributes:nil
                          error:nil];
    return url;
}

bool Sys_GetPath(sysPath_t type, idStr &path) {
    @autoreleasepool {
        NSURL *url = nil;
        switch (type) {
            case PATH_BASE: {
                NSURL *documents = [NSFileManager.defaultManager
                    URLsForDirectory:NSDocumentDirectory
                            inDomains:NSUserDomainMask].firstObject;
                url = [documents URLByAppendingPathComponent:@"SkinDeep"
                                                  isDirectory:YES];
                break;
            }
            case PATH_CONFIG:
            case PATH_SAVE:
                url = SDApplicationSupportURL();
                break;
            case PATH_EXE:
                url = NSBundle.mainBundle.bundleURL;
                break;
        }
        if (url == nil) {
            path.Clear();
            return false;
        }
        path = url.fileSystemRepresentation;
        return true;
    }
}

void Sys_Shutdown(void) {
    Posix_Shutdown();
}

int Sys_GetSystemRam(void) {
    return (int)(NSProcessInfo.processInfo.physicalMemory / (1024ULL * 1024ULL));
}

void Sys_DoStartProcess(const char *exeName, bool dofork) {
    (void)dofork;
    Sys_Printf("StartProcess is unavailable on iOS: %s\n", exeName ?: "");
}
