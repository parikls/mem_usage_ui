<script>
    import {Line, mixins} from 'vue-chartjs'
    import eventBus from "./bus";

    const {reactiveProp} = mixins;

    export default {
        extends: Line,
        mixins: [reactiveProp],
        props: ["points-visible"],
        data() {
            return {
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    width: "100%",
                    events: [],
                    scales: {
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Megabytes'
                            }
                        }],
                        xAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Time'
                            }
                        }]
                    },
                    tooltips: {
                        intersect: false
                    }
                }
            };
        },
        mounted() {
            this.renderChart(this.chartData, this.options);

            // export chart as image
            let self = this;
            eventBus.$on("chart.export", function (chartName) {

                // create temp download url
                let linkSource = self.$refs.canvas.toDataURL('image/png');
                let fileName = `${chartName}.png`;

                let downloadLink = document.createElement("a");
                downloadLink.href = linkSource;
                downloadLink.download = fileName;

                // click to start the download
                downloadLink.click();

                // cleanup element
                downloadLink.remove();
            })
        },

        watch: {
            pointsVisible: function (value) {

                if (value === true) {

                    // let's do a deep-copy of existing options
                    let extendedOptions = JSON.parse(JSON.stringify(this.options));

                    // and extend them with tooltips and events
                    extendedOptions.tooltips.callbacks = {
                        label: function (tooltipItem, data) {
                            return `${tooltipItem.yLabel} MB`;
                        }
                    };

                    extendedOptions.events = ["mousemove"];

                    // and finally re-render the chart with tooltips
                    this.renderChart(this.chartData, extendedOptions);
                } else {
                    this.renderChart(this.chartData, this.options);
                }
            }
        }
    }
</script>
