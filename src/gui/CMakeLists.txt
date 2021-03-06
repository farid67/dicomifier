find_package(
    Boost COMPONENTS filesystem program_options python regex system REQUIRED)
find_package(Odil REQUIRED)
find_package(PythonLibs 2.7 REQUIRED)
find_package(Qt4 REQUIRED QtCore QtGui)

include(${QT_USE_FILE})

file(GLOB_RECURSE files "*.cpp")
file(GLOB_RECURSE headers "*.h")
file(GLOB_RECURSE forms "*.ui")
file(GLOB_RECURSE resources "*.qrc")

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/../lib
    ${Boost_INCLUDE_DIRS} ${Odil_INCLUDE_DIR} ${PYTHON_INCLUDE_DIRS}
    ${QT_INCLUDES}
    ${CMAKE_CURRENT_BINARY_DIR})
add_definitions(
    ${DCMTK_DEFINITIONS} -DBOOST_FILESYSTEM_VERSION=3)
link_directories(
    ${Boost_LIBRARY_DIRS} ${DCMTK_LIBRARY_DIRS})

QT4_WRAP_CPP(mocs ${headers})
QT4_WRAP_UI(compiled_forms ${forms})
QT4_ADD_RESOURCES(compiled_resources ${resources})

add_executable(
    dicomifier MACOSX_BUNDLE 
    ${files} ${mocs} ${compiled_forms} ${compiled_resources})

target_link_libraries(
    dicomifier
    libdicomifier ${Boost_LIBRARIES} ${Odil_LIBRARY} ${PYTHON_LIBRARIES}
    ${QT_LIBRARIES})

install(
    TARGETS dicomifier
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin)

SET(APPS "\${CMAKE_INSTALL_PREFIX}/bin/dicomifier")
SET(qtconf_dest_dir bin)
if(APPLE)
    set(APPS "\${CMAKE_INSTALL_PREFIX}/dicomifier.app")
    set(qtconf_dest_dir dicomifier.app/Contents/Resources)
    # We need an empty qt.conf in order to override the hard-coded paths that are 
    # compiled into the Qt library. 
    install(CODE "
        file(WRITE \"\${CMAKE_INSTALL_PREFIX}/${qtconf_dest_dir}/qt.conf\" \"\")
        ")
    
    set(LIBRARIES )
    install(
        TARGETS bruker2dicom dicom2nifti 
        RUNTIME DESTINATION dicomifier.app/Contents/MacOS)
    
    install(CODE "
        macro(gp_resolve_item_override context item exepath dirs resolved_item_var resolved_var)
            if(NOT \${resolved_var})
                # Context is sometimes wrong: look in dirs
                if(item MATCHES \"^@loader_path\")
                    string(REPLACE \"@loader_path/\" \"\" noprefix_item \"\${item}\")
                    set(ri \"ri-NOTFOUND\")
                    find_file(ri \"\${noprefix_item}\" \${dirs} NO_DEFAULT_PATH)
                    find_file(ri \"\${noprefix_item}\" \${dirs} /usr/lib)
                    if(EXISTS \"\${ri}\")
                        set(\${resolved_var} 1)
                        set(\${resolved_item_var} \"\${ri}\")
                        set(ri \"ri-NOTFOUND\")
                    endif()
                endif()
            endif()
        endmacro()
        set(BU_CHMOD_BUNDLE_ITEMS ON)
        include(BundleUtilities)
        fixup_bundle(\"${APPS}\" \"${LIBRARIES}\" \"${EXTRA_BUNDLE_DIRS}\")
        ")
endif()
