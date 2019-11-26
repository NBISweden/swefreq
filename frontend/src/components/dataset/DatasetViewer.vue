<template>
<div class="container">
  <div v-if="error">
    Unable to retrieve the dataset<span v-if="datasetVersion">/version combination</span> ({{ datasetName }}<span v-if="datasetVersion">/{{ datasetVersion }}</span>). Maybe it doesn't exist?
  </div>

  <div v-else>
    <div class="row">
      <div>
	<div v-if="dataset.future" class="alert alert-danger alert-future">This version will become public at {{dataset.version.availableFrom}}</div>
	<h1>{{ dataset.fullName }}</h1>
      </div>
      <dataset-nav-bar :datasetName="datasetName" :datasetVersion="datasetVersion"></dataset-nav-bar>
    </div>
    <div class="row">
      <router-view></router-view>
    </div>
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
      error: null,
    }
  },
  computed: {
    ...mapGetters(['dataset', 'tmp'])
  },
  props: ["datasetName", "datasetVersion"],
  components: {
    'dataset-nav-bar': DatasetViewerBar,
  },
  created() {
    this.$store.dispatch('getDataset', {
      datasetName: this.$props.datasetName,
      datasetVersion: this.$props.datasetVersion,
    })
      .catch((error) => {
        this.error = error;
      });
  },
};

</script>

<style scoped>

</style>
