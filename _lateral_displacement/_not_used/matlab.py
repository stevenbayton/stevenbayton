import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Placeholder functions
# You will need to implement these
# -----------------------------
def k_sand(phi):

    a = 0.423
    b = -20.6
    c = 226

    k = (a*np.power(phi, 2) + b*phi + c) * 1000

    return k

def p_ult_sand(z, phi, gamma_, D):

    a = [2.632e-4, -8.489e-5, 1.064e-2]
    b = [-1.593e-2, 1.018e-2, -6.910e-1]
    c = [4.144e-1, -2.371e-1, 1.639e1]
    d = [-3.278, 2.948, -1.287e2]

    C1 = a[0]*np.power(phi, 3) + b[0]*np.power(phi, 2) + c[0]*phi + d[0]
    C2 = a[1]*np.power(phi, 3) + b[1]*np.power(phi, 2) + c[1]*phi + d[1]
    C3 = a[2]*np.power(phi, 3) + b[2]*np.power(phi, 2) + c[2]*phi + d[2]

    z_r = (C3 - C2)*D/C1

    if z < 0:
        p_ult_sand = 1e-10
    elif z < z_r:
        p_ult_sand = max(1e-10, (C1*z + C2*D)*gamma_*z)
    else:
        p_ult_sand = C3*D*gamma_*z

    return p_ult_sand


def p_y_sand(z, p_ult_sand, A, k, y):

    p = A*p_ult_sand*np.tanh((k*z/A/p_ult_sand)*y)

    return p


def p_ult_clay(z, su, gamma_, D, J=0.5):

    z_r = 6*D / (gamma_*D / su + J)

    if z < 0:
        p_ult_clay = 0
    elif z <= z_r:
        p_ult_clay = (3*su + gamma_*z)*D + J*su
    else:
        p_ult_clay = 9*su*D

    return p_ult_clay


D = 36 * 25.4 / 1000
T = 1.5 * 25.4 / 1000
L = 20
Es = 205e3 # kN/m2

I = np.pi/64 * (np.power(D, 4) - np.power((D - 2*T), 4))  # m^4

Q_top = []
y_py = []
p_py = []
E_py = []
Mt_py = []
Q_py = []
R_py = []

