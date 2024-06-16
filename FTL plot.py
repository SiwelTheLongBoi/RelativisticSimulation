from math import degrees, radians, cos, sin, sqrt, atan
import datetime, csv, os
import matplotlib.pyplot as plt

def step_forward(last_step, step_size, c_sq, x_acc, y_acc, z_acc):
    next_step = last_step

    # Also this is a nightmare to edit because each part is defined by position in the list rather than a set of variable names
    # So any adjustment of the positions inthe list requires all of these steps to be rewritten

    # time step
    next_step[0] = last_step[0] + step_size

    # x coordinate (in meters)
    next_step[1] = last_step[1] + (last_step[3] * step_size)

    # y coordinate (in meters)
    next_step[2] = last_step[2] + (last_step[4] * step_size) - (0.5 * y_acc * (step_size ** 2))

    # velocity along x axis
    next_step[3] = (last_step[3] + (x_acc * step_size)) / ( 1 + ( (last_step[3] * (x_acc * step_size)) / c_sq ) )

    # relativistic velocity along y axis
    #next_step[4] = last_step[4] + (y_acc * step_size)
    next_step[4] = (last_step[4] + (y_acc * step_size)) / ( 1 + ( (last_step[4] * (y_acc * step_size)) / c_sq ) )

    # velocity
    next_step[5] = sqrt((next_step[3] ** 2) + (next_step[4] ** 2))

    # Time dilation 
    # Since the step_size is in seconds its already delta time
    lorentz_factor = sqrt(1 - (next_step[5] ** 2) / c_sq)
    next_step[9] = step_size * lorentz_factor

    # Cumulative time dilation
    next_step[10] = last_step[10] + next_step[9]

    return next_step

def step_forward_dict(last_step, step_size, c_sq, x_acc, y_acc, z_acc):
    c_sq = 299800000 ** 2
    next_step = last_step
    
    next_step["sim_time"] = last_step["sim_time"] + step_size
    next_step["x_pos"] = last_step["x_pos"] + (last_step["x_vel"] * step_size)
    next_step["y_pos"] = last_step["y_pos"] + (last_step["y_vel"] * step_size)
    next_step["z_pos"] = last_step["z_pos"] + (last_step["z_vel"] * step_size)
    next_step["x_vel"] = (last_step["x_vel"] + (x_acc * step_size)) / ( 1 + ( (last_step["x_vel"] * (x_acc * step_size)) / c_sq ) )
    next_step["y_vel"] = (last_step["y_vel"] + (y_acc * step_size)) / ( 1 + ( (last_step["y_vel"] * (y_acc * step_size)) / c_sq ) )
    next_step["z_vel"] = (last_step["z_vel"] + (z_acc * step_size)) / ( 1 + ( (last_step["z_vel"] * (z_acc * step_size)) / c_sq ) )
    next_step["velocity"] = sqrt((next_step["x_vel"] ** 2) + (next_step["y_vel"] ** 2) + (next_step["z_vel"] ** 2))
    lorentz_factor = sqrt(1 - (last_step["velocity"] ** 2) / c_sq)
    next_step["time_dilation"] = step_size * lorentz_factor
    next_step["time_dilation_accumulated"] = last_step["time_dilation_accumulated"] + last_step["time_dilation"]
    
    return next_step

def write_output(file, data, c, ly):
        file.write(f'''{
        str(data["sim_time"])
        }, {str(data["x_pos"])
        }, {str(data["y_pos"])
        }, {str(data["z_pos"])
        }, {str(data["x_pos"]/ly)
        }, {str(data["y_pos"]/ly)
        }, {str(data["z_pos"]/ly)
        }, {str(data["x_vel"])
        }, {str(data["y_vel"])
        }, {str(data["z_vel"])
        }, {str(data["velocity"])
        }, {str(data["velocity"]/c)
        }, {str(data["time_dilation"])
        }, {str(data["time_dilation_accumulated"])
    }\n''')

dir = os.path.dirname(os.path.abspath(__file__)) + "\\"

# Define constants
c = 299800000
c_sq = c ** 2
ly = 9460730472580800

# 1G gravity
g = 9.81

# Acceleration along each axis
# Ultimately will be calculated from the thrust vector in the sim loop
# Can only handle one axis of acceleration at this time
x_acc = 0
y_acc = g * 5
z_acc = 0

# Step size in seconds
step_size = 100000

