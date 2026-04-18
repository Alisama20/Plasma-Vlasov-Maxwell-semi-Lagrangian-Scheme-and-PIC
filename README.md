# Vlasov--Maxwell: Semi-Lagrangian and Monte Carlo Numerical Methods

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive study of numerical methods for solving the Vlasov--Maxwell system in kinetic plasma physics, combining **semi-Lagrangian grid-based methods** and **Particle-in-Cell (PIC) Monte Carlo approaches**.

## Overview

This project implements advanced numerical solvers for the coupled Vlasov--Maxwell equations governing collisionless plasma dynamics. The work includes:

- **Theoretical framework**: existence, uniqueness, and convergence analysis of semi-Lagrangian schemes
- **Semi-Lagrangian solver (1D1V and 1D2V)**: high-order Strang splitting with cubic Catmull--Rom interpolation
- **PIC/Monte Carlo solver (1D1V)**: stochastic particle-in-cell method with CIC deposition and FFT Poisson solver
- **Physical applications**: two-stream instability and Weibel instability in relativistic/quasi-relativistic plasma

## Repository Structure

```
.
├── MemoriaES.pdf              # Full thesis (Spanish)
├── MemoryEN.pdf               # Full thesis (English)
├── README.md                  # This file
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore rules
├── 1D1V.py                    # Grid-based Vlasov--Poisson solver (1D1V)
├── 1D2V.py                    # Semi-Lagrangian Weibel instability solver (1D2V)
├── 1D1V_PIC.py                # Particle-in-Cell two-stream solver (Monte Carlo)
├── *.png                      # Generated figures (phase space, field evolution)
└── REDACCION/                 # LaTeX source
    ├── memroria.tex           # Spanish thesis source
    ├── memoria_en.tex         # English thesis source
    ├── bibliografia.bib       # BibTeX references
    └── *.png                  # Figure files
```

## Scripts

### 1D1V.py – Grid-Based Two-Stream Instability
Semi-Lagrangian solver for the electrostatic Vlasov--Poisson system on a fixed mesh.

**Features:**
- Two counter-propagating Maxwellian beams
- CFL-free time integration (no CFL restriction)
- Cubic interpolation in phase space
- FFT-based Poisson solver
- Diagnostics: max|E|(t), phase-space vortex formation

**Output:**
- `doshaces.png` – Phase space evolution at t=0, 15, 20, 30

### 1D2V.py – Weibel Instability (Electromagnetic)
Semi-Lagrangian solver for 1D2V quasi-relativistic Vlasov--Maxwell with anisotropic temperature.

**Features:**
- Bi-Maxwellian anisotropic distribution (Ty > Tx)
- Electromagnetic seed triggering exponential B-field growth
- Strang-symmetric splitting with Störmer--Verlet EM update
- Cubic Catmull--Rom interpolation
- Automatic linear growth rate extraction

**Output:**
- `weibel_campos.png` – max|Bz|(t) and max|Ex|(t) with growth-rate fit
- `weibel_fpx.png` – Marginal f(x,px) showing filamentation
- `weibel_fpy.png` – Marginal f(x,py) showing anisotropy-driven mode

### 1D1V_PIC.py – Particle-in-Cell Monte Carlo
Stochastic particle-based solver using macroparticles and fixed grid for fields.

**Features:**
- N = 200,000 macroparticles (two-stream counterbeam setup)
- Cloud-in-Cell (CIC) charge deposition
- FFT Poisson solver for E-field
- Leapfrog particle push (Boris initialization)
- BGK vortex detection in phase space

**Output:**
- `twostream_campos.png` – max|E|(t) with exponential fit vs. two-stream theory
- `twostream_fase.png` – Phase space (x,v) showing BGK vortex formation

## Numerical Methods

### Semi-Lagrangian Scheme (Grid-Based)

The solver follows characteristics backward in time via **Strang splitting**:

1. Half-step advection in velocity (momentum)
2. Full-step advection in space
3. Half-step advection in velocity

Advantages:
- Unconditionally stable (no CFL restriction)
- Second-order accuracy in time
- Preserves compact support of distribution

### Particle-in-Cell (Monte Carlo)

The PIC method represents f as a weighted sum of macroparticles:

$$f(t,x,v) \approx \sum_p w_p \, \delta(x - x_p(t)) \, \delta(v - v_p(t))$$

Advantages:
- Error scales as O(1/√N), independent of phase-space dimension
- Naturally captures BGK vortices and filamentation
- Lower memory footprint than fixed grids for high-dimensional phase spaces

## Physical Models

### Two-Stream Instability (1D1V Vlasov--Poisson)

**Setup:**
- Two counter-propagating beams: v₀ = ±2, vT = 0.3
- Spatial seed: density modulation 1 + 0.05·cos(0.5x)
- Unstable for kv₀ < √2

**Observables:**
- Exponential growth of E-field (phase linear regime)
- BGK vortex trapping and saturation (nonlinear phase)
- Self-consistent filamentation in (x,v) phase space

### Weibel Instability (1D2V Vlasov--Maxwell)

**Setup:**
- Bi-Maxwellian: Tx=1, Ty=4 (anisotropic)
- Electromagnetic seed: Ay(x,0) = 10⁻² cos(0.5x)
- Grid: Nx=128, Np_x=Np_y=64; Δt=0.02; T_max=50

**Observables:**
- Exponential growth of transverse B-field
- Oscillating longitudinal E-field
- Filamentation in (x, py) due to magnetic deflection

## Compilation & Execution

### Requirements

```bash
pip install numpy matplotlib numba tqdm
```

### Run Simulations

```bash
# 1D1V grid-based (electrostatic)
python 1D1V.py

# 1D2V semi-Lagrangian (electromagnetic Weibel)
python 1D2V.py

# 1D1V PIC Monte Carlo
python 1D1V_PIC.py
```

Each script generates PNG diagnostics automatically.

### Compile Thesis

```bash
cd REDACCION
pdflatex memroria.tex           # Spanish
pdflatex memoria_en.tex          # English
bibtex memroria                  # Bibliography
# Run pdflatex again for references
```

## Mathematical Framework

### Vlasov Equation (Characteristic Form)

$$\frac{dX}{dt} = v(P), \quad \frac{dP}{dt} = -F(t,X)$$

where for electrons (q=-1):
- In 1D1V: F = E
- In 1D2V: F = (E + (py/γ)Bz, U - (px/γ)Bz)

### Convergence Result (Main Theorem)

Under appropriate regularity assumptions, the semi-Lagrangian error satisfies:

$$e_n \le C(\Delta t^2 + \Delta x^2 + \Delta p^2 + \Delta t \cdot \Delta p^2) + C\frac{\Delta x^2 + \Delta p^2}{\Delta t}$$

allowing fine temporal discretization with coarser spatial grids (unlike CFL-restricted finite-difference methods).

## References

Key citations (see `REDACCION/bibliografia.bib`):

- Carrillo, J. A., et al. (2006). Global classical solutions to the Vlasov–Maxwell system with boundary conditions.
- Bostan, M. (2009). Convergence analysis for a semi-Lagrangian discretization of the Vlasov--Poisson system.
- Weibel, E. S. (1959). Phys. Rev. Lett. 2(3), 83–84.

## Author

**A. S. Amari**  
Master's Thesis in Physics and Mathematics  
Faculty of Sciences, University of Granada  
Academic Year 2025/2026

Email: [alisalemstd@gmail.com](mailto:alisalemstd@gmail.com)

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) file.

---

**Language Versions:**
- 📘 Spanish: [MemoriaES.pdf](MemoriaES.pdf)
- 📗 English: [MemoryEN.pdf](MemoryEN.pdf)
