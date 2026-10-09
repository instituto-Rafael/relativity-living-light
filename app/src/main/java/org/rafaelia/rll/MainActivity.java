package org.rafaelia.rll;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Hosted Android diagnostic surface for the existing JNI/C kernel.
 *
 * This is not a cosmology solver or freestanding L0. It requires the Android
 * framework; numerical truth comes from the native kernel, with a separate
 * Java expectation for small, overflow-safe input values.
 */
public final class MainActivity extends Activity {
    private static final int PAPER = Color.rgb(17, 24, 39);
    private static final int SURFACE = Color.rgb(31, 41, 55);
    private static final int TEXT = Color.rgb(249, 250, 251);
    private static final int MUTED = Color.rgb(209, 213, 219);
    private static final int PASS = Color.rgb(134, 239, 172);
    private static final int FAIL = Color.rgb(253, 164, 175);
    private static final int ACCENT = Color.rgb(147, 197, 253);
    private static final int LIMIT = 10000;

    private TextView status;
    private TextView runtime;
    private TextView checks;
    private TextView manualResult;
    private EditText inputX;
    private EditText inputY;
    private String diagnosticReceipt = "";
    private String manualReceipt = "";

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private TextView label(LinearLayout parent, String value, int sizeSp, int color, boolean bold) {
        TextView text = new TextView(this);
        text.setText(value);
        text.setTextSize(sizeSp);
        text.setTextColor(color);
        if (bold) {
            text.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        }
        text.setPadding(0, dp(5), 0, dp(5));
        text.setTextIsSelectable(true);
        parent.addView(text);
        return text;
    }

    private LinearLayout section(LinearLayout root, String heading) {
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16), dp(14), dp(16), dp(16));
        panel.setBackgroundColor(SURFACE);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, 0, 0, dp(12));
        root.addView(panel, params);
        label(panel, heading, 18, TEXT, true);
        return panel;
    }

    private Button action(LinearLayout parent, String title, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(title);
        button.setAllCaps(false);
        button.setTextSize(15);
        button.setOnClickListener(listener);
        parent.addView(button, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        return button;
    }

    private EditText field(LinearLayout parent, String title, String initial) {
        label(parent, title, 14, MUTED, false);
        EditText edit = new EditText(this);
        edit.setSingleLine(true);
        edit.setText(initial);
        edit.setTextColor(TEXT);
        edit.setHintTextColor(MUTED);
        edit.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_SIGNED);
        parent.addView(edit, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        return edit;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(PAPER);
        getWindow().setNavigationBarColor(PAPER);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(PAPER);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(20), dp(16), dp(24));
        scroll.addView(root);

        label(root, "RLL • Diagnóstico nativo", 25, TEXT, true);
        label(root, "Java ↔ JNI ↔ núcleo C  |  ARM32 / ARM64", 14, MUTED, false);

        LinearLayout statusPanel = section(root, "01  Estado da execução");
        status = label(statusPanel, "Não aferido", 17, MUTED, true);
        runtime = label(statusPanel, "Leitura local aguardando execução", 14, MUTED, false);
        action(statusPanel, "Executar verificações", v -> runDiagnostics());

        LinearLayout samplePanel = section(root, "02  Testes de fronteira JNI");
        checks = label(samplePanel, "Não executados", 14, MUTED, false);
        label(samplePanel, "Entradas pequenas e determinísticas; comparação Java × C.", 13, MUTED, false);

        LinearLayout manualPanel = section(root, "03  Explorar o kernel");
        label(manualPanel, "score = ((x × 31) XOR (y × 17)) + arquitetura", 14, ACCENT, true);
        inputX = field(manualPanel, "Valor x (−10000 a 10000)", "7");
        inputY = field(manualPanel, "Valor y (−10000 a 10000)", "11");
        manualResult = label(manualPanel, "Escolha valores e execute", 14, MUTED, false);
        action(manualPanel, "Calcular no núcleo C", v -> runManual());

        LinearLayout evidencePanel = section(root, "04  Evidências e limites");
        label(evidencePanel, "Aferido aqui: ABI, chamada JNI, resultado C e invariantes de quatro casos.", 14, TEXT, false);
        label(evidencePanel, "Não aferido: instalação em outros aparelhos, cosmologia, CLASS/CAMB, GPS, sensores, assinatura de release ou modo freestanding completo.", 14, MUTED, false);
        label(evidencePanel, "Nenhuma conexão de rede, permissão adicional ou envio automático de dados.", 13, ACCENT, false);
        action(evidencePanel, "Copiar recibo local", v -> copyReceipt());

        new FormulaLabView(this).attach(root);
        new ReleaseGateView(this).attach(root);
        setContentView(scroll);
        runDiagnostics();
    }

    private static int expectedScore(int arch, int x, int y) {
        return ((x * 31) ^ (y * 17)) + arch;
    }

    private static String abiDescription(int arch) {
        if (arch == 32) return "ARM32";
        if (arch == 64) return "ARM64";
        return "Desconhecida (" + arch + ")";
    }

    private void runDiagnostics() {
        final int[][] vectors = {{0, 0}, {7, 11}, {1, 1}, {12, 21}};
        StringBuilder receipt = new StringBuilder();
        receipt.append("RLL native diagnostic v1\n");
        receipt.append("scope=LOCAL_ANDROID_JNI_C_ONLY\n");
        receipt.append("claim_allowed=false\n");
        receipt.append("source=live_app_runtime_not_GitHub_CI\n");
        try {
            int arch = KernelBridge.archDetect();
            String abi = Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "TOKEN_VAZIO";
            boolean known = arch == 32 || arch == 64;
            StringBuilder rows = new StringBuilder();
            int passed = 0;
            for (int[] pair : vectors) {
                int observed = KernelBridge.kernelScore(pair[0], pair[1]);
                int expected = expectedScore(arch, pair[0], pair[1]);
                boolean equal = observed == expected;
                if (equal) passed++;
                rows.append("x=").append(pair[0]).append("  y=").append(pair[1])
                    .append("  C=").append(observed)
                    .append("  Java=").append(expected)
                    .append(equal ? "  OK\n" : "  FALHA\n");
                receipt.append("vector=").append(pair[0]).append(",").append(pair[1])
                    .append(";observed=").append(observed)
                    .append(";expected=").append(expected)
                    .append(";pass=").append(equal).append("\n");
            }
            boolean allPass = known && passed == vectors.length;
            status.setText(allPass ? "PASS • 4/4 verificações nativas" : "ATENÇÃO • diagnóstico incompleto");
            status.setTextColor(allPass ? PASS : FAIL);
            runtime.setText("Núcleo C: " + abiDescription(arch) + " (" + arch + ")\n"
                    + "ABI Android: " + abi + "\n"
                    + "Ponte: JNI carregada; testes " + passed + "/" + vectors.length);
            checks.setText(rows.toString().trim());
            receipt.append("arch=").append(arch).append("\nandroid_abi=").append(abi).append("\n");
            receipt.append("gate=").append(allPass ? "PASS_SCOPED" : "FAIL_SCOPED").append("\n");
        } catch (LinkageError | RuntimeException error) {
            status.setText("FALHA • ponte JNI indisponível");
            status.setTextColor(FAIL);
            runtime.setText("Falha no carregamento ou execução do núcleo C: "
                    + error.getClass().getSimpleName());
            checks.setText("TOKEN_VAZIO_RUNTIME_EXECUTION");
            receipt.append("gate=FAIL_JNI\nerror_type=")
                    .append(error.getClass().getSimpleName()).append("\n");
        }
        diagnosticReceipt = receipt.toString();
    }

    private void runManual() {
        try {
            int x = Integer.parseInt(inputX.getText().toString().trim());
            int y = Integer.parseInt(inputY.getText().toString().trim());
            if (x < -LIMIT || x > LIMIT || y < -LIMIT || y > LIMIT) {
                manualResult.setText("Entrada fora do intervalo seguro: −10000 a 10000.");
                manualResult.setTextColor(FAIL);
                manualReceipt = "";
                return;
            }
            int arch = KernelBridge.archDetect();
            int observed = KernelBridge.kernelScore(x, y);
            int expected = expectedScore(arch, x, y);
            boolean match = (arch == 32 || arch == 64) && observed == expected;
            manualResult.setText("C=" + observed + "   referência Java=" + expected
                    + (match ? "   PASS" : "   FALHA"));
            manualResult.setTextColor(match ? PASS : FAIL);
            manualReceipt = "manual_x=" + x + ";manual_y=" + y + ";native_score="
                    + observed + ";reference=" + expected + ";match=" + match + "\n";
        } catch (NumberFormatException error) {
            manualResult.setText("Digite dois números inteiros válidos.");
            manualResult.setTextColor(FAIL);
            manualReceipt = "";
        } catch (LinkageError | RuntimeException error) {
            manualResult.setText("TOKEN_VAZIO_RUNTIME_EXECUTION: "
                    + error.getClass().getSimpleName());
            manualResult.setTextColor(FAIL);
            manualReceipt = "";
        }
    }

    private void copyReceipt() {
        String payload = diagnosticReceipt + manualReceipt
                + "device_install_proof=TOKEN_VAZIO_NOT_ATTESTED\n"
                + "scientific_validation=TOKEN_VAZIO_NOT_RUN\n";
        ClipboardManager clipboard = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("RLL diagnostic receipt", payload));
            Toast.makeText(this, "Recibo local copiado", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Área de transferência indisponível", Toast.LENGTH_SHORT).show();
        }
    }
}
