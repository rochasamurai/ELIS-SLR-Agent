"""Test integration with OpenAlex only"""

from benchmark_2_integration import ELISBenchmark2Bridge

# Initialize bridge
bridge = ELISBenchmark2Bridge()

# Test with just OpenAlex
print("\nTesting with OpenAlex only...")
result = bridge.execute_benchmark(databases=["OpenAlex"])

# Save results
bridge.save_results(result)

print(f"\n✓ Test complete!")
print(f"Retrieval rate: {result['retrieval_rate']:.1%}")
