if(NOT TARGET Ultravox::Ultravox)
    # Find library and include paths
    find_library(ULTRAVOX_LIBRARY NAMES ultravox)
    find_path(ULTRAVOX_INCLUDE_DIR NAMES ultravox/ultravox.h)

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(Ultravox DEFAULT_MSG ULTRAVOX_LIBRARY ULTRAVOX_INCLUDE_DIR)

    if(ULTRAVOX_FOUND)
        add_library(Ultravox::Ultravox UNKNOWN IMPORTED)
        set_target_properties(Ultravox::Ultravox PROPERTIES
            IMPORTED_LOCATION "${ULTRAVOX_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${ULTRAVOX_INCLUDE_DIR}")
    endif()
endif()

mark_as_advanced(ULTRAVOX_INCLUDE_DIR ULTRAVOX_LIBRARY)
