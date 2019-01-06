<template>
    <div id="mem">

        <div class="processes grey darken-1">

            <div class="row">
                <div class="input-field col s12 m12 l12">
                    <input type="text" class="input white-text" placeholder="Filter processes" v-model="processFilter">
                </div>

                <div class="input-field col s12 m12 l12">
                    <input type="text" id="snapshot-interval" class="input white-text" placeholder="1" v-model="snapshotInterval">
                    <label for="snapshot-interval">Memory snapshot interval</label>
                </div>


                <p class="center-align">
                    <a class="btn refresh-processes grey darken-2 white-text" @click="refreshProcesses">refresh processes</a>
                </p>
            </div>

            <table class="highlight centered responsive-table white-text">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>Command line</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="process in filteredProcesses" @click="subscribe(process)">
                        <td>{{ process.pid }}</td>
                        <td>{{ process.name }}</td>
                        <td>{{ process.cmdline}}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="chart">
            <p class="center-align red-text" v-if="errorMessage">{{ errorMessage }}</p>
            <line-chart :chart-data="chartDataCollection"></line-chart>
            <div class="filter">
                <div class="row">
                    <div class="col s12 m12 l12">
                        <p class="center-align">
                            <a class="btn grey darken-1 white-text" v-if="snapshotEnabled" @click="unsubscribe">Stop snapshotting</a>
                        </p>
                    </div>
                </div>
            </div>

        </div>


    </div>
</template>

<script>
    import axios from "axios";
    import LineChart from "./Chart"
    import WS from "./websocket"

    export default {
        name: 'app',
        components: {
            LineChart
        },
        data() {
            return {
                ws: null,
                processFilter: "",
                processes: [],
                activeProcess: {},

                chartDataCollection: null,
                chartData: {
                    memory: [],
                    timestamps: []
                },

                snapshotInterval: 1,
                snapshotEnabled: false,
                errorMessage: null

            }
        },

        mounted() {
            this.refreshProcesses();
            this.ws = new WS(`ws://${window.location.host}/ws`, this.handleRealtimeMessage);
        },

        methods: {
            /**
             * Get list of all running processes
             */
            refreshProcesses() {
                axios.get("/processes").then(response => {
                    this.$set(this, "processes", response.data);
                })
            },

            /**
             * Perform subscribing to a particular process
             * @param process
             */
            subscribe(process) {

                console.log(`Subscribing to process ${process.name}. PID = ${process.pid}`);

                // same process?
                if (process.pid === this.activeProcess.pid) {
                    console.log(`Attempt to subscribe to already subscribed process`);
                    return
                }

                // clear all previous subscribing variables
                this.activeProcess = process;
                this.snapshotEnabled = true;
                this.errorMessage = null;
                this.chartData = {
                    memory: [],
                    timestamps: []
                };

                // send `subscribe` message
                this.ws.server.send(JSON.stringify({
                    type: "subscribe",
                    pid: process.pid,
                    interval: this.snapshotInterval

                }));

            },

            /**
             * Unsubscribe from current active process
             */
            unsubscribe() {
                if (!this.activeProcess.pid){ return }

                this.ws.server.send(JSON.stringify({
                    type: "unsubscribe",
                    pid: this.activeProcess.pid
                }));
                this.snapshotEnabled = false;
                this.activeProcess = {};
            },

            /**
             * Handle websocket messages and push mem snapshot values.
             * Chart is being updated reactive
             * @param message: websocket event
             */
            handleRealtimeMessage(message) {
                let data = JSON.parse(message.data);
                if (data.success) {
                    this.chartData.memory.push(data.rss);
                    this.chartData.timestamps.push((new Date).toLocaleTimeString());

                    // update chart
                    this.chartDataCollection = {
                        labels: this.chartData.timestamps,
                        datasets: [{
                            label: `Memory consumption for ${this.activeProcess.name}`,
                            backgroundColor: '#ff3d00',
                            data: this.chartData.memory
                        }]
                    }
                } else {
                    // bad response
                    this.activeProcess = {};
                    this.snapshotEnabled = false;
                    this.errorMessage = data.message;
                }
            }

        },

        computed: {
            filteredProcesses() {
                return this.processes
                    .filter(
                        (process) => process.name.toLowerCase().indexOf(this.processFilter.toLowerCase()) !== -1
                    )
            }
        }
    }
</script>

<style>
    .chart {
        position: absolute;
        left: 50vw;
        margin-top: 20vh;
        padding-left: 5vw;
        width: 50vw;
        max-width: 50vw;
        height: 100vh;
        max-height: 100vh;
    }

    .processes {
        position: absolute;
        overflow: scroll;
        height: 100vh;
        max-height: 100vh;
        width: 50vw;
        max-width: 50vw;
    }

    td {
        cursor: pointer;
        max-width: 15vw;
        overflow-wrap: break-word;
    }

    input[type=text]:not(.browser-default):focus:not([readonly]) {
        border-bottom: 1px solid #ff3d00;
        box-shadow: 0 1px 0 0 #ff3d00;
    }

    input[type=text]:not(.browser-default):focus:not([readonly]) + label {
        color: #ff3d00
    }

    .refresh-processes {
        margin-top: 3vh;
    }

</style>