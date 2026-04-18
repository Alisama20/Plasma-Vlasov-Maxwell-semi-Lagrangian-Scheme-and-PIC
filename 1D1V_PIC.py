"""
Inestabilidad de dos haces — PIC (Monte Carlo) 1D1V no relativista
===================================================================
Sistema Vlasov-Poisson (electrostático) con iones de fondo fijos.
Las partículas muestrean f(x,v) por Monte Carlo; los campos se
resuelven en malla (Particle-in-Cell clásico).

Ecuaciones:
  dx/dt = v
  dv/dt = q/m · E(x)        (q = -1, m = 1 para electrones)
  ∂E/∂x = ρ − 1             (Poisson; fondo iónico ρ_i = 1)

Configuración inicial: dos Maxwellianas contrapropagantes
  f0(x,v) = (n0/2)·[g(v−v0) + g(v+v0)]·(1 + α cos(k0 x))
con g(v) = exp(-v²/2vT²)/√(2π vT²).

Esquema temporal: leapfrog
  v^{n+1/2} = v^{n-1/2} + Δt · a(x^n)
  x^{n+1}   = x^n       + Δt · v^{n+1/2}
Inicialización de Boris: v^{-1/2} = v^0 − ½Δt · a(x^0).

Depósito/interpolación: CIC (Cloud-In-Cell, 1.er orden).
"""

import numpy as np
import matplotlib.pyplot as plt
from numba import njit
from tqdm import tqdm

# ============================================================
# Parámetros
# ============================================================
N     = 200_000          # nº de macropartículas
nx    = 128              # celdas de malla
Lx    = 4.0 * np.pi      # dominio espacial

v0    = 2.0              # velocidad de cada haz  (k·v0 < √2 para inestabilidad)
vT    = 0.3              # dispersión térmica de cada haz
k0    = 0.5              # modo perturbado (k0·Lx = 2π)
alpha = 0.05             # amplitud de la perturbación de densidad

dt    = 0.05
tmax  = 40.0

dx    = Lx / nx
x_grid = np.linspace(0.0, Lx, nx, endpoint=False)

# Peso por macropartícula (densidad de fondo n0 = 1)
w = Lx / N

rng = np.random.default_rng(42)

# ============================================================
# Muestreo Monte Carlo de la distribución inicial
# ============================================================
# Posiciones: x uniforme + perturbación sinusoidal por rechazo-inversión
#   n(x) = 1 + α cos(k0 x)  →  CDF invertible numéricamente
u  = rng.random(N)
xp = u * Lx
for _ in range(3):                       # 3 iteraciones Newton para invertir CDF
    xp -= (xp + (alpha / k0) * np.sin(k0 * xp) - u * Lx) \
          / (1.0 + alpha * np.cos(k0 * xp))
xp = np.mod(xp, Lx)

# Velocidades: mitad en +v0, mitad en −v0
vp = vT * rng.standard_normal(N)
sign = np.where(rng.random(N) < 0.5, +1.0, -1.0)
vp  += sign * v0

# ============================================================
# Núcleos Numba — depósito CIC y interpolación
# ============================================================
@njit
def deposit_cic(xp, w, nx, dx, Lx):
    rho = np.zeros(nx)
    inv_dx = 1.0 / dx
    for p in range(xp.size):
        xi = (xp[p] % Lx) * inv_dx
        i  = int(xi)
        t  = xi - i
        i0 = i % nx
        i1 = (i + 1) % nx
        rho[i0] += w * (1.0 - t)
        rho[i1] += w * t
    return rho / dx                      # densidad (por unidad de longitud)


@njit
def interp_cic(xp, E_grid, nx, dx, Lx):
    Ep = np.empty(xp.size)
    inv_dx = 1.0 / dx
    for p in range(xp.size):
        xi = (xp[p] % Lx) * inv_dx
        i  = int(xi)
        t  = xi - i
        i0 = i % nx
        i1 = (i + 1) % nx
        Ep[p] = (1.0 - t) * E_grid[i0] + t * E_grid[i1]
    return Ep


# ============================================================
# Poisson por FFT.
#   ρ_carga(x) = n_i − n_e = 1 − n_e     (iones fijos, n_i = 1)
#   ∂E/∂x = ρ_carga  ⇒  Ê(k) = −i·ρ̂_carga / k
# ============================================================
kk = 2.0 * np.pi * np.fft.fftfreq(nx, d=dx)
kk[0] = 1.0

def solve_E(ne):
    rho_charge = 1.0 - ne
    rh = np.fft.fft(rho_charge - np.mean(rho_charge))
    Eh = -1j * rh / kk
    Eh[0] = 0.0
    return np.real(np.fft.ifft(Eh))


