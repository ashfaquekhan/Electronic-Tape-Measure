# Digital Handheld Measurement Device
#### [I will try to come up with a good name]
## Description
This is a very simple and basic tool which helps in measuring distance [using a rotary encoder ] and also knows the heading-refference/orientation via an IMU sensor[MPU-6050].

So that's it .

## Further Scope
For now our devices only measures 2D space , but we can use it to measure 3D space [the last thing humanity needs to be done is measuring 3D space using this tool ]

But some major devlopment which can be added or contributed(🥲) are :
1. Restructuring the controll flow in the main.py[software side]
2. Changes in many/every function.
3. Not using the software in the first place [it was built so that we feel we did something], displaying all the metrics in a separate display[I2C]/the hardware itself.
4. Adding a pointer/sight/refference to help the user holding it know where to start and stop.
5. Using a better IMU Sensor , we are using MPU6050 on top with DMP, so there is a significant yaw drift[we had only one thing to do 😔].
6. Using a hall effect sensor , instead of a rotary encoder[we just went with the flow, although we knew it was coming].
7. Closing the project and not working on stupid ideas,[but it can be effeicent if made ina very small form factor]. 

## Still It gets the Job Done 😮‍💨 :
Altough it has some limitations, it does work, and works fin---e.

It gives the following output to the user:
* Distance
* Displacement
* Area
* X and Y axis Displacement 

Although, its very easy after we get the two points[start and end]. 

## Demo Video 📺



