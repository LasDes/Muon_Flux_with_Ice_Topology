import numpy as np
import matplotlib.pylab as plt
from math import *
plt.style.use("IceCube")

f = open("./surface.txt", 'r')

surface = []

while 1:
    temp = f.readline().split()

    if len(temp) < 1:
        break

    surface_temp = []

    for i in range(len(temp)):
        surface_temp.append(float(temp[i]))

    surface.append(surface_temp)


def get_rad(xp, yp):
    # todo: change here
    y = yp
    x = xp

    x_list = np.linspace(-250000, 250000, 1000)
    y_list = np.linspace(250000, -250000, 1000)

    index_y = -1
    index_x = -1

    for i in range(len(x_list))[1:]:
        if x >= x_list[i - 1] and x <= x_list[i]:
            index_x = i - 1

    for i in range(len(y_list))[1:]:
        if y <= y_list[i - 1] and y >= y_list[i]:
            index_y = i - 1

    if index_x == -1 or index_y == -1:
        print(xp, yp)
        print("range error of x or y")
        exit()

    height = surface[index_y][index_x]

    return height

"""
x_list = np.linspace(-166500, 166000, 666)
y_list = np.linspace(166500, -166000, 666)

height_list = []

for i in range(len(y_list)):
    print(i)
    temp_height = []
    for j in range(len(x_list)):
        height = get_rad(x_list[j], y_list[i])

        temp_height.append(height)

    height_list.append(temp_height)

plt.imshow(height_list, extent=(min(x_list)/1000, max(x_list)/1000, min(y_list)/1000, max(y_list)/1000))
plt.xlabel("x in km")
plt.ylabel("y in km")
plt.colorbar()
plt.show()
"""


"""--------------------------- simple test -----------------------------"""



def getnewE_inc(E, dis):
    b = 0.000363

    a = 0.259

    density = 0.9167
    # todo: check this: the unit for a and b are /mwe, which is meter water equivalence, as the result
    # todo: density is used here to convert into ice.
    # todo: however on the original paper a and b are plotted for ice, so I don't know if density is needed
    # todo: paper is at  FIG.21 from arXiv:hep-ph/0407075v3

    # convert E in GeV to use this eq
    A = (E / pow(10, 9) * b * density) + a * density
    # convert E_final back in eV
    E = (A * np.power(e, b * 1 * dis * density) - a * density) / (b * density) * pow(10, 9)

    return E



def get_dis(theta, phi):

    ori_pos = np.array([0, 0, 6371000 + get_rad(0, 0) - 2000])

    curr_pos = ori_pos

    dir = np.array([sin(theta)*cos(phi), sin(theta)*sin(phi), cos(theta)])

    while 1:

        #print(dir)

        curr_pos = curr_pos + dir * 10

        curr_dis = np.linalg.norm(curr_pos - ori_pos)

        curr_x = curr_pos[0]
        curr_y = curr_pos[1]

        curr_radius = 6371000 + get_rad(curr_x, curr_y)

        if np.linalg.norm(curr_pos) >= curr_radius:
            return curr_dis, curr_pos / np.linalg.norm(curr_pos)


        #escape_pos = curr_radius * curr_pos/np.linalg.norm(curr_pos)

        #curr_escape_dis = np.linalg.norm(escape_pos - ori_pos)


        #if curr_dis > curr_escape_dis:
        #    return curr_dis, curr_pos/np.linalg.norm(curr_pos)





def get_flux(theta, E):


    val = (0.14 * pow(E, -2.7)) * (1 / (1 + 1.1 * E * np.cos(theta) / (115))
                                   + 0.054 / (1 + 1.1 * E * np.cos(theta) / (850)))

    return val





cos_theta = np.linspace(1, 0.1, 41)[1:]

theta_list = np.arccos(cos_theta)

phi_list = np.linspace(0, 2*pi, 10)

flux_map = []

avg_flux = []

for theta in theta_list:
    # todo: change here
     # + pi

    flux_list = []


    for phi in phi_list:

        #print("doing theta = " + str(theta) + " phi = " + str(phi))

        dir = np.array([sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta)])

        dis, normal_dir = get_dis(theta, phi)

        zenith = acos(np.dot(dir, normal_dir) / (np.linalg.norm(dir) * np.linalg.norm(normal_dir)))

        E_ini = 1e10

        E_fin = getnewE_inc(E_ini, dis)

        print("doing theta = " + str(theta) + " phi = " + str(phi) + " " + "E_fin = " + str(E_fin))

        E_range = np.logspace(np.log10(E_fin), 17, 1000)/pow(10, 9)

        curr = 0

        for ene in E_range:

            flux = get_flux(zenith, ene)

            curr = curr + flux * (np.log10(E_range[1]) - np.log10(E_range[0])) * ene

        curr = curr * log(10)

        flux_list.append(curr)

        print(curr)

    flux_list = np.array(flux_list)
    avg_flux.append(flux_list.mean())
    flux_list = flux_list / flux_list.mean()

    flux_map.append(flux_list)


f = plt.figure()
plt.imshow(flux_map, extent=(0, 2 * pi, 0.1, cos_theta.max()), aspect='auto')
plt.colorbar(label="flux")
plt.xlabel("phi in rad")
plt.ylabel("cos theta")


f2 = plt.figure()
for i in range(len(flux_map)):
    plt.plot(phi_list, flux_map[i], label=str("{:.2f}".format(cos_theta[i])))

plt.legend()
plt.xlabel('phi')



f3 = plt.figure()
plt.plot(cos_theta, avg_flux)
plt.yscale('log')
plt.xlabel('cos theta')
plt.ylabel('avg integrated flux')
plt.show()

exit()


