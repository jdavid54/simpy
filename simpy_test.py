# https://simpy.readthedocs.io/en/latest/simpy_intro/basic_concepts.html

import simpy

# https://simpy.readthedocs.io/en/latest/simpy_intro/basic_concepts.html
print('\nbasic_concepts')
def car(env):
    while True:
         print('Start parking at %d' % env.now)
         parking_duration = 5
         yield env.timeout(parking_duration)

         print('Start driving at %d' % env.now)
         trip_duration = 2
         yield env.timeout(trip_duration)
         
env = simpy.Environment()
env.process(car(env))
env.run(until=15)
print()

# https://simpy.readthedocs.io/en/latest/simpy_intro/process_interaction.html
print('\nprocess_interaction')

class Car(object):
    def __init__(self, env):
     self.env = env
     # Start the run process everytime an instance is created.
     self.action = env.process(self.run())

    def run(self):
     while True:
         print('Start parking and charging at %d' % self.env.now)
         charge_duration = 5
         # We yield the process that process() returns
         # to wait for it to finish
         yield self.env.process(self.charge(charge_duration))

         # The charge process has finished and
         # we can start driving again.
         print('Start driving at %d' % self.env.now)
         trip_duration = 2
         yield self.env.timeout(trip_duration)

    def charge(self, duration):
     yield self.env.timeout(duration)

env = simpy.Environment()
car = Car(env)
env.run(until=25)

def driver(env, car):
    yield env.timeout(3)
    car.action.interrupt()

class Car2(object):
    def __init__(self, env):
     self.env = env
     self.action = env.process(self.run())

    def run(self):
     while True:
         print('Start parking and charging at %d' % self.env.now)
         charge_duration = 5
         # We may get interrupted while charging the battery
         try:
             yield self.env.process(self.charge(charge_duration))
         except simpy.Interrupt:
             # When we received an interrupt, we stop charging and
             # switch to the "driving" state
             print('Was interrupted. Hope, the battery is full enough ')

         print('Start driving at %d' % self.env.now)
         trip_duration = 2
         yield self.env.timeout(trip_duration)

    def charge(self, duration):
     yield self.env.timeout(duration)



env = simpy.Environment()
car = Car2(env)
env.process(driver(env, car))
env.run(until=15)



# https://simpy.readthedocs.io/en/latest/simpy_intro/shared_resources.html
print('\nshared_resources')

def car(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the BCS
    yield env.timeout(driving_time)

    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
     yield req

     # Charge the battery
     print('%s starting to charge at %s' % (name, env.now))
     yield env.timeout(charge_duration)
     print('%s leaving the bcs at %s' % (name, env.now))
     
env = simpy.Environment()
bcs = simpy.Resource(env, capacity=2)

for i in range(4):
    env.process(car(env, 'Car %d' % i, bcs, i*2, 5))
    
env.run()