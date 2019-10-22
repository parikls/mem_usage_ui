<template>
    <div id="mem">

        <div class="processes grey darken-1" v-if="!fullScreenView">

            <div class="row">
                <div class="input-field col s12 m12 l12">
                    <input type="text" class="input white-text" placeholder="Filter processes" v-model="processFilter">
                </div>

                <div class="input-field col s12 m12 l12">
                    <input type="text" id="snapshot-interval" class="input white-text" placeholder="1"
                           v-model="snapshotInterval">
                    <label for="snapshot-interval">Memory snapshot interval</label>
                </div>

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

        <div v-bind:class="{'chart-full': fullScreenView, 'chart': !fullScreenView}">
            <p class="center-align red-text" v-if="errorMessage">{{ errorMessage }}</p>
            <line-chart :chart-data="chartDataCollection" :points-visible="pointsVisible"></line-chart>
            <div class="filter">
                <div class="row">
                    <div class="col s12 m12 l12">
                        <p class="center-align">
                            <a class="btn grey darken-1 white-text" v-if="snapshotEnabled" @click="unsubscribe">Stop snapshotting</a>
                            <a class="btn grey darken-1 white-text" @click="fullScreenView = !fullScreenView">{{ fullScreenText }}</a>
                            <a class="btn grey darken-1 white-text" v-if="activeProcessUniqueId" @click="exportChartAsImage">Export chart as image</a>
                        </p>
                    </div>
                </div>
            </div>

        </div>

        <contacts></contacts>

    </div>
</template>

<script>
    import LineChart from "./Chart"
    import WS from "./websocket"
    import eventBus from "./bus";
    import Contacts from "./components/Contacts";

    const PID_UPDATE = "pid_update";
    const PROCESS_DIFF = "process_diff";

    export default {
        name: 'app',
        components: {
            LineChart, Contacts
        },
        data() {
            return {
                ws: null,
                processFilter: "",
                processes: {},
                activeProcess: {},

                chartDataCollection: null,
                chartData: {
                    memory: [],
                    timestamps: []
                },

                snapshotInterval: 1,
                snapshotEnabled: false,
                errorMessage: null,
                fullScreenView: false,
                pointsVisible: false,
                activeProcessUniqueId: null
            }
        },

        mounted() {
            this.ws = new WS(`ws://${window.location.host}/ws`, this.websocketHandler);
        },

        methods: {

            /**
             * Perform subscribing to a particular process
             * @param process
             */
            subscribe(process) {

                // already subscribed to some process
                if (this.activeProcess.pid) {
                    // same process?
                    if (process.pid === this.activeProcess.pid) {
                        this.errorMessage = `Attempt to subscribe to already subscribed process`;
                        return
                    } else {
                        // unsubscribe from existing one
                        this.unsubscribe();
                    }
                }

                // clear all previous subscribing variables
                this.activeProcess = process;
                this.snapshotEnabled = true;
                this.errorMessage = null;
                this.pointsVisible = false;
                this.chartData = {
                    memory: [],
                    timestamps: []
                };

                this.activeProcessUniqueId = `${this.activeProcess.name}_${this.activeProcess.pid}`;

                // send `subscribe` event
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
                if (!this.activeProcess.pid) {
                    return
                }

                this.ws.server.send(JSON.stringify({
                    type: "unsubscribe",
                    pid: this.activeProcess.pid
                }));
                this.snapshotEnabled = false;
                this.activeProcess = {};
                this.pointsVisible = true;
            },

            /**
             * Main entry point for any message which comes from websocket
             */
            websocketHandler(message){
                let data;

                try {
                    data = JSON.parse(message.data);
                } catch (e) {
                    alert(`Cant represent '${data}' as JSON`);
                    return;
                }

                if (data.type === PID_UPDATE){
                    this.handlePidUpdate(data);
                } else if (data.type === PROCESS_DIFF){
                    this.handleProcessDiff(data);
                } else {
                    // unknown type
                    alert(`Unknown message type ${data.type}`)
                }
            },

            /**
             * Handle websocket messages and push mem snapshot values.
             * Chart is being updated reactive
             * @param data: payload
             */
            handlePidUpdate(data) {
                if (data.success) {
                    if (this.chartData.memory[this.chartData.memory.length - 1] === data.process.rss &&
                        this.chartData.memory[this.chartData.memory.length - 2] === data.process.rss) {
                        // memory consumption didn't changed.
                        // do not draw extra point - just adjust timestamp
                        this.chartData.timestamps[this.chartData.timestamps.length - 1] = (new Date).toLocaleTimeString();
                    } else {
                        this.chartData.memory.push(data.process.rss);
                        this.chartData.timestamps.push((new Date).toLocaleTimeString());
                    }

                    // update chart
                    this.chartDataCollection = {
                        labels: this.chartData.timestamps,
                        datasets: [{
                            label: this.activeProcess.cmdline,
                            backgroundColor: '#ff3d00',
                            data: this.chartData.memory
                        }]
                    }
                } else {
                    // bad response - cleanup internal variables
                    this.activeProcess = {};
                    this.snapshotEnabled = false;
                    this.errorMessage = data.message;
                    this.pointsVisible = true;
                }
            },

            /**
             * Handles processes diff payload.
             * @param data: processes diff
             */
            handleProcessDiff(data){

                let self = this;

                for (let pid of data.payload.terminated){
                    self.$delete(self.processes, pid);
                }

                for (let [pid, process] of Object.entries(data.payload.new)){
                    self.$set(self.processes, pid, process);
                }
            },

            exportChartAsImage(){
                eventBus.$emit("chart.export", this.activeProcessUniqueId)
            }
        },

        computed: {
            filteredProcesses() {
                return Object.values(this.processes)
                    .filter(
                        (process) =>
                            process.name.toLowerCase().indexOf(this.processFilter.toLowerCase()) !== -1 ||
                            process.cmdline.toLowerCase().indexOf(this.processFilter.toLowerCase()) !== -1
                    )
            },

            fullScreenText(){
                return this.fullScreenView ? "Turn OFF full-screen view" : "Turn ON full-screen view"
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

    .chart-full {
        position: absolute;
        margin-top: 20vh;
        padding-left: 5vw;
        width: 100vw;
        max-width: 100vw;
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

</style>