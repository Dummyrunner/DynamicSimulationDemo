# Notes

## Control the inverted pendulum
#### Sources
- https://acme.byu.edu/00000179-af79-d5e1-a97b-bf796edc0000/pendulum2020-pdf
- https://www.ijirset.com/upload/2018/april/49_PD-PID%20control.pdf
- https://scispace.com/pdf/state-space-based-linear-controller-design-for-the-inverted-4j498roohh.pdf
- https://ctms.engin.umich.edu/CTMS/index.php?example=InvertedPendulum&section=ControlPID


### Summarizing sources
#### Kuczmann - Comprehensive Survey of PID Controller Design for the Inverted Pendulum
##### Modeling
phi $\varphi$ inclination angle
Input force $u = F$ to stabilize $\varphi \rightarrow 0$
$x$ horizontal position

Modeling via Euler-Lagrange method, generalized coordinates
$q_1 = x, q_2 = \varphi, \tau_1 = F, \tau_2 = 0$.

Resulting differential equations (Eq. (7)):

$(m + M)\ddot{x}+ ML \cos(\varphi)\ddot\varphi - ML\sin(\varphi) {\dot\varphi}^2 = F \\ 
ML \cos(\varphi)\ddot{x}  + (ML^2 + \Theta)\ddot{\varphi} - MgL\sin(\varphi) = 0$ 
nonlinear PDE.

Choos state variables
$x^1 = x, x_2 = \dot x = \dot{x_1}, x_3 = \varphi, x_4  = \dot \varphi = \dot{x}_3$

Linearization:
$ \sin \varphi \approx \varphi, \cos \varphi \approx 1$

Result: LTI state space representation

$\dot x = Ax + bu \\ y = Cx + Du$

input $u$ influences $x_2 = \dot x, x_4 = \dot\varphi$. 

as output, use $\varphi$, or $(x,\varphi)$

Calculate transfer function $\frac{\Phi(s)}{U(s)} = \frac{\alpha}{s^2 - p^2}$ -> one stable one unstable pole

#### Control design for angle diminishing only

$W_O$ Transfer function of open loop
$W_C$ Transfer function of controller

Use Nyquist criterion:
Need one ccw encircling of (-1, 1) for stability. Can not be satisfied, when gain is negative

Analytically check poles of cl system.
Again gain the insight, that system has poles with positive Re, if $K_P$ is positive

PD controller: analyze transfer function with PD controller represented as
$W_C = K_{PD}\frac{1 + s T_D}{1 + s T_D'}$
Setting of $T_D, T'_D$, $K_P$ has to be negative

Phase Considerations ? 

PI Controller
TF of PI controller: $W_C = K_{PI} \frac{1 + s T_I}{s T_I}$
calculations yield, that system is not stabilizable by PI controller

PID Controller
$W_C = K_{PID} \frac{1 + sT_I}{sT_I} \frac{1 + sT_D}{1 + sT'_D}$
able to stabilize the PID criterion for params in certain ranges. Used Routh-Hurwitz criterion.

##### Stabilizing the Horizontal Movement
One PID controller not sufficient to control angle and x-axis position.
Solution: control signal not calculated by one PID controller, but sum of two PID controllers.

16 possible combinations for a pair of P, I, D controllers

Outlook:
combining 2 PID controllers rather uncomfortable, look to state feedback

#### Kuczmann - State Space Based Linear Controller Design for the Inverted Pendulum



### Control structure

