# Android build contract

## Decisão estrutural

Este repositório deve conter o app Android mínimo porque já possui uma ponte Java/C em `core/lowlevel_runtime` e o contrato Android precisa validar essa integração nativa no mesmo grafo de build. O módulo `:app` é a fonte de verdade para empacotar a biblioteca JNI `rll_kernel_bridge` com NDK/CMake.

## Estrutura Android adicionada

- `settings.gradle` inclui o módulo `:app` e repositórios oficiais Gradle/Android.
- `build.gradle` raiz fixa o Android Gradle Plugin.
- `gradle/wrapper/gradle-wrapper.jar` é versionado e validado pelo `setup-gradle`; o SHA-256 oficial do Wrapper 8.10.2 é `2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046`.
- O script `gradlew` carrega esse JAR com `-classpath` e executa `org.gradle.wrapper.GradleWrapperMain`; **não** executa o JAR com `java -jar` (o JAR oficial não declara `Main-Class` no manifesto).
- `app/build.gradle` declara SDK, NDK, CMake, ABIs, trilhas debug/release e assinatura externa.
- `app/src/main/AndroidManifest.xml` declara a aplicação e a `MainActivity` de validação nativa.
- `app/src/main/java/org/rafaelia/rll/KernelBridge.java` carrega `rll_kernel_bridge` e expõe JNI.
- `app/src/main/cpp/CMakeLists.txt` compila `rll_jni.c` junto com `core/lowlevel_runtime/c/kernel_bridge.c`.

## ABIs suportadas

A matriz Android oficial deste repositório é:

- `armeabi-v7a`
- `arm64-v8a`

As mesmas ABIs são declaradas em `defaultConfig.externalNativeBuild.cmake.abiFilters` e `defaultConfig.ndk.abiFilters`. Não adicione outra ABI sem atualizar Gradle, CI e esta documentação no mesmo commit.

## Trilhas de build

### Debug / validação interna

Use debug para validação interna e smoke test do runtime nativo. Se `gradle/wrapper/gradle-wrapper.jar` estiver ausente por corrupção de checkout, restaure-o do Git; para recuperação controlada, gere-o com:

```bash
ANDROID_HOME=/opt/android-sdk JAVA_HOME=/path/to/jdk-21 scripts/bootstrap-gradle-wrapper.sh
ANDROID_HOME=/opt/android-sdk JAVA_HOME=/path/to/jdk-21 ./gradlew --no-daemon :app:assembleDebug :app:assembleValidationUnsigned
```

Artefato esperado:

- `app/build/outputs/apk/debug/app-debug.apk`
- `app/build/outputs/apk/validationUnsigned/app-validationUnsigned-unsigned.apk`

### Release assinado / entrega oficial

Release oficial exige keystore externo. Não há keystore versionado no Git. Configure por variáveis de ambiente ou propriedades Gradle externas:

```bash
export RLL_RELEASE_STORE_FILE=/secure/path/release.jks
export RLL_RELEASE_STORE_PASSWORD='***'
export RLL_RELEASE_KEY_ALIAS='***'
export RLL_RELEASE_KEY_PASSWORD='***'
ANDROID_HOME=/opt/android-sdk JAVA_HOME=/path/to/jdk-21 scripts/bootstrap-gradle-wrapper.sh
ANDROID_HOME=/opt/android-sdk JAVA_HOME=/path/to/jdk-21 ./gradlew --no-daemon :app:assembleRelease :app:bundleRelease
```

Artefatos esperados:

- `app/build/outputs/apk/release/app-release.apk`
- `app/build/outputs/bundle/release/app-release.aab`

Se qualquer secret de assinatura estiver ausente, `:app:packageRelease` falha por contrato. Isso evita transformar release oficial em unsigned por conveniência.

## GitHub Actions

O workflow `.github/workflows/android-build.yml` executa:

1. checkout;
2. setup JDK 17;
3. setup Gradle e validação do Gradle Wrapper JAR versionado; geração local somente se o JAR estiver ausente e o ambiente permitir bootstrap;
4. setup Android SDK, NDK `27.2.12479018` e CMake `3.22.1`;
5. build debug e validation unsigned;
6. build release assinado somente quando todos os secrets existem;
7. upload dos APKs/AABs por `actions/upload-artifact@v4`.

Secrets esperados para release no GitHub Actions:

- `RLL_RELEASE_KEYSTORE_BASE64`
- `RLL_RELEASE_STORE_PASSWORD`
- `RLL_RELEASE_KEY_ALIAS`
- `RLL_RELEASE_KEY_PASSWORD`

## Validação nativa

A `MainActivity` chama `KernelBridge.archDetect()` e `KernelBridge.kernelScore(...)`. Em ARM32, `archDetect()` deve retornar `32`; em ARM64, deve retornar `64`. Isso valida a fronteira Java → JNI → C sem chamadas por elemento em hot path real.
