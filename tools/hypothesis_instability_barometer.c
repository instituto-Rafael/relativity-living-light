#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NODES 128
#define MAX_EDGES 256
#define MAX_LINE 512
#define DIM_COUNT 10

static const char *DIM_NAMES[DIM_COUNT] = {
    "formal", "dimensional", "mechanism", "observable", "data",
    "covariance", "nested_limit", "stability", "falsifier", "reproduction"
};

typedef enum {
    ST_UNSET = -1,
    ST_CLOSED = 0,
    ST_PARTIAL = 500,
    ST_OPEN = 1000,
    ST_TOKEN_VAZIO = 1001
} GapState;

typedef struct {
    char id[24];
    char family[64];
    GapState gap[DIM_COUNT];
    int unknowns;
    int intrinsic;
    int tension;
    int barometer;
    const char *route;
} Node;

typedef struct {
    char from[24];
    char to[24];
    int weight;
} Edge;

typedef struct {
    int weights[DIM_COUNT];
    int execute_shadow_max;
    int formalize_max;
    int block_unknowns;
    Node nodes[MAX_NODES];
    size_t node_count;
    Edge edges[MAX_EDGES];
    size_t edge_count;
    uint64_t fingerprint;
} Config;

static char *trim(char *s) {
    while (isspace((unsigned char)*s)) s++;
    if (*s == '\0') return s;
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) *end-- = '\0';
    return s;
}

static void strip_comment(char *s) {
    char *p = strchr(s, '#');
    if (p) *p = '\0';
}

static int key_value(char *line, char **key, char **value) {
    char *colon = strchr(line, ':');
    if (!colon) return 0;
    *colon = '\0';
    *key = trim(line);
    *value = trim(colon + 1);
    return 1;
}

static int dim_index(const char *key) {
    for (int i = 0; i < DIM_COUNT; ++i) {
        if (strcmp(key, DIM_NAMES[i]) == 0) return i;
    }
    return -1;
}

static GapState parse_state(const char *s) {
    if (strcmp(s, "CLOSED") == 0) return ST_CLOSED;
    if (strcmp(s, "PARTIAL") == 0) return ST_PARTIAL;
    if (strcmp(s, "OPEN") == 0) return ST_OPEN;
    if (strcmp(s, "TOKEN_VAZIO") == 0) return ST_TOKEN_VAZIO;
    return ST_UNSET;
}

static int state_value(GapState s) {
    if (s == ST_TOKEN_VAZIO) return 1000;
    if (s == ST_UNSET) return 1000;
    return (int)s;
}

