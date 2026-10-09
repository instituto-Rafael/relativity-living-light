package org.rafaelia.rll;

import android.app.Activity;
import android.app.ActivityManager;
import android.os.Build;
import android.os.StatFs;
import android.os.SystemClock;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.Locale;

/** Bounded, private read-only hardware / process probe. No root, other apps or identifiers. */
public final class OmegaDeepDiagnostics {
    private OmegaDeepDiagnostics(){}
    private static String safe(String value){
        if(value==null)return "TOKEN_VAZIO_NULL";
        return value.replaceAll("[^A-Za-z0-9_.-]","_").substring(0,Math.min(80,value.length()));
    }
    private static String boundedFirstLine(File file){
        if(!file.isFile()||!file.canRead())return "TOKEN_VAZIO_PERMISSION_OR_NOT_AVAILABLE";
        try(BufferedReader r=new BufferedReader(new FileReader(file))){
            String l=r.readLine();
            return l==null?"TOKEN_VAZIO_EMPTY":safe(l);
        }catch(Exception ex){return "TOKEN_VAZIO_"+ex.getClass().getSimpleName();}
    }
    public static String capture(Activity host) {
        StringBuilder s=new StringBuilder("schema=rll.omega.hw-process-probe.v1\n"
           +"origin=LIVE_ANDROID_OWN_PROCESS_SELF_REPORT\n"
           +"scope=PUBLIC_APIS_SELF_PROC_BOUNDARY\n"
           +"claim_allowed=false\n");
        s.append("wall_utc_ms=").append(System.currentTimeMillis()).append('\n')
         .append("elapsed_realtime_ms=").append(SystemClock.elapsedRealtime()).append('\n')
         .append("sdk=").append(Build.VERSION.SDK_INT).append('\n')
         .append("abi_count=").append(Build.SUPPORTED_ABIS.length).append('\n');
        for(int i=0;i<Build.SUPPORTED_ABIS.length;i++)
            s.append("abi_").append(i).append('=').append(safe(Build.SUPPORTED_ABIS[i])).append('\n');
        s.append("processors_visible=").append(Runtime.getRuntime().availableProcessors()).append('\n')
         .append("java_max_heap_bytes=").append(Runtime.getRuntime().maxMemory()).append('\n');
        try {
            ActivityManager m=(ActivityManager)host.getSystemService(Activity.ACTIVITY_SERVICE);
            if(m==null)s.append("physical_mem=TOKEN_VAZIO_SERVICE_UNAVAILABLE\n");
            else {
                ActivityManager.MemoryInfo info=new ActivityManager.MemoryInfo();m.getMemoryInfo(info);
                s.append("reported_total_mem_bytes=").append(info.totalMem).append('\n')
                 .append("reported_available_mem_bytes=").append(info.availMem).append('\n')
                 .append("low_memory=").append(info.lowMemory).append('\n');
            }
        }catch(Exception ex){s.append("physical_mem=TOKEN_VAZIO_")
                            .append(ex.getClass().getSimpleName()).append('\n');}
        try {
            StatFs stat=new StatFs(host.getFilesDir().getAbsolutePath());
            s.append("app_private_storage_total_bytes=").append(stat.getTotalBytes()).append('\n')
             .append("app_private_storage_available_bytes=").append(stat.getAvailableBytes()).append('\n');
        }catch(Exception ex){s.append("storage=TOKEN_VAZIO_")
                            .append(ex.getClass().getSimpleName()).append('\n');}
        s.append("numa_sysfs_node_online=")
         .append(boundedFirstLine(new File("/sys/devices/system/node/online"))).append('\n');
        s.append("numa_topology_inferred=false\n");
        try(BufferedReader r=new BufferedReader(new FileReader("/proc/self/status"))){
            String line;int lines=0;
            while((line=r.readLine())!=null && ++lines<512){
                if(line.startsWith("VmRSS:")||line.startsWith("VmSize:")||line.startsWith("Threads:"))
                    s.append("proc_status_").append(safe(line)).append('\n');
            }
        }catch(Exception ex){s.append("self_proc_status=TOKEN_VAZIO_")
             .append(ex.getClass().getSimpleName()).append('\n');}
        s.append("independent_hardware_witness=TOKEN_VAZIO_NOT_ATTESTED\n")
         .append("hardware_serial_or_imei_collected=false\n")
         .append("gate=RECORDED_APP_SCOPED\n");
        return s.toString();
    }
}
