package org.rafaelia.rll;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.zip.Adler32;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** Synthetic APK/DEX/ELF adversarial falsifiers run before hosted Android Gradle. */
public final class OmegaBinaryInspectorSelfTest {
    private static int checks=0;
    private static void ok(boolean pass,String label){checks++;if(!pass)throw new AssertionError(label);}
    private static void u32(byte[] x,int off,long v){
        for(int i=0;i<4;i++)x[off+i]=(byte)(v>>(8*i));
    }
    private static byte[] dex(boolean valid)throws Exception{
        byte[] b=new byte[112];
        byte[] magic=new byte[]{'d','e','x',10,'0','3','5',0};
        System.arraycopy(magic,0,b,0,magic.length);
        u32(b,32,b.length);u32(b,36,112);u32(b,40,0x12345678);
        byte[] sha=MessageDigest.getInstance("SHA-1").digest(
            java.util.Arrays.copyOfRange(b,32,b.length));
        System.arraycopy(sha,0,b,12,20);
        Adler32 adler=new Adler32();adler.update(b,12,b.length-12);
        u32(b,8,adler.getValue());
        if(!valid)b[75]^=1;
        return b;
    }
    private static byte[] elf(boolean is64){
        byte[] b=new byte[is64?64:52];
        b[0]=127;b[1]='E';b[2]='L';b[3]='F';b[4]=(byte)(is64?2:1);
        b[5]=1;b[6]=1;b[16]=3;
        int machine=is64?183:40;
        b[18]=(byte)machine;b[19]=(byte)(machine>>8);
        return b;
    }
    private static void entry(ZipOutputStream z,String name,byte[] data)throws Exception{
        ZipEntry e=new ZipEntry(name);e.setTime(0L);z.putNextEntry(e);
        z.write(data);z.closeEntry();
    }
    private static File archive(boolean valid,boolean elfPresent)throws Exception{
        File path=File.createTempFile("rll-own-apk-fixture-",".apk");
        try(ZipOutputStream zip=new ZipOutputStream(new FileOutputStream(path))){
            entry(zip,"AndroidManifest.xml",new byte[]{3,0,8,0});
            entry(zip,"classes.dex",dex(valid));
            if(elfPresent){
                entry(zip,"lib/armeabi-v7a/librll_kernel_bridge.so",elf(false));
                entry(zip,"lib/arm64-v8a/librll_kernel_bridge.so",elf(true));
            }
        }
        return path;
    }
    public static void main(String[] args)throws Exception{
        File good=archive(true,true),bad=archive(false,true),missing=archive(true,false);
        try{
            String pass=OmegaBinaryInspector.inspect(good);
            ok(pass.contains("gate=PASS_SCOPED_APK_DEX_ELF_CRC"),"good APK");
            ok(pass.contains("dex_valid=1"),"DEX SHA1+Adler valid");
            ok(pass.contains("elf_abi_valid=2"),"ARM32 and ARM64");
            ok(pass.contains("android_apksigner_v2_v3=TOKEN_VAZIO_NOT_VERIFIED"),"no fake crypto proof");
            ok(OmegaBinaryInspector.inspect(bad).contains("gate=FAIL_BINARY_STRUCTURE"),"mutated DEX fails");
            ok(OmegaBinaryInspector.inspect(missing).contains("gate=FAIL_BINARY_STRUCTURE"),"missing ELF fails");
            ok(OmegaBinaryInspector.inspect(null).contains("TOKEN_VAZIO"),"no APK typed");
        }finally{good.delete();bad.delete();missing.delete();}
        System.out.println("RLL_OMEGA_BINARY_INSPECTOR_PASS checks="+checks);
    }
}
