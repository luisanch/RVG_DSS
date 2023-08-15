---
author:
- Luis Fernando Sanchez Martin [^1]
date: July 2023
title: RVG DSS Design Notes
---
# Design Notes

## Encounter Classifier

The encounter classifier is a module meant to provide an encounter
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

### Encounter Classifying Method

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

$$\varphi = atan2((E_{TS} - E),(N_{TS} - N)) - \chi$$

The RBS is then determined by checking where in the range of
$[\theta_1, -\theta_1, \theta_2, -\theta_2]$ the angle $\varphi$ lands.

$$
    RBS = 
    \begin{cases}
        1 : 2\pi-\theta_1 < \varphi < \theta_1\\
        2 : \theta_1  < \varphi < \theta_2\\
        3 : \theta_2  < \varphi < 2\pi -\theta_2\\
        4 : 2`\pi-\theta_2 < \varphi < 2`\pi-\theta_1
    \end{cases}
    $$

The next step is to determine the SS. For this, we use a rotated version
of the angles from eq. [\[eq:rbs\]](#eq:rbs){reference-type="ref"
reference="eq:rbs"} $[\theta'_1, -\theta'_1, \theta'_2, -\theta'_2]$.

$$
\begin{matrix}
       \theta'_1 = \theta_1 + \varphi_{TS} \\
        \theta'_2 = \theta_2 + \varphi_{TS}
    \end{matrix}
    $$

The SS is then determined by checking where in this range the course of
the target vessel $c_{ts}$ lands.

$$
SS = 
    \begin{cases}
        1 : 2\pi-\theta'_1  < c_{ts} < \theta'_1\\
        2 : \theta'_1       < c_{ts} < \theta'_2\\
        3 : \theta'_2       < c_{ts} < 2\pi -\theta'_2\\
        4 : 2`\pi-\theta'_2 < c_{ts} < 2`\pi-\theta'_1
    \end{cases}
    $$

Finally, in order to determine whether the outer or the inner section of
the circle segment should be chosen, it is determined whether the range
between the vessels is increasing or decreasing. This is done by
obtaining the dot product of the relative position $p_{rel}$ and
velocity $v_{rel}$.

$$
\begin{matrix}
        p_{rel} = [n_{ts} - n, e_{ts} - e] \\
        v_{rel} = v_{ts} - v_{os}
    \end{matrix}
    $$

Where

$$
\begin{matrix}
        v_{os} = [u  cos(c), u  sin(c)]^T \\
        v_{ts} = [u_{ts}  cos(c_{ts}), u_{ts}  sin(c_{ts})]^T
    \end{matrix}
    $$

With $u$ and $u_{ts}$ being the speed over ground of the own ship and
target ship respectively; and $c$ being the course of the own ship. The
range situation $RS$ is therefore selected as:

$$
RS = \begin{cases}
        closing :p_{rel} \cdot v_{rel} \geq 0\\
        increasing :p_{rel} \cdot v_{rel} < 0
    \end{cases}
    $$

This information is used to select one of 6 encounter types:

$$
\begin{matrix}
        SAFE = 1\\
    OVERTAKING \,STARBOARD = 2\\
    OVERTAKING\,PORT = 3\\
    HEADON = 4\\
    GIVEWAY = 5\\
    STANDON = 6
    \end{matrix}
    $$

### Encounter Classifier State Machine

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
Classifying Method is SAFE or the exit conditions are met.[^4]

[^1]: luissanchezmtn@gmail.com 

[^3]: Thyri, Emil and Breivik, Morten. A domain-based and reactive COLAV
    method with a partially COLREGs-compliant domain for ASVs operating
    in confined waters, 2022

[^4]: Entry and exit conditions are being tinkered with but they will
    likely be based on the D@CPA and T2CPA
