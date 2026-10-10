/**
 * Smart Education Platform - Dynamic Chart Visualizations (Chart.js)
 */

window.EduCharts = {
  // 1. Radar Chart for Topic Mastery
  renderRadarChart: function(canvasId, labels, dataPoints) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Mastery Level (%)',
          data: dataPoints,
          backgroundColor: 'rgba(67, 97, 238, 0.2)',
          borderColor: '#4361ee',
          pointBackgroundColor: '#4361ee',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#4361ee',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(0, 0, 0, 0.08)' },
            grid: { color: 'rgba(0, 0, 0, 0.08)' },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { stepSize: 20, display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  // 2. Bar Chart for Subject Performance & Marks
  renderBarChart: function(canvasId, labels, dataPoints, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Score (%)',
          data: dataPoints,
          backgroundColor: colors || '#4361ee',
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  },

  // 3. Line Chart for Quiz Attempts & Trend
  renderLineChart: function(canvasId, labels, dataPoints) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Quiz Score (%)',
          data: dataPoints,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
};
