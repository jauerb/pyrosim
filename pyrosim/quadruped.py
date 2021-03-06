import math
import numpy as np
import math

HEIGHT = 0.3
EPS = 0.05


def send_to_simulator(sim, weight_matrix):
    # if np.shape(weight_matrix) != ()
    body_id = 0
    joint_id = 0
    sensor_id = 0
    neuron_id = 0

    main_body = sim.send_box(x=0, y=0, z=HEIGHT+EPS,
                             length=HEIGHT, width=HEIGHT, height=EPS*2.0, mass=1)

    thighs = [0]*4
    shins = [0]*4
    hips = [0]*4
    knees = [0]*4
    foot_sensors = [0]*4
    sensor_neurons = [0]*5
    motor_neurons = [0]*8

    delta = float(math.pi)/2.0

    for i in range(4):
        theta = delta*i
        x_pos = math.cos(theta)*HEIGHT
        y_pos = math.sin(theta)*HEIGHT

        thighs[i] = sim.send_cylinder(x=x_pos, y=y_pos, z=HEIGHT+EPS,
                                      r1=x_pos, r2=y_pos, r3=0,
                                      length=HEIGHT, radius=EPS, capped=True
                                      )

        hips[i] = sim.send_hinge_joint(first_body_id=main_body, second_body_id=thighs[i],
                                       x=x_pos/2.0, y=y_pos/2.0, z=HEIGHT+EPS,
                                       n1=-y_pos, n2=x_pos, n3=0,
                                       lo=-math.pi/4.0, hi=math.pi/4.0,
                                       speed=1.0)

        motor_neurons[i] = sim.send_motor_neuron(joint_id=hips[i])

        x_pos2 = math.cos(theta)*1.5*HEIGHT
        y_pos2 = math.sin(theta)*1.5*HEIGHT

        shins[i] = sim.send_cylinder(x=x_pos2, y=y_pos2, z=(HEIGHT+EPS)/2.0,
                                     r1=0, r2=0, r3=1,
                                     length=HEIGHT, radius=EPS,
                                     mass=1., capped=True)

        knees[i] = sim.send_hinge_joint(first_body_id=thighs[i], second_body_id=shins[i],
                                        x=x_pos2, y=y_pos2, z=HEIGHT+EPS,
                                        n1=-y_pos, n2=x_pos, n3=0,
                                        lo=-math.pi/4.0, hi=math.pi/4.0)

        motor_neurons[i+4] = sim.send_motor_neuron(joint_id=knees[i])

        foot_sensors[i] = sim.send_touch_sensor(body_id=shins[i])

        sensor_neurons[i] = sim.send_sensor_neuron(sensor_id=foot_sensors[i])

    light_sensor = sim.send_light_sensor(body_id=main_body)

    sensor_neurons[-1] = sim.send_sensor_neuron(sensor_id=light_sensor)

    count = 0

    for source_id in sensor_neurons:
        for target_id in motor_neurons:
            count += 1
            start_weight = weight_matrix[source_id, target_id, 0]
            end_weight = weight_matrix[source_id, target_id, 1]
            time = weight_matrix[source_id, target_id, 2]
            sim.send_developing_synapse(source_neuron_id=source_id, target_neuron_id=target_id,
                                        start_weight=start_weight, end_weight=end_weight,
                                        start_time=time, end_time=time)

    layout = {'thighs': thighs,
              'shins': shins,
              'hips': hips,
              'knees': knees,
              'feet': foot_sensors,
              'light': light_sensor,
              'sensor_neurons': sensor_neurons,
              'motor_neurons': motor_neurons}

    env_box = sim.send_box(x=2, y=-2, z=HEIGHT/2.0, length=HEIGHT, width=HEIGHT, height=HEIGHT, collision_group=1,
                           mass=3.)
    sim.send_slider_joint(pyrosim.Simulator.WORLD, main_body, x=0,y=.4,z=1, position_control=True)

    MASS = 3
    sim.send_external_force(env_box, x=0, y=0, z=MASS*20., time=300)
    sim.send_external_force(env_box, x=-MASS*70., y=MASS*73., z=0, time=320)

    sim.create_collision_matrix('all')

    # for t in range(1000):
    #   x = math.cos(0.045*t)
    #   y = math.sin(0.045*t)
    #   if t%2==0:
    #     sim.send_external_force(main_body,x=x,y=y, z=0, time=t)

    return layout

if __name__ == "__main__":
    import pyrosim

    eval_time = 1000
    gravity = -1.0
    NUM = 1
    if NUM == 1:
        BLIND = False
    else:
        BLIND = True

    sim = [0]*NUM
    for j in range(NUM):
        for i in range(NUM):
            sim[i] = pyrosim.Simulator(eval_time=eval_time, debug=True, dt=0.045, play_paused=True,
                                       gravity=gravity, play_blind=BLIND, use_textures=True)
            num_sensors = 5
            num_motors = 8

            weight_matrix = np.random.rand(
                num_sensors+num_motors, num_sensors+num_motors, 3)
            weight_matrix[:, :, 0:1] = weight_matrix[:, :, 0:1]*2.-1.
            time_matrix = np.random.rand(num_sensors+num_motors)

            layout = send_to_simulator(sim[i], weight_matrix=weight_matrix)
            # sim[i].film_body(0)
            sim[i].start()
        for i in range(NUM):
            results = sim[i].wait_to_finish()
            print i, j
