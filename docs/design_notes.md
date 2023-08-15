---
author:
- Luis Fernando Sanchez Martin [^1]
date: July 2023
title: RVG DSS Design Notes
---
# Design Notes

## Encounter Classifier

The encounter classifier is a[Title](../rvg_leidarstein_core/scripts/test_ec_dsm.py) module meant to provide an encounter
classification between the own ship and a target vessel in accordance
with COLREGS. The resulting classification will be visualized as part of
the information available in the front end. Still, more importantly, it
will provide a basis for selecting an adequate CBF own ship domain. The
domain itself will be a polygon made up of half-plane constraints that
will help the own vessel maneuver around an obstacle while complying
with COLREGS.

The encounter classifier module, will therefore take the information
processed by the arpa module, determine the type of encounter for the
relevant vessels and then hand over the encounter type information to
the CBF module.

### Input 

The input of the encounter classifier will be the output of the arpa
module. this will comprehend NED information regarding the own ship, the
target ships, and their arpa parameters.

### Output 

The output of the module will consist of an enum from 1-7 identifying
the resulting encounter classification.

### Design 

The encounter classifier consists of two main components; an encounter
classifying method for determining the type of encounter, and a state
machine for consistently maintaining classification and preventing
chatter.

#### Encounter Classifying Method

The method for classifying encounters will follow the one proposed by
Thyri[^3], see Figure [5.1](#fig:class){reference-type="ref"
reference="fig:class"}.

![Graphic representation of the classification algorithm, where the
position of the OS is at the center of the middle circle. In situation
sectors with two encounter classifications, the outer one is chosen when
the involved vessels have a closing range, while the inner one is chosen
for increasing range.](./figs/encounter_class.PNG)

