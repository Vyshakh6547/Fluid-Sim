# -*- coding: utf-8 -*-
"""RBC.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Gj8MiOjWGwjdZPLmhrctrMWBsC2erhcU
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import scipy.special as spe
import scipy.linalg as sp
from pylab import rcParams
rcParams['figure.figsize']=9,7

#constants and parameters
pi=np.pi
Ly = 10
Lx = 10
Lz = 2*np.sqrt(2)
Nx = Ny = Nz = 8
N = 8

Nt = 20
t = 0.0
tfinal= 10.0
dt = 1/1000.0
Rac = 657.51136448
Ra = 0.1*Rac
Pr = 0.01
kappa = 7.28*(10**-8)

x =  np.linspace(-Lx/2.0,Lx/2.0,N)
y =  np.linspace(-Ly/2.0,Ly/2.0,N)
z =  np.linspace(-Lz/2.0,Lz/2.0,N)
tn=  np.linspace(0,tfinal,int(tfinal/dt))
dx = x[1]-x[0]
dy = y[1]-y[0]
dz = z[1]-z[0]

#allocating arrays

kr = np.zeros((Nx,Ny,Nz))
pr = np.zeros((Nx,Ny,Nz))
qr = np.zeros((Nx,Ny,Nz))
kx = np.fft.fftfreq(Nx,dx)
ky = np.fft.fftfreq(Ny,dy)
kz = np.fft.fftfreq(Nz,dz)
k1 = np.array([kx,ky,kz])
pre= np.zeros((3,Nx,Ny,Nz))
th = np.zeros((Nx,Ny,Nz))
ux = np.zeros((Nx,Ny,Nz))
uy = np.zeros((Nx,Ny,Nz))
uz = np.zeros((Nx,Ny,Nz))
uxn = np.zeros((Nx,Ny,Nz))
uyn = np.zeros((Nx,Ny,Nz))
uzn = np.zeros((Nx,Ny,Nz))
u_ri = np.array([ux,uy,uz])
u_r = np.zeros((3,8,8,8),dtype='complex')
utemp_r = np.zeros((3,8,8,8),dtype='complex')
uk = np.zeros((3,8,8,8),dtype='complex')
Nu = np.zeros((3,8,8,8),dtype='complex')
Ntheta = np.zeros((8,8,8),dtype='complex')
utemp = np.array([uxn,uyn,uzn])

X,Y = np.meshgrid(x,y)

#initial conds and velocity amplitudes

k = np.array([[1.0,0,0],[0.5,np.sqrt(3)/2.0,0],[0.5,-np.sqrt(3)/2.0,0]])
# Amp = np.array([[0,np.sqrt(3),-np.sqrt(3)],[-2.0,-1.0,-1],[2.0,-2.0,-2.0]])
Amp = np.array([[0,-1,1],[np.sqrt(3)/2.0,-0.5,0],[np.sqrt(3)/2.0,0.5,0]])
tamp = np.array([0,0,2])

for i in range(N):
    for j in range(N):
        for m in range(N):
            kr[i,j,m]=k[0][2]*z[i]+k[0][0]*x[j]+k[0][1]*y[m]
            pr[i,j,m]=k[1][2]*z[i]+k[1][0]*x[j]+k[1][1]*y[m]
            qr[i,j,m]=k[2][2]*z[i]+k[2][0]*x[j]+k[2][1]*y[m]
n = {0,0,1}

for i in range(3):
    u_ri[i] = Amp[0][i]*np.exp(1j*kr)+Amp[1][i]*np.exp(1j*pr)+Amp[2][i]*np.exp(1j*qr)
#     th = tamp[0]*np.exp(1j*kr)+tamp[1]*np.exp(1j*pr)+tamp[2]*np.exp(1j*qr)
'''

u_ri[:,0,:,:]=0
u_ri[:,:,0,:]=0
u_ri[:,:,:,0]=0
u_ri[:,-1,:,:]=0
u_ri[:,:,-1,:]=0
u_ri[:,:,:,-1]=0
'''
th_r[0,:,:]=0
th_r[-1,:,:]=10
#Doing FFT

for i in range(3):
    uk[i] = np.fft.fftn(u_ri[i])
thk = np.fft.fftn(th)
ter=np.zeros(8)
te=np.zeros(int(tfinal/dt))
nstep=0

utemp=uk
thetatemp=thk

# initial plot
fig, _axs = plt.subplots(nrows=2, ncols=2)
fig.subplots_adjust(hspace=0.3)
axs = _axs.flatten()

cset1 = axs[0].contourf(X,Y,(u_ri[0][1]) , linewidths=0.5, cmap="RdBu_r")
axs[0].contour(X,Y,u_ri[0][1], colors='k')
axs[0].set_title('Ux in a xy plane')
fig.colorbar(cset1, ax=axs[0])

cset2 = axs[1].contourf(X,Y,(u_ri[1][1]) , linewidths=0.5, cmap="RdBu_r")
axs[1].contour(X,Y,u_ri[1][1] , colors='k')
axs[1].set_title('Uy in a xy plane')
fig.colorbar(cset2, ax=axs[1])

cset3 = axs[2].contourf(X,Y,(u_ri[2,:,1,:]) , linewidths=0.5, cmap="RdBu_r")
axs[2].contour(X,Y,u_ri[2,:,1,:] , colors='k')
axs[2].set_title('Uz in a yz plane')
fig.colorbar(cset3, ax=axs[2])

cset4 = axs[3].contourf(X,Y,(th[:,1,:]) , linewidths=0.5, cmap="RdBu_r")
axs[3].contour(X,Y,th[:,1,:] , colors='k')
axs[3].set_title('Temp in a yz plane')
fig.colorbar(cset4, ax=axs[3])

fig.tight_layout()
plt.show()



#solving pdes using euler and plotting with each time step
while t<tfinal:

#     utemp[i][5:,5:,5:]=0.0
#     thetatemp[5:,5:,5:]=0.0
    for i in range(3):
        u_r[i] = np.fft.ifftn(utemp[i])
    th_r = np.fft.ifftn(thetatemp)

    th_r[0]=0
    th_r[-1]=10

    '''
    #Boundary Conditions(FSS)
    th_r[0]=10
    th_r[-1]=0
    u_r[:,0,:,:]=0
    u_r[:,:,0,:]=0
    u_r[:,:,:,0]=0
    u_r[:,-1,:,:]=0
    u_r[:,:,-1,:]=0
    u_r[:,:,:,-1]=0
'''
    for i in range(3):
        utemp[i] = np.fft.fftn(u_r[i])
    thetatemp=np.fft.fftn(th_r)

    #Nonlinear-terms Calculation
    Nu = np.zeros((3,8,8,8),dtype='complex')
    Ntheta = np.zeros((8,8,8),dtype='complex')
    for i in range(3):
        Ntheta += 1j*k1[i]*np.fft.fftn(u_r[i]*th_r)
        for j in range(3):
            Nu[i] += 1j*k1[j]*np.fft.fftn(u_r[i]*u_r[j])
        #antialiasing
        Nu[i,5:,5:,5:]=0.0 #only filling 2/3rd of the array
    Ntheta[5:,5:,5:]=0.0

#     print(abs(utemp[i]-u_ri[i]))


    #timestepping euler
    for i in range (3):
        v=k1[0]*Nu[0]+k1[1]*Nu[1]+k1[2]*Nu[2]#N.k calculation
        pre[i]=(1.0/np.dot(k1[i],k1[i]))*(k1[i]*v-Ra*Pr*k1[2]*thetatemp*k1[i])#pressure

        #velocity time stepping
        if i==2:
            utemp[i]=utemp[i]+dt*(-Nu[i]+Ra*Pr*thetatemp-Pr*np.dot(k1[i],k1[i])*utemp[i]+pre[i])#to account for delta(i,3)*Force term

        else:
            utemp[i]=utemp[i]+dt*(-Nu[i]-Pr*np.dot(k1[i],k1[i])*utemp[i]+pre[i])

    thetatemp=thetatemp+dt*(-Ntheta+utemp[2]-kappa*np.dot(k1[i],k1[i])*thetatemp)#temp time stepping

    '''#RK-2
    for i in range(3):
        thetatemp=thetatemp+dt*(-Ntheta+utemp[2]-kappa*np.dot(k1[i],k1[i])*thetatemp)
        v=k1[0]*Nu[0]+k1[1]*Nu[1]+k1[2]*Nu[2]
        pre[i]=(1.0/np.dot(k1[i],k1[i]))*(k1[i]*v-Ra*Pr*k1[2]*thk)
        utemp[i]=uk[i]+dt*(-Nu[i]-Pr*np.dot(k1[i],k1[i])*uk[i]+pre[i])
        if i==2:
            utemp[i]=uk[i]+dt*(-Nu[i]+Ra*Pr*thetatemp-Pr*np.dot(k1[i],k1[i])*uk[i]+pre[i])
    '''

    for i in range(3):
        utemp_r[i] = np.fft.ifftn(utemp[i])
    #if t!=0:print(abs(utemp_r[0][1])-ter)
    ter=abs(utemp_r[0][1])
    th_r = np.fft.ifftn(thetatemp)
    #print(abs(utemp_r[0][1]))

    #plotting
    fig, _axs = plt.subplots(nrows=2, ncols=2)
    fig.subplots_adjust(hspace=0.3)
    axs = _axs.flatten()

    cset1 = axs[0].contourf(X,Y,(utemp_r[0][1]) , linewidths=0.5, cmap="RdBu_r")
    axs[0].contour(X,Y,utemp_r[0][1], colors='k')
    axs[0].set_title('Ux in a xy plane')
    fig.colorbar(cset1, ax=axs[0])

    cset2 = axs[1].contourf(X,Y,(utemp_r[1][1]) , linewidths=0.5, cmap="RdBu_r")
    axs[1].contour(X,Y,utemp_r[1][1] , colors='k')
    axs[1].set_title('Uy in a xy plane')
    fig.colorbar(cset2, ax=axs[1])

    cset3 = axs[2].contourf(X,Y,(utemp_r[2,:,1,:]) , linewidths=0.5, cmap="RdBu_r")
    axs[2].contour(X,Y,utemp_r[2,:,1,:] , colors='k')
    axs[2].set_title('Uz in a yz plane')
    fig.colorbar(cset3, ax=axs[2])

    cset4 = axs[3].contourf(X,Y,(th_r[:,1,:]) , linewidths=0.5, cmap="RdBu_r")
    axs[3].contour(X,Y,th_r[:,1,:] , colors='k')
    axs[3].set_title('Temp in a yz plane')
    fig.colorbar(cset4, ax=axs[3])

    fig.tight_layout()
    plt.show()
    '''plt.contourf(X,Y,utemp_r[0][:,1,:] , linewidths=0.5, cmap="RdBu_r")
    axs[3].contour(X,Y,utemp_r[0][:,1,:] , colors='k')
    axs[3].set_title('Ux in a yz plane')
    fig.colorbar(cset4, ax=axs[3])
    plt.show()
    plt.contourf(X,Y,utemp_r[2][1] , linewidths=0.5, cmap="RdBu_r")
    plt.show()
    plt.contourf(X,Y,(th_r[1]) , linewidths=0.5, cmap="RdBu_r")
    plt.show()'''
    t=t+dt
    print(t,nstep)

    te[nstep]=np.sqrt(utemp[0][0,0,1]**2+utemp[1][0,0,1]**2+utemp[2][0,0,1]**2)
    nstep=nstep+1

plt.plot(tn,te)
plt.xlabel('time(s)')
plt.ylabel('Velocity')
plt.show()

# plt.plot(tn,te)
plt.plot(tn[:400],te[:400])
plt.xlabel('time(s)')
plt.ylabel('Velocity')
plt.show()