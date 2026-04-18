import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

# ============================================================
# Parámetros
# ============================================================
nx = 128
nvx = 96
nvy = 96

Lx = 4*np.pi
pmax_x = 6.0
pmax_y = 6.0

dx = Lx / nx
dpx = 2*pmax_x / nvx
dpy = 2*pmax_y / nvy

dt = 0.05
tmax = 4.0

alpha = 0.01
k0 = 0.5

# ============================================================
# Mallas
# ============================================================
x = np.linspace(0, Lx, nx, endpoint=False)
px = np.linspace(-pmax_x, pmax_x, nvx, endpoint=False)
py = np.linspace(-pmax_y, pmax_y, nvy, endpoint=False)

# FFT para Poisson
k = 2*np.pi*np.fft.fftfreq(nx, d=dx)
k[0] = 1.0

# ============================================================
# Inicialización: bi-Maxwelliano anisótropo
# ============================================================
Tx = 1.0
Ty = 4.0

X, PX = np.meshgrid(x, px, indexing='ij')
Mx = (1/np.sqrt(2*np.pi*Tx))*np.exp(-PX**2/(2*Tx))

PY = np.meshgrid(py, x, indexing='ij')[0]
My = (1/np.sqrt(2*np.pi*Ty))*np.exp(-PY**2/(2*Ty))

f = np.zeros((nx, nvx, nvy))
for i in range(nx):
    for j in range(nvx):
        f[i,j,:] = Mx[i,j]*My[:,0]*(1 + alpha*np.cos(k0*x[i]))

# ============================================================
# Campos electromagnéticos
# ============================================================
A = np.zeros(nx)
U = np.zeros(nx)  # dA/dt
V = np.zeros(nx)  # dA/dx

# ============================================================
# Rutinas auxiliares
# ============================================================
def rho_from_f(f):
    return np.sum(f, axis=(1,2))*dpx*dpy

def j_from_f(f, px, py):
    gamma = np.sqrt(1 + px[None,:,None]**2 + py[None,None,:]**2)
    vx = px[None,:,None]/gamma
    return np.sum(f*vx, axis=(1,2))*dpx*dpy

def solve_poisson(rho):
    rho0 = np.mean(rho)
    rh = np.fft.fft(rho - rho0)
    Eh = 1j*rh/k
    Eh[0] = 0.0
    return np.real(np.fft.ifft(Eh))

# ============================================================
# Interpolaciones
# ============================================================
@njit
def interp_line(fline, x_new, L, dx):
    nx = fline.shape[0]
    out = np.empty_like(x_new)
    x_mod = x_new % L
    xi = x_mod/dx
    i0 = np.floor(xi).astype(np.int64)
    i1 = (i0+1) % nx
    w = xi - i0
    for i in range(nx):
        out[i] = (1-w[i])*fline[i0[i]] + w[i]*fline[i1[i]]
    return out

@njit
def interp_v(fline, v_new, vmax, dv):
    nv = fline.shape[0]
    out = np.empty_like(v_new)
    for j in range(nv):
        vv = v_new[j]
        if vv < -vmax: vv = -vmax
        if vv >  vmax: vv =  vmax
        eta = (vv + vmax)/dv
        j0 = int(np.floor(eta))
        if j0 < 0: j0 = 0
        if j0 > nv-2: j0 = nv-2
        j1 = j0+1
        w = eta - j0
        out[j] = (1-w)*fline[j0] + w*fline[j1]
    return out

# ============================================================
# Advecciones
# ============================================================
@njit(parallel=True)
def advect_px(f, Fx, px, pmax_x, dpx, dt_half):
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for i in prange(nx):
        px_old = px + Fx[i]*dt_half
        for ky in range(nvy):
            fnew[i,:,ky] = interp_v(f[i,:,ky], px_old, pmax_x, dpx)
    return fnew

@njit(parallel=True)
def advect_py(f, Fy, py, pmax_y, dpy, dt_half):
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for i in prange(nx):
        py_old = py + Fy[i]*dt_half
        for j in range(nvx):
            fnew[i,j,:] = interp_v(f[i,j,:], py_old, pmax_y, dpy)
    return fnew

@njit(parallel=True)
def advect_x(f, x, px, py, Lx, dx, dt_full):
    nx, nvx, nvy = f.shape
    fnew = np.zeros_like(f)
    for j in prange(nvx):
        for k in range(nvy):
            gamma = np.sqrt(1 + px[j]**2 + py[k]**2)
            vx = px[j]/gamma
            x_old = x - vx*dt_full
            fline = f[:,j,k]
            fnew[:,j,k] = interp_line(fline, x_old, Lx, dx)
    return fnew

# ============================================================
# Bucle temporal
# ============================================================
snapshots = {0.0: np.sum(f, axis=2)}

t = 0.0
while t < tmax:

    rho = rho_from_f(f)
    E = solve_poisson(rho)

    # fuerzas QR
    Fx = -(E + A*V)
    Fy = -U

    # medio paso en p_y
    f = advect_py(f, Fy, py, pmax_y, dpy, 0.5*dt)

    # medio paso en p_x
    f = advect_px(f, Fx, px, pmax_x, dpx, 0.5*dt)

    # paso completo en x
    f = advect_x(f, x, px, py, Lx, dx, dt)

    # actualizar A, U, V
    A_new = A + dt*U
    U_new = U + dt*((np.roll(A, -1) - np.roll(A, 1))/(2*dx)) - dt*rho*A
    V_new = (np.roll(A_new, -1) - np.roll(A_new, 1))/(2*dx)

    A, U, V = A_new, U_new, V_new

    # otro medio paso en p_x y p_y
    Fx = -(E + A*V)
    Fy = -U
    f = advect_px(f, Fx, px, pmax_x, dpx, 0.5*dt)
    f = advect_py(f, Fy, py, pmax_y, dpy, 0.5*dt)

    t += dt

    # snapshots QR típicos
    for T in [1, 2, 3]:
        if abs(t - T) < 0.5*dt and T not in snapshots:
            snapshots[T] = np.sum(f, axis=2)

# ============================================================
# Gráficas f(x,px,t)
# ============================================================
fig, axes = plt.subplots(2,2,figsize=(12,10))
times = [0, 1, 2, 3]

for ax,T in zip(axes.flatten(), times):
    snap = snapshots[T]
    im = ax.imshow(
        snap.T,
        extent=[0,Lx,-pmax_x,pmax_x],
        aspect='auto',
        origin='lower',
        cmap='jet'
    )
    ax.set_title(f"t = {T}")
    ax.set_xlabel("x")
    ax.set_ylabel("p_x")
    plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.show()
