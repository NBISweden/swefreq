<template>
<div class="dataset-bar">
  <ul class="nav nav-tabs">
    <li :class="{'active': this.$route.path.endsWith('/about')}"><router-link :to="'/dataset/' + datasetName + '/about'">Information</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/terms')}"><router-link :to="'/dataset/' + datasetName + '/terms'">Terms</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/download')}"><router-link :to="'/dataset/' + datasetName + '/download'">Dataset Access</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/beacon')}"><router-link :to="'/dataset/' + datasetName + '/beacon'">Beacon</router-link></li>
    <li :class="{'active': this.$route.path.includes('/browser')}"><router-link :to="'/dataset/' + datasetName + '/browser'">Browser</router-link></li>
    <li :class="{'active': this.$route.path.endsWith('/admin'), 'pull-right': true, 'admin-tab': true}"><router-link :to="'/dataset/' + datasetName + '/admin'">Admin</router-link></li>
  </ul>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetViewerBar',
  data() {
    return {
    }
  },
  props: [
    "datasetName",
  ],
  computed: {
    ...mapGetters(['dataset'])
  },
};

</script>

<style scoped>
</style>
