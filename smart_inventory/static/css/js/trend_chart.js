document.addEventListener("DOMContentLoaded", function () {
  const data = window.forecastData;
  if (!data) return;

  const ctx = document.getElementById('trendChart');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.dates,
      datasets: [
        {
          label: 'Actual Sales',
          data: data.actual,
          borderColor: 'rgb(54,162,235)',
          backgroundColor: 'rgba(54,162,235,0.15)',
          fill: true,
          tension: 0.3
        },
        {
          label: 'Forecasted Sales',
          data: data.forecast,
          borderColor: 'rgb(255,159,64)',
          backgroundColor: 'rgba(255,159,64,0.12)',
          borderDash: [6,4],
          fill: false,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: data.productName + ' — Sales & Forecast' },
        tooltip: { mode: 'index', intersect: false },
        legend: { position: 'bottom' }
      },
      interaction: { mode: 'nearest', axis: 'x', intersect: false },
      scales: {
        x: { title: { display: true, text: 'Date' } },
        y: { title: { display: true, text: 'Quantity' }, beginAtZero: true }
      }
    }
  });
});
function renderTrendChart(forecastData) {
  const ctx = document.getElementById("trendChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: forecastData.dates,
      datasets: [
        {
          label: forecastData.productName + " Actual Sales",
          data: forecastData.actual,
          borderColor: "blue",
          fill: false,
        },
        {
          label: forecastData.productName + " Forecast",
          data: forecastData.forecast,
          borderColor: "red",
          borderDash: [5, 5],
          fill: false,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" }
      },
      scales: {
        x: { title: { display: true, text: "Date" } },
        y: { title: { display: true, text: "Quantity Sold" } }
      }
    }
  });
}
