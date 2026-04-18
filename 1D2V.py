"""
Inestabilidad de Weibel — Vlasov-Maxwell 1D-2V relativista
===========================================================
Sistema: electrones con distribución bi-Maxwelliana (Ty > Tx) en un plasma
1D homogéneo con iones de fondo fijos.  La anisotropía de temperatura impulsa
el crecimiento exponencial de un campo magnético transversal B_z = ∂Ay/∂x.

Ecuaciones resueltas:
  ∂f/∂t + vx ∂f/∂x + Fx ∂f/∂px + Fy ∂f/∂py = 0       (Vlasov)
  ∂²Ay/∂t²  =  ∂²Ay/∂x²  −  Jy                         (onda EM)
  ∂Ex/∂x    =  ρ − 1                                     (Poisson)

Fuerzas (momentos mecánicos, γ = √(1+px²+py²)):
  Fx = Ex + (py/γ) Bz ,    Fy = −U − (px/γ) Bz
  vx = px/γ ,   Bz = ∂Ay/∂x ,   U = ∂Ay/∂t

Esquema temporal: Strang splitting 2.º orden (Störmer-Verlet en el campo EM).
Interpolación: Catmull-Rom cúbica.

Referencia: Weibel, E. S. (1959). Phys. Rev. Lett. 2(3), 83-84.
"""

import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange
from tqdm import tqdm

# ============================================================
# Parámetros
# ============================================================
nx,  nvx, nvy  = 128, 64, 64
Lx             = 4 * np.pi          # longitud de onda: λ = 2π/k0
pmax_x         = 6.0
pmax_y         = 9.0                # mayor rango porque vTy = √Ty = 2

dx  = Lx / nx
dpx = 2 * pmax_x / nvx
dpy = 2 * pmax_y / nvy

dt   = 0.02
tmax = 50.0

# ── Anisotropía de temperatura (Weibel) ──────────────────────
Tx   = 1.0    # temperatura (energía) en x
Ty   = 4.0    # temperatura en y  →  Ty > Tx  →  inestable
k0   = 0.5    # número de onda del modo Weibel sembrado
eps  = 1e-2   # amplitud inicial de la perturbación en Ay

# ── Mallas ───────────────────────────────────────────────────
x  = np.linspace(0, Lx,     nx,  endpoint=False)
px = np.linspace(-pmax_x, pmax_x, nvx, endpoint=False)
py = np.linspace(-pmax_y, pmax_y, nvy, endpoint=False)

# Arrays de broadcast para funciones vectorizadas
X  = x[:, None, None]
PX = px[None, :, None]
PY = py[None, None, :]

# ============================================================
# Inicialización — bi-Maxwelliana uniforme en x
# ============================================================
# f0(px, py) = [1/(2π √(Tx Ty))] exp(-px²/2Tx) exp(-py²/2Ty)
# La anisotropía Ty/Tx > 1 provoca la inestabilidad de Weibel.
f = (1.0 / (2.0 * np.pi * np.sqrt(Tx * Ty))) \
    * np.exp(-PX**2 / (2.0 * Tx)) \
    * np.exp(-PY**2 / (2.0 * Ty)) \
    * np.ones((nx, 1, 1))          # uniforme en x (broadcast)

# Sembrar el modo EM con una pequeña perturbación en Ay
# → Bz = ∂Ay/∂x = −eps·k0·sin(k0·x)  (seed electromagnético limpio)
A = eps * np.cos(k0 * x)
U = np.zeros(nx)                   # ∂Ay/∂t = 0 en t=0

# Tasa de crecimiento lineal de Weibel (límite no-relativista, c=ωp=1):
#   γ = k0 · √[(Ty − Tx) / (1 + k0²)]
gamma_lin = k0 * np.sqrt((Ty - Tx) / (1.0 + k0**2))
print(f"Tasa de crecimiento lineal estimada: γ ≈ {gamma_lin:.4f} ωp")
print(f"Saturación esperada en t ≈ {np.log(0.1/eps/k0)/gamma_lin:.1f}")

# ============================================================
# Funciones auxiliares (Python puro)
# ============================================================
def rho_from_f(f):
    """ρ(x) = ∫ f dpx dpy  — densidad de carga electrónica."""
    return np.sum(f, axis=(1, 2)) * dpx * dpy


def J_y_from_f(f):
    """Jy(x) = ∫ f·(py/γ) dpx dpy  — corriente transversal."""
    gamma = np.sqrt(1.0 + PX**2 + PY**2)
    return np.sum(f * (PY / gamma), axis=(1, 2)) * dpx * dpy


