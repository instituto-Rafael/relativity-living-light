package org.rafaelia.rll;

import android.app.Activity;
import android.content.pm.ApplicationInfo;
import android.os.Build;
import android.os.SystemClock;
import android.system.Os;
import android.system.StructUtsname;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

/** Public Android APIs + bounded kernel version reads; no root, serial, IMEI or arbitrary filesystem scan. */
public final class OmegaKernelEnvironment {
    private OmegaKernelEnvironment(){}
    private static String bounded(String value,int limit) {
        if(value==null)return "TOKEN_VAZIO_NULL";
        StringBuilder s=new StringBuilder();
        for(int i=0;i<value.length()&&s.length()<limit;i++) {
            char c=value.charAt(i);
            s.append(c<32||c==127?' ':c);
        }
        return s.toString();
    }
    private static String line(String path){
        File file=new File(path);
        if(!file.isFile()||!file.canRead())return "TOKEN_VAZIO_KERNEL_PATH_NOT_ACCESSIBLE";
        try(BufferedReader r=new BufferedReader(new FileReader(file))){
            return bounded(r.readLine(),512);
        }catch(Exception ex){return "TOKEN_VAZIO_KERNEL_"+ex.getClass().getSimpleName();}
    }
    public static String inspect(Activity host) {
        StringBuilder out=new StringBuilder("schema=rll.omega.kernel-platform-build.v1\n"
            +"source=ANDROID_OS_READ_ONLY_PUBLIC_AND_ACCESSIBLE_PROC\n"
            +"scope=OS_KERNEL_BUILD_INFORMATION_NOT_TRUSTED_BOOT_HARDWARE_ATTESTATION\n"
            +"claim_allowed=false\n");
        out.append("utc_ms=").append(System.currentTimeMillis()).append('\n')
           .append("elapsed_realtime_ms=").append(SystemClock.elapsedRealtime()).append('\n')
           .append("android_sdk=").append(Build.VERSION.SDK_INT).append('\n')
           .append("android_release=").append(bounded(Build.VERSION.RELEASE,60)).append('\n')
           .append("security_patch=").append(bounded(Build.VERSION.SECURITY_PATCH,60)).append('\n')
           .append("board=").append(bounded(Build.BOARD,90)).append('\n')
           .append("hardware=").append(bounded(Build.HARDWARE,90)).append('\n')
           .append("supported_abis_count=").append(Build.SUPPORTED_ABIS.length).append('\n');
        try {
            StructUtsname uts=Os.uname();
            if(uts==null)out.append("uname=TOKEN_VAZIO_API_NULL\n");
            else out.append("uname_sysname=").append(bounded(uts.sysname,50)).append('\n')
                .append("uname_release=").append(bounded(uts.release,150)).append('\n')
                .append("uname_version=").append(bounded(uts.version,240)).append('\n')
                .append("uname_machine=").append(bounded(uts.machine,90)).append('\n');
        }catch(Exception ex){out.append("uname=TOKEN_VAZIO_").append(ex.getClass().getSimpleName()).append('\n');}
        out.append("proc_kernel_version=").append(line("/proc/version")).append('\n')
           .append("sys_kernel_release=").append(line("/proc/sys/kernel/osrelease")).append('\n')
           .append("java_vm_name=").append(bounded(System.getProperty("java.vm.name"),90)).append('\n')
           .append("java_vm_version=").append(bounded(System.getProperty("java.vm.version"),90)).append('\n')
           .append("runtime_os_arch=").append(bounded(System.getProperty("os.arch"),90)).append('\n');
        try {
            ApplicationInfo app=host.getApplicationInfo();
            out.append("app_debuggable_flag=")
               .append((app.flags&ApplicationInfo.FLAG_DEBUGGABLE)!=0).append('\n')
               .append("app_has_native_library_dir=").append(app.nativeLibraryDir!=null).append('\n');
        }catch(Exception ex){out.append("app_info=TOKEN_VAZIO_").append(ex.getClass().getSimpleName()).append('\n');}
        out.append("build_config_debug=").append(BuildConfig.DEBUG).append('\n')
           .append("build_config_type=").append(bounded(BuildConfig.BUILD_TYPE,32)).append('\n')
           .append("build_config_git_checkout_sha_label=").append(BuildConfig.RLL_GITHUB_HEAD).append('\n')
           .append("build_config_ci_run_id_label=").append(BuildConfig.RLL_GITHUB_RUN_ID).append('\n')
           .append("build_contract_gradle_declared=8.10.2\n")
           .append("build_contract_java_declared=17\n")
           .append("build_contract_android_compile_sdk_declared=35\n")
           .append("build_contract_ndk_declared=27.2.12479018\n")
           .append("build_contract_cmake_declared=3.22.1\n")
           .append("declared_toolchain_is_not_local_compiler_attestation=true\n")
           .append("git_source_feature_head=TOKEN_VAZIO_APP_ONLY_HAS_CHECKOUT_LABEL\n")
           .append("kernel_source_binaries=TOKEN_VAZIO_NOT_EXPORTED\n")
           .append("kernel_module_list=TOKEN_VAZIO_NOT_ATTEMPTED_REQUIRES_SYSTEM_BOUNDARY\n")
           .append("verified_boot_hardware_attestation=TOKEN_VAZIO_NOT_ATTESTED\n")
           .append("gate=RECORDED_SCOPED_KERNEL_AND_BUILD_CONTEXT\n");
        return out.toString();
    }
}
