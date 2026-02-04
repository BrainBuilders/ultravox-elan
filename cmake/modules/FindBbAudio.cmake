if(NOT TARGET BbAudio::BbAudio)
    # Find library and include paths
    find_library(BBAUDIO_LIBRARY NAMES bb-audio)
    find_path(BBAUDIO_INCLUDE_DIR NAMES bb/audio.h)

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