def solve_poisson(rho):
    """Ex(x) de la ecuación de Poisson  ∂Ex/∂x = ρ − 1  vía FFT.
    No modifica el array de entrada."""
    kk     = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)
    kk[0]  = 1.0
    rh     = np.fft.fft(rho - np.mean(rho))
    Eh     = 1j * rh / kk
    Eh[0]  = 0.0
    return np.real(np.fft.ifft(Eh))


# ============================================================
# Núcleos Numba — interpolación cúbica Catmull-Rom
# ============================================================
@njit
def cubic_interp_velocity(fline, vnew, vmax, dv):
    nv  = fline.shape[0]
    out = np.empty_like(vnew)
    for m in range(vnew.size):
        vv = min(max(vnew[m], -vmax), vmax)
        xi = (vv + vmax) / dv
        i  = int(np.floor(xi))
        t  = xi - i
        if i < 1:      i, t = 1,    0.0
        if i > nv - 3: i, t = nv-3, 1.0
        fm1 = fline[i-1]; f0c = fline[i]
        f1  = fline[i+1]; f2  = fline[i+2]
        out[m] = 0.5*(2*f0c + (-fm1+f1)*t
                      + (2*fm1 - 5*f0c + 4*f1 - f2)*t**2
                      + (-fm1 + 3*f0c - 3*f1 + f2)*t**3)
    return out


@njit
def cubic_interp_periodic(fline, xnew, L, dx):
    nx  = fline.shape[0]
    out = np.empty_like(xnew)
    for m in range(xnew.size):
        xx  = xnew[m] % L
        xi  = xx / dx
        i   = int(np.floor(xi))
        t   = xi - i
        im1 = (i-1) % nx;  i0 = i % nx
        i1  = (i+1) % nx;  i2 = (i+2) % nx
        fm1 = fline[im1]; f0c = fline[i0]
        f1  = fline[i1];  f2  = fline[i2]
        out[m] = 0.5*(2*f0c + (-fm1+f1)*t
                      + (2*fm1 - 5*f0c + 4*f1 - f2)*t**2
                      + (-fm1 + 3*f0c - 3*f1 + f2)*t**3)
    return out


# ============================================================
# Advecciones semi-Lagrangianas
# ============================================================
@njit(parallel=True)
def advect_px(f, E_x, B_z, px, py, pmax_x, dpx, dt_half):
    """½Δt en px.  Fuerza sobre electrón (q=-1):
       Fx = -Ex - (py/γ)·Bz
    """
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for i in prange(nx):
        for k in range(nvy):
            px_old = np.empty(nvx)
            for j in range(nvx):
                g         = np.sqrt(1.0 + px[j]**2 + py[k]**2)
                Fx        = -E_x[i] - (py[k] / g) * B_z[i]
                px_old[j] = px[j] - Fx * dt_half
            fnew[i, :, k] = cubic_interp_velocity(
                f[i, :, k], px_old, pmax_x, dpx)
    return fnew


@njit(parallel=True)
def advect_py(f, U, B_z, px, py, pmax_y, dpy, dt_half):
    """½Δt en py.  Fuerza sobre electrón (q=-1):
       Fy = -Ey + (px/γ)·Bz  =  U + (px/γ)·Bz    (Ey = -∂Ay/∂t = -U)
    """
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for i in prange(nx):
        for j in range(nvx):
            py_old = np.empty(nvy)
            for k in range(nvy):
                g         = np.sqrt(1.0 + px[j]**2 + py[k]**2)
                Fy        = U[i] + (px[j] / g) * B_z[i]
                py_old[k] = py[k] - Fy * dt_half
            fnew[i, j, :] = cubic_interp_velocity(
                f[i, j, :], py_old, pmax_y, dpy)
    return fnew


@njit(parallel=True)
def advect_x(f, px, py, x, Lx, dx, dt_full):
    """Δt en x.  vx = px/γ  (relativista)."""
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for j in prange(nvx):
        for k in range(nvy):
            g     = np.sqrt(1.0 + px[j]**2 + py[k]**2)
            vx    = px[j] / g
            x_old = x - vx * dt_full
            fnew[:, j, k] = cubic_interp_periodic(
                f[:, j, k], x_old, Lx, dx)
    return fnew


