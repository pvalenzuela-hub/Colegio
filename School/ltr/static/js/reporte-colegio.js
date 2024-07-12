document.addEventListener("DOMContentLoaded", function() {
    const colegio_id = document.getElementById("colegio_id").value;

    const getOptionChart1 = async (colegio_id) => {
        try {
            const response = await fetch(`/api/chart1_colegio?colegio_id=${colegio_id}`);
            return await response.json();
        } catch (ex) {
            alert(ex);
        }
    };

    const getOptionChart2 = async (colegio_id) => {
        try {
            const response = await fetch(`/api/chart2_colegio?colegio_id=${colegio_id}`);
            return await response.json();
        } catch (ex) {
            alert(ex);
        }
    };

    const getOptionChart3 = async (colegio_id) => {
        try {
            const response = await fetch(`/api/chart3_colegio?colegio_id=${colegio_id}`);
            return await response.json();
        } catch (ex) {
            alert(ex);
        }
    };

    const getOptionChart4 = async (colegio_id) => {
        try {
            const response = await fetch(`/api/chart4_colegio?colegio_id=${colegio_id}`);
            return await response.json();
        } catch (ex) {
            alert(ex);
        }
    };

    const initChart = async () => {
        const myChart1 = echarts.init(document.getElementById("chart1"));
        const myChart2 = echarts.init(document.getElementById("chart2"));
        const myChart3 = echarts.init(document.getElementById("chart3"));
        const myChart4 = echarts.init(document.getElementById("chart4"));

        myChart1.setOption(await getOptionChart1(colegio_id));
        myChart2.setOption(await getOptionChart2(colegio_id));
        myChart3.setOption(await getOptionChart3(colegio_id));
        myChart4.setOption(await getOptionChart4(colegio_id));

        myChart1.resize();
        myChart2.resize();
        myChart3.resize();
        myChart4.resize();
    };

    initChart();  // Llama a initChart aquí
});
