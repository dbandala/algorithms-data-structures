import java.util.Arrays;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

public class greed_dices {

	public static int score(int[] dice) {
		if (dice == null || dice.length != 5) {
			throw new IllegalArgumentException("Input must contain exactly 5 dice values.");
		}

		int[] freq = new int[7];
		for (int die : dice) {
			if (die < 1 || die > 6) {
				throw new IllegalArgumentException("Each die value must be between 1 and 6.");
			}
			freq[die]++;
		}

		int total = 0;

		// Score triplets first so each die is counted only once.
		for (int value = 1; value <= 6; value++) {
			if (freq[value] >= 3) {
				total += (value == 1) ? 1000 : value * 100;
				freq[value] -= 3;
			}
		}

		// Score remaining single 1s and 5s.
		total += freq[1] * 100;
		total += freq[5] * 50;

		return total;
	}

	public static int scoreUsingCollectors(int[] dice) {
		if (dice == null || dice.length != 5) {
			throw new IllegalArgumentException("Input must contain exactly 5 dice values.");
		}

		for (int die : dice) {
			if (die < 1 || die > 6) {
				throw new IllegalArgumentException("Each die value must be between 1 and 6.");
			}
		}

		Map<Integer, Long> counts = Arrays.stream(dice)
			.boxed()
			.collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

		int total = 0;

		for (int value = 1; value <= 6; value++) {
			long count = counts.getOrDefault(value, 0L);
			if (count >= 3) {
				total += (value == 1) ? 1000 : value * 100;
				count -= 3;
			}

			if (value == 1) {
				total += (int) count * 100;
			} else if (value == 5) {
				total += (int) count * 50;
			}
		}

		return total;
	}

    public static int scoreUsingCollectorsAndStream(int[] dice) {
		if (dice == null || dice.length != 5) {
			throw new IllegalArgumentException("Input must contain exactly 5 dice values.");
		}

		for (int die : dice) {
			if (die < 1 || die > 6) {
				throw new IllegalArgumentException("Each die value must be between 1 and 6.");
			}
		}

		Map<Integer, Long> counts = Arrays.stream(dice)
			.boxed()
			.collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));


		return counts.entrySet().stream()
            .mapToInt(entry -> {
                int value = entry.getKey();
                long count = entry.getValue();
                int score = 0;

                if (count >= 3) {
                    score += (value == 1) ? 1000 : value * 100;
                    count -= 3;
                }

                if (value == 1) {
                    score += (int) count * 100;
                } else if (value == 5) {
                    score += (int) count * 50;
                }

                return score;
            })
            .sum();

	}

	public static void main(String[] args) {
		System.out.println(score(new int[] {5, 1, 3, 4, 1})); // 250
		System.out.println(score(new int[] {1, 1, 1, 3, 1})); // 1100
		System.out.println(score(new int[] {2, 4, 4, 5, 4})); // 450

		System.out.println(scoreUsingCollectors(new int[] {5, 1, 3, 4, 1})); // 250
		System.out.println(scoreUsingCollectors(new int[] {1, 1, 1, 3, 1})); // 1100
		System.out.println(scoreUsingCollectors(new int[] {2, 4, 4, 5, 4})); // 450
	}
}