Visually, this works by identifying the position of the target vessel
relative to the own ship and assigning it to a relative bearing sector
(RBS, The one at the center of Figure
[5.1](#fig:class){reference-type="ref" reference="fig:class"}). Then, we
proceed to identify the situation sector (SS, the segments of either of
the circles surrounding the one at the center in Figure
[5.1](#fig:class){reference-type="ref" reference="fig:class"}) by
selecting the one that the target ship is pointing towards. The relative
velocity of the vessels is taken into consideration when selecting the
inner and outer SS the outer one is chosen when the involved vessels
have a closing range, while the inner one is chosen for an increasing
range. An example of this classification can be seen in Figure
[5.2](#fig:class_ex){reference-type="ref" reference="fig:class_ex"}

![Classification examples for an arbitrary set of target ships (red),
and the blue OS. Classification is made by selecting the encounter type
of the sector within which the TS course vector lies. ](./figs/encounter_class_ex.PNG)

The operation of the Encounter Classifier Method is done in three steps.
First the RBS sector is identified d based on the relative bearing of
the TS from the OS.

```math
\varphi = atan2((E_{TS} - E),(N_{TS} - N)) - \chi
```

The RBS is then determined by checking where in the range of
$[\theta_1, -\theta_1, \theta_2, -\theta_2]$ the angle $\varphi$ lands.

```math
    RBS = 
    \begin{cases}
        1 : 2\pi-\theta_1 < \varphi < \theta_1\\
        2 : \theta_1  < \varphi < \theta_2\\
        3 : \theta_2  < \varphi < 2\pi -\theta_2\\
        4 : 2`\pi-\theta_2 < \varphi < 2`\pi-\theta_1
    \end{cases}
```

The next step is to determine the SS. For this, we use a rotated version
of the angles from eq. [\[eq:rbs\]](#eq:rbs){reference-type="ref"
reference="eq:rbs"} $[\theta'_1, -\theta'_1, \theta'_2, -\theta'_2]$.

```math
\begin{matrix}
       \theta'_1 = \theta_1 + \varphi_{TS} \\
        \theta'_2 = \theta_2 + \varphi_{TS}
    \end{matrix}
```

The SS is then determined by checking where in this range the course of
the target vessel $c_{ts}$ lands.

```math
SS = 
    \begin{cases}
        1 : 2\pi-\theta'_1  < c_{ts} < \theta'_1\\
        2 : \theta'_1       < c_{ts} < \theta'_2\\
        3 : \theta'_2       < c_{ts} < 2\pi -\theta'_2\\
        4 : 2`\pi-\theta'_2 < c_{ts} < 2`\pi-\theta'_1
    \end{cases}
```

Finally, in order to determine whether the outer or the inner section of
the circle segment should be chosen, it is determined whether the range
between the vessels is increasing or decreasing. This is done by
obtaining the dot product of the relative position $p_{rel}$ and
velocity $v_{rel}$.

```math
\begin{matrix}
        p_{rel} = [n_{ts} - n, e_{ts} - e] \\
        v_{rel} = v_{ts} - v_{os}
    \end{matrix}
```

Where

```math
\begin{matrix}
        v_{os} = [u  sin(c), u  cos(c)]^T \\
        v_{ts} = [u_{ts}  sin(c_{ts}), u_{ts}  cos(c_{ts})]^T
    \end{matrix}
```

With $u$ and $u_{ts}$ being the speed over ground of the own ship and
target ship respectively; and $c$ being the course of the own ship. The
range situation $RS$ is therefore selected as:

```math
RS = \begin{cases}
        closing :p_{rel} \cdot v_{rel} \leq 0\\
        increasing :p_{rel} \cdot v_{rel} > 0
    \end{cases}
```

This information is used to select one of 6 encounter types:

```math
\begin{matrix}
    SAFE = 1\\
    OVERTAKING \,STARBOARD = 2\\
    OVERTAKING\,PORT = 3\\
    HEADON = 4\\
    GIVEWAY = 5\\
    STANDON = 6
    \end{matrix}
```

#### Encounter Classifier State Machine

As previously mentioned a State Machine (DSM)is required in order to
keep the encounter classification. The state machine is designed so that
classification will be kept until the encounter is deemed safe, see
Figure [5.3](#fig:class_dsm){reference-type="ref"
reference="fig:class_dsm"}. It is worth noting that an instance of the
DSM is created for each relevant target vessel.

![COLREGs state machine. The abbreviations "GSF," "GSO," "GOT,""GGW," and
"GHO" denote geometrical situations, while "entryxx" and "exitxx" denote
additional state-dependent entry and exit criterias](./figs/encounter_class_dsm.PNG)

The Geometrical situation for the transitions is provided by the
Encounter Classifier Method described in the previous section. The
current state of the state machine will effectively be the output of the
Encounter Classifier Module.

The state transitions are defined in the following fashion: each state
must transition to and from the initial safe state when the entry or
exit conditions are met. For the time being, the emergency state will be
ignored.

As an example, the state machine can only transition from the SAFE state
to the HEADON state if the entry condition is met and the geometrical
situation provided by the Encounter Classifying Method is HEADON.
Conversely, the HEADON state can only be exited if the Encounter
Classifying Method is SAFE or the exit conditions are met. The entry and exit 
conditions ("entryxx" and "exitxx") are dictated by the time to the closest point of approach (T2CPA) and the distance at the closest point of approach (D@CPA) between the own vessel and the target vessel. The entry condition is then defined as:

```math
(D@CPA < \bar{d}_{entry}) \land (\underbar{t}_{entry} < T2CPA < \bar{t}_{entry})
```

where $\bar{d}_{entry}$ is the upper boundary for entry distance, and $\underbar{t}_{entry}$, $\bar{t}_{entry}$ are the lower and upper boundaries for entry time. If this conditions are true, coupled with the geometrical interpretation of the situation, the state machine can transition from the safe state to that indicated by the geometrical classification. These conditions ensure that a transition will not happen is the vessels are too far apart at the CPA or if the CPA is too far in the future. Note that 
$\underbar{t}_{entry}$ will normally be zero. 

Conversely, the exit condition is defined as:

```math
(D@CPA \geq \underbar{d}_{exit}) \lor (T2CPA < \underbar{t}_{exit} \lor T2CPA >  \bar{t}_{exit})
```

where $\underbar{d}_{exit}$ is the lower boundary for exit distance, and $\underbar{t}_{exit}$, $\bar{t}_{exit}$ are the lower and upper boundaries for exit time. If this conditions are true, the state machine will go back to the SAFE state. This ensures that the state machine will revert back to the SAFE state once the own vessel gets far away enough from the target vessel.

### Implementation 

A class containing the Encounter Classifier Method along with the Enounter Classifier State Machine will be created. An instance of this class is to be created for every vessel identified in the arpa parameters. The object is to be updated whenever new arpa information is received. These will live inside of the colav_manager class.
In the forntend, the resulting encounter classification will be provided in the tooltips already existing in the react webapp.

## Polygonal CBF
The previous implementation of the CBF will be updated in order to make use of the encounter types. The objective is to use the encounter type for a given ship to determine the which polygonal obstacle domain will be used for the computations. This will build atop of the previous implementations of the CBF i.e; the 4dof simulation used to predict the own ships. That said, the polygonal domains call for a different implementation of the domain istelf since it will no loger be a circular domain, these will be based on the work of M. Marley [^5]

### Input 

The input of the Polygonal CBF will be the output of the arpa
module. this will comprehend NED information regarding the own ship, the
target ships, and their arpa parameters. Additionally the 

### Output

The output of the Polygonal CBF will be a message containing the points describing the trajectory generated by the 4dof prediction resulting from the input from the Polygonal CBF computations.

### Design
(This section is taken verbatim from Mathias's Work)
Let $Q \subset \N$ be a finite set, let $q \in Q$ be a logic variable, and define $B_1: \R^6 \times Q \rarr \R$ as 

```math
B_1 (x,q) := d_q - \tau_q^T(p-p_0)
```

for each fixed $q$, the zero sublevel set

```math
\{ x \in \R^6: B_1(x,q)\leq 0 \}
```

represents a half-plane constraint with distance parameter $d_q > 0$ and unit normal vector $\tau_q \in $\mathbb{S} _{one}$ referred to as the orientation. We assume the distance parameters are selected such that $|p-p_0| > min_{q\in Q}d_q$ implies that the ships are not iin contact. The collection of half-plane constraints form a Target Ship Critical Area (TSCA) given by

```math
TSCA(p_0):= \{p\in \R^2: B_1 (x,q) > 0 ,\forall q \in Q \}
```

where the parameter set $\{ (d_q, \tau_q): q \in Q\}$ is selected such that TSCA(p_o) forms a closed convex ploygon. 

Collision avoidance is then achieved by steering the ownship such that it stays clear of $TSCA(po)$, i.e., by enforcing $p(t) \notin TSCA(p_0(t))$ for all $t \geq 0$. Since $p \in TSCA(p_0) H \rArr B1(x, q) > 0$, this is equivalent to
maintaining $B_1(x(t), q(t)) \leq 0$ for all $t \geq 0$.\\
The key idea behind CBFs is to enforce safety by restricting
the evolution of $B_1$ along the system. However, since
$L_g B_1(x, q) = 0$, we have no direct control over $\dot{B}_1 = L_f B_1(x, q)$. Instead, we backstep the CBF by defining a second function $B_2 : 6 × Q → \R $ 

```math
B2(x, q) := Lf B1(x, q) + \gamma_1 B_1(x, q), 
```

where $\gamma_1 > 0$ is a tuning parameter. $B_2$ is used to identify an
input set

```math
U_B(x, q) := {r_d \in \R : \dot{B}
2(x, q, r_d ) \leq − \gamma_2 B_2(x, q)},
```

```math
\dot{B}_2(x, q, rd ) := L_f B_2(x, q) + L_g B_2(x, q) r_d
```

with tuning parameter $\gamma_2 > 0$. For each $(x, q) \in \R^6 × Q, U_B(x, q)$ is the set of inputs such that the evolution of $B_2$ along satisfies $\dot{B}_2 \leq - \gamma_2 B_2$

#### SAFEGUARDING CONTROL LAW
(This section is taken verbatin from Mathias's Work)
The state-dependent input constraint may be synthesized
with any nominal control law by always selecting the safe
input that is closest to the nominal input, i.e., by defining the
safeguarding control law

```math
rd,safe(x, q) :=  \underset{r_d \in U_B(x,q)}{arg \, min} \,\,\, |rd − r_{d,nom}(x)|
```


where $r_{d,nom} : \R^6 → \R$ is a nominal control law. For the
DSS we select the nominal control law 

```math
r_{d,nom}(z) := \frac{-k_1 \tilde{z}_2}{ \sqrt{1 - \lambda^2 \tilde{z}_1^2}}, \, \, \tilde{z}:= [ z_d \,\, S z_d ]^T \, z
```

$k1 > 0, 0 < \lambda < 1$, which regulates the ship heading to a
constant desired heading $z_d := (cos(\psi_d ),sin(\psi_d )) ∈ S_{one}$

#### SWITCHING LOGIC
(This section is taken verbatin from Mathias's Work)
For each fixed q, the closed-loop system moves
within the set $\{ x : B1(x, q) ≤ 0 \}$. What remains is to design a
logic for proper switching of the active safety constraint. 
Let $q^+$ denote the value of $q$ after a switch. We propose a dynamic
update law for $q$ based on bounded increase of $B_1$ and strict
decrease of $B_2$. In particular, we require that, whenever $q$
toggles, the inequalities
```math
B_1 (x, q^+) \leq max \{ 0, B1(x, q) \} 
```

```math
B_2 (x, q^+) \leq B_2(x, q) − \delta
```

are satisfied, with hysteresis width $\delta > 0$. Note that the
requirement of strict decrease of $B_2$ prevents chattering, since
it excludes the possibility of consecutive switches between
two values of $q$. Define
```math
H_1(x, q) : = \{h \in Q : B_1(x, h) \leq max \{ 0, B1(x, q) \} \},
```

```math
H_2(x, q) : = \{ h \in Q : B_2(x, h) \leq B_2(x, q) − \delta \}
```

```math
H(x, q) : = H_1(x, q) \cap H_2(x, q)
```

which identifies the subset of $q$ such that  is satisfied. The
switching logic is then formally stated as

```math
if H(x, q)  \not ={\emptyset}  :
```

```math
q^+ \in G(x, q) : = arg \underset{h \in H(x,q)}{min}  
B_2(x, h)
```

In the rare case that $G(x, q)$ is not unique, $q^+$ is selected at random.

### Implementation

The Polygonal CBF class will inherit the 4dof_cbf class and the aforementioned functionality will be implemented in this new class. A different polygon is to be selected based on the encounter type. The class itself will be instantiated within the colav_manager class and a prediction will be triggered whenever new arpa data is available. It is worth noting that the polygon effectively comprises a set of $q$ barriers disposed in different arrangements depending on the encounter type. The polygons themselves will be explored in order to determine which arrangements better enforce the enounter policy according to COLREGS.

Tentatively, a method for visually updating these polygons is to be implemented in the forntend to facilitate exploration.


[^1]: luissanchezmtn@gmail.com 

[^3]: Thyri, Emil and Breivik, Morten. A domain-based and reactive COLAV
    method with a partially COLREGs-compliant domain for ASVs operating
    in confined waters, 2022

[^4]: Entry and exit conditions are being tinkered with but they will
    likely be based on the D@CPA and T2CPA

[^5]: Four Degree-of-Freedom Hydrodynamic
Maneuvering Model of a Small Azipod-Actuated
Ship With Application to Onboard
Decision Support Systems, M. Marley et al. 2023
 