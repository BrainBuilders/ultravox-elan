if(NOT TARGET BbAudio::BbAudio)
    # Set common directories for Windows
    if(WIN32)
        set(WINDOWS_SEARCH_DIRS
                "C:/Program Files/bb-audio"
                "C:/Program Files (x86)/bb-audio"
                "C:/bb-audio"
        )
    endif()

    # Also search relative to this project (sibling directory)
    set(BBAUDIO_SIBLING_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../bb-audio")

    # Find library and include paths
    find_library(BBAUDIO_LIBRARY NAMES bb-audio
        PATHS ${WINDOWS_SEARCH_DIRS}
        HINTS "${BBAUDIO_SIBLING_DIR}/build"
    )
    find_path(BBAUDIO_INCLUDE_DIR NAMES bb/audio.h
        PATHS ${WINDOWS_SEARCH_DIRS}
        HINTS "${BBAUDIO_SIBLING_DIR}/include"
    )

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(BbAudio DEFAULT_MSG BBAUDIO_LIBRARY BBAUDIO_INCLUDE_DIR)

    if(BBAUDIO_FOUND)
        add_library(BbAudio::BbAudio UNKNOWN IMPORTED)
        set_target_properties(BbAudio::BbAudio PROPERTIES
            IMPORTED_LOCATION "${BBAUDIO_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${BBAUDIO_INCLUDE_DIR}")
    endif()
endif()

mark_as_advanced(BBAUDIO_INCLUDE_DIR BBAUDIO_LIBRARY)
