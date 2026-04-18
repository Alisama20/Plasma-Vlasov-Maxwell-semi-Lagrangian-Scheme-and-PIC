import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.stats import gaussian_kde

# Parámetros
N = 50
Lx, Ly = 10.0, 10.0
dt = 0.1
steps = 500
sigma_pos = 0.1  # para ruido

# Inicialización
x = np.random.uniform(0, Lx, N)
vx = 0.1 * np.random.randn(N)  # movimiento simple
history_len = 50
pos_history = []

# Configuración de la figura
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))

# Subplot partículas
scat = ax1.scatter(x, np.zeros_like(x), c='blue', s=20)
ax1.set_xlim(0, Lx)
ax1.set_ylim(-0.5, 0.5)
ax1.set_xlabel('x')
ax1.set_title('Posiciones de partículas')

# Subplot densidad
x_plot = np.linspace(0, Lx, 200)
line, = ax2.plot(x_plot, np.zeros_like(x_plot))
ax2.set_ylim(0, 0.5)
ax2.set_xlabel('x')
ax2.set_ylabel('Densidad de probabilidad')
ax2.set_title('Evolución de la densidad de probabilidad')

def compute_density(x_history, x_plot, bw=0.2):
    if len(x_history) == 0:
        return np.zeros_like(x_plot)
    all_x = np.hstack(x_history)
    kde = gaussian_kde(all_x, bw_method=bw)
    return kde(x_plot)

def update(frame):
    global x, pos_history
    
    # Movimiento simple + ruido
    x += vx * dt + sigma_pos * np.random.randn(N) * np.sqrt(dt)
    x = np.clip(x, 0, Lx)
    
    # Actualizar partículas
    scat.set_offsets(np.c_[x, np.zeros_like(x)])
    
    # Guardar historial
    pos_history.append(x.copy())
    if len(pos_history) > history_len:
        pos_history.pop(0)
    
    # Actualizar densidad
    density = compute_density(pos_history, x_plot)
    line.set_ydata(density)
    
    return scat, line

ani = FuncAnimation(fig, update, frames=steps, interval=100, blit=True)
plt.tight_layout()
plt.show()