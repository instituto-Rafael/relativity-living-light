# Observatório Ambiental Distribuído por Telefones

## Campo geomagnético, pressão, GNSS, rádio, acústica e movimento

> **Status:** documento canônico de arquitetura e hipótese operacional.
>
> **Escopo:** organizar uma rede voluntária de telefones como conjunto de nós
> ambientais heterogêneos, calibrados e governados.
>
> **Gate:** `research_only` até validação contra instrumentos meteorológicos,
> geodésicos e radioelétricos de referência.

## 1. Invariante

```text
O ambiente produz muitas assinaturas.
Nenhuma assinatura isolada identifica sua causa.
```

A arquitetura deve preservar:

```text
medida bruta
→ contexto do aparelho
→ modelo físico esperado
→ resíduo
→ consenso espacial
→ hipótese
→ confiança
→ decisão governada
```

## 2. Correção terminológica geomagnética

Nas cartas náuticas e modelos geomagnéticos:

```text
isogônica = linha de igual declinação magnética
agônica    = linha de declinação zero
```

“Linha antagônica” não é o termo técnico padrão nesse domínio.

## 3. Referência geomagnética

O World Magnetic Model é referência de navegação e rumo. O WMM2025 foi
publicado em 17 de dezembro de 2024 e permanece válido até o fim de 2029.

Ele fornece:

- `F`: intensidade total;
- `H`: intensidade horizontal;
- `X`: componente norte;
- `Y`: componente leste;
- `Z`: componente vertical;
- `I`: inclinação;
- `D`: declinação.

A leitura real do telefone é uma soma:

\[
B_{observado}=B_{principal}+B_{crustal}+B_{disturbio}+B_{local}+B_{dispositivo}
\]

O WMM representa o campo principal e sua variação secular, não todas as fontes.

## 4. Telefone como nó heterogêneo

O Android define sensores ambientais, mas sua existência depende do fabricante.
Não se deve assumir que todos os aparelhos possuam:

- barômetro;
- temperatura ambiente;
- umidade relativa;
- sensor de luz com qualidade científica.

A temperatura da bateria é disponibilizada em muitos aparelhos como estado da
bateria. Ela não é temperatura ambiente.

## 5. Vetor de estado do nó

\[
x_i(t)=
[p,v,q,h,b_{clock},T_{battery},P_{charge},C_i,Q_i]
\]

onde:

- `p`: posição;
- `v`: velocidade;
- `q`: orientação;
- `h`: altitude e referência vertical;
- `b_clock`: erro de relógio;
- `T_battery`: temperatura da bateria;
- `P_charge`: estado de carga e alimentação;
- `C_i`: capacidades reais do aparelho;
- `Q_i`: qualidade e calibração.

## 6. Canais observáveis

### 6.1 Magnetômetro

- campo calibrado;
- campo não calibrado;
- hard-iron bias;
- orientação;
- resíduo relativo ao WMM;
- mapa magnético local.

### 6.2 Pressão

- pressão em hPa;
- tendência temporal;
- altitude relativa;
- referência externa;
- estado imóvel/móvel;
- ambiente pressurizado.

### 6.3 Temperatura e umidade

- temperatura ambiente somente quando sensor existir;
- umidade somente quando sensor existir;
- temperatura da bateria como variável de correção;
- luz e proximidade como contexto.

### 6.4 GNSS

- posição e incerteza;
- satélite e constelação;
- azimute e elevação;
- pseudodistância;
- Doppler;
- fase/ADR quando disponível;
- `C/N0`;
- AGC quando disponível;
- efeméride e relógio;
- resíduo troposférico sob controle adequado.

### 6.5 Wi-Fi e Bluetooth

- identidade pseudonimizada de âncora;
- frequência e canal;
- RSSI;
- RTT quando suportado;
- CSI somente quando legitimamente acessível;
- Channel Sounding ou Direction Finding quando suportados;
- piso de ruído;
- erro e retransmissão sem conteúdo de payload.

### 6.6 Rede celular

- Cell ID/PCI/TAC sob política de privacidade;
- RSRP, RSRQ, SINR;
- frequência/banda;
- timing advance quando disponibilizado;
- banco de âncoras autorizado.

### 6.7 Acústica

- clique, chirp ou sequência codificada;
- resposta impulsiva;
- tempo de retorno;
- qualidade do eco;
- temperatura/umidade para velocidade do som.

### 6.8 IMU

- aceleração;
- rotação;
- gravidade;
- movimento do observador;
- mudança de pose;
- detecção de elevador, veículo e caminhada.

## 7. O resíduo como unidade central

