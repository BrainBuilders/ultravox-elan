#include <bb/audio.h>
#include <spdlog/sinks/stdout_sinks.h>
#include <spdlog/sinks/udp_sink.h>
#include <spdlog/spdlog.h>
#include <ultravox/experiment.h>
#include <ultravox/ultravox.h>

#include <atomic>
#include <csignal>
#include <cstring>
#include <iostream>
#include <string>

static std::atomic<bool> g_running{true};

static void SignalHandler(int) { g_running = false; }

int main(int argc, char *argv[]) {
    // Parse command-line arguments
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <file.uvl> [--log-target <ip:port>]\n";
        return 1;
    }

    std::string config_path = argv[1];
    std::string log_host;
    uint16_t log_port = 0;
    for (int i = 2; i < argc; ++i) {
        if (std::strcmp(argv[i], "--log-target") == 0 && i + 1 < argc) {
            std::string target = argv[++i];
            auto colon = target.rfind(':');
            if (colon == std::string::npos) {
                std::cerr << "Error: --log-target must be <ip:port>\n";
                return 1;
            }
            log_host = target.substr(0, colon);
            log_port = static_cast<uint16_t>(std::stoi(target.substr(colon + 1)));
        } else {
            std::cerr << "Unknown argument: " << argv[i] << "\n";
            return 1;
        }
    }

    // Setup logging for both libraries
    auto audio_logger = bb::audio::SetupLogger();
    auto uv_logger = uv::SetupLogger();

    // CSV logger: stdout
    auto stdout_sink = std::make_shared<spdlog::sinks::stdout_sink_mt>();
    auto csv = std::make_shared<spdlog::logger>("csv", stdout_sink);

    // Create shared UDP sink if network logging requested
    if (!log_host.empty()) {
        spdlog::sinks::udp_sink_config cfg(log_host, log_port);
        auto udp_sink = std::make_shared<spdlog::sinks::udp_sink_mt>(cfg);
        audio_logger->sinks().push_back(udp_sink);
        uv_logger->sinks().push_back(udp_sink);
        csv->sinks().push_back(udp_sink);
    }

    // Write CSV messages as raw text without timestamps or log levels
    csv->set_pattern("%v");

    // Set log levels
    audio_logger->set_level(spdlog::level::debug);
    uv_logger->set_level(spdlog::level::debug);
    csv->set_level(spdlog::level::info);

    // Handle signals for graceful shutdown
    std::signal(SIGINT, SignalHandler);
    std::signal(SIGTERM, SignalHandler);

    // Load UVL file
    auto live_detection = uv::experiment::LoadLiveDetection(config_path.c_str());
    auto method = live_detection->GetDetectionMethod();

    int call_num = 0;

    if (method == uv::experiment::DetectionMethod::USVSEG) {
        csv->info("Call;Device;Name;Start (s);End (s);Freq (Hz);Entropy;Sigma");
    } else {
        csv->info("Call;Device;Name;Start (s);End (s);Freq (Hz);Amp");
    }

    live_detection->DetectCalls(
            [&](const uv::experiment::ILiveDetection::DetectedCall &call) {
                if (method == uv::experiment::DetectionMethod::USVSEG) {
                    csv->info("{};{};{};{:.3f};{:.3f};{:.0f};{:.4f};{:.2f}", ++call_num, call.device_name,
                              call.call_name, call.start_time, call.end_time, call.peak_freq_hz, call.wiener_entropy,
                              call.noise_sigma);
                } else {
                    csv->info("{};{};{};{:.3f};{:.3f};{:.0f};{:.1f}", ++call_num, call.device_name, call.call_name,
                              call.start_time, call.end_time, call.peak_freq_hz, call.mean_amp);
                }
            },
            [&]() { return g_running.load(); });

    return 0;
}
