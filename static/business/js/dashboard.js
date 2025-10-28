new Chart(
    document.getElementById('financeCharts'),
    {
      type: 'bar',
      data: {
        labels: ['red,lue,green,yellow,purple,orange'],
        datasets: [
          {
            label: 'Acquisitions by year',
            data: [12, 19, 3, 5, 2, 3],
            borderWidth: 1
          }
        ]
      },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    }
  );