Para cada canal:

\[
r_{i,k,t}=z_{i,k,t}-\widehat{z}_{i,k,t}
\]

O esperado deve considerar:

```text
local
+ horário
+ data
+ altitude
+ orientação
+ modelo do telefone
+ estado térmico
+ estado de carga
+ ambiente interno/externo
+ referência física
```

Não se deve usar um baseline único para toda a cidade ou para todos os aparelhos.

## 8. Linhas isogônicas e mapa residual

O WMM permite calcular declinação e demais componentes para posição, altitude e
data. O magnetômetro mede o campo total local.

```text
campo medido
− WMM
− bias do dispositivo
− orientação
→ resíduo magnético local
```

Esse resíduo pode refletir estrutura metálica, campo crustal, corrente elétrica,
ímã local ou distúrbio geomagnético. Meteorologia não deve ser inferida sem
outros canais.

## 9. Pressão, altitude e clima

A pressão pode variar porque o aparelho:

- subiu;
- desceu;
- entrou em elevador;
- entrou em veículo pressurizado;
- mudou de prédio;
- experimentou vento local;
- sofreu mudança meteorológica.

O canal deve declarar sua interpretação:

```text
altitude_relative
weather_pressure
unknown_mixture
```

`unknown_mixture` não pode ser promovido automaticamente a meteorologia.

## 10. Nuvens, chuva e rádio

Dia nublado e chuva podem coincidir com mudanças de rádio, mas não existe regra
universal “nuvem altera noise floor desta forma”.

O piso de ruído também depende de:

- outros transmissores;
- controle automático de ganho;
- micro-ondas;
- Bluetooth;
- motores;
- fontes elétricas;
- tráfego;
- interferência;
- descarga atmosférica.

Atenuação por chuva é especialmente relevante em enlaces de micro-ondas altos e
caminhos longos. Em Wi-Fi curto de 2,4/5 GHz, o efeito meteorológico pode ser
menor que os confundidores locais.

## 11. GNSS meteorológico

A atmosfera introduz atraso nos sinais GNSS. Redes geodésicas estimam atraso
troposférico e vapor d’água precipitável.

A rede de telefones pode investigar esse canal, mas deve registrar:

```text
smartphone_GNSS
≠
geodetic_GNSS_station
```

Fatores críticos:

- antena;
- orientação;
- multipercurso;
- relógio;
- continuidade de fase;
- qualidade da efeméride;
- dupla frequência;
- acesso a medidas brutas.

## 12. Campo cooperativo

Um evento só ganha força quando aparece de modo coerente em vários nós:

\[
R_k(t,\Omega)=\sum_i W_i r_{i,k,t}
\]

onde \(W_i\) depende de:

- calibração;
- contexto;
- qualidade temporal;
- estabilidade histórica;
- proximidade de referência;
- consistência com vizinhos;
- disponibilidade do sensor.

## 13. Tempestades

### 13.1 Defensável

Uma rede barométrica densa pode enriquecer campos de pressão hiperlocais e
contribuir para *nowcasting* terrestre quando assimilada com fontes oficiais.

### 13.2 Hipótese

A fusão de pressão, GNSS, RF, luz, acústica e movimento pode produzir ganho
incremental de detecção ou antecedência para eventos convectivos locais.

### 13.3 Não demonstrado

```text
rede de telefones
→ previsão autônoma de furacão horas antes
```

Ciclones tropicais se formam frequentemente sobre oceanos, fora da cobertura de
telefones. Previsão exige satélites, radar, boias, navios, aeronaves,
dropsondes, observação oceânica e modelos numéricos.

A rede telefônica pode contribuir na aproximação e landfall, mas o ganho deve
ser comparado a alertas oficiais que já operam em horizontes de dezenas de
horas.

## 14. Pipeline operacional

```text
CAPABILITY_DISCOVERY
→ RAW_ACQUISITION
→ TIME_ALIGNMENT
→ DEVICE_CALIBRATION
→ SELF_MOTION_COMPENSATION
→ PHYSICAL_REFERENCE
→ RESIDUAL_EXTRACTION
→ NODE_QUALITY
→ SPATIAL_CONSENSUS
→ OFFICIAL_DATA_ASSIMILATION
→ HYPOTHESIS
→ FALSIFIER_CHECK
→ HUMAN_REVIEW
```

## 15. Deep learning

Uso permitido:

- classificação de regime;
- modelagem de deriva;
- detecção de anomalia;
- aprendizado de qualidade;
- fusão temporal;
- adaptação entre aparelhos.

Uso bloqueado:

- identificar pessoa a partir de perturbação ambiental;
- interpretar payload de comunicação;
- inventar dado ausente;
- declarar causa sem evidência cruzada;
- emitir alerta público sem validação operacional.

## 16. Matrix Semântica 7D

| Direção | Aplicação |
|---|---|
| D1 lexical | isogônica, agônica, pressão, altitude, ruído |
| D2 domínio | geomagnetismo, meteorologia, GNSS, RF, acústica |
| D3 isogônica | convergência de resíduos coerentes |
| D4 antagônica | confundidores e hipóteses rivais |
| D5 causal-temporal | trajetória, tendência e atraso |
| D6 epistêmica | medida, hipótese, lacuna, contradição |
| D7 operacional | privacidade, segurança, alerta e auditoria |

## 17. TOKEN_VAZIO aplicado

```text
ambient_temperature_sensor = TOKEN_VAZIO quando ausente
relative_humidity = TOKEN_VAZIO quando não medida
weather_cause = TOKEN_VAZIO quando pressão mistura altitude
hurricane_lead_time_gain = TOKEN_VAZIO até estudo comparativo
person_identity = BLOCKED_NOT_INFERRED
```

## 18. Privacidade

A rede deve usar:

- adesão voluntária;
- pseudônimos rotativos;
- agregação espacial;
- processamento local;
- retenção mínima;
- ausência de conteúdo de pacote;
- proibição de rastreamento individual;
- finalidade explícita;
- logs auditáveis;
- direito de retirada.

## 19. Artefatos

- `docs/canonicos/32_OBSERVATORIO_AMBIENTAL_DISTRIBUIDO_TELEFONES.md`
- `schemas/ambient_field_observation.schema.json`
- `fixtures/ambient_field_observation.example.json`
- `rafaelmeloreisnovo/papers/docs/perception-memory/04_DISTRIBUTED_PHONE_ENVIRONMENTAL_OBSERVATORY.md`

## 20. Fontes e referências

1. NOAA NCEI Geomagnetic Modeling Team; British Geological Survey. *World
   Magnetic Model 2025*. <https://doi.org/10.25921/aqfd-sd83>
2. Chulliat, A. et al. *The US/UK World Magnetic Model for 2025–2030*.
   <https://doi.org/10.25923/prbc-s316>
3. NOAA/NCEI. World Magnetic Model.
   <https://www.ncei.noaa.gov/products/world-magnetic-model>
4. Android Developers. Environment sensors.
   <https://developer.android.com/develop/sensors-and-location/sensors/sensors_environment>
5. Android Developers. Sensor API.
   <https://developer.android.com/reference/android/hardware/Sensor>
6. Android Developers. BatteryManager.
   <https://developer.android.com/reference/android/os/BatteryManager>
7. Vaquero-Martínez, J., & Antón, M. (2024). GNSS meteorology and water
   vapor. <https://arxiv.org/abs/2401.12148>
8. Chakraborty, A., Lahiri, S. N., & Wilson, A. (2019). Noisy crowdsourced
   weather data. <https://arxiv.org/abs/1902.06183>
9. Monteiro, M., & Marti, A. C. (2016). Smartphone pressure sensors and
   vertical motion. <https://arxiv.org/abs/1607.00363>
10. Olsson, G. K. et al. (2023). Participatory GNSS jammer localization.
    <https://arxiv.org/abs/2305.02038>
11. ITU-R P.838. Specific attenuation model for rain.
    <https://www.itu.int/rec/R-REC-P.838/>
12. National Hurricane Center. <https://www.nhc.noaa.gov/aboutintro.shtml>
13. NASA CYGNSS. <https://www.nasa.gov/missions/cygnss/>

## 21. Estados epistêmicos

| Alegação | Estado |
|---|---|
| WMM calcula campo principal | `VERIFIED` |
| sensores Android são opcionais | `VERIFIED` |
| bateria pode aquecer a leitura contextual | `VERIFIED_CONTEXT` |
| GNSS permite meteorologia de atraso | `VERIFIED_METHOD` |
| crowdsourcing pode melhorar granularidade | `SUPPORTED` |
| nuvem determina noise floor | `HYPOTHESIS_LOCAL` |
| telefones preveem furacão sozinhos | `NOT_SUPPORTED` |
| ganho de antecedência hiperlocal | `TOKEN_VAZIO` |

## 22. Síntese

```text
Muitos sensores imperfeitos
não formam automaticamente um instrumento perfeito.

Mas sensores calibrados,
ancorados em modelos físicos,
com resíduos auditáveis,
podem formar um observatório probabilístico distribuído.
```
