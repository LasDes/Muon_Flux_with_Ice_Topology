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

    x_list = np.linspace(-250000, 249500, 1000)
    y_list = np.linspace(250000, -249500, 1000)

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


    val = (0.14 * pow(E/pow(10, 9), -2.7)) * (1 / (1 + 1.1 * E * np.cos(theta) / (115 * pow(10, 9)))
                                   + 0.054 / (1 + 1.1 * E * np.cos(theta) / (850 * pow(10, 9))))

    return val


cos_theta = np.linspace(1, 0.1, 11)[1:]

theta_list = np.arccos(cos_theta)

flux_map = []
dis_map = []

for theta in theta_list:
    # todo: change here
    phi_list = np.linspace(0, 2*pi, 20) # + pi

    flux_list = []
    dis_list = []


    for phi in phi_list:

        dir = np.array([sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta)])

        dis, normal_dir = get_dis(theta, phi)

        zenith = acos(np.dot(dir, normal_dir)/(np.linalg.norm(dir) * np.linalg.norm(normal_dir)))

        E = getnewE_inc(pow(10, 10), dis)

        print("doing theta = " + str(theta) + " phi = " + str(phi) + "E = " + str(E/pow(10, 9)))

        flux = get_flux(zenith, E)

        flux_list.append(flux)
        dis_list.append(np.log10(E/pow(10,9)))


    flux_list = np.array(flux_list)
    flux_list = flux_list/flux_list.mean()

    flux_map.append(flux_list)

    dis_list = np.array(dis_list)
    #dis_list = dis_list/dis_list.mean()
    dis_map.append(dis_list)


f = plt.figure()
plt.imshow(flux_map, extent=(0, 2*pi, 0, cos_theta.max()), aspect='auto')
plt.colorbar(label="Relative number of events")
plt.xlabel("phi in rad")
plt.ylabel("cos theta")
plt.show()
