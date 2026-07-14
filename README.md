Markdown
# 🛰️ Orbital Mechanics & Satellite Ground Track Visualizer

A Python-based simulation and visualization suite designed to model, calculate, and animate satellite orbits around Earth. This project progresses from a fundamental circular model to an interactive, real-time simulator that plots orbital trajectories and 2D ground tracks while accounting for Earth's rotation.

---

## 🚀 Features

The repository contains three progressive scripts:

### 1. Circular Orbit Simulator (`orbit_circular.py`)
* Models a simple circular orbit at a fixed altitude (e.g., ISS altitude of 420 km) using uniform circular motion.
* Features a clean, looping 2D animation of a satellite orbiting a scaled Earth.

### 2. Elliptical Orbit & Telemetry Simulator (`orbit_elliptical.py`)
* Introduces orbital eccentricity ($e = 0.6$).
* Dynamically solves Kepler's Equation for eccentric anomaly using a Newton-Raphson iterative algorithm.
* Animates dynamic vector overlays:
  * **Velocity Vector** (split into $v_x$ and $v_y$ components).
  * **Gravitational Acceleration Vector** (pointing toward Earth's center of mass).
  * **Radial Vector** and auxiliary projection circle.
* Displays real-time telemetry (Altitude, Velocity, and Acceleration).

### 3. Interactive Ground Track Visualizer (`orbit_interactive.py`)
* **Real-time Sliders:** Dynamically adjust orbital **Eccentricity**, **Inclination**, and **Satellite Height** on the fly.
* **Dual-Plot Interface:** 
  * **Left:** Interactive 2D orbital plane showcasing the dynamic velocity components.
  * **Right:** Synchronized 2D global projection showing the satellite's ground track.
* **Earth Rotation Physics:** Translates 3D orbital coordinates and rotates the satellite's position westward to simulate Earth's actual rotation ($\omega_E \approx 7.2921 \times 10^{-5} \text{ rad/s}$).

---

## 🧮 Physics & Mathematics Under the Hood

This simulator models real-world orbital mechanics principles:

* **Vis-Viva Equation:** Used to calculate instantaneous orbital velocity ($v$) along the elliptical trajectory:
  $$v = \sqrt{G M_E \left(\frac{2}{r} - \frac{1}{a}\right)}$$
* **Kepler's Equation Solver:** To locate the satellite's position over time, the mean anomaly ($M$) is converted to eccentric anomaly ($E$) via the Newton-Raphson method:
  $$M = E - e \sin E$$
* **Ground Track Projection:** 3D coordinates are projected into latitude and longitude while accounting for Earth's rotational displacement ($E_{rot} = \omega_E \cdot t$) over the orbit's duration.

---
