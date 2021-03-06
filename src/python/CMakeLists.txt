find_package(PythonInterp REQUIRED)

execute_process(
    COMMAND ${PYTHON_EXECUTABLE} -c "from distutils import sysconfig; print( sysconfig.get_python_lib( plat_specific=True, prefix='' ) )"
    OUTPUT_VARIABLE PYTHON_SITE_PACKAGES OUTPUT_STRIP_TRAILING_WHITESPACE)
set(PYTHON_SITE_PACKAGES "${PYTHON_SITE_PACKAGES}" CACHE INTERNAL "Relative package path")

add_subdirectory(dicomifier)

install(
    DIRECTORY .
    DESTINATION ${CMAKE_INSTALL_PREFIX}/${PYTHON_SITE_PACKAGES}
    FILES_MATCHING PATTERN *.py
    # Avoid empty directory
    PATTERN "bruker" EXCLUDE
    PATTERN "nifti" EXCLUDE
)

file(GLOB_RECURSE python_files "*.py")
add_custom_target(
    PythonFiles ${CMAKE_COMMAND} -E echo "Python files" SOURCES ${python_files})
