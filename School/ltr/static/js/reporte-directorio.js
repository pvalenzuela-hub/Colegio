const getOptionChart1 = async () => {
  try {
    const response = await fetch("/api/casosporarea");
    return await response.json();

  } catch (ex) {
    alert(ex);
  }
};

const getOptionChart2 = async () => {
  try {
    const response = await fetch("/api/tiempopromedio");
    return await response.json();

  } catch (ex) {
    alert(ex);
  }
};

const getOptionChart3 = async () => {
  try {
    const response = await fetch("/api/casotipocontacto");
    return await response.json();

  } catch (ex) {
    alert(ex);
  }
};

const initChart = async () => {
    const myChart1 = echarts.init(document.getElementById("chart1"));
    const myChart2 = echarts.init(document.getElementById("chart2"));
    const myChart3 = echarts.init(document.getElementById("chart3"));

    myChart1.setOption(await getOptionChart1());
    myChart2.setOption(await getOptionChart2());
    myChart3.setOption(await getOptionChart3());

    myChart1.resize();
    myChart2.resize();
    myChart3.resize();
    
};

window.addEventListener("load", async () => {
    await initChart();
});