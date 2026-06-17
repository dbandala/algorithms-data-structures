// Monte Carlo algorithm
// Statistical technique for numerical estimation using random sampling.
// Use cases:
//   1. Estimating pi by sampling random points in a unit square
//   2. Numerical integration via random sampling

#include <iostream>
#include <functional>
#include <random>

class MonteCarlo {
public:
    int num_samples;

    MonteCarlo(int num_samples) : num_samples(num_samples) {}

    double estimate_pi() {
        std::mt19937_64 rng{std::random_device{}()};
        std::uniform_real_distribution<double> dist(-1.0, 1.0);
        int inside_circle = 0;
        for (int i = 0; i < num_samples; ++i) {
            double x = dist(rng);
            double y = dist(rng);
            if (x * x + y * y <= 1.0)
                ++inside_circle;
        }
        return (static_cast<double>(inside_circle) / num_samples) * 4.0;
    }

    double integrate(std::function<double(double)> func, double a, double b) {
        std::mt19937_64 rng{std::random_device{}()};
        std::uniform_real_distribution<double> dist(a, b);
        double total = 0.0;
        for (int i = 0; i < num_samples; ++i)
            total += func(dist(rng));
        return (b - a) * total / num_samples;
    }
};

int main() {
    MonteCarlo mc(1'000'000);
    std::cout << "Estimated pi: " << mc.estimate_pi() << "\n";  // ~3.14159

    // Integrate f(x) = x^2 from 0 to 1; exact result = 1/3 ≈ 0.333
    MonteCarlo mc2(1'000'000);
    std::cout << "Integral of x^2 from 0 to 1: "
              << mc2.integrate([](double x) { return x * x; }, 0.0, 1.0)
              << "\n";  // ~0.333
    return 0;
}
