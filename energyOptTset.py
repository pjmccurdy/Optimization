# energyOptTset ... expanding on energyOpt1 by solving for Tset

from cvxopt import matrix, solvers
from cvxopt.modeling import op, dot, variable
import time
start_time=time.clock()

# Parameters
timestep = 5*60
comfortZone_upper = 23.0
comfortZone_lower = 20.0
n=3 # number of timesteps; in future can determine from size of T_oudoor matrix

# Constants for indoor temperature equation
c1 = 2.04*10**-5
c2 = -1.50*10**-3
c3 = 1.20*10**-6
d1 = 1007
d2 = -907
d3 = -181
d4 = -0.434

heatorcool = 'cool'

# Data from EnergyPlus
temp_indoor_initial = 23.0
temp_outdoor = matrix([21.1,21.333334,21.566668,21.799999,22.033333,22.266666,22.5,22.733334,22.966667,23.200001,23.433332,23.666666,23.9,24.041666,24.183332,24.325001,24.466667,24.608334,24.75,24.891666,25.033333,25.174999,25.316668,25.458334,25.6,25.825001,26.049999,26.275,26.5,26.725,26.950001,27.174999,27.4,27.625,27.85,28.075001,28.299999,28.166666,28.033333,27.9,27.766666,27.633333,27.5,27.366667,27.233334,27.1,26.966667,26.833334,26.700001])
#([13.70,13.72,13.73,13.75,13.77,13.78,13.80,13.82,13.83,13.85,13.87,13.88,13.90,13.83,13.75,13.68,13.60,13.53,13.45,13.38,13.30,13.23,13.15,13.08,13.00,12.92,12.83,12.75,12.67,12.58,12.50,12.42,12.33,12.25,12.17,12.08,12.00,11.93,11.85,11.78,11.70,11.63,11.55,11.48,11.40,11.33,11.25,11.18,])

n=len(temp_outdoor)
q_solar = matrix([111.5,112.416664,113.333336,114.25,115.166664,116.083336,117,117.416664,117.833336,118.25,118.666664,119.083336,119.5,119.916664,120.333336,120.75,121.166664,121.583336,122,122.083336,122.166664,122.25,122.333336,122.416664,122.5,122.583336,122.666664,122.75,122.833336,122.916664,123,122.75,122.5,122.25,122,121.75,121.5,121.25,121,120.75,120.5,120.25,120,119.333336,118.666664,118,117.333336,116.666664,116])
#([725.5,716.583313,707.666687,698.75,689.833313,680.916687,672,652.083313,632.166687,612.25,592.333313,572.416687,552.5,532.583313,512.666687,492.75,472.833344,452.916656,433,400.75,368.5,336.25,304,271.75,239.5,207.25,175,142.75,110.5,78.25,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

####
y=variable(n)
x=matrix(0.0, (n,1))
#k=0
#while k<n:
#	x[k]=abs(y[k])
#	k=k+1

# A matrix is coefficients of energy used variables in constraint equations
A = matrix(0.0, (n*2,n))

#i = 0;
#while i<n:
#	A[i,i] = 0.0 # setting boundary condition: Energy used at each timestep must be greater than 0
#	i +=1

k = 0
while k<n:
	j = 2*k
	A[j,k] = timestep*c2
	A[j+1,k] = -timestep*c2
	k=k+1
k=0
while k<n:
	j=2*k+2
	while j<2*n-1:
		A[j,k] = A[j-2,k]*-timestep*c1+ A[j-2,k]
		A[j+1,k] = A[j-1,k]*-timestep*c1+ A[j-1,k]
		j+=2
	k=k+1
#print(A)

# creating S matrix to make b matrix simpler
S = matrix(0.0, (n,1))
S[0,0] = timestep*(c1*(temp_outdoor[0]-temp_indoor_initial)+c3*q_solar[0])+temp_indoor_initial

i=1
while i<n: 
	S[i,0] = timestep*(c1*(temp_outdoor[i]-S[i-1,0])+c3*q_solar[i])+S[i-1,0]
	i+=1
#print(S)

# b matrix is constant term in constaint equations
b = matrix(0.0, (n*2,1))

k = 0;
while k<n:
	b[2*k,0]=comfortZone_upper-S[k,0]
	b[2*k+1,0]=-comfortZone_lower+S[k,0]
	k=k+1
#print(b)


##
#c=matrix(0.20,(1,n))
#j=0
#while j<n:
#	if j < 35 or j> 45:
#		c[0,j]=0.20
#		j = j+1
#	else:
#		c[0,j]=2.0
#		j=j+1


# c matric is hourly cost per kWh of energy
c = matrix(0.20, (n,1))
j=0
while j<n:
	if j < 35 or j> 45:
		c[j,0]=0.20
		j = j+1
	else:
		c[j,0]=2.0
		j=j+1

#print(c)


##

heat_positive = matrix(0.0, (n,n))
i = 0
while i<n:
	heat_positive[i,i] = -1.0 # setting boundary condition: Energy used at each timestep must be greater than 0
	i +=1

cool_negative = matrix(0.0, (n,n))
i = 0
while i<n:
	cool_negative[i,i] = 1.0 # setting boundary condition: Energy used at each timestep must be less than 0
	i +=1

d = matrix(0.0, (n,1))

ineq = (A*y <= b)
heatineq = (heat_positive*y<=d)
coolineq = (cool_negative*y<=d)


if heatorcool == 'heat':
	lp2 = op(dot(c,y),ineq)
	op.addconstraint(lp2, heatineq)
if heatorcool == 'cool':
	lp2 = op(dot(-c,y),ineq)
	op.addconstraint(lp2, coolineq)
lp2.solve()
energy = y.value
print(energy)
print(lp2.objective.value()) # total cost

# time to solve for energy at each timestep
#sol=solvers.lp(c,A,b)

#energy = sol['x']

#cost = c.trans()*energy
#temp_indoor = matrix(0.0, (n,1))
#temp_indoor[0,0] = temp_indoor_initial
#p = 1
#while p<n:
#	temp_indoor[p,0] = timestep*(c1*(temp_outdoor[p-1,0]-temp_indoor[p-1,0])+c2*energy[p-1,0]+c3*q_solar[p-1,0])+temp_indoor[p-1,0]
#	p = p+1
#
# solve for thermostat temperature at each timestep
#thermo = matrix(0.0, (n,1))
#i = 0
#while i<n:
#	thermo[i,0] = (-d2*temp_indoor[i,0]-d3*temp_outdoor[i]-d4*q_solar[i]+energy[i]*1000*12)/d1
#	i = i+1


#print(energy)
#print("price =") 
#print(cost)
#print(thermo)
#print(temp_indoor)
print("--- %s seconds ---" % (time.clock()-start_time))
