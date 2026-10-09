package org.rafaelia.rll;

import android.app.Activity;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
import android.os.Build;
import android.os.SystemClock;
import android.util.Log;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/** First-party opt-in per-run operational trace. Never read other apps' logs. */
public final class OmegaRuntimeEvidence {
    private static final String TAG="RLL_OMEGA";
    private static final int MAX_CHARS=48000;
    private final long startedUtc=System.currentTimeMillis();
    private final long startedElapsed=SystemClock.elapsedRealtime();
    private final StringBuilder trace=new StringBuilder();
    private int steps=0;
    public synchronized void event(String gate,String state,long elapsedMillis){
        if(trace.length()>MAX_CHARS-320)return;
        if(!gate.matches("[A-Z0-9_]{1,48}")||!state.matches("[A-Z0-9_]{1,65}"))
            throw new IllegalArgumentException("Invalid diagnostic token");
        String row=String.format(Locale.US,"%d\t%d\t%s\t%s\t%d\n",
                steps++,SystemClock.elapsedRealtime()-startedElapsed,gate,state,elapsedMillis);
        trace.append(row);
        Log.i(TAG,gate+" "+state);
    }
    public synchronized String trace(){
        return "schema=rll.omega.runtime-trace.v1\n"
           +"start_wall_utc_ms="+startedUtc+"\nstart_elapsed_realtime_ms="+startedElapsed
           +"\norigin=APP_INSTRUMENTATION_NOT_EXTERNAL_ATTESTATION\n"
           +"step\telapsed_from_start_ms\tgate\tstatus\tstage_duration_ms\n"
           +trace.toString();
    }
    public String context(Activity host){
        StringBuilder b=new StringBuilder();
        b.append("schema=rll.omega.runtime-context.v1\n")
         .append("origin=APP_OWN_PROCESS_ANDROID_OS_FIELDS\n")
         .append("timestamp_utc_ms=").append(System.currentTimeMillis()).append('\n')
         .append("elapsed_realtime_ms=").append(SystemClock.elapsedRealtime()).append('\n')
         .append("uptime_millis=").append(SystemClock.uptimeMillis()).append('\n')
         .append("process_pid=").append(android.os.Process.myPid()).append('\n')
         .append("process_uid=").append(android.os.Process.myUid()).append('\n')
         .append("sdk=").append(Build.VERSION.SDK_INT).append('\n')
         .append("cpu_abi=").append(Build.SUPPORTED_ABIS.length>0?Build.SUPPORTED_ABIS[0]:"TOKEN_VAZIO").append('\n');
        Runtime r=Runtime.getRuntime();
        b.append("heap_total_bytes=").append(r.totalMemory()).append('\n')
         .append("heap_free_bytes=").append(r.freeMemory()).append('\n')
         .append("heap_max_bytes=").append(r.maxMemory()).append('\n');
        try{
            Intent battery=host.registerReceiver(null,new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if(battery!=null){
                int level=battery.getIntExtra(BatteryManager.EXTRA_LEVEL,-1);
                int scale=battery.getIntExtra(BatteryManager.EXTRA_SCALE,-1);
                b.append("battery_level=").append(level).append('\n')
                 .append("battery_scale=").append(scale).append('\n')
                 .append("battery_plugged_code=").append(battery.getIntExtra(BatteryManager.EXTRA_PLUGGED,-1)).append('\n');
            }else b.append("battery=TOKEN_VAZIO_STICKY_EVENT_UNAVAILABLE\n");
        }catch(RuntimeException ex){
            b.append("battery=TOKEN_VAZIO_").append(ex.getClass().getSimpleName()).append('\n');
        }
        b.append("hardware_identity_independent=TOKEN_VAZIO_NOT_ATTESTED\n");
        return b.toString();
    }
    /**
     * Only the invoking process PID, only on user request; optional, bounded.
     * Does not request READ_LOGS, root, shell ADB, other app IDs, or full device logs.
     */
    public String ownPidLogcat() {
        final StringBuilder header=new StringBuilder()
           .append("schema=rll.omega.logcat.v1\n")
           .append("scope=OWN_PROCESS_PID_ONLY\n")
           .append("privileged_READ_LOGS=false\n")
           .append("source=ANDROID_LOGCAT_BEST_EFFORT_NOT_SYSTEM_WIDE\n")
           .append("pid=").append(android.os.Process.myPid()).append('\n');
        final String[] output={"TOKEN_VAZIO_LOGCAT_NOT_RUN"};
        try{
            ProcessBuilder builder=new ProcessBuilder("logcat","-d","-t","150",
                     "--pid="+android.os.Process.myPid(),"RLL_OMEGA:I","*:S");
            builder.redirectErrorStream(true);
            final java.lang.Process process=builder.start();
            Thread reader=new Thread(()->{
                try(InputStream in=process.getInputStream();ByteArrayOutputStream bytes=new ByteArrayOutputStream()){
                    byte[] buf=new byte[2048];int n;
                    while((n=in.read(buf))!=-1){
                        if(bytes.size()+n>MAX_CHARS)break;
                        bytes.write(buf,0,n);
                    }
                    output[0]=new String(bytes.toByteArray(),StandardCharsets.UTF_8);
                }catch(Exception ex){
                    output[0]="TOKEN_VAZIO_LOGCAT_READER_"+ex.getClass().getSimpleName();
                }
            },"rll-own-logcat-reader");
            reader.setDaemon(true);reader.start();
            reader.join(1800);
            if(reader.isAlive()){
                process.destroy();
                reader.interrupt();
                header.append("gate=TOKEN_VAZIO_LOGCAT_TIMEOUT\n");
            }else if(!output[0].isEmpty()&&!output[0].startsWith("TOKEN_VAZIO")){
                header.append("gate=CAPTURED_OWN_PROCESS_BEST_EFFORT\n");
            }else header.append("gate=TOKEN_VAZIO_LOGCAT_EMPTY_OR_RESTRICTED\n");
            process.destroy();
        }catch(Exception ex){
            header.append("gate=TOKEN_VAZIO_LOGCAT_").append(ex.getClass().getSimpleName()).append('\n');
        }
        // Logcat may contain runtime metadata; all bytes remain only in the user-saved ZIP.
        if(output[0].length()>MAX_CHARS)output[0]=output[0].substring(0,MAX_CHARS);
        return header.append("---OWN_PID_LOGCAT---\n").append(output[0]).append('\n').toString();
    }
}
