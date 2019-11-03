<template>
<div class="dataset-viewer">
  <div class="container">
    <div class="row">
      <div>
        <div v-if="dataset.future" class="alert alert-danger alert-future">This version will become public at {{ctrl.dataset.version.availableFrom}}</div>
        <h1>{{ dataset.fullName }}</h1>
      </div>
      <dataset-nav-bar :datasetName="datasetName"></dataset-nav-bar>
    </div>
    <div class="row">
      <div id="tab-bar">
      </div>
    </div>
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
    ...mapGetters(['dataset', 'collections', 'study'])
  },
  props: ["datasetName"],
  components: {
    'dataset-nav-bar': DatasetViewerBar,
  },
  created() {
    this.$store.dispatch('getDataset', this.datasetName);
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
