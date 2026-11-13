
---

# SinExp and Alpha Synaptic Plasticity Model

This repository contains everything required to **compile, run, and test** a preliminary implementation of the **SinExp** and **Alpha synaptic plasticity models**.

---

## Directory Structure

* The subfolder custom_stdp (in the repo) contains the source code for the needed version of the cerebellum that we will test. The first one contains four E-GLIF models for Granule cell (eglif_cond_alpha_multisyn), Inferior Olivary cell (eglif_io_nestml), Purkinje cell (eglif_pc_nestml) and MLI (eglif_mli)

* Subfolders include E-GLIF models:

  * `eglif_cond_alpha_multisyn`: Granule Cell
  * `eglif_io_nestml`: Inferior Olivary Cell
  * `eglif_pc_nestml`: Purkinje Cell
  * `eglif_mli_nestml`: Molecular Layer Interneuron (MLI) and more ...

---

## Compilation Instructions

To compile the extension modules:

1. **Create a build directory** (at the same level as the source folder (inside the tests folder)):

   ```
   mkdir build_dir
   cd build_dir
   ```

2. **Clean previous builds** (only if rebuilding):

   ```
   rm -rf *
   ```

3. **Run CMake with appropriate paths**:

   ```
   cmake -Dwith-nest=<path_to_your_nest> <path_to_custom_stdp>
   make
   make install
   ```

---

## Building controller_neurons_module

The controller neurons (e.g. `diff_neuron_nestml`) are **generated with NESTML** from `controller_nest_module/controller_module.nestml`, then compiled as described in *Compilation Instructions*. 
This requires NEST 3.10 and `nestml==8.3.0`.

1. **Create a folder for the generated code** (at the same level as `build_dir`, inside the tests folder):

   ```
   mkdir nestml_generated
   ```

2. **Generate the C++ code**:

   ```
   echo '{"nest_version": "v3.10.0"}' > nestml_generated/nestml_codegen_opts.json
   nestml --input_path ../controller_nest_module/controller_module.nestml \
          --target_path nestml_generated \
          --target_platform NEST --module_name controller_neurons_module \
          --codegen_opts nestml_generated/nestml_codegen_opts.json
   ```

   NESTML's own build step is expected to fail: only the generated files (`controller_neurons_module.cpp`, `CMakeLists.txt`, `*_nestml.h`) are needed.

3. **Patch the generated headers** (NESTML 8.3.0 defines a helper class more than once when a module contains several neurons):

   ```
   python ../docker/fix_nestml_duplicate_class.py nestml_generated/*_nestml.h
   ```

4. **Remove the cache of the failed build**:

   ```
   rm -rf nestml_generated/CMakeCache.txt nestml_generated/CMakeFiles
   ```

5. **Compile and install** as in *Compilation Instructions*, replacing `<path_to_custom_stdp>` with `nestml_generated`. Use a separate build directory for each module (e.g. `build_controller`), or clean `build_dir` first.

To regenerate, delete `nestml_generated` and repeat from step 1.

---

## Using the Module in Python

To load the compiled module:

```python
import nest
nest.Install("custom_stdp_module")  # Replace with actual module name if different
```

---

## Running Tests

To test neuron connections and plasticity logic:

1. **Install the required Python library**:

   ```
   pip install pynest
   ```

2. **Navigate to the test directory** (go to the same directory with 'tests').

3. **Run tests using `pytest`**:

   ```
   pytest
   ```

