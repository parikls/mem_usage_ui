<script>
    import {Line, mixins} from 'vue-chartjs'

    const {reactiveProp} = mixins;

    export default {
        extends: Line,
        mixins: [reactiveProp],
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
            this.renderChart(this.chartdata, this.options)
        }
    }
</script>

<style>
</style>