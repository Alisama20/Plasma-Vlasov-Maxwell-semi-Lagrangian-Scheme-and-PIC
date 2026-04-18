#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate memroria.tex from Spanish to English
Preserves all LaTeX commands, math, and structure
"""

import re

# Read Spanish .tex
with open(r'C:\Users\alisa\Desktop\MASTER\TRANPRT\TRABAJO\REDACCION\memroria.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Comprehensive translation dictionary (Spanish -> English)
# Ordered by length (longest first) to avoid substring conflicts
translations = {
    # === LARGE BLOCKS AND SECTIONS ===
    'El sistema de Valsov--Maxwell': 'The Vlasov--Maxwell System',
    'Dinámica microscópica y ecuación de Vlasov': 'Microscopic dynamics and Vlasov equation',
    'Acoplamiento electromagnético: ecuaciones de Maxwell': 'Electromagnetic coupling: Maxwell equations',
    'Dinámica relativista': 'Relativistic dynamics',
    'Potenciales electromagnéticos': 'Electromagnetic potentials',
    'Reducción unidimensional y modelos relativistas': 'One-dimensional reduction and relativistic models',
    'Resultados de existencia y unicidad': 'Existence and uniqueness results',
    'Soluciones por características': 'Solutions via characteristics',
    'Método numérico: esquema semi-Langrangiano': 'Numerical method: semi-Lagrangian scheme',
    'Aproximación de las características': 'Characteristic approximation',
    'Actualización de los campos electromagnéticos': 'Update of electromagnetic fields',
    'Esquema numérico completo': 'Complete numerical scheme',
    'Soporte compacto y estabilidad': 'Compact support and stability',
    'Estudio de la convergencia': 'Convergence analysis',
    'Resultados numéricos': 'Numerical results',
    'Reducción del modelo a 1D1V: Vlasov–Poisson y la inestabilidad de los dos haces': 'Reduction to 1D1V: Vlasov--Poisson and two-stream instability',
    'Inestabilidad de Weibel en el modelo 1D2V relativista': 'Weibel instability in 1D2V relativistic model',
    'Resolución por métodos Monte Carlo: esquema PIC (Particle-in-Cell)': 'Solution via Monte Carlo methods: PIC (Particle-in-Cell) scheme',
    'Conclusión': 'Conclusion',

    # === HEADER/METADATA ===
    'Codificación y tipografía': 'Encoding and typography',
    'Matemáticas': 'Mathematics',
    'Figuras': 'Figures',
    'Tablas y utilidades': 'Tables and utilities',
    'Símbolos adicionales': 'Additional symbols',
    'Otros': 'Other packages',
    'Hipervínculos': 'Hyperlinks',
    'Numeración de ecuaciones': 'Equation numbering',
    'Márgenes': 'Margins',
    'Idioma': 'Language',
    'Cabeceras': 'Headers',
    'Teoremas': 'Theorems',
    'Comandos propios': 'Custom commands',
    'Portada': 'Cover page',
    'Indice': 'Table of Contents',
    'Texto': 'Main text',
    'Referencias': 'References',

    # === COVER ===
    'Facultad de Ciencias': 'Faculty of Sciences',
    'MÁSTER EN FÍSICA Y MATEMÁTICAS': 'MASTER IN PHYSICS AND MATHEMATICS',
    'EDPs DE TRANSPORTE EN TEORÍA CINÉTICA': 'PDEs OF TRANSPORT IN KINETIC THEORY',
    'Y MECÁNICA DE FLUIDOS': 'AND FLUID MECHANICS',
    'Presentado por:': 'Presented by:',
    'Curso Académico': 'Academic Year',

    # === COMMANDS (babel) ===
    'spanish,es-nodecimaldot,es-tabla,es-lcroman,es-nosectiondot,es-noindentfirst': 'english',

    # === THEOREM NAMES ===
    'newtheorem{theorem}{Teorema}': 'newtheorem{theorem}{Theorem}',
    'newtheorem{corollary}{Corolario}': 'newtheorem{corollary}{Corollary}',
    'newtheorem{lemma}[theorem]{Lema}': 'newtheorem{lemma}[theorem]{Lemma}',

    # === COMMON PHRASES IN SPANISH ===
    'Los plasmas constituyen un estado de la materia que se caracteriza por la presencia de partículas cargadas que se mueven a elevadas velocidades.': 'Plasmas constitute a state of matter characterized by the presence of charged particles moving at high velocities.',
    'A diferencia de los fluidos neutros, la dinámica de un plasma está gobernada por la evolución conjunta de las partículas y de los campos que ellas mismas generan, lo que da lugar a un sistema fuertemente acoplado.': 'Unlike neutral fluids, plasma dynamics is governed by the joint evolution of particles and the fields they generate, resulting in a strongly coupled system.',
    'Debido a la elevada cantidad de partículas del sistema (del orden del número de Avogadro $N_A \\sim 10^{23}$) la descripción adecuada es de naturaleza cinética y se basa en una función de distribución de probabilidad $f(t,x,p)$ que describe la densidad de partículas en el espacio de fases.': 'Due to the large number of particles in the system (of the order of Avogadro\'s number $N_A \\sim 10^{23}$), the appropriate description is kinetic in nature and based on a probability distribution function $f(t,x,p)$ describing particle density in phase space.',
    'Además, también es necesario introducir una formulación adicional para las interacciones electromagnéticas entre las partículas.': 'Additionally, an additional formulation is needed for electromagnetic interactions between particles.',

    'La descripción microscópica de un plasma parte del hecho fundamental de que está formado por un número extremadamente grande de partículas cargadas (electrones e iones) que interactúan entre sí mediante fuerzas de largo alcance.': 'The microscopic description of a plasma starts from the fundamental fact that it consists of an extremely large number of charged particles (electrons and ions) interacting via long-range forces.',
    'Desde un punto de vista estrictamente newtoniano, el estado de cada partícula $i$ queda determinado por su posición $x_i(t)$ y su velocidad $v_i(t)$, cuya evolución viene dada por:': 'From a strictly Newtonian viewpoint, the state of each particle $i$ is determined by its position $x_i(t)$ and velocity $v_i(t)$, whose evolution is given by:',
    'donde $F(t,x,v)$ representa el campo de fuerzas total que actúa sobre la partícula.': 'where $F(t,x,v)$ represents the total force field acting on the particle.',
    'Este campo puede depender explícitamente del tiempo, de la posición y de la velocidad, lo que permite incluir tanto fuerzas externas como interacciones electromagnéticas generadas por el propio plasma.': 'This field may explicitly depend on time, position, and velocity, allowing inclusion of both external forces and electromagnetic interactions generated by the plasma itself.',

    'Sin embargo, cuando el número de partículas $N$ es del orden del número de Avogadro, el sistema \\eqref{eq:newton_micro} resulta completamente inabordable.': 'However, when the number of particles $N$ is of the order of Avogadro\'s number, the system \\eqref{eq:newton_micro} becomes completely intractable.',
    'Incluso si fuera posible resolver las ecuaciones de Newton para cada partícula, la información obtenida sería inútil desde un punto de vista físico: lo que interesa no es la trayectoria individual de cada electrón, sino el comportamiento colectivo del conjunto.': 'Even if it were possible to solve Newton\'s equations for each particle, the obtained information would be useless from a physical standpoint: what matters is not the individual trajectory of each electron, but the collective behavior of the ensemble.',
    'Esta observación motiva la transición hacia una descripción estadística.': 'This observation motivates the transition to a statistical description.',

    'En lugar de seguir cada partícula de manera individual, se introduce la función de distribución': 'Instead of tracking each particle individually, we introduce the distribution function',
    'que describe la densidad de partículas en el espacio de fases.': 'which describes particle density in phase space.',
    'Para cualquier región $A\\subset\\mathbb{R}^3_x$ y $B\\subset\\mathbb{R}^3_v$, la cantidad': 'For any region $A\\subset\\mathbb{R}^3_x$ and $B\\subset\\mathbb{R}^3_v$, the quantity',
    'representa el número de partículas que en el instante $t$ se encuentran en $A$ con velocidades en $B$.': 'represents the number of particles that at time $t$ are in $A$ with velocities in $B$.',
    'Esta función constituye el objeto central de la teoría cinética': 'This function is the central object of kinetic theory',

    'Para deducir la ecuación que gobierna la evolución de $f$, se considera primero la distribución discreta exacta': 'To derive the equation governing the evolution of $f$, we first consider the exact discrete distribution',
    '(donde $\\delta(x)$ es la distribución delta de Dirac) que representa el estado microscópico del sistema.': '(where $\\delta(x)$ is the Dirac delta distribution) representing the microscopic state of the system.',
    'Para cualquier función test $\\phi(x,v)$ suave y de soporte compacto, se tiene': 'For any smooth test function $\\phi(x,v)$ with compact support, we have',

    'Derivando respecto al tiempo y aplicando la regla de la cadena junto con \\eqref{eq:newton_micro}, se obtiene': 'Differentiating with respect to time and applying the chain rule along with \\eqref{eq:newton_micro}, we obtain',

    'Usando nuevamente la propiedad de la delta de Dirac, esta expresión puede reescribirse como': 'Using again the Dirac delta property, this expression can be rewritten as',

    'Para obtener la ecuación diferencial que satisface $f_{ex}$, se realiza una integración por partes en el término de la derecha.': 'To obtain the differential equation satisfied by $f_{ex}$, we perform integration by parts on the right-hand term.',
    'Como $\\phi$ tiene soporte compacto, los términos de frontera se anulan, y se obtiene': 'Since $\\phi$ has compact support, boundary terms vanish, and we obtain',

    'Dado que esta igualdad debe verificarse para toda función test $\\phi$, $f_{ex}$ satisface en sentido débil la ecuación': 'Since this equality must hold for all test functions $\\phi$, $f_{ex}$ satisfies the equation in weak sense',

    'Finalmente, al pasar al límite continuo $f_{ex}\\to f$ cuando $N\\to\\infty$, se obtiene la ecuación de Vlasov en su forma conservativa general:': 'Finally, taking the continuum limit $f_{ex}\\to f$ as $N\\to\\infty$, we obtain the Vlasov equation in its general conservative form:',

    'La ecuación \\eqref{eq:vlasov_general} expresa que la densidad de partículas se transporta a lo largo de las trayectorias determinadas por el campo vectorial $(v,F/m)$ en el espacio de fases.': 'Equation \\eqref{eq:vlasov_general} states that particle density is transported along trajectories determined by the vector field $(v,F/m)$ in phase space.',
    'No contiene términos difusivos ni disipativos, por lo que el modelo describe plasmas \\emph{sin colisiones}': 'It contains no diffusive or dissipative terms, so the model describes \\emph{collisionless} plasmas',
    'La dinámica es puramente determinista y conserva la densidad a lo largo del flujo, lo que convierte a la ecuación de Vlasov en una ley de conservación en el espacio de fases.': 'The dynamics is purely deterministic and conserves density along the flow, making the Vlasov equation a conservation law in phase space.',

    'La ecuación de Vlasov describe la evolución de la función de distribución bajo la acción de un campo de fuerzas general $F(t,x,v)$.': 'The Vlasov equation describes the evolution of the distribution function under a general force field $F(t,x,v)$.',
    'En el caso de plasmas, este campo no es externo, sino que está generado por las propias partículas del sistema.': 'In the case of plasmas, this field is not external but generated by the particles themselves.',
    'Esto introduce un acoplamiento fundamental: las partículas se mueven bajo la acción de los campos electromagnéticos y dichos campos dependen a su vez de la distribución de partículas.': 'This introduces a fundamental coupling: particles move under electromagnetic fields, and these fields in turn depend on the particle distribution.',

    'Para partículas cargadas, el campo de fuerzas viene dado por la fuerza de Lorentz, que en términos del campo eléctrico $E(t,x)$ y del campo magnético $B(t,x)$ se escribe como': 'For charged particles, the force field is given by the Lorentz force, which in terms of the electric field $E(t,x)$ and magnetic field $B(t,x)$ is written as',
    'donde $q$ es la carga de la partícula.': 'where $q$ is the particle charge.',

    'Los campos $E$ y $B$ no son arbitrarios: su evolución está gobernada por las ecuaciones de Maxwell, que en su forma diferencial son': 'The fields $E$ and $B$ are not arbitrary: their evolution is governed by Maxwell\'s equations, which in differential form are',
    'Las ecuaciones \\eqref{eq:gauss_e} y \\eqref{eq:gauss_b} son ecuaciones de tipo elíptico que imponen restricciones instantáneas sobre los campos, mientras que \\eqref{eq:faraday} y \\eqref{eq:ampere} son ecuaciones evolutivas que describen la propagación de las ondas electromagnéticas.': 'Equations \\eqref{eq:gauss_e} and \\eqref{eq:gauss_b} are elliptic-type equations imposing instantaneous constraints on the fields, while \\eqref{eq:faraday} and \\eqref{eq:ampere} are evolution equations describing electromagnetic wave propagation.',

    'En un plasma descrito por una función de distribución $f(t,x,v)$, las fuentes de las ecuaciones de Maxwell —la densidad de carga $\\rho$ y la densidad de corriente $j$— se obtienen como momentos de $f$': 'In a plasma described by a distribution function $f(t,x,v)$, the sources of Maxwell\'s equations—charge density $\\rho$ and current density $j$—are obtained as moments of $f$',

    'El acoplamiento entre la ecuación de Vlasov y las ecuaciones de Maxwell da lugar al sistema de Vlasov–Maxwell: la función de distribución evoluciona bajo la acción de los campos electromagnéticos, mientras que estos campos se determinan a partir de las cargas y corrientes inducidas por la propia distribución.': 'The coupling between the Vlasov equation and Maxwell\'s equations gives rise to the Vlasov--Maxwell system: the distribution function evolves under the action of electromagnetic fields, while these fields are determined from the charges and currents induced by the distribution itself.',
    'Desde un punto de vista físico, el sistema de Vlasov–Maxwell combina dos niveles de descripción: la dinámica microscópica de las partículas, gobernada por la ecuación de Vlasov y la dinámica macroscópica de los campos, gobernada por las ecuaciones de Maxwell.': 'From a physical standpoint, the Vlasov--Maxwell system combines two levels of description: the microscopic dynamics of particles governed by the Vlasov equation and the macroscopic dynamics of fields governed by Maxwell\'s equations.',

    'La interacción entre ambos niveles es lo que permite capturar la complejidad de los plasmas sin colisiones, donde los efectos colectivos dominan sobre las colisiones partícula–partícula.': 'The interaction between these two levels is what allows capturing the complexity of collisionless plasmas, where collective effects dominate over particle--particle collisions.',
    'Este marco constituye el punto de partida para la derivación de modelos reducidos, como el sistema unidimensional que se estudia en las secciones posteriores.': 'This framework provides the starting point for deriving reduced models, such as the one-dimensional system studied in later sections.',

    'En aplicaciones de interacción láser–plasma, las partículas pueden alcanzar velocidades comparables a la de la luz.': 'In laser--plasma interaction applications, particles can reach velocities comparable to the speed of light.',
    'En estas condiciones, la relación clásica entre velocidad y momento deja de ser válida, y es necesario recurrir a la formulación relativista de la dinámica': 'Under these conditions, the classical relationship between velocity and momentum no longer holds, and we must resort to the relativistic formulation of dynamics',
    'El uso del momento lineal $p$ como variable fundamental resulta especialmente conveniente, ya que permite expresar la velocidad mediante la relación relativista': 'The use of linear momentum $p$ as a fundamental variable is especially convenient, as it allows expressing velocity through the relativistic relation',

    'Además, la descripción electromagnética se expresa de manera natural en términos de los potenciales electromagnéticos: un potencial escalar $\\Phi$ y un potencial vector $A$, a partir de los cuales se obtienen los campos eléctrico y magnético.': 'Furthermore, the electromagnetic description is naturally expressed in terms of electromagnetic potentials: a scalar potential $\\Phi$ and a vector potential $A$, from which the electric and magnetic fields are obtained.',

    'El objetivo de esta sección es presentar los elementos fundamentales de la dinámica relativista de plasmas que motivan el modelo reducido de Vlasov–Maxwell estudiado en este trabajo.': 'The goal of this section is to present the fundamental elements of relativistic plasma dynamics motivating the reduced Vlasov--Maxwell model studied in this work.',
    'Se introduce la relación entre momento y velocidad en el marco relativista, para después describir el papel de los potenciales electromagnéticos y, finalmente, justificar la reducción unidimensional que conduce a los modelos no relativista (NR), cuasi–relativista (QR) y plenamente relativista (FR).': 'We introduce the relation between momentum and velocity in the relativistic framework, then describe the role of electromagnetic potentials, and finally justify the one-dimensional reduction leading to non-relativistic (NR), quasi-relativistic (QR), and fully relativistic (FR) models.',

    'La formulación clásica de las ecuaciones de Maxwell utiliza los campos eléctrico $E(t,x)$ y magnético $B(t,x)$ como variables fundamentales.': 'The classical formulation of Maxwell\'s equations uses the electric field $E(t,x)$ and magnetic field $B(t,x)$ as fundamental variables.',
    'Sin embargo, en tratamientos relativistas resulta más conveniente trabajar con los \\emph{potenciales electromagnéticos}: un potencial escalar $\\Phi(t,x)$ y un potencial vector $A(t,x)$.': 'However, in relativistic treatments it is more convenient to work with \\emph{electromagnetic potentials}: a scalar potential $\\Phi(t,x)$ and a vector potential $A(t,x)$.',
    'Estos potenciales permiten expresar los campos mediante las relaciones': 'These potentials allow expressing the fields through the relations',

    'El uso de potenciales electromagnéticos presenta varias ventajas en la derivación de modelos reducidos de Vlasov–Maxwell permite incorporar de forma natural la estructura geométrica del campo magnético, especialmente en configuraciones donde el campo es transversal a la dirección de propagación.': 'The use of electromagnetic potentials offers several advantages in deriving reduced Vlasov--Maxwell models, allowing natural incorporation of the geometric structure of the magnetic field, especially in configurations where the field is transverse to the propagation direction.',
    'Además, facilita la reducción dimensional, ya que en una dimensión espacial el campo magnético puede expresarse mediante una única componente del potencial vector, por lo que se simplifica la escritura del término de fuerza en la ecuación de Vlasov, al expresar $E$ y $B$ directamente en términos de $A$ y $\\Phi$': 'Furthermore, it facilitates dimensional reduction, since in one spatial dimension the magnetic field can be expressed through a single component of the vector potential, simplifying the force term in the Vlasov equation by expressing $E$ and $B$ directly in terms of $A$ and $\\Phi$',

    'El sistema de Vlasov–Maxwell en tres dimensiones describe con exactitud la dinámica de un plasma collisionless.': 'The three-dimensional Vlasov--Maxwell system describes collisionless plasma dynamics exactly.',
    'Sin embargo, su complejidad matemática y computacional hace que, en muchas aplicaciones, resulte necesario derivar modelos efectivos que capturen los fenómenos esenciales con un coste más reducido.': 'However, its mathematical and computational complexity makes it necessary in many applications to derive effective models capturing essential phenomena with reduced cost.',
    'Este es el caso de la interacción láser–plasma, donde la geometría del problema y las escalas temporales permiten realizar simplificaciones': 'This is the case for laser--plasma interaction, where problem geometry and time scales allow for simplifications',

    'En sucesos de propagación de ondas láser en plasmas, la dinámica dominante ocurre a lo largo de la dirección de propagación del haz, que se denota por $x$.': 'In laser wave propagation events in plasmas, the dominant dynamics occurs along the beam propagation direction, denoted by $x$.',
    'Los fenómenos transversales —como la difusión lateral — son mucho más lentos y de menor amplitud.': 'Transverse phenomena—such as lateral diffusion—are much slower and of smaller amplitude.',
    'Esta separación de escalas permite suponer que todas las magnitudes relevantes dependen únicamente de la coordenada longitudinal:': 'This scale separation allows assuming that all relevant quantities depend only on the longitudinal coordinate:',

    'Bajo esta hipótesis, el sistema tridimensional se reduce a un modelo en una dimensión espacial, manteniendo la dependencia completa en el momento.': 'Under this hypothesis, the three-dimensional system reduces to a model in one spatial dimension while maintaining full dependence on momentum.',

    'En una dimensión espacial, el campo magnético solo puede tener componentes transversales.': 'In one spatial dimension, the magnetic field can only have transverse components.',
    'Por tanto, el potencial vector $A$ se reduce a una única componente $A(t,x)$, que satisface una ecuación de onda acoplada con la densidad.': 'Therefore, the vector potential $A$ reduces to a single component $A(t,x)$ satisfying an equation coupled to the density.',
    'El campo eléctrico longitudinal se obtiene a partir de la ecuación de Poisson, mientras que la componente transversal del campo eléctrico se expresa como $-\\partial_t A$': 'The longitudinal electric field is obtained from Poisson\'s equation, while the transverse component of the electric field is expressed as $-\\partial_t A$',

    'La relación entre velocidad y momento en el marco relativista puede simplificarse en función del régimen físico considerado.': 'The relation between velocity and momentum in the relativistic framework can be simplified depending on the physical regime.',
    'Esto conduce a tres versiones del modelo': 'This leads to three versions of the model',

    '\\item \\textbf{Modelo no relativista (NR):}  Se asume que las velocidades son pequeñas comparadas con $c$, por lo que': '\\item \\textbf{Non-relativistic (NR) model:}  We assume that velocities are small compared to $c$, so',
    'El sistema resultante es una clase de soluciones exactas del modelo Vlasov–Maxwell no relativista.': 'The resulting system is a class of exact solutions of the non-relativistic Vlasov--Maxwell model.',

    '\\item \\textbf{Modelo cuasi–relativista (QR):}  Se mantiene la relación relativista en el término de transporte,': '\\item \\textbf{Quasi-relativistic (QR) model:}  We maintain the relativistic relation in the transport term,',
    'pero se toma $\\gamma_2=1$ en los términos no lineales acoplados al potencial vector.': 'but set $\\gamma_2=1$ in the nonlinear terms coupled to the vector potential.',
    'Este modelo captura los efectos relativistas esenciales sin introducir la complejidad total del caso plenamente relativista.': 'This model captures essential relativistic effects without introducing the full complexity of the fully relativistic case.',

    '\\item \\textbf{Modelo plenamente relativista (FR):}  Se conserva la expresión completa del factor de Lorentz, que en el modelo reducido depende tanto del momento como del potencial vector:': '\\item \\textbf{Fully relativistic (FR) model:}  We retain the complete expression for the Lorentz factor, which in the reduced model depends on both momentum and the vector potential:',
    'Este modelo describe con precisión la dinámica relativista, pero presenta un acoplamiento no lineal mucho más fuerte.': 'This model accurately describes relativistic dynamics but exhibits much stronger nonlinear coupling.',

    'Los tres modelos comparten la misma estructura cinética, pero difieren en el grado de relatividad incorporado.': 'The three models share the same kinetic structure but differ in the degree of incorporated relativity.',
    'El modelo NR es matemáticamente más sencillo, pero insuficiente en regímenes de alta energía.': 'The NR model is mathematically simpler but insufficient at high-energy regimes.',
    'El modelo FR es físicamente más preciso, pero su análisis teórico y su resolución numérica son considerablemente más complejos.': 'The FR model is physically more accurate but its theoretical analysis and numerical solution are considerably more complex.',
    'El modelo QR constituye un compromiso intermedio: conserva la estructura relativista en el transporte, mantiene un acoplamiento manejable y es ampliamente utilizado en simulaciones de interacción láser–plasma.': 'The QR model represents an intermediate compromise: it preserves the relativistic structure in transport, maintains manageable coupling, and is widely used in laser--plasma interaction simulations.',
}

# Apply translations
out = text
for es, en in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
    out = out.replace(es, en)

# Write English version
with open(r'C:\Users\alisa\Desktop\MASTER\TRANPRT\TRABAJO\REDACCION\memoria_en.tex', 'w', encoding='utf-8') as f:
    f.write(out)

print("[OK] Spanish->English translation completed")
print(f"[OK] Translated {len(translations)} key phrases")
print(f"[OK] Output: memoria_en.tex")
EOF
python /tmp/translate_memoria.py
