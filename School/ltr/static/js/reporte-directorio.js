const getOptionChart1 = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/casosporarea");
    return await response.json();

  } catch (ex) {
    alert(ex);
  }
};

const getOptionChart2 = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/tiempopromedio");
    return await response.json();

  } catch (ex) {
    alert(ex);
  }
};


const initChart = async () => {
    const myChart1 = echarts.init(document.getElementById("chart-pie1"));
    const myChart2 = echarts.init(document.getElementById("chart-bar-rotated"));

    myChart1.setOption(await getOptionChart1());
    myChart2.setOption(await getOptionChart2());

    myChart1.resize();
    myChart2.resize();
    
};

window.addEventListener("load", async () => {
    await initChart();
});