# Step counter for while loop
steps = 0

# Defining the dict variable for each simulation step
step = {
    "sim_time": 0, 
    "x_pos": 0, 
    "y_pos": 0, 
    "z_pos": 0, 
    "x_vel": 0, 
    "y_vel": 0, 
    "z_vel": 0, 
    "velocity": 0,
    "time_dilation": step_size,
    "time_dilation_accumulated": 0
}

# Bool for the simulation loop
simulate = True

# Empty lists for the mathplotlib
# This is because the simulation records each row as a step, but mathplotlib axis needs the columns and this is easier for now
time = []
x_position = []
y_position = []
x_velocity = []
y_velocity = []
velocity = []
velocity_c = []
distance = []
distance_ly = []
time_dilation = []
time_dilation_cumulative = []
decelerate = False

# Start a timer to record the program execution speed
start = datetime.datetime.now()

# Dump all the simulation data into a file
logfile = open(dir + "FTL_data_output.csv", 'w')
logfile.write("sim_time,x_pos,y_pos,z_pos,x_pos ly,y_pos ly,z_pos ly,x_velocity,y_velocity,z_velocity,velocity,velocity c,time_dilation,time_dilation_accumulated\n")
write_output(logfile, step, c, ly)

while simulate:
    steps += 1# Step one sim step forward
    step = step_forward_dict(step, step_size, c_sq, x_acc, y_acc, z_acc)# Simulate the step

    # Write to CSV file
    write_output(logfile, step, c, ly)
    
    # Append everything to lists to choose from later when graphing
    time.append(step["sim_time"])
    x_position.append(step["x_pos"])
    y_position.append(step["y_pos"])
    x_velocity.append(step["x_vel"])
    y_velocity.append(step["y_vel"])
    velocity.append(step["velocity"])
    velocity_c.append(step["velocity"]/c)# Velocity expressed in terms of c
    distance.append(sqrt((step["x_pos"] ** 2) + (step["y_pos"] ** 2) + (step["z_pos"] ** 2)))
    distance_ly.append(sqrt((step["x_pos"] ** 2) + (step["y_pos"] ** 2) + (step["z_pos"] ** 2))/ly)# Distance expressed in terms of light years
    time_dilation_cumulative.append(step["time_dilation_accumulated"])
    
    # Simulation specifics
    if step["y_pos"] >= 2*ly and y_acc > 0:# Decelerate once 2 light years away
        #simulate = False
        y_acc = -y_acc
        decelerate = True
    if y_acc < 0:
        if y_position[-1] < y_position[-2]:# Stop the simulation once slowed down again
            simulate = False
    if steps >= 105:# Stop the simulation after 20000 steps (to prevent infinite looping)
        simulate = False

logfile.close()
compute_time = datetime.datetime.now() - start

flight_distance = sqrt((step["x_pos"] ** 2) + (step["y_pos"] ** 2)+ (step["z_pos"] ** 2))

sim_time = steps * step_size
print(f"   steps: {steps} (of size {step_size}s)")
print(f'final velocity: {round(step["velocity"],3)}m/s ({round(step["velocity"]/c,5)}c)')
print(f'  max velocity: {max(velocity_c)}c')
print(f'final distance: {round(flight_distance,3)}m ({round(flight_distance/ly,5)}ly)')
print(f' observer time: {sim_time}s ({round(sim_time/86400,2)}d) ({round(sim_time/31536000,2)}y)')
tda = step["time_dilation_accumulated"]
print(f'traveller time: {int(tda)}s ({round(tda/86400,2)}d) ({round(tda/31536000,2)}y) ({round(tda/sim_time,3)}%)')
print(f'      calc in : {compute_time}')
#print(step)

# ----- Display data plots with matplotlib ----- #

# Create the plot
fig, ax = plt.subplots()

x_plot = time
y_plot = distance_ly
ax.plot(x_plot, velocity_c, linestyle='-', marker=None)
ax.plot(x_plot, distance_ly, linestyle='-', marker=None)

#x_plot = time
#y_plot = time_dilation_cumulative
#ax.plot(x_plot, y_plot, linestyle='-', marker=None)

# Optionally, set the axis limits and ticks for better visualization
ax.set(xlim=(min(x_plot), 1.01*max(x_plot)), ylim=(min(y_plot), 1.01*max(y_plot)))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add labels and title for better understanding
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')

# Display the plot
plt.show()
