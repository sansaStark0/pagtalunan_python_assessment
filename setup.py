from cx_Freeze import setup, Executable 
  
build_exe_options = {
    "packages": ["os", "matplotlib", "pandas", "scipy" ],
    "excludes": ["numpy"], 
    "optimize": 2 

}


setup(name = "Pagtalunan" , 
      version = "0.1" , 
      description = "Calculates Power" , 
      executables = [Executable("main.py")]) 