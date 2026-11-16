package org.rafaelia.rll;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Enumeration;
import java.util.zip.Adler32;
import java.util.zip.CRC32;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/** Read-only APK ZIP / DEX / ELF inspector. All evidence comes from exact local bytes. */
public final class OmegaBinaryInspector {
    private OmegaBinaryInspector(){}
    private static final int MAX_APK_ENTRIES=1024, MAX_ENTRY_BYTES=8*1024*1024;
    private static final long MAX_APK_BYTES=32L*1024*1024;
    private static String hex(byte[] bytes){
        StringBuilder out=new StringBuilder(bytes.length*2);
        for(byte v:bytes)out.append(String.format(java.util.Locale.ROOT,"%02x",v&255));
        return out.toString();
    }
    private static long u32(byte[] b,int p){
        return (b[p]&255L)|((b[p+1]&255L)<<8)|((b[p+2]&255L)<<16)|((b[p+3]&255L)<<24);
    }
    private static int u16(byte[] b,int p){return (b[p]&255)|((b[p+1]&255)<<8);}
    private static byte[] read(InputStream in)throws Exception {
        try(ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] tmp=new byte[8192]; int n;
            while((n=in.read(tmp))!=-1) {
                if(out.size()+n>MAX_ENTRY_BYTES)throw new IllegalStateException("ENTRY_LIMIT");
                out.write(tmp,0,n);
            }
            return out.toByteArray();
        }
    }
    private static boolean dex(byte[] b){
        if(b.length<112 || b[0]!='d'||b[1]!='e'||b[2]!='x'||b[3]!=10
           ||b[7]!=0 || b[4]<'0'||b[4]>'9'||b[5]<'0'||b[5]>'9'
           ||b[6]<'0'||b[6]>'9'||u32(b,32)!=b.length
           ||u32(b,36)!=112 ||u32(b,40)!=0x12345678L)return false;
        try {
            MessageDigest sha=MessageDigest.getInstance("SHA-1"); // DEX format mandated checksum; not a security trust primitive.
            sha.update(b,32,b.length-32);
            byte[] signature=sha.digest();
            for(int i=0;i<20;i++)if(signature[i]!=b[12+i])return false;
            Adler32 checksum=new Adler32();checksum.update(b,12,b.length-12);
            return checksum.getValue()==u32(b,8);
        }catch(Exception failure){return false;}
    }
    private static String elf(byte[] b,String path){
        if(b.length<52 || b[0]!=127||b[1]!='E'||b[2]!='L'||b[3]!='F')
            return "FAIL_ELF_MAGIC";
        int bits=b[4]&255, endianness=b[5]&255, kind=u16(b,16),machine=u16(b,18);
        if(endianness!=1 || (bits!=1&&bits!=2) || (bits==2&&b.length<64))
            return "FAIL_ELF_ENDIAN_OR_CLASS";
        boolean arm32=path.startsWith("lib/armeabi-v7a/")&&bits==1&&machine==40;
        boolean arm64=path.startsWith("lib/arm64-v8a/")&&bits==2&&machine==183;
        return (kind==3&&(arm32||arm64))?"PASS_ELF_SHARED_ABI":"FAIL_ELF_ABI_OR_TYPE";
    }
    /** Uses local app package path, never enumerates or reads another app's private files. */
    public static String inspect(File apk){
        StringBuilder s=new StringBuilder("schema=rll.omega.apk-binary-inspection.v1\n"
             +"origin=APP_OWN_APK_BYTES_SELF_INSPECTION_NOT_EXTERNAL_ATTESTATION\n"
             +"scope=OWN_APK_ONLY_NO_EXTERNAL_FILE_SCAN\n"
             +"claim_allowed=false\n");
        if(apk==null||!apk.isFile()||apk.length()>MAX_APK_BYTES||apk.length()<64)
            return s.append("gate=TOKEN_VAZIO_APK_UNREADABLE_OR_SIZE_BOUND\n").toString();
        int entries=0,dexOk=0,elfOk=0,fail=0;boolean manifest=false;
        try(ZipFile archive=new ZipFile(apk)){
            Enumeration<? extends ZipEntry> members=archive.entries();
            while(members.hasMoreElements()){
                ZipEntry entry=members.nextElement();
                if(++entries>MAX_APK_ENTRIES)throw new IllegalStateException("ENTRY_COUNT_BOUND");
                String path=entry.getName();
                if(path.startsWith("/")||path.contains("..")||path.indexOf('\\')>=0)
                    throw new IllegalStateException("UNSAFE_APK_MEMBER_PATH");
                if(entry.isDirectory())continue;
                byte[] data;
                try(InputStream stream=archive.getInputStream(entry)){data=read(stream);}
                CRC32 crc=new CRC32();crc.update(data);
                boolean crcOk=(entry.getCrc()==crc.getValue()&&entry.getSize()==data.length);
                if(!crcOk)fail++;
                if(path.equals("AndroidManifest.xml"))manifest=true;
                if(path.matches("classes([0-9]+)?\\.dex")){
                    boolean ok=crcOk&&dex(data);
                    if(ok)dexOk++;else fail++;
                    s.append("dex=").append(path).append(";sha256=")
                      .append(hex(MessageDigest.getInstance("SHA-256").digest(data)))
                      .append(";gate=").append(ok?"PASS_DEX_HEADER_SHA1_ADLER32":"FAIL_DEX_CHECKSUM")
                      .append('\n');
                }else if(path.matches("lib/(armeabi-v7a|arm64-v8a)/[^/]+\\.so")){
                    String gate=crcOk?elf(data,path):"FAIL_ZIP_CRC";
                    if(gate.startsWith("PASS"))elfOk++;else fail++;
                    s.append("elf=").append(path).append(";sha256=")
                      .append(hex(MessageDigest.getInstance("SHA-256").digest(data)))
                      .append(";gate=").append(gate).append('\n');
                }
            }
            s.append("zip_entries=").append(entries).append("\nmanifest_present=").append(manifest)
             .append("\ndex_valid=").append(dexOk).append("\nelf_abi_valid=").append(elfOk)
             .append("\nfailed_checks=").append(fail).append('\n')
             .append("elf_dynamic_dependencies=TOKEN_VAZIO_NOT_DECODED\n");
            boolean ok=manifest&&dexOk>0&&elfOk>0&&fail==0;
            s.append("gate=").append(ok?"PASS_SCOPED_APK_DEX_ELF_CRC":"FAIL_BINARY_STRUCTURE").append('\n');
        }catch(Exception ex){
            s.append("gate=FAIL_OR_TOKEN_VAZIO_APK_INSPECT_")
             .append(ex.getClass().getSimpleName()).append('\n');
        }
        s.append("android_apksigner_v2_v3=TOKEN_VAZIO_NOT_VERIFIED\n");
        return s.toString();
    }
}