# ============================================================
# Bucle temporal — Strang splitting 2.º orden
#
#   ½Δt py  →  ½Δt px  →  Δt x  →  actualizar A, U  →  ½Δt px  →  ½Δt py
#
# Campo EM: Störmer-Verlet explícito
#   U^{n+½} = U^{n-½} + Δt·(∂²Ay/∂x² − Jy)
#   A^{n+1} = A^n     + Δt·U^{n+½}
#
# Para 2.º orden en el Strang palíndromo, la segunda mitad de momentum
# usa campos centrados en t^n:
#   U_c     = (U^{n-½} + U^{n+½})/2  ≈  U^n   →  E_y^n = −U_c
#   B_z_mid = (B_z^n   + B_z^{n+1})/2 ≈  B_z^{n+½}
# ============================================================
snap_times = [0.0, 15.0, 30.0, 50.0]
f_maps_px  = {0.0: np.sum(f, axis=2) * dpy}   # marginal f(x, px)
f_maps_py  = {0.0: np.sum(f, axis=1) * dpx}   # marginal f(x, py)
B_max      = []
E_max      = []

nsteps = int(tmax / dt)
t      = 0.0

for step in tqdm(range(nsteps)):

    # ── Campos al comienzo del paso ─────────────────────────
    rho = rho_from_f(f)
    E_x = solve_poisson(rho)
    B_z = (np.roll(A, -1) - np.roll(A, 1)) / (2.0 * dx)   # ∂Ay/∂x (periódico)

    # ── Primera mitad en momentum ───────────────────────────
    f = advect_py(f, U, B_z, px, py, pmax_y, dpy, 0.5 * dt)
    f = advect_px(f, E_x, B_z, px, py, pmax_x, dpx, 0.5 * dt)

    # ── Paso completo en x ──────────────────────────────────
    f = advect_x(f, px, py, x, Lx, dx, dt)

    # ── Actualizar onda EM  (Störmer-Verlet) ─────────────────
    #   U^{n+½} = U^{n-½} + Δt·(∂²Ay/∂x² − Jy)
    #   A^{n+1} = A^n     + Δt·U^{n+½}
    J_y   = J_y_from_f(f)
    d2A   = (np.roll(A, -1) - 2.0 * A + np.roll(A, 1)) / dx**2
    U_old = U.copy()                                              # U^{n-½}
    U     = U + dt * (d2A - J_y)                                 # U^{n+½}
    A     = A + dt * U                                           # A^{n+1}

    # Campos centrados en t^n (restauran la simetría palíndromo del Strang):
    #   U_c     = (U^{n-½} + U^{n+½})/2  ≈  U^n   →  E_y^n = −U_c
    #   B_z_mid = (B_z^n   + B_z^{n+1})/2 ≈  B_z^{n+½}
    B_z_next = (np.roll(A, -1) - np.roll(A, 1)) / (2.0 * dx)   # ∂A^{n+1}/∂x
    U_c      = 0.5 * (U_old + U)
    B_z_mid  = 0.5 * (B_z + B_z_next)

    # ── Campos electrostáticos al final del paso ─────────────
    rho = rho_from_f(f)
    E_x = solve_poisson(rho)

    # ── Segunda mitad en momentum (campos centrados en t^n) ──
    f = advect_px(f, E_x, B_z_mid, px, py, pmax_x, dpx, 0.5 * dt)
    f = advect_py(f, U_c, B_z_mid, px, py, pmax_y, dpy, 0.5 * dt)

    t += dt

    # ── Diagnósticos ────────────────────────────────────────
    B_max.append(float(np.max(np.abs(B_z_next))))
    E_max.append(float(np.max(np.abs(E_x))))

    for t_snap in snap_times[1:]:
        if abs(t - t_snap) < 0.5 * dt and t_snap not in f_maps_px:
            f_maps_px[t_snap] = np.sum(f, axis=2) * dpy
            f_maps_py[t_snap] = np.sum(f, axis=1) * dpx


# ============================================================
# Figura 1 — Crecimiento de Bz y Ex en función del tiempo
# ============================================================
t_arr = np.arange(len(B_max)) * dt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

# Bz máximo (principal diagnóstico de Weibel)
ax1.semilogy(t_arr, B_max, "b-", lw=1.5, label=r"$\max|B_z(t)|$")
# Ajuste exponencial sobre la fase lineal detectada automáticamente
B_arr  = np.asarray(B_max)
mask   = (B_arr > 3.0 * B_arr[0]) & (B_arr < 0.3 * B_arr.max())
if mask.sum() > 5:
    gamma_fit, logB0 = np.polyfit(t_arr[mask], np.log(B_arr[mask]), 1)
    t_lin = np.linspace(t_arr[mask][0], t_arr[mask][-1], 200)
    ax1.semilogy(t_lin, np.exp(logB0) * np.exp(gamma_fit * t_lin),
                 "r--", lw=1.4,
                 label=rf"ajuste: $\gamma_{{\rm sim}}={gamma_fit:.3f}$")
