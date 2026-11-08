package org.rafaelia.rllcad;
/** Android/Dalvik/ART Java API boundary. The APK's d8 produces DEX separately.
 * Requires native library compiled for armeabi-v7a or arm64-v8a and packaged by host.
 * This source is NOT a built APK nor an executed DEX binary.
 */
public final class RllCadBridge {
    static { System.loadLibrary("rllcad"); }
    private RllCadBridge() {}
    /** Input: 9 int fields Q16.16 except alpha_micro_per_K integer.
     * Output: 13 int fields, last 1 flags; status returned separately.
     * This is an illustrative model, not structural certification.
     */
    public static native int evaluate(int[] inputQ16, int[] outputQ16AndFlags);
}
