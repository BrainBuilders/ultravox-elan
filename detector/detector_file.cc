#include <bb/audio.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>
#include <ultravox/audio.h>
#include <ultravox/experiment.h>
#include <ultravox/ultravox.h>

#include <cstring>
#include <iostream>
#include <string>
#include <vector>

static void PrintUsage(const char *prog) {
    std::cerr << "Usage: " << prog << " <file.uvl> <audio.wav> [--debug]\n"
              << "\n"
              << "Run call detection on a WAV file using settings from a UVL config.\n"
              << "Produces the same CSV output as the live streaming detector.\n"
              << "\n"
              << "The detection method (threshold or usvseg) is determined by the\n"
              << "DetectionMethod field in the UVL [Control] section.\n";
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        PrintUsage(argv[0]);
        return 1;
    }

    std::string config_path = argv[1];
    std::string wav_path = argv[2];
    bool debug = false;

    for (int i = 3; i < argc; ++i) {
        if (std::strcmp(argv[i], "--debug") == 0) {
            debug = true;
        } else if (std::strcmp(argv[i], "--help") == 0 || std::strcmp(argv[i], "-h") == 0) {
            PrintUsage(argv[0]);
            return 0;
        } else {
            std::cerr << "Unknown argument: " << argv[i] << "\n";
            return 1;
        }
    }

    // Setup logging
    auto audio_logger = bb::audio::SetupLogger();
    auto uv_logger = uv::SetupLogger();

    audio_logger->set_level(debug ? spdlog::level::debug : spdlog::level::warn);
    uv_logger->set_level(debug ? spdlog::level::debug : spdlog::level::warn);

    auto stdout_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    auto csv = std::make_shared<spdlog::logger>("csv", stdout_sink);
    csv->set_pattern("%v");
    csv->set_level(spdlog::level::info);

    // Load UVL config for call definitions and detection method
    auto live_detection = uv::experiment::LoadLiveDetection(config_path.c_str());
    auto method = live_detection->GetDetectionMethod();
    auto call_defs = live_detection->GetCallDefinitions();

    if (call_defs.empty()) {
        std::cerr << "Error: No call definitions in " << config_path << "\n";
        return 1;
    }

    // Convert call definitions to audio format
    std::vector<uv::audio::CallDef> audio_call_defs;
    int id = 0;
    for (const auto &def : call_defs) {
        audio_call_defs.push_back({id++, static_cast<float>(def->GetMinFreq()), static_cast<float>(def->GetMaxFreq()),
                                   static_cast<float>(def->GetMinDur()), static_cast<float>(def->GetMaxDur()),
                                   static_cast<float>(def->GetMinAmp()), static_cast<float>(def->GetMinGap())});
    }

    // Load WAV file
    bb::audio::Init();
    auto track = bb::audio::CreateTrackFromWaveFile(wav_path);
    if (!track) {
        std::cerr << "Error: Could not open " << wav_path << "\n";
        bb::audio::Terminate();
        return 1;
    }

    double duration = (track->End() - track->Begin()) / track->SampleRate();
    std::string method_name = (method == uv::experiment::DetectionMethod::USVSEG) ? "usvseg" : "threshold";
    std::cerr << "Config: " << config_path << "\n"
              << "Input:  " << wav_path << "\n"
              << "Method: " << method_name << "\n"
              << "Sample rate: " << track->SampleRate() << " Hz\n"
              << "Duration: " << duration << " s\n"
              << "Call definitions: " << call_defs.size() << "\n";

    // Use the WAV filename as device name
    std::filesystem::path wav_fs(wav_path);
    std::string device_name = wav_fs.stem().string();

    int call_num = 0;
    int fft_size = 512;
    float overlap = 0.5f;
    bool is_usvseg = (method == uv::experiment::DetectionMethod::USVSEG);

    if (is_usvseg) {
        csv->info("Call;Device;Name;Start (s);End (s);Freq (Hz);Entropy;Sigma");
    } else {
        csv->info("Call;Device;Name;Start (s);End (s);Freq (Hz);Amp");
    }

    auto analyzer = uv::audio::CreateAnalyzer(audio_call_defs, method);
    analyzer->SetTrack(track);

    analyzer->DetectCalls(
            fft_size, overlap,
            [&](const uv::audio::Call &call) {
                std::string call_name = call.call_def_id < static_cast<int>(call_defs.size())
                                                ? call_defs[call.call_def_id]->GetName()
                                                : "Unknown";
                if (is_usvseg) {
                    csv->info("{};{};{};{:.3f};{:.3f};{:.0f};{:.4f};{:.2f}", ++call_num, device_name, call_name,
                              call.start_time, call.end_time, call.peak_freq_hz, call.wiener_entropy, call.noise_sigma);
                } else {
                    csv->info("{};{};{};{:.3f};{:.3f};{:.0f};{:.1f}", ++call_num, device_name, call_name,
                              call.start_time, call.end_time, call.peak_freq_hz, call.mean_amp);
                }
            },
            nullptr);

    std::cerr << "Detected " << call_num << " calls\n";

    bb::audio::Terminate();
    return 0;
}
