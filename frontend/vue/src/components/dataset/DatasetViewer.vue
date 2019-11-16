<template>
<div class="container">
  <div class="row">
    <div>
      <div v-if="dataset.future" class="alert alert-danger alert-future">This version will become public at {{ctrl.dataset.version.availableFrom}}</div>
      <h1>{{ dataset.fullName }}</h1>
    </div>
    <dataset-nav-bar :datasetName="datasetName" :datasetVersion="datasetVersion"></dataset-nav-bar>
  </div>
  <div class="row">
    <router-view></router-view>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import DatasetViewerBar from './DatasetViewerBar.vue';

export default {
  name: 'DatasetViewer',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset', 'user'])
  },
  props: ["datasetName", "datasetVersion"],
  components: {
    'dataset-nav-bar': DatasetViewerBar,
  },
  created() {
    this.$store.dispatch('getDataset', {
      datasetName: this.$props.datasetName,
      datasetVerstion: this.$props.datasetVersion,
    });
  },
};

</script>

<style scoped>

</style>
