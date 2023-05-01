# Digital Handheld Measurement Device
#### [I will try to come up with a good name]
![ezgif com-gif-to-apng](https://user-images.githubusercontent.com/42895491/235434160-bbd7a57a-e483-450a-81c9-0b649d452f14.png)

## Description
This is a very simple and basic tool that helps in measuring distance [using a rotary encoder ] and also knows the heading reference/orientation via an IMU sensor[MPU-6050].

So that's it.

## Further Scope
For now, our devices only measure 2D space, but we can use them to measure 3D space [the last thing humanity needs to be done is measure 3D space using this tool ]

But some major development that can be added or contributed(🥲) are :
1. Restructuring the control flow in the main.py[software side]
2. Changes in many/every function.
3. Not using the software in the first place [it was built so that we feel we did something], displaying all the metrics in a separate display[I2C]/the hardware itself.
4. Adding a pointer/sight/reference to help the user holding it know where to start and stop.
5. Using a better IMU Sensor, we are using MPU6050 on top with DMP, so there is a significant yaw drift[we had only one thing to do 😔].
6. Using a hall effect sensor, instead of a rotary encoder[we just went with the flow, although we knew it was coming].
7. Closing the project and not working on stupid ideas,[but it can be efficient if made in a very small form factor]. 

## Still It Gets the Job Done 🔥 :
Although it has some limitations, it does work and works fine.

It gives the following output to the user:
* Distance
* Displacement
* Area
* X and Y axis Displacement 

Although, it is very easy after we get the two points[start and end]. 

## Demo Video 📺
[![Preview](https://img.youtube.com/vi/7DulpQM3AjI/maxresdefault.jpg)](https://www.youtube.com/watch?v=7DulpQM3AjI)


## Compensator Testing 
[![Preview](https://img.youtube.com/vi/4gAEML8vUaQ/maxresdefault.jpg)](https://youtu.be/4gAEML8vUaQ)


## Circuit
The First Prototype Consists of : 
* Arduino Pro Micro
* Bluetooth HC-05
* Rotary Encoder
* MPU-6050


### Schematics: 
![Schematic_prjX_2023-04-29 (1)](https://user-images.githubusercontent.com/42895491/235427178-459d43a8-e698-48b8-bb20-69d057791a28.png)
### PCB [What it Should Look like]: 
<img width="868" alt="image" src="https://user-images.githubusercontent.com/42895491/235429166-7d047377-3a9f-44f3-8d62-b9ebc6102ccc.png">


## Current Build [🙈🙉🙊]
![20230501_134313](https://user-images.githubusercontent.com/42895491/235428368-39fea1a1-82fa-4dbb-be33-a042bd999802.jpg)
![20230501_134249](https://user-images.githubusercontent.com/42895491/235428373-f043af6d-c804-4358-b16f-b4fffd3389d8.jpg)


## I tried to change the Form-Factor
### [Do not mind the HC-05(Bluetooth 2.0) connected to Arduino Nano RP2040 which already has a BLE 5.0]
![20230501_134422](https://user-images.githubusercontent.com/42895491/235428654-c3c58829-6a2d-413f-86c0-216b2d327559.jpg)






