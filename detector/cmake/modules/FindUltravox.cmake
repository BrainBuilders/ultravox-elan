if(NOT TARGET Ultravox::Ultravox)
    # Set common directories for Windows
    if(WIN32)
        set(WINDOWS_SEARCH_DIRS
                "C:/Program Files/ultravox-sdk"
                "C:/Program Files (x86)/ultravox-sdk"
                "C:/ultravox-sdk"
        )
    endif()

    # Check sibling directory first (local build)
    set(ULTRAVOX_SIBLING_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../ultravox-sdk")
    find_library(ULTRAVOX_LIBRARY NAMES ultravox
        HINTS "${ULTRAVOX_SIBLING_DIR}/build"
        NO_DEFAULT_PATH
    )
    find_path(ULTRAVOX_INCLUDE_DIR NAMES ultravox/ultravox.h
        HINTS "${ULTRAVOX_SIBLING_DIR}/include"
        NO_DEFAULT_PATH
    )

    # Fall back to system / Windows paths
    find_library(ULTRAVOX_LIBRARY NAMES ultravox
        PATHS ${WINDOWS_SEARCH_DIRS}
    )
    find_path(ULTRAVOX_INCLUDE_DIR NAMES ultravox/ultravox.h
        PATHS ${WINDOWS_SEARCH_DIRS}
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
