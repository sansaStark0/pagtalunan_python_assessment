from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'console'

executables = [
    Executable('main.py', base=base, target_name = 'Pagtalunan_Python')
]

setup(name='Pagtalunan_Python',
      version = '1',
      description = 'Calculates power through processing current and voltage raw data.',
      options = {'build_exe': build_options},
      executables = executables)
