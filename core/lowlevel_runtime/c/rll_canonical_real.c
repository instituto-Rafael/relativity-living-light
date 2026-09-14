#include "rll_canonical_real.h"

#define RLL_C_KMS 299792.458
#define RLL_PI 3.1415926535897932384626433832795
#define RLL_LN2 0.69314718055994530941723212145818
#define RLL_LN10 2.3025850929940456840179914546844
#define RLL_EPS 1.0e-14
#define RLL_BIG 1.0e300

static double rll_abs(double x) { return x < 0.0 ? -x : x; }
static int rll_is_finite(double x) { return (x == x) && (x < RLL_BIG) && (x > -RLL_BIG); }
static double rll_clamp(double x, double lo, double hi) { return x < lo ? lo : (x > hi ? hi : x); }

static double rll_sqrt(double x) {
    double g;
    rll_u32 i;
    if (!(x > 0.0)) return x == 0.0 ? 0.0 : -1.0;
    g = x > 1.0 ? x : 1.0;
    for (i = 0u; i < 28u; ++i) g = 0.5 * (g + x / g);
    return g;
}

static double rll_cbrt(double x) {
    double g = 1.0;
    rll_u32 i;
    if (x == 0.0) return 0.0;
    if (x < 0.0) return -rll_cbrt(-x);
    while (g * g * g < x && g < 1.0e100) g *= 2.0;
    while ((g * 0.5) * (g * 0.5) * (g * 0.5) > x) g *= 0.5;
    for (i = 0u; i < 24u; ++i) g = (2.0 * g + x / (g * g)) / 3.0;
    return g;
}

static double rll_exp(double x) {
    double term = 1.0;
    double sum = 1.0;
    double scale = 1.0;
    rll_u32 i;
    x = rll_clamp(x, -60.0, 60.0);
    while (x > RLL_LN2) { x -= RLL_LN2; scale *= 2.0; }
    while (x < -RLL_LN2) { x += RLL_LN2; scale *= 0.5; }
    for (i = 1u; i <= 18u; ++i) {
        term *= x / (double)i;
        sum += term;
    }
    return sum * scale;
}

static double rll_log(double x) {
    double y;
    double y2;
    double term;
    double sum;
    double k = 0.0;
    rll_u32 n;
    if (!(x > 0.0)) return -RLL_BIG;
    while (x > 1.5) { x *= 0.5; k += 1.0; }
    while (x < 0.75) { x *= 2.0; k -= 1.0; }
    y = (x - 1.0) / (x + 1.0);
    y2 = y * y;
    term = y;
    sum = 0.0;
    for (n = 1u; n <= 31u; n += 2u) {
        sum += term / (double)n;
        term *= y2;
    }
    return 2.0 * sum + k * RLL_LN2;
}

static double rll_pow_pos(double x, double p) {
    if (!(x > 0.0)) return -1.0;
    return rll_exp(p * rll_log(x));
}

static double rll_transition(double z, const rll_cosmo_params *p) {
    double width = p->transition_width;
    double arg;
    if (!(width > 0.0)) return -1.0;
    arg = rll_clamp((z - p->z_transition) / width, -60.0, 60.0);
    return 1.0 / (1.0 + rll_exp(arg));
}

static double rll_e2(double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    double zp1 = 1.0 + z;
    double matter;
    double radiation;
    double ol;
    double fz;
    double e2;
    if (!p || z < 0.0 || !(p->omega_m > 0.0) || !(p->h0 > 0.0)) {
        if (status) *status |= RLL_RUN_MODEL_DOMAIN;
        return -1.0;
    }
    matter = p->omega_m * zp1 * zp1 * zp1;
    radiation = p->omega_r * zp1 * zp1 * zp1 * zp1;
    if (model == RLL_MODEL_LCDM) {
        e2 = matter + radiation + (1.0 - p->omega_m - p->omega_r);
    } else if (model == RLL_MODEL_LOGISTIC) {
        fz = rll_transition(z, p);
        ol = 1.0 - p->omega_m - p->omega_r - p->omega_s0;
        e2 = matter + radiation + ol + p->omega_s0 * (fz + (1.0 - fz) * zp1 * zp1 * zp1);
    } else {
        if (status) *status |= RLL_RUN_MODEL_DOMAIN;
        return -1.0;
    }
    if (!(e2 > 0.0) || !rll_is_finite(e2)) {
        if (status) *status |= RLL_RUN_MODEL_DOMAIN;
        return -1.0;
    }
    return e2;
}

static double rll_e(double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    double e2 = rll_e2(z, p, model, status);
    return e2 > 0.0 ? rll_sqrt(e2) : -1.0;
}

static double rll_comoving_distance(double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    rll_u32 n;
    rll_u32 i;
    double xmax;
    double h;
    double sum;
    if (!(z >= 0.0) || !p || !(p->h0 > 0.0)) {
        if (status) *status |= RLL_RUN_BAD_INPUT;
        return -1.0;
    }
    if (z == 0.0) return 0.0;
    n = p->integration_steps;
    if (n < 128u) n = 128u;
    if (n > 4096u) n = 4096u;
    if (n & 1u) ++n;
    xmax = rll_log(1.0 + z);
    h = xmax / (double)n;
    sum = 0.0;
    for (i = 0u; i <= n; ++i) {
        double x = h * (double)i;
        double zp1 = rll_exp(x);
        double zi = zp1 - 1.0;
        double ei = rll_e(zi, p, model, status);
        double integrand;
        double w;
        if (!(ei > 0.0)) return -1.0;
        integrand = zp1 / ei;
        w = (i == 0u || i == n) ? 1.0 : ((i & 1u) ? 4.0 : 2.0);
        sum += w * integrand;
    }
    return (RLL_C_KMS / p->h0) * (h / 3.0) * sum;
}

static double rll_omega_m_z(double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    double zp1 = 1.0 + z;
    double e2 = rll_e2(z, p, model, status);
    if (!(e2 > 0.0)) return -1.0;
    return p->omega_m * zp1 * zp1 * zp1 / e2;
}

static double rll_growth_factor(double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    rll_u32 n = p->integration_steps;
    rll_u32 i;
    double xmax;
    double h;
    double sum = 0.0;
    if (n < 128u) n = 128u;
    if (n > 2048u) n = 2048u;
    if (n & 1u) ++n;
    xmax = rll_log(1.0 + z);
    h = xmax / (double)n;
    for (i = 0u; i <= n; ++i) {
        double x = h * (double)i;
        double zi = rll_exp(x) - 1.0;
        double omz = rll_omega_m_z(zi, p, model, status);
        double f;
        double w;
        if (!(omz > 0.0)) return -1.0;
        f = rll_pow_pos(omz, p->growth_gamma);
        w = (i == 0u || i == n) ? 1.0 : ((i & 1u) ? 4.0 : 2.0);
        sum += w * f;
    }
    return rll_exp(-(h / 3.0) * sum);
}

rll_cosmo_params rll_params_fase18e_map(void) {
    rll_cosmo_params p;
    p.h0 = 66.99367300987414;
    p.omega_m = 0.32475606452625294;
    p.omega_b = 0.04993606066218619;
    p.omega_r = 9.18e-5;
    p.omega_s0 = 0.011594905594391598;
    p.z_transition = 11.452558895186602;
    p.transition_width = 0.22656819958262459;
    p.sigma8_0 = 0.811;
    p.growth_gamma = 0.55;
    p.rd_mpc = 148.98654354573253;
    p.rs_star_mpc = 142.91992714632195;
    p.sn_magnitude_offset = 0.0;
    p.integration_steps = 1024u;
    return p;
}

rll_cosmo_params rll_params_fase18e_lcdm(void) {
    rll_cosmo_params p;
    p.h0 = 67.66725167785673;
    p.omega_m = 0.3162598585368923;
    p.omega_b = 0.04900975504762562;
    p.omega_r = 9.18e-5;
    p.omega_s0 = 0.0;
    p.z_transition = 1.0;
    p.transition_width = 0.3;
    p.sigma8_0 = 0.811;
    p.growth_gamma = 0.55;
    p.rd_mpc = 149.8314329013423;
    p.rs_star_mpc = 143.67973843293154;
    p.sn_magnitude_offset = 0.0;
    p.integration_steps = 1024u;
    return p;
}

double rll_predict_observable(rll_u32 observable, double z, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    double e;
    double dc;
    double dh;
    if (!p) {
        if (status) *status |= RLL_RUN_BAD_INPUT;
        return -1.0;
    }
    if (observable == RLL_OBS_HZ_KM_S_MPC) {
        e = rll_e(z, p, model, status);
        return e > 0.0 ? p->h0 * e : -1.0;
    }
    if (observable == RLL_OBS_FSIGMA8) {
        double omz = rll_omega_m_z(z, p, model, status);
        double f = omz > 0.0 ? rll_pow_pos(omz, p->growth_gamma) : -1.0;
        double d = rll_growth_factor(z, p, model, status);
        return (f > 0.0 && d > 0.0) ? f * p->sigma8_0 * d : -1.0;
    }
    if (observable == RLL_OBS_BAO_DH_OVER_RD) {
        e = rll_e(z, p, model, status);
        if (!(e > 0.0) || !(p->rd_mpc > 0.0)) return -1.0;
        return (RLL_C_KMS / (p->h0 * e)) / p->rd_mpc;
    }
    if (observable == RLL_OBS_BAO_DM_OVER_RD || observable == RLL_OBS_BAO_DV_OVER_RD) {
        if (!(p->rd_mpc > 0.0)) return -1.0;
        dc = rll_comoving_distance(z, p, model, status);
        if (!(dc >= 0.0)) return -1.0;
        if (observable == RLL_OBS_BAO_DM_OVER_RD) return dc / p->rd_mpc;
        e = rll_e(z, p, model, status);
        if (!(e > 0.0)) return -1.0;
        dh = RLL_C_KMS / (p->h0 * e);
        return rll_cbrt(z * dc * dc * dh) / p->rd_mpc;
    }
    if (observable == RLL_OBS_CMB_R || observable == RLL_OBS_CMB_LA) {
        dc = rll_comoving_distance(z, p, model, status);
        if (!(dc > 0.0)) return -1.0;
        if (observable == RLL_OBS_CMB_R) return rll_sqrt(p->omega_m) * p->h0 * dc / RLL_C_KMS;
        if (!(p->rs_star_mpc > 0.0)) return -1.0;
        return RLL_PI * dc / p->rs_star_mpc;
    }
    if (observable == RLL_OBS_CMB_OBH2) {
        double h100 = p->h0 / 100.0;
        return p->omega_b * h100 * h100;
    }
    if (observable == RLL_OBS_SN_MU) {
        double dl = (1.0 + z) * rll_comoving_distance(z, p, model, status);
        if (!(dl > 0.0)) return -1.0;
        return 5.0 * (rll_log(dl) / RLL_LN10) + 25.0 + p->sn_magnitude_offset;
    }
    if (status) *status |= RLL_RUN_BAD_INPUT;
    return -1.0;
}

double rll_chi2_diagonal(const rll_real_point *points, rll_u32 count, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    rll_u32 i;
    double chi2 = 0.0;
    if (!points || !p) {
        if (status) *status |= RLL_RUN_BAD_INPUT;
        return -1.0;
    }
    for (i = 0u; i < count; ++i) {
        double pred;
        double r;
        if (!(points[i].sigma > 0.0)) {
            if (status) *status |= RLL_RUN_BAD_SIGMA;
            return -1.0;
        }
        pred = rll_predict_observable(points[i].observable, points[i].z, p, model, status);
        if (!rll_is_finite(pred) || pred < 0.0) {
            if (status) *status |= RLL_RUN_NONFINITE;
            return -1.0;
        }
        r = (points[i].observed - pred) / points[i].sigma;
        chi2 += r * r;
    }
    return chi2;
}

double rll_chi2_bao_correlated(const rll_real_point *points, rll_u32 count, const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    rll_u32 i = 0u;
    double chi2 = 0.0;
    if (!points || !p) {
        if (status) *status |= RLL_RUN_BAD_INPUT;
        return -1.0;
    }
    while (i < count) {
        const rll_real_point *a = &points[i];
        double pa = rll_predict_observable(a->observable, a->z, p, model, status);
        if (!(a->sigma > 0.0) || !rll_is_finite(pa)) {
            if (status) *status |= RLL_RUN_BAD_SIGMA | RLL_RUN_NONFINITE;
            return -1.0;
        }
        if (a->covariance_group != 0u && i + 1u < count && points[i + 1u].covariance_group == a->covariance_group) {
            const rll_real_point *b = &points[i + 1u];
            double pb = rll_predict_observable(b->observable, b->z, p, model, status);
            double rho = a->correlation;
            double xa;
            double xb;
            double den = 1.0 - rho * rho;
            if (!(b->sigma > 0.0) || !(den > RLL_EPS) || !rll_is_finite(pb)) {
                if (status) *status |= RLL_RUN_COVARIANCE_SINGULAR;
                return -1.0;
            }
            xa = (a->observed - pa) / a->sigma;
            xb = (b->observed - pb) / b->sigma;
            chi2 += (xa * xa - 2.0 * rho * xa * xb + xb * xb) / den;
            i += 2u;
        } else {
            double x = (a->observed - pa) / a->sigma;
            chi2 += x * x;
            i += 1u;
        }
    }
    return chi2;
}

