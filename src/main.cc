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

int main(int argc, char* argv[]) {
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

  // Create shared UDP sink if network logging requested
  std::shared_ptr<spdlog::sinks::udp_sink_mt> udp_sink;
  if (!log_host.empty()) {
    spdlog::sinks::udp_sink_config cfg(log_host, log_port);
    udp_sink = std::make_shared<spdlog::sinks::udp_sink_mt>(cfg);
  }

  // Setup logging for both libraries
  auto audio_logger = bb::audio::SetupLogger();
  audio_logger->set_level(spdlog::level::debug);

  auto uv_logger = uv::SetupLogger();
  uv_logger->set_level(spdlog::level::debug);

  if (udp_sink) {
    audio_logger->sinks().push_back(udp_sink);
    uv_logger->sinks().push_back(udp_sink);
  }

  // CSV logger: stdout + optional UDP, raw message only
  auto stdout_sink = std::make_shared<spdlog::sinks::stdout_sink_mt>();
  std::vector<spdlog::sink_ptr> csv_sinks{stdout_sink};
  if (udp_sink) {
    csv_sinks.push_back(udp_sink);
  }
  auto csv = std::make_shared<spdlog::logger>("csv", csv_sinks.begin(), csv_sinks.end());
  csv->set_pattern("%v");
  csv->set_level(spdlog::level::info);

  std::signal(SIGINT, SignalHandler);
  std::signal(SIGTERM, SignalHandler);

  // Load UVL file
  auto live_detection = uv::experiment::LoadLiveDetection(config_path.c_str());

  csv->info("Call;Device;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp");

  // Detect calls
  int call_num = 0;
  live_detection->DetectCalls(
      [&](const std::string& device_name, const std::string& call_name, double start, double end,
          double freq_at_max_amp, double mean_amp) {
        csv->info("{};{};{};{:.1f};{:.3f};{:.3f};{:.0f};{:.1f}", ++call_num, device_name, call_name,
                  (end - start) * 1000.0, start, end, freq_at_max_amp, mean_amp);
      },
      [&]() { return g_running.load(); });

  return 0;
}
