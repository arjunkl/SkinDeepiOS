#import <Foundation/Foundation.h>
#import <OpenGLES/ES3/gl.h>
#import <OpenGLES/EAGL.h>
#import <UIKit/UIKit.h>

static NSString *const SDBundleIdentifier = @"org.skindeep.ios.bootstrap";
static NSString *const SDReadyMarker = @"SKINDEEP_BOOTSTRAP_READY";

static NSString *SDGLString(GLenum name) {
    const GLubyte *value = glGetString(name);
    return value ? [NSString stringWithUTF8String:(const char *)value] : @"";
}

@interface SDAppDelegate : UIResponder <UIApplicationDelegate>
@property(nonatomic, strong) UIWindow *window;
@property(nonatomic, strong) EAGLContext *glContext;
@end

@implementation SDAppDelegate

- (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    (void)application;
    (void)launchOptions;

    NSFileManager *files = NSFileManager.defaultManager;
    NSURL *documents = [files URLsForDirectory:NSDocumentDirectory
                                      inDomains:NSUserDomainMask].firstObject;
    NSURL *gameData = [documents URLByAppendingPathComponent:@"SkinDeep/base"
                                                 isDirectory:YES];
    NSError *directoryError = nil;
    BOOL directoryReady = [files createDirectoryAtURL:gameData
                          withIntermediateDirectories:YES
                                           attributes:nil
                                                error:&directoryError];

    self.glContext = [[EAGLContext alloc] initWithAPI:kEAGLRenderingAPIOpenGLES3];
    BOOL contextReady = self.glContext != nil && [EAGLContext setCurrentContext:self.glContext];

    NSString *glVersion = contextReady ? SDGLString(GL_VERSION) : @"";
    NSString *glVendor = contextReady ? SDGLString(GL_VENDOR) : @"";
    NSString *glRenderer = contextReady ? SDGLString(GL_RENDERER) : @"";
    BOOL ready = directoryReady && contextReady && glVersion.length > 0;

    NSDictionary *evidence = @{
        @"marker": SDReadyMarker,
        @"status": ready ? @"ready" : @"failed",
        @"bundle_identifier": NSBundle.mainBundle.bundleIdentifier ?: SDBundleIdentifier,
        @"documents_path": documents.path ?: @"",
        @"game_data_path": gameData.path ?: @"",
        @"filesystem_ready": @(directoryReady),
        @"filesystem_error": directoryError.localizedDescription ?: @"",
        @"graphics_api": @"OpenGL ES 3",
        @"context_ready": @(contextReady),
        @"gl_version": glVersion,
        @"gl_vendor": glVendor,
        @"gl_renderer": glRenderer,
    };

    NSError *jsonError = nil;
    NSData *json = [NSJSONSerialization dataWithJSONObject:evidence
                                                   options:NSJSONWritingPrettyPrinted | NSJSONWritingSortedKeys
                                                     error:&jsonError];
    NSURL *evidenceURL = [documents URLByAppendingPathComponent:@"bootstrap.json"];
    BOOL evidenceWritten = json != nil && [json writeToURL:evidenceURL
                                                   options:NSDataWritingAtomic
                                                     error:&jsonError];

    NSLog(@"%@ status=%@ evidence=%@", SDReadyMarker,
          ready && evidenceWritten ? @"ready" : @"failed", evidenceURL.path);

    UIViewController *controller = [[UIViewController alloc] init];
    controller.view.backgroundColor = UIColor.blackColor;

    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.translatesAutoresizingMaskIntoConstraints = NO;
    label.numberOfLines = 0;
    label.textAlignment = NSTextAlignmentCenter;
    label.textColor = UIColor.whiteColor;
    label.font = [UIFont monospacedSystemFontOfSize:16 weight:UIFontWeightRegular];
    label.accessibilityIdentifier = @"skindeep.bootstrap.status";
    label.text = ready && evidenceWritten
        ? [NSString stringWithFormat:@"Skin Deep iOS\nPlatform bootstrap ready\n%@", glVersion]
        : [NSString stringWithFormat:@"Skin Deep iOS\nBootstrap failed\n%@",
                                     jsonError.localizedDescription ?: directoryError.localizedDescription ?: @"OpenGL ES 3 unavailable"];
    [controller.view addSubview:label];
    [NSLayoutConstraint activateConstraints:@[
        [label.leadingAnchor constraintGreaterThanOrEqualToAnchor:controller.view.safeAreaLayoutGuide.leadingAnchor constant:24],
        [label.trailingAnchor constraintLessThanOrEqualToAnchor:controller.view.safeAreaLayoutGuide.trailingAnchor constant:-24],
        [label.centerXAnchor constraintEqualToAnchor:controller.view.centerXAnchor],
        [label.centerYAnchor constraintEqualToAnchor:controller.view.centerYAnchor],
    ]];

    self.window = [[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
    self.window.rootViewController = controller;
    [self.window makeKeyAndVisible];
    return YES;
}

@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass(SDAppDelegate.class));
    }
}
