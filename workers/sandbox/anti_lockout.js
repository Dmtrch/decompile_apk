// Frida script to bypass common server connectivity and SSL pinning checks
// This script keeps the app alive even if the server is emulated or unreachable

Java.perform(function () {
    console.log("[*] Anti-Lockout & SSL Pinning Bypass script loaded");

    // 1. Bypass SSL Pinning (common libraries)
    const TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    if (TrustManagerImpl) {
        TrustManagerImpl.checkServerTrusted.implementation = function () {
            console.log("[+] SSL Pinning Bypassed (checkServerTrusted)");
            return;
        };
    }

    // 2. Prevent App Exit on Network Errors
    const System = Java.use('java.lang.System');
    System.exit.implementation = function (code) {
        console.log("[!] App tried to exit with code: " + code + ". Preventing exit...");
        return;
    };

    // 3. Mock Network Connectivity
    const ConnectivityManager = Java.use('android.net.ConnectivityManager');
    if (ConnectivityManager) {
        ConnectivityManager.getActiveNetworkInfo.implementation = function () {
            console.log("[+] Mocking ActiveNetworkInfo (always connected)");
            const NetworkInfo = Java.use('android.net.NetworkInfo');
            // Mocking a connected state
            return null; // Simplified for now, real implementation would return a proxy object
        };
    }
});
