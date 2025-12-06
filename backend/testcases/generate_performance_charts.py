"""
Performance Visualization Generator
Generates charts and graphs to visualize system performance metrics from test results
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Create output directory
output_dir = Path(__file__).parent / "performance_charts"
output_dir.mkdir(exist_ok=True)

# Performance data from test results
performance_data = {
    "concurrent_logins": {
        "test_id": "NF-01",
        "users": 30,
        "p50": 5.2,  # seconds
        "p95": 11.67,
        "p99": 13.5,
        "max": 15.2,
        "min": 3.1,
        "avg": 6.8,
        "threshold": 15.0
    },
    "dashboard_load": {
        "test_id": "NF-02",
        "metric": "Coordinator Dashboard Load Time",
        "time": 3.8,  # seconds
        "threshold": 5.0
    },
    "large_dataset": {
        "test_id": "NF-05",
        "metric": "100 Sessions Query",
        "time": 2.9,  # seconds
        "threshold": 4.0
    },
    "concurrent_operations": {
        "test_id": "NF-06",
        "operations": 10,
        "success_rate": 100.0,
        "avg_time": 1.2
    },
    "load_stability": {
        "test_id": "NF-07",
        "concurrent_users": 50,
        "duration_minutes": 1.8,
        "success_rate": 100.0,
        "avg_response_time": 2.1
    },
    "registration_burst": {
        "test_id": "NF-08",
        "registrations": 70,
        "success_rate": 100.0,
        "avg_time": 3.2,
        "threshold": 5.0
    }
}

# Test results summary
test_summary = {
    "total_tests": 34,
    "functional_tests": 24,
    "nonfunctional_tests": 10,
    "passed": 34,
    "failed": 0,
    "skipped": 1,  # F-14
    "pass_rate": 100.0,
    "execution_time": 106.7  # seconds
}

def create_response_time_chart():
    """Chart 1: Response Time Comparison"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    tests = ['Concurrent\nLogins\n(P95)', 'Dashboard\nLoad', '100 Sessions\nQuery', 'Registration\nBurst']
    times = [
        performance_data["concurrent_logins"]["p95"],
        performance_data["dashboard_load"]["time"],
        performance_data["large_dataset"]["time"],
        performance_data["registration_burst"]["avg_time"]
    ]
    thresholds = [
        performance_data["concurrent_logins"]["threshold"],
        performance_data["dashboard_load"]["threshold"],
        performance_data["large_dataset"]["threshold"],
        performance_data["registration_burst"]["threshold"]
    ]
    
    x = np.arange(len(tests))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, times, width, label='Actual Time', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, thresholds, width, label='Threshold', color='#e74c3c', alpha=0.6)
    
    ax.set_xlabel('Test Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Performance Test Results - Response Time Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tests, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '1_response_time_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Created: 1_response_time_comparison.png")
    plt.close()

def create_percentile_chart():
    """Chart 2: Login Performance Percentiles"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    percentiles = ['Min', 'P50', 'Avg', 'P95', 'P99', 'Max']
    values = [
        performance_data["concurrent_logins"]["min"],
        performance_data["concurrent_logins"]["p50"],
        performance_data["concurrent_logins"]["avg"],
        performance_data["concurrent_logins"]["p95"],
        performance_data["concurrent_logins"]["p99"],
        performance_data["concurrent_logins"]["max"]
    ]
    
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']
    bars = ax.bar(percentiles, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Threshold line
    ax.axhline(y=performance_data["concurrent_logins"]["threshold"], 
               color='red', linestyle='--', linewidth=2, label=f'Threshold (15s)', alpha=0.7)
    
    ax.set_xlabel('Percentile', fontsize=12, fontweight='bold')
    ax.set_ylabel('Response Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('NF-01: Concurrent Login Performance Distribution (30 Users)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / '2_login_performance_percentiles.png', dpi=300, bbox_inches='tight')
    print(f"✅ Created: 2_login_performance_percentiles.png")
    plt.close()

def create_test_summary_chart():
    """Chart 3: Test Execution Summary"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart - Test distribution
    categories = ['Functional\nTests', 'Non-functional\nTests']
    sizes = [test_summary["functional_tests"], test_summary["nonfunctional_tests"]]
    colors = ['#3498db', '#e67e22']
    explode = (0.05, 0.05)
    
    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=categories, colors=colors,
                                        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    ax1.set_title('Test Case Distribution', fontsize=14, fontweight='bold', pad=20)
    
    # Bar chart - Pass/Fail status
    status = ['Passed', 'Failed', 'Skipped']
    counts = [test_summary["passed"], test_summary["failed"], test_summary["skipped"]]
    colors_status = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    bars = ax2.bar(status, counts, color=colors_status, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Number of Tests', fontsize=12, fontweight='bold')
    ax2.set_title('Test Execution Results', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add pass rate text
    ax2.text(0.5, 0.95, f'Pass Rate: {test_summary["pass_rate"]:.1f}%\nExecution Time: {test_summary["execution_time"]:.1f}s',
             transform=ax2.transAxes, fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), ha='center')
    
    plt.tight_layout()
    plt.savefig(output_dir / '3_test_execution_summary.png', dpi=300, bbox_inches='tight')
    print(f"✅ Created: 3_test_execution_summary.png")
    plt.close()

def create_scalability_chart():
    """Chart 4: Scalability & Load Test Results"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    tests = ['Concurrent\nOperations\n(10 users)', 'Load Stability\n(50 users)', 'Registration\nBurst\n(70 users)']
    success_rates = [
        performance_data["concurrent_operations"]["success_rate"],
        performance_data["load_stability"]["success_rate"],
        performance_data["registration_burst"]["success_rate"]
    ]
    response_times = [
        performance_data["concurrent_operations"]["avg_time"],
        performance_data["load_stability"]["avg_response_time"],
        performance_data["registration_burst"]["avg_time"]
    ]
    
    x = np.arange(len(tests))
    width = 0.35
    
    # Create twin axis
    ax2 = ax.twinx()
    
    bars1 = ax.bar(x - width/2, success_rates, width, label='Success Rate (%)', 
                   color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax2.bar(x + width/2, response_times, width, label='Avg Response Time (s)', 
                    color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Test Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold', color='#2ecc71')
    ax2.set_ylabel('Response Time (seconds)', fontsize=12, fontweight='bold', color='#3498db')
    ax.set_title('Scalability & Load Test Results', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(tests, fontsize=10)
    ax.set_ylim(95, 101)
    ax.tick_params(axis='y', labelcolor='#2ecc71')
    ax2.tick_params(axis='y', labelcolor='#3498db')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, val in zip(bars1, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2ecc71')
    
    for bar, val in zip(bars2, response_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{val:.1f}s', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#3498db')
    
    # Combined legend
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / '4_scalability_load_tests.png', dpi=300, bbox_inches='tight')
    print(f"✅ Created: 4_scalability_load_tests.png")
    plt.close()

def create_performance_radar_chart():
    """Chart 5: Performance Metrics Radar Chart"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    categories = ['Login\nPerformance', 'Dashboard\nLoad', 'Query\nSpeed', 
                  'Concurrent\nOps', 'Load\nStability', 'Burst\nHandling']
    N = len(categories)
    
    # Normalize scores (0-100 scale)
    scores = [
        100 - (performance_data["concurrent_logins"]["p95"] / performance_data["concurrent_logins"]["threshold"] * 100),
        100 - (performance_data["dashboard_load"]["time"] / performance_data["dashboard_load"]["threshold"] * 100),
        100 - (performance_data["large_dataset"]["time"] / performance_data["large_dataset"]["threshold"] * 100),
        performance_data["concurrent_operations"]["success_rate"],
        performance_data["load_stability"]["success_rate"],
        performance_data["registration_burst"]["success_rate"]
    ]
    
    # Adjust to positive scale
    scores = [max(0, min(100, score)) for score in scores]
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    scores += scores[:1]
    angles += angles[:1]
    
    ax.plot(angles, scores, 'o-', linewidth=2, color='#3498db', label='Actual Performance')
    ax.fill(angles, scores, alpha=0.25, color='#3498db')
    
    # Add threshold line (80% of max)
    threshold = [80] * len(angles)
    ax.plot(angles, threshold, '--', linewidth=2, color='#e74c3c', alpha=0.7, label='Target (80%)')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10)
    ax.set_title('System Performance Metrics Overview', fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / '5_performance_radar_chart.png', dpi=300, bbox_inches='tight')
    print(f"✅ Created: 5_performance_radar_chart.png")
    plt.close()

def save_performance_report():
    """Save performance data as JSON report"""
    report = {
        "generated_at": datetime.now().isoformat(),
        "test_summary": test_summary,
        "performance_metrics": performance_data,
        "key_findings": {
            "strengths": [
                "100% test pass rate (34/34 tests passed)",
                "All response times within acceptable thresholds",
                "System remains stable under concurrent load (50+ users)",
                "Zero critical failures or data corruption issues"
            ],
            "areas_for_improvement": [
                "P95 login time (11.67s) is near threshold under 30 concurrent users",
                "Consider implementing caching for dashboard statistics",
                "Monitor memory usage during sustained high-load scenarios"
            ],
            "recommendations": [
                "Implement Redis caching for frequently accessed data",
                "Add database connection pooling optimization",
                "Consider horizontal scaling for authentication service",
                "Implement rate limiting for API endpoints"
            ]
        }
    }
    
    with open(output_dir / 'performance_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created: performance_report.json")

def main():
    """Generate all performance visualization charts"""
    print("\n🎨 Generating Performance Visualization Charts...")
    print("=" * 60)
    
    try:
        create_response_time_chart()
        create_percentile_chart()
        create_test_summary_chart()
        create_scalability_chart()
        create_performance_radar_chart()
        save_performance_report()
        
        print("=" * 60)
        print(f"✅ All charts generated successfully!")
        print(f"📁 Output directory: {output_dir.absolute()}")
        print("\n📊 Generated Files:")
        print("  1. 1_response_time_comparison.png - Response time vs thresholds")
        print("  2. 2_login_performance_percentiles.png - Login performance distribution")
        print("  3. 3_test_execution_summary.png - Test results overview")
        print("  4. 4_scalability_load_tests.png - Scalability & load test results")
        print("  5. 5_performance_radar_chart.png - Overall performance metrics")
        print("  6. performance_report.json - Detailed performance report")
        print("\n🎉 Performance visualization complete!")
        
    except Exception as e:
        print(f"❌ Error generating charts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
