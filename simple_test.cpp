#include <iostream>

int main() {
    std::cout << "Simple test program" << std::endl;
    std::cout << "This should print to console" << std::endl;

    // Test basic math
    float bpm = 120.0f;
    float interval_ms = 60000.0f / bpm;
    std::cout << "120 BPM = " << interval_ms << " ms intervals" << std::endl;

    return 0;
}

