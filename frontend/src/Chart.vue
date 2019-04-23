<script>
    import {Line, mixins} from 'vue-chartjs'

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
                    }
                }
            }
        },
        mounted() {
            this.renderChart(this.chartData, this.options)
        },

        watch: {
            pointsVisible: function(value){

                if (value === true){

                    // let's do a deep-copy of existing options
                    let extendedOptions = JSON.parse(JSON.stringify(this.options));

                    // and extend them with tooltips and events
                    extendedOptions.tooltips = {
                        callbacks: {
                            label: function (tooltipItem, data) {
                                return `${tooltipItem.yLabel} MB`;
                            }
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

<style>
</style>