<template>
<div class="dataset-bar">
  <ul class="nav nav-tabs">
    <li class="{'active': active=='main'}"><router-link :to="{ path: '/dataset/' + datasetName + '/about', params: {datasetName: datasetName}}">Information</router-link></li>
    <li class="{'active': active=='terms'}"><router-link :to="{ path: '/dataset/' + datasetName + '/terms', params: {datasetName: datasetName}}">Terms</router-link></li>
    <li class="{'active': active=='download'}"><router-link :to="{ path: '/dataset/' + datasetName + '/download', params: {datasetName: datasetName}}">Dataset Access</router-link></li>
    <li class="{'active': active=='beacon'}"><router-link :to="{ path: '/dataset/' + datasetName + '/beacon', params: {datasetName: datasetName}}">Beacon</router-link></li>
    <li class="{'active': active=='browser'}"><router-link :to="{ path: '/dataset/' + datasetName + '/browser', params: {datasetName: datasetName}}">Browser</router-link></li>
    <li class="{'active': active=='admin', 'pull-right': true, 'admin-tab': true}"><router-link :to="{ path: '/dataset/' + datasetName + '/admin', params: {datasetName: datasetName}}">Admin</router-link></li>
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
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
