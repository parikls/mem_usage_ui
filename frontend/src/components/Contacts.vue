<template>

    <div class="fixed-action-btn direction-top active">

        <a id="menu" class="waves-effect waves-light btn btn-floating deep-orange accent-3">
            <i class="material-icons" @click="toggleContacts">stars</i></a>

        <div ref="taptarget" class="tap-target deep-orange accent-3 white-text" data-target="menu">
            <div class="tap-target-content">
                <h5>Thank You!</h5>
                <p>Questions? - feel free to contact me - <a class="link" href="mailto:porovozls@gmail.com">porovozls@gmail.com</a></p>
                <p>Or via github - <a class="link" href="https://github.com/parikls">https://github.com/parikls</a> </p>
                <p>Really appreciate for a star!)

                    <iframe
                            src="https://ghbtns.com/github-btn.html?user=parikls&repo=mem_usage_ui&type=star&count=true"
                            frameborder="0"
                            scrolling="0"
                            width="80px"
                            height="20px">
                    </iframe>
                </p>
            </div>
        </div>

    </div>
</template>

<script>
    export default {
        data() {
            return {
                tapTarget: null
            }

        },
        mounted() {
            this.tapTarget = M.TapTarget.init(this.$refs.taptarget, {});
        },

        methods: {
            toggleContacts() {
                this.tapTarget.open();
            }
        }

    }
</script>

<style scoped>
    .tap-target-content {
        left: 2vw !important;
        text-align: right !important;
        padding-left: 0 !important;
    }

    .link {
        color: black;
    }

</style>