#include <bb/audio.h>
#include <spdlog/spdlog.h>
#include <ultravox/experiment.h>
#include <ultravox/ultravox.h>

#include <atomic>
#include <csignal>
#include <iomanip>
#include <iostream>

static std::atomic<bool> g_running{true};
static void SignalHandler(int) { g_running = false; }

int main(int argc, char* argv[]) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " <file.uvl>\n";
    return 1;
  }

  // Setup logging for both libraries
  bb::audio::SetupLogger()->set_level(spdlog::level::warn);
  uv::SetupLogger()->set_level(spdlog::level::debug);

  std::signal(SIGINT, SignalHandler);
  std::signal(SIGTERM, SignalHandler);

  // Load UVL file
  auto live_detection = uv::experiment::LoadLiveDetection(argv[1]);

  // CSV header
  std::cout << "Call;Mic;Name;Duration (ms);Start (s);End (s);Freq (Hz);Amp\n";

  // Detect calls
  uint64_t call_num = 0;
  live_detection->DetectCalls(
      512, 0.5f,
      [&](const std::string& mic, const std::string& name, double start, double end, double freq, double amp) {
        std::cout << ++call_num << ";" << mic << ";" << name << ";" << std::fixed << std::setprecision(1)
                  << (end - start) * 1000.0 << ";" << std::setprecision(3) << start << ";" << end << ";"
                  << std::setprecision(0) << freq << ";" << std::setprecision(1) << amp << "\n";
        std::cout.flush();
      },
      []() { return g_running.load(); });

  return 0;
}