static uint64_t fnv1a_update(uint64_t h, const unsigned char *p, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        h ^= (uint64_t)p[i];
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static Node *find_node(Config *cfg, const char *id) {
    for (size_t i = 0; i < cfg->node_count; ++i) {
        if (strcmp(cfg->nodes[i].id, id) == 0) return &cfg->nodes[i];
    }
    return NULL;
}

static int parse_config(const char *path, Config *cfg) {
    memset(cfg, 0, sizeof(*cfg));
    cfg->execute_shadow_max = 360;
    cfg->formalize_max = 690;
    cfg->block_unknowns = 4;
    cfg->fingerprint = UINT64_C(1469598103934665603);

    FILE *fp = fopen(path, "rb");
    if (!fp) {
        fprintf(stderr, "cannot open config: %s\n", path);
        return 0;
    }

    enum { SEC_NONE, SEC_WEIGHTS, SEC_THRESHOLDS, SEC_HYPOTHESES, SEC_EDGES } section = SEC_NONE;
    Node *cur_node = NULL;
    Edge *cur_edge = NULL;
    char raw[MAX_LINE];

    while (fgets(raw, sizeof(raw), fp)) {
        cfg->fingerprint = fnv1a_update(cfg->fingerprint, (const unsigned char *)raw, strlen(raw));
        strip_comment(raw);
        char *line = trim(raw);
        if (*line == '\0') continue;

        if (strcmp(line, "weights:") == 0) { section = SEC_WEIGHTS; continue; }
        if (strcmp(line, "thresholds:") == 0) { section = SEC_THRESHOLDS; continue; }
        if (strcmp(line, "hypotheses:") == 0) { section = SEC_HYPOTHESES; continue; }
        if (strcmp(line, "edges:") == 0) { section = SEC_EDGES; continue; }

        if (section == SEC_HYPOTHESES && strncmp(line, "- id:", 5) == 0) {
            if (cfg->node_count >= MAX_NODES) {
                fprintf(stderr, "too many nodes\n");
                fclose(fp);
                return 0;
            }
            cur_node = &cfg->nodes[cfg->node_count++];
            memset(cur_node, 0, sizeof(*cur_node));
            for (int i = 0; i < DIM_COUNT; ++i) cur_node->gap[i] = ST_UNSET;
            char *v = trim(line + 5);
            snprintf(cur_node->id, sizeof(cur_node->id), "%s", v);
            continue;
        }

        if (section == SEC_EDGES && strncmp(line, "- from:", 7) == 0) {
            if (cfg->edge_count >= MAX_EDGES) {
                fprintf(stderr, "too many edges\n");
                fclose(fp);
                return 0;
            }
            cur_edge = &cfg->edges[cfg->edge_count++];
            memset(cur_edge, 0, sizeof(*cur_edge));
            char *v = trim(line + 7);
            snprintf(cur_edge->from, sizeof(cur_edge->from), "%s", v);
            continue;
        }

        char *key = NULL;
        char *value = NULL;
        if (!key_value(line, &key, &value)) continue;

        if (section == SEC_WEIGHTS) {
            int idx = dim_index(key);
            if (idx >= 0) cfg->weights[idx] = (int)strtol(value, NULL, 10);
            continue;
        }

        if (section == SEC_THRESHOLDS) {
            int v = (int)strtol(value, NULL, 10);
            if (strcmp(key, "execute_shadow_max") == 0) cfg->execute_shadow_max = v;
            else if (strcmp(key, "formalize_max") == 0) cfg->formalize_max = v;
            else if (strcmp(key, "block_unknowns") == 0) cfg->block_unknowns = v;
            continue;
        }

        if (section == SEC_HYPOTHESES && cur_node) {
            if (strcmp(key, "family") == 0) {
                snprintf(cur_node->family, sizeof(cur_node->family), "%s", value);
            } else {
                int idx = dim_index(key);
                if (idx >= 0) {
                    GapState st = parse_state(value);
                    if (st == ST_UNSET) {
                        fprintf(stderr, "invalid state %s for %s.%s\n", value, cur_node->id, key);
                        fclose(fp);
                        return 0;
                    }
                    cur_node->gap[idx] = st;
                }
            }
            continue;
        }

        if (section == SEC_EDGES && cur_edge) {
            if (strcmp(key, "to") == 0) snprintf(cur_edge->to, sizeof(cur_edge->to), "%s", value);
            else if (strcmp(key, "weight") == 0) cur_edge->weight = (int)strtol(value, NULL, 10);
        }
    }

    fclose(fp);

    if (cfg->node_count == 0) {
        fprintf(stderr, "no hypotheses configured\n");
        return 0;
    }

    int weight_sum = 0;
    for (int i = 0; i < DIM_COUNT; ++i) weight_sum += cfg->weights[i];
    if (weight_sum <= 0) {
        fprintf(stderr, "weight sum must be positive\n");
        return 0;
    }

    for (size_t n = 0; n < cfg->node_count; ++n) {
        Node *node = &cfg->nodes[n];
        long long acc = 0;
        node->unknowns = 0;
        for (int d = 0; d < DIM_COUNT; ++d) {
            if (node->gap[d] == ST_UNSET || node->gap[d] == ST_TOKEN_VAZIO) node->unknowns++;
            acc += (long long)cfg->weights[d] * state_value(node->gap[d]);
        }
        node->intrinsic = (int)(acc / weight_sum);
    }

    for (size_t e = 0; e < cfg->edge_count; ++e) {
        Edge *edge = &cfg->edges[e];
        if (!find_node(cfg, edge->from) || !find_node(cfg, edge->to) || edge->weight <= 0) {
            fprintf(stderr, "invalid edge %s -> %s\n", edge->from, edge->to);
            return 0;
        }
    }

    return 1;
}

static void compute_topology(Config *cfg) {
    for (size_t i = 0; i < cfg->node_count; ++i) {
        long long weighted_tension = 0;
        long long edge_weight_sum = 0;

        for (size_t e = 0; e < cfg->edge_count; ++e) {
            Edge *edge = &cfg->edges[e];
            Node *other = NULL;
            if (strcmp(edge->from, cfg->nodes[i].id) == 0) other = find_node(cfg, edge->to);
            else if (strcmp(edge->to, cfg->nodes[i].id) == 0) other = find_node(cfg, edge->from);
            if (!other) continue;

            int delta = cfg->nodes[i].intrinsic - other->intrinsic;
            if (delta < 0) delta = -delta;
            weighted_tension += (long long)edge->weight * delta;
            edge_weight_sum += edge->weight;
        }

        cfg->nodes[i].tension = edge_weight_sum ? (int)(weighted_tension / edge_weight_sum) : 0;
        cfg->nodes[i].barometer = (3 * cfg->nodes[i].intrinsic + cfg->nodes[i].tension) / 4;

        if (cfg->nodes[i].unknowns >= cfg->block_unknowns) {
            cfg->nodes[i].route = "BLOCKED_TOKEN_VAZIO";
        } else if (cfg->nodes[i].barometer <= cfg->execute_shadow_max) {
            cfg->nodes[i].route = "EXECUTE_SHADOW";
        } else if (cfg->nodes[i].barometer <= cfg->formalize_max) {
            cfg->nodes[i].route = "FORMALIZE_FIRST";
        } else {
            cfg->nodes[i].route = "BLOCKED_UNSTABLE";
        }
    }
}

static int write_json(const char *path, const Config *cfg) {
    FILE *fp = fopen(path, "wb");
    if (!fp) return 0;

    fprintf(fp, "{\n");
    fprintf(fp, "  \"schema\": \"rll.hypothesis-instability-barometer.result.v1\",\n");
    fprintf(fp, "  \"claim_allowed\": false,\n");
    fprintf(fp, "  \"config_fingerprint_fnv1a64\": \"%016llx\",\n", (unsigned long long)cfg->fingerprint);
    fprintf(fp, "  \"nodes\": [\n");
    for (size_t i = 0; i < cfg->node_count; ++i) {
        const Node *n = &cfg->nodes[i];
        fprintf(fp,
                "    {\"id\":\"%s\",\"family\":\"%s\",\"intrinsic\":%d,\"topology_tension\":%d,\"barometer\":%d,\"token_vazio_count\":%d,\"route\":\"%s\"}%s\n",
                n->id, n->family, n->intrinsic, n->tension, n->barometer, n->unknowns,
                n->route, (i + 1 == cfg->node_count) ? "" : ",");
    }
    fprintf(fp, "  ]\n}\n");
    fclose(fp);
    return 1;
}

static int write_matrix(const char *path, const Config *cfg) {
    FILE *fp = fopen(path, "wb");
    if (!fp) return 0;

    fprintf(fp, "{\"include\":[");
    int first = 1;
    for (size_t i = 0; i < cfg->node_count; ++i) {
        const Node *n = &cfg->nodes[i];
        if (strcmp(n->route, "EXECUTE_SHADOW") != 0) continue;
        if (!first) fputc(',', fp);
        fprintf(fp, "{\"id\":\"%s\",\"family\":\"%s\",\"barometer\":%d}", n->id, n->family, n->barometer);
        first = 0;
    }
    fprintf(fp, "]}\n");
    fclose(fp);
    return 1;
}

static int write_markdown(const char *path, const Config *cfg) {
    FILE *fp = fopen(path, "wb");
    if (!fp) return 0;

    fprintf(fp, "# RLL Hypothesis Instability Barometer\n\n");
    fprintf(fp, "`claim_allowed=false` · `TOKEN_VAZIO!=0` · fast triage only.\n\n");
    fprintf(fp, "| ID | Family | Intrinsic | Topology tension | Barometer | TOKEN_VAZIO | Route |\n");
    fprintf(fp, "|---|---|---:|---:|---:|---:|---|\n");
    for (size_t i = 0; i < cfg->node_count; ++i) {
        const Node *n = &cfg->nodes[i];
        fprintf(fp, "| %s | %s | %d | %d | %d | %d | %s |\n",
                n->id, n->family, n->intrinsic, n->tension, n->barometer, n->unknowns, n->route);
    }
    fprintf(fp, "\nThe score is an operational routing heuristic, not a probability, measurement, likelihood or scientific claim.\n");
    fclose(fp);
    return 1;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s CONFIG.yml RESULT.json MATRIX.json SUMMARY.md\n", argv[0]);
        return 64;
    }

    Config cfg;
    if (!parse_config(argv[1], &cfg)) return 65;
    compute_topology(&cfg);

    if (!write_json(argv[2], &cfg)) return 66;
    if (!write_matrix(argv[3], &cfg)) return 67;
    if (!write_markdown(argv[4], &cfg)) return 68;

    return 0;
}
