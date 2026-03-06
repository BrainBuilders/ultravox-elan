if(NOT TARGET Ultravox::Ultravox)
    # Set common directories for Windows
    if(WIN32)
        set(WINDOWS_SEARCH_DIRS
                "C:/Program Files/ultravox-sdk"
                "C:/Program Files (x86)/ultravox-sdk"
                "C:/ultravox-sdk"
        )
    endif()

    # Also search relative to this project (sibling directory)
    set(ULTRAVOX_SIBLING_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../ultravox-sdk")

    # Find library and include paths
    find_library(ULTRAVOX_LIBRARY NAMES ultravox
        PATHS ${WINDOWS_SEARCH_DIRS}
        HINTS "${ULTRAVOX_SIBLING_DIR}/build"
    )
    find_path(ULTRAVOX_INCLUDE_DIR NAMES ultravox/ultravox.h
        PATHS ${WINDOWS_SEARCH_DIRS}
        HINTS "${ULTRAVOX_SIBLING_DIR}/include"
    )

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
