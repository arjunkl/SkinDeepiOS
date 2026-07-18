#import <UIKit/UIKit.h>

#include <sys/param.h>
#include <unistd.h>

#include <string>

#include "framework/Common.h"
#include "framework/CVarSystem.h"
#include "idlib/Str.h"
#include "sys/posix/posix_public.h"
#include "sys/sys_local.h"
#include "sys/sys_public.h"

int screen_width = 1280;
int screen_height = 720;
int gl_format = 0x8888;
int gl_depth_bits = 24;
int gl_msaa = 0;

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

static NSURL *SDDocumentsURL(void) {
    NSFileManager *files = NSFileManager.defaultManager;
    NSURL *documents = [files URLsForDirectory:NSDocumentDirectory
                                      inDomains:NSUserDomainMask].firstObject;
    NSURL *url = [documents URLByAppendingPathComponent:@"SkinDeep"
                                            isDirectory:YES];
    [files createDirectoryAtURL:url
    withIntermediateDirectories:YES
                     attributes:nil
                          error:nil];
    return url;
}

static void SDWriteStartupEvidence(NSString *status, NSString *message) {
    @autoreleasepool {
        NSDictionary *evidence = @{
            @"marker": @"SKINDEEP_ENGINE_STARTUP",
            @"phase": @"common_init",
            @"status": status,
            @"message": message ?: @"",
            @"pid": @(NSProcessInfo.processInfo.processIdentifier),
        };
        NSError *error = nil;
        NSData *data = [NSJSONSerialization dataWithJSONObject:evidence
                                                       options:NSJSONWritingPrettyPrinted
                                                         error:&error];
        NSURL *url = [SDDocumentsURL() URLByAppendingPathComponent:@"startup.json"];
        if (data == nil || ![data writeToURL:url options:NSDataWritingAtomic error:&error]) {
            fprintf(stderr, "SKINDEEP_STARTUP_EVIDENCE_WRITE_FAILED: %s\n",
                    error.localizedDescription.UTF8String ?: "unknown error");
        } else {
            fprintf(stderr, "SKINDEEP_STARTUP_EVIDENCE: %s\n",
                    url.fileSystemRepresentation);
        }
        fflush(stderr);
    }
}

void SkinDeepIOS_RecordStartupBegin(void) {
    SDWriteStartupEvidence(@"started", @"");
}

void SkinDeepIOS_RecordStartupSuccess(void) {
    SDWriteStartupEvidence(@"initialized", @"");
}

void SkinDeepIOS_RecordFatalError(const char *message) {
    NSString *text = message == nullptr
        ? @"Unknown engine fatal error"
        : [NSString stringWithUTF8String:message];
    SDWriteStartupEvidence(@"fatal", text);
}

bool Sys_GetPath(sysPath_t type, idStr &path) {
    @autoreleasepool {
        NSURL *url = nil;
        switch (type) {
            case PATH_BASE: {
                url = SDDocumentsURL();
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

const char *Sys_ApplicationHomePath(void) {
    static const std::string path = [] {
        @autoreleasepool {
            return std::string(SDApplicationSupportURL().fileSystemRepresentation);
        }
    }();
    return path.c_str();
}

FILE *Sys_tmpfile(void) {
    @autoreleasepool {
        NSString *pattern = [NSTemporaryDirectory()
            stringByAppendingPathComponent:@"skindeep-XXXXXX"];
        char fileName[MAXPATHLEN];
        if (![pattern getFileSystemRepresentation:fileName
                                         maxLength:sizeof(fileName)]) {
            return nullptr;
        }
        int descriptor = mkstemp(fileName);
        if (descriptor < 0) {
            return nullptr;
        }
        unlink(fileName);
        FILE *file = fdopen(descriptor, "w+b");
        if (file == nullptr) {
            close(descriptor);
        }
        return file;
    }
}

void Sys_SyncState(void) {}

void Sys_Analog(int &side, int &forward, const int &keyMoveSpeed) {
    (void)side;
    (void)forward;
    (void)keyMoveSpeed;
}

void Android_PollInput(void) {}

float Android_GetConsoleMaxHeightFrac(float fraction) {
    return fraction;
}

bool GLimp_CheckGLInitialized(void) {
    return true;
}

void Sys_ForceResolution(void) {
    @autoreleasepool {
        CGRect bounds = UIScreen.mainScreen.nativeBounds;
        if (bounds.size.width > 0.0 && bounds.size.height > 0.0) {
            screen_width = (int)bounds.size.width;
            screen_height = (int)bounds.size.height;
        }
    }
    cvarSystem->SetCVarBool("r_fullscreen", true);
    cvarSystem->SetCVarInteger("r_mode", -1);
    cvarSystem->SetCVarInteger("r_customWidth", screen_width);
    cvarSystem->SetCVarInteger("r_customHeight", screen_height);
}

const char *OSX_GetLocalizedString(const char *value) {
    return value;
}

bool OSX_GetCPUIdentification(int &cpuId, bool &oldArchitecture) {
    cpuId = 0;
    oldArchitecture = false;
    return true;
}

void OSX_GetVideoCard(int &vendorId, int &deviceId) {
    vendorId = -1;
    deviceId = -1;
}

void idSysLocal::OpenURL(const char *url, bool quit) {
    (void)quit;
    if (url == nullptr || url[0] == '\0') {
        return;
    }
    @autoreleasepool {
        NSURL *target = [NSURL URLWithString:[NSString stringWithUTF8String:url]];
        if (target == nil) {
            return;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            [UIApplication.sharedApplication openURL:target
                                             options:@{}
                                   completionHandler:nil];
        });
    }
}

void Sys_DoStartProcess(const char *exeName, bool dofork) {
    (void)dofork;
    Sys_Printf("StartProcess is unavailable on iOS: %s\n", exeName ?: "");
}