ax1.set_xlabel(r"$t\;[\omega_p^{-1}]$", fontsize=11)
ax1.set_ylabel(r"$\max|B_z|$", fontsize=11)
ax1.set_title(r"Crecimiento del campo magnético transversal $B_z$", fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(True, which="both", alpha=0.3)

# Ex máximo (modo electrostático secundario)
ax2.semilogy(t_arr, E_max, "g-", lw=1.5)
ax2.set_xlabel(r"$t\;[\omega_p^{-1}]$", fontsize=11)
ax2.set_ylabel(r"$\max|E_x|$", fontsize=11)
ax2.set_title(r"Campo eléctrico longitudinal $E_x$", fontsize=11)
ax2.grid(True, which="both", alpha=0.3)

fig.suptitle(
    rf"Inestabilidad de Weibel — $T_x={Tx}$, $T_y={Ty}$, $k_0={k0}$",
    fontsize=12)
fig.tight_layout()
plt.savefig("weibel_campos.png", dpi=150)
plt.show()

# ============================================================
# Figura 2 — Marginal f(x, px) a tiempos seleccionados
#             Muestra la formación de filamentos/vórtices en px
# ============================================================
n_snap = len(f_maps_px)
fig, axes = plt.subplots(1, n_snap, figsize=(4.5 * n_snap, 4))

f0_px = f_maps_px[0.0]
vlim_px = max(1e-12, max(np.max(np.abs(f_maps_px[t] - f0_px))
                         for t in sorted(f_maps_px) if t > 0))
for ax, t_snap in zip(axes, sorted(f_maps_px)):
    snap = f_maps_px[t_snap] - f0_px
    im = ax.imshow(
        snap.T,
        extent=[0, Lx, -pmax_x, pmax_x],
        origin="lower", aspect="auto", cmap="RdBu_r",
        vmin=-vlim_px, vmax=vlim_px,
    )
    ax.set_title(rf"$t = {t_snap:.0f}$", fontsize=10)
    ax.set_xlabel(r"$x$", fontsize=9)
    ax.set_ylabel(r"$p_x$", fontsize=9)
    plt.colorbar(im, ax=ax, label=r"$\Delta\!\int f\,dp_y$", fraction=0.046)

fig.suptitle(
    rf"Perturbación $\Delta f(x,p_x)$ — inestabilidad de Weibel"
    rf"  ($T_x={Tx}$, $T_y={Ty}$)",
    fontsize=11)
fig.tight_layout()
plt.savefig("weibel_fpx.png", dpi=150)
plt.show()

# ============================================================
# Figura 3 — Marginal f(x, py) a tiempos seleccionados
#             Muestra la modulación en py (filamentation en la dirección de Jy)
# ============================================================
fig, axes = plt.subplots(1, n_snap, figsize=(4.5 * n_snap, 4))

f0_py = f_maps_py[0.0]
vlim_py = max(1e-12, max(np.max(np.abs(f_maps_py[t] - f0_py))
                         for t in sorted(f_maps_py) if t > 0))
for ax, t_snap in zip(axes, sorted(f_maps_py)):
    snap = f_maps_py[t_snap] - f0_py
    im = ax.imshow(
        snap.T,
        extent=[0, Lx, -pmax_y, pmax_y],
        origin="lower", aspect="auto", cmap="RdBu_r",
        vmin=-vlim_py, vmax=vlim_py,
    )
    ax.set_title(rf"$t = {t_snap:.0f}$", fontsize=10)
    ax.set_xlabel(r"$x$", fontsize=9)
    ax.set_ylabel(r"$p_y$", fontsize=9)
    plt.colorbar(im, ax=ax, label=r"$\Delta\!\int f\,dp_x$", fraction=0.046)

fig.suptitle(
    rf"Perturbación $\Delta f(x,p_y)$ — inestabilidad de Weibel"
    rf"  ($T_x={Tx}$, $T_y={Ty}$)",
    fontsize=11)
fig.tight_layout()
plt.savefig("weibel_fpy.png", dpi=150)
plt.show()