static int rll_ldlt_n(const double *a, rll_u32 n, double *l, double *d) {
    rll_u32 i;
    rll_u32 j;
    rll_u32 k;
    if (!a || !l || !d || n == 0u) return 0;
    for (i = 0u; i < n * n; ++i) l[i] = 0.0;
    for (i = 0u; i < n; ++i) {
        for (j = 0u; j < i; ++j) {
            double acc = a[i * n + j];
            for (k = 0u; k < j; ++k) acc -= l[i * n + k] * d[k] * l[j * n + k];
            if (rll_abs(d[j]) < RLL_EPS) return 0;
            l[i * n + j] = acc / d[j];
        }
        {
            double acc = a[i * n + i];
            for (k = 0u; k < i; ++k) acc -= l[i * n + k] * l[i * n + k] * d[k];
            if (!(acc > RLL_EPS)) return 0;
            d[i] = acc;
            l[i * n + i] = 1.0;
        }
    }
    return 1;
}

double rll_chi2_full_covariance(const rll_real_point *points, rll_u32 count, const double *covariance, const rll_cosmo_params *p, rll_u32 model, double *l, double *d, double *v, rll_u32 *status) {
    rll_u32 i;
    rll_u32 j;
    double chi2 = 0.0;
    if (!points || !covariance || !p || !l || !d || !v || count == 0u) {
        if (status) *status |= RLL_RUN_BAD_INPUT;
        return -1.0;
    }
    if (!rll_ldlt_n(covariance, count, l, d)) {
        if (status) *status |= RLL_RUN_COVARIANCE_SINGULAR;
        return -1.0;
    }
    for (i = 0u; i < count; ++i) {
        double pred = rll_predict_observable(points[i].observable, points[i].z, p, model, status);
        if (!rll_is_finite(pred) || pred < 0.0) {
            if (status) *status |= RLL_RUN_NONFINITE;
            return -1.0;
        }
        v[i] = points[i].observed - pred;
    }
    for (i = 0u; i < count; ++i) {
        double acc = v[i];
        for (j = 0u; j < i; ++j) acc -= l[i * count + j] * v[j];
        v[i] = acc;
    }
    for (i = 0u; i < count; ++i) chi2 += (v[i] * v[i]) / d[i];
    return chi2;
}

double rll_chi2_cmb_full_covariance(const rll_cosmo_params *p, rll_u32 model, rll_u32 *status) {
    double l[9];
    double d[3];
    double v[3];
    return rll_chi2_full_covariance(rll_real_cmb_prior_points, 3u, rll_real_cmb_covariance, p, model, l, d, v, status);
}

rll_canonical_result rll_run_canonical_real(const rll_cosmo_params *p, rll_u32 model) {
    rll_canonical_result out;
    rll_u32 status = RLL_RUN_OK;
    out.chi2_hz = rll_chi2_diagonal(rll_real_hz_points, rll_real_hz_count, p, model, &status);
    out.chi2_growth = rll_chi2_diagonal(rll_real_fsigma8_points, rll_real_fsigma8_count, p, model, &status);
    out.chi2_bao = rll_chi2_bao_correlated(rll_real_desi_dr2_bao_points, rll_real_desi_dr2_bao_count, p, model, &status);
    out.chi2_cmb = rll_chi2_cmb_full_covariance(p, model, &status);
    out.chi2_total = out.chi2_hz + out.chi2_growth + out.chi2_bao + out.chi2_cmb;
    out.n_hz = rll_real_hz_count;
    out.n_growth = rll_real_fsigma8_count;
    out.n_bao = rll_real_desi_dr2_bao_count;
    out.n_cmb = rll_real_cmb_prior_count;
    out.status = status;
    out.claim_allowed = 0u;
    return out;
}