# ============================================================
# Bucle temporal — leapfrog
#   Fuerza sobre electrón:  a = (q/m)·E = −E
# ============================================================
nsteps = int(tmax / dt)
t_arr  = np.zeros(nsteps)
E_max  = np.zeros(nsteps)
E_ener = np.zeros(nsteps)              # ½∫E² dx  (energía electrostática)

snap_times = [10.0, 20.0, 30.0, 40.0]
snaps = {}

# Paso inicial: retroceder v medio paso (Boris)
rho = deposit_cic(xp, w, nx, dx, Lx)
E   = solve_E(rho)
Ep  = interp_cic(xp, E, nx, dx, Lx)
vp -= 0.5 * dt * (-Ep)                 # v^{-1/2} = v^0 - ½Δt·a

t = 0.0
for step in tqdm(range(nsteps)):
    rho = deposit_cic(xp, w, nx, dx, Lx)
    E   = solve_E(rho)
    Ep  = interp_cic(xp, E, nx, dx, Lx)

    vp += dt * (-Ep)                    # a = -E (electrón, q=-1)
    xp  = np.mod(xp + dt * vp, Lx)

    t += dt
    t_arr[step] = t
    E_max[step] = np.max(np.abs(E))
    E_ener[step] = 0.5 * np.sum(E**2) * dx

    for ts in snap_times:
        if abs(t - ts) < 0.5 * dt and ts not in snaps:
            snaps[ts] = (xp.copy(), vp.copy())


# ============================================================
# Figura 1 — Evolución de max|E| y energía electrostática
# ============================================================
# Tasa lineal teórica (dos haces fríos iguales, velocidad ±v0):
#   ω² = k²v0² + 1 − √(1 + 4k²v0²)
# Inestable si k·v0 < 1; γ = √(-ω²).
omega2 = k0**2 * v0**2 + 1.0 - np.sqrt(1.0 + 4.0 * k0**2 * v0**2)
gamma_lin = np.sqrt(-omega2) if omega2 < 0 else 0.0

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.3))
a1.semilogy(t_arr, E_max, "b-", lw=1.4, label=r"$\max|E(t)|$")
if gamma_lin > 0:
    mask = (E_max > 3 * E_max[0]) & (E_max < 0.3 * E_max.max())
    if mask.sum() > 5:
        gf, lb = np.polyfit(t_arr[mask], np.log(E_max[mask]), 1)
        tl = np.linspace(t_arr[mask][0], t_arr[mask][-1], 100)
        a1.semilogy(tl, np.exp(lb + gf * tl), "r--", lw=1.3,
                    label=rf"ajuste $\gamma_{{\rm sim}}={gf:.3f}$")
    a1.axhline(E_max[0], color="k", alpha=0.2)
    a1.set_title(rf"max$|E|$  (teoría: $\gamma={gamma_lin:.3f}$)", fontsize=11)
a1.set_xlabel(r"$t\;[\omega_p^{-1}]$"); a1.set_ylabel(r"$\max|E|$")
a1.legend(); a1.grid(True, which="both", alpha=0.3)

a2.semilogy(t_arr, E_ener, "g-", lw=1.4)
a2.set_xlabel(r"$t\;[\omega_p^{-1}]$"); a2.set_ylabel(r"$\frac{1}{2}\int E^2\,dx$")
a2.set_title(r"Energía electrostática", fontsize=11)
a2.grid(True, which="both", alpha=0.3)

fig.suptitle(
    rf"Two-stream PIC — $N={N}$, $v_0=\pm{v0}$, $v_T={vT}$, $k_0={k0}$",
    fontsize=12)
fig.tight_layout()
plt.savefig("twostream_campos.png", dpi=150)
plt.show()

# ============================================================
# Figura 2 — Espacio de fases (x, v): formación de vórtices
# ============================================================
n_snap = len(snaps)
fig, axes = plt.subplots(1, n_snap, figsize=(4.3 * n_snap, 4))

for ax, ts in zip(axes, sorted(snaps)):
    xs, vs = snaps[ts]
    # Submuestreo para no saturar el scatter
    idx = rng.choice(N, size=min(N, 20_000), replace=False)
    ax.scatter(xs[idx], vs[idx], s=0.25, c=vs[idx],
               cmap="coolwarm", vmin=-2*v0, vmax=2*v0,
               alpha=0.6, rasterized=True)
    ax.set_xlim(0, Lx); ax.set_ylim(-2.2*v0, 2.2*v0)
    ax.set_title(rf"$t = {ts:.0f}$", fontsize=10)
    ax.set_xlabel(r"$x$"); ax.set_ylabel(r"$v$")

fig.suptitle("Espacio de fases — inestabilidad de dos haces (PIC)", fontsize=12)
fig.tight_layout()
plt.savefig("twostream_fase.png", dpi=150)
plt.show()
