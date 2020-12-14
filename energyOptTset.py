# energyOptTset ... expanding on energyOpt1 by solving for Tset

from cvxopt import matrix, solvers
import time
import pandas as pd
start_time=time.process_time()

# Parameters
timestep = 5*60
comfortZone_upper = 23.0
comfortZone_lower = 20.0
n=3 # number of timesteps; in future can determine from size of T_oudoor matrix

# Constants for indoor temperature equation
c1 = 2.04*10**-5
c2 = -1.50*10**-3
c3 = 1.20*10**-6
d1 = 677.0
d2 = -579.0
d3 = -168.0
d4 = -0.630

# Data from EnergyPlus
temp_indoor_initial = 23.0
#temp_outdoor = matrix([21.1,21.333334,21.566668,21.799999,22.033333,22.266666,22.5,22.733334,22.966667,23.200001,23.433332,23.666666,23.9,24.041666,24.183332,24.325001,24.466667,24.608334,24.75,24.891666,25.033333,25.174999,25.316668,25.458334,25.6,25.825001,26.049999,26.275,26.5,26.725,26.950001,27.174999,27.4,27.625,27.85,28.075001,28.299999,28.166666,28.033333,27.9,27.766666,27.633333,27.5,27.366667,27.233334,27.1,26.966667,26.833334,26.700001])
df = pd.read_excel('outdoorTemp.xlsx', sheet_name='Sheet1')
# print(len(df))
temp_outdoor_all=matrix(df.to_numpy())
n=48
#q_solar = matrix([111.5,112.416664,113.333336,114.25,115.166664,116.083336,117,117.416664,117.833336,118.25,118.666664,119.083336,119.5,119.916664,120.333336,120.75,121.166664,121.583336,122,122.083336,122.166664,122.25,122.333336,122.416664,122.5,122.583336,122.666664,122.75,122.833336,122.916664,123,122.75,122.5,122.25,122,121.75,121.5,121.25,121,120.75,120.5,120.25,120,119.333336,118.666664,118,117.333336,116.666664,116])
df = pd.read_excel('Solar.xlsx', sheet_name='Sheet1')
# print(len(df))
q_solar_all=matrix(df.to_numpy())
#print(temp_outdoor)
#print(type(temp_outdoor))

# c matric is hourly cost per kWh of energy
# 0:00-1:00 ==> j = 0-12
# 1:00-2:00 ==> j = 12-24
# 2:00-3:00 ==> j = 24-36
# 3:00-4:00 ==> j = 36-48
# 4:00-5:00 ==> j = 48-60
# 5:00-6:00 ==> j = 60-72
# 6:00-7:00 ==> j = 72-84
# 7:00-8:00 ==> j = 84-96
# 8:00-9:00 ==> j = 96-108
# 9:00-10:00 ==> j = 108-120
# 10:00-11:00 ==> j = 120-132
# 11:00-12:00 ==> j = 132-144
# 12:00-13:00 ==> j = 144-156
# 13:00-14:00 ==> j = 156-168
# 14:00-15:00 ==> j = 168-180
# 15:00-16:00 ==> j = 180-192
# 16:00-17:00 ==> j = 192-204
# 17:00-18:00 ==> j = 204-216
# 18:00-19:00 ==> j = 216-228
# 19:00-20:00 ==> j = 228-240
# 20:00-21:00 ==> j = 240-252
# 21:00-22:00 ==> j = 252-264
# 22:00-23:00 ==> j = 264-276
# 23:00-00:00 ==> j = 276-288
Output = matrix(0.00, (324,2))
cost =0
c = matrix(0.20, (324,1))
# j=0
# while j<324:
	# if j < 35 or j> 45:
	# c[j,0]=0.20
	# j = j+1
	# else:
	# 	c[j,0]=2.0
	# 	j=j+1
################################################################

# A matrix is coefficients of energy used variables in constraint equations
AA = matrix(0.0, (n*3,n))
i = 0;
while i<n:
	AA[i,i] = -1.0 # setting boundary condition: Energy used at each timestep must be greater than 0
	i +=1

k = 0
while k<n:
	j = n+2*k
	AA[j,k] = timestep*c2
	AA[j+1,k] = -timestep*c2
	k=k+1

k = 0
while k<n:
	j=n+2*k+2
	while j<n*3-1:
		AA[j,k] = AA[j-2,k]*-timestep*c1+ AA[j-2,k]
		AA[j+1,k] = AA[j-1,k]*-timestep*c1+ AA[j-1,k]
		j+=2
	k=k+1

# creating S matrix to make b matrix simpler
for ii in range(0,24):
	temp_outdoor= temp_outdoor_all[ii*12:ii*12+48,0]
	q_solar=q_solar_all[ii*12:ii*12+48,0]
	cc=c[ii*12:ii*12+48,0]
	S = matrix(0.0, (n,1))
	S[0,0] = timestep*(c1*(temp_outdoor[0]-temp_indoor_initial)+c3*q_solar[0])+temp_indoor_initial

	i=1
	while i<n:
		S[i,0] = timestep*(c1*(temp_outdoor[i]-S[i-1,0])+c3*q_solar[i])+S[i-1,0]
		i+=1
	#print(S)

	# b matrix is constant term in constaint equations
	b = matrix(0.0, (n*3,1))

	k = 0;
	while k<n:
		b[2*k+n,0]=comfortZone_upper-S[k,0]
		b[2*k+n+1,0]=-comfortZone_lower+S[k,0]
		k=k+1
	#print(b)

	# time to solve for energy at each timestep
	print(cc)
	print(AA)
	print(b)
	sol=solvers.lp(cc,AA,b)
	energy = sol['x']
	cost = cc.trans()*energy
	temp_indoor = matrix(0.0, (n,1))
	temp_indoor[0,0] = temp_indoor_initial
	p = 1
	while p<n:
		temp_indoor[p,0] = timestep*(c1*(temp_outdoor[p-1,0]-temp_indoor[p-1,0])+c2*energy[p-1,0]+c3*q_solar[p-1,0])+temp_indoor[p-1,0]
		p = p+1
	Output[ii*12:ii*12+12,0] = energy[0:12,0]
	Output[ii*12:ii*12+12,1] = temp_indoor[0:12,0]
	cost = cost + cc[0:12,0].trans()*energy[0:12,0]
	# print(ii)
	# print(cost)
	# print(Output)
	# print(temp_indoor)
	temp_indoor_initial= temp_indoor[12,0]
	print(temp_indoor_initial)

# # solve for thermostat temperature at each timestep
# thermo = matrix(0.0, (n,1))
# i = 0
# while i<n:
# 	thermo[i,0] = (-d2*temp_indoor[i,0]-d3*temp_outdoor[i]-d4*q_solar[i]+energy[i]*1000/12)/d1
# 	i = i+1


print(Output)
print("Total price =") 
print(cost)
# print("Thermostat setup =") 
# print(thermo)
# print("Indoor Temperature =") 
# print(temp_indoor)
print("--- %s seconds ---" % (time.process_time()-start_time))