for f in range(500):
    Q_top.append(1*f) # kN

    ecc_top = 5
    Q_bottom = 0
    ecc_bottom = 0
    Q_a = 0
    h = 0.05

    k = k_sand(phi) # kN/m2

    N1 = int(ecc_top/h)
    N2 = int(L/h+1)

    a = np.zeros(N1+N2)
    b = np.zeros(N1+N2)
    c = np.zeros(N1+N2)
    d = np.zeros(N1+N2)
    e = np.zeros(N1+N2)
    K = np.zeros((N1+N2, N1+N2))
    B = np.zeros(N1+N2)
    y = [np.zeros(N1+N2)]
    p = [np.zeros(N1+N2)]

    B[0] = 2*Q_top[-1]*h**3
    z_array = np.array([-ecc_top + h*i for i in range(N1+N2)])
    mudline_idx = np.where((z_array < h/2) & (z_array > -h/2))[0]

    A = np.array([max(0.9, (3 - 0.8*zi/D)) for zi in z_array])

    
    
    E_0 = 10000 # kPa
    E = [np.array([0 if zi < 0 else E_0 for zi in z_array])]

    count = 1
    Err = [1]
    while Err[-1] > 1e-6:
        c[0] = (2*Es*I-2*Q_a*h**2) + E[count-1][0]*h**4
        d[0] = (-4*Es*I+2*Q_a*h**2)
        e[0] = (2*Es*I)
        b[1] = (-2*Es*I+Q_a*h**2)
        c[1] = (5*Es*I-2*Q_a*h**2) + E[count-1][1]*h**4
        d[1] = (-4*Es*I+Q_a*h**2)
        e[1] = (Es*I)

        for j in range(2, N1+N2-2):
            a[j] = Es*I
            b[j] = -4*Es*I + Q_a*h**2
            c[j] = 6*Es*I - 2*Q_a*h**2 + E[count-1][j]*h**4
            d[j] = -4*Es*I + Q_a*h**2
            e[j] = Es*I

        a[-2] = Es*I
        b[-2] = -4*Es*I + Q_a*h**2
        c[-2] = 5*Es*I - 2*Q_a*h**2 + E[count-1][-1]*h**4
        d[-2] = -2*Es*I + Q_a*h**2
        a[-1] = 2*Es*I
        b[-1] = -4*Es*I
        c[-1] = 2*Es*I + E[count-1][-2]*h**4

        K[0,0] = c[0]
        K[0,1] = d[0]
        K[0,2] = e[0]
        K[1,0] = b[1]
        K[1,1] = c[1]
        K[1,2] = d[1]
        K[1,3] = e[1]

        for j in range(2, N1+N2-2):
            K[j,j-2] = a[j]
            K[j,j-1] = b[j]
            K[j,j]   = c[j]
            K[j,j+1] = d[j]
            K[j,j+2] = e[j]

        K[-2,-4] = a[-2]
        K[-2,-3] = b[-2]
        K[-2,-2] = c[-2]
        K[-2,-1] = d[-2]
        K[-1,-3] = a[-1]
        K[-1,-2] = b[-1]
        K[-1,-1] = c[-1]

        y_new = np.linalg.solve(K, B) # m
        y_new = np.array([1e-10 if yi == 0 else yi for yi in y_new])
        y.append(y_new)

        p_new = np.zeros(N1+N2)
        E_new = np.zeros(N1+N2)

        p_new = np.array([p_y_sand(z_array[i], p_ult_sand[i], A[i], k[i], y[i]) for i in range(N1+N2)])
        E_new = np.array([p_new[i]/y_new[i] for i in range(N1+N2)])

        p.append(p_new)
        E.append(E_new)

        Err.append(np.sum(np.abs(y_new - y[-1])))
        
    y_py.append(y[-1])
    p_py.append(p[-1])
    E_py.append(E[-1])

    Mt = np.zeros(N1+N2)
    for i in range(1, N1+N2-1):
        Mt[i] = Es*I/h**2*(y[-1][i-1] - 2*y[-1][i] + y[-1][i+1])
    Mt_py.append(Mt)

    Q = np.zeros(N1+N2)
    Q[0] = (1/(2*h))*(-3*Mt[0] + 4*Mt[1] - Mt[2])
    for i in range(1, N1+N2-1):
        Q[i] = (1/(2*h))*(Mt[i+1] - Mt[i-1])
    Q[mudline_idx] = Q_top[f]
    Q[-1] = (1/(2*h))*(3*Mt[-1] - 4*Mt[-2] + Mt[-3])
    Q_py.append(Q)

    diff = y[-1][mudline_idx-1] - y[-1][mudline_idx+1]
    R = 180/np.pi*np.arctan(diff/(2*h))
    R_py.append(R)

plt.figure()
plt.plot([x[mudline_idx] for x in y_py], Q_top)
plt.show()

fig, ax = plt.subplots(1, 5, sharey=True, figsize=(14, 10))

ax[1].plot(p_u*A, z_array, ls='--', color='grey')
ax[1].plot(-p_u*A, z_array, ls='--', color='grey')
for i, q_top_i in enumerate(Q_top):
    if i % 50 == 0:
        ax[0].plot(y_py[i], z_array)
        ax[1].plot(p_py[i], z_array)
        ax[2].plot(E_py[i], z_array)
        ax[3].plot(Mt_py[i], z_array)
        ax[4].plot(Q_py[i], z_array, label=q_top_i)

ax[0].set_ylim(max(z_array), -1)
ax[0].set_xlabel('Displacement (m)')
ax[0].set_xlim(min(y_py[i])*1.1, y_py[i][mudline_idx]*1.1)
ax[1].set_xlabel('Reaction force (kN/m)')
ax[2].set_xlabel('Secant stiffness (kPa)')
ax[3].set_xlabel('Moment (kNm)')
ax[4].set_xlabel('Shear (kN)')
ax[0].grid('on')
ax[1].grid('on')
ax[2].grid('on')
ax[3].grid('on')
ax[4].grid('on')

plt.legend()
plt.show()

plt.figure()
depth_plot = [0.25, 0.5, 0.75, 1, 1.5, 2]
for depth_ploti in depth_plot:
    depth_plot_idx = np.where((z_array < depth_ploti + h/2) & (z_array > depth_ploti - h/2))[0]
    plt.plot([x[depth_plot_idx] for x in y_py], [y[depth_plot_idx] for y in p_py], label=depth_ploti)

plt.legend()
