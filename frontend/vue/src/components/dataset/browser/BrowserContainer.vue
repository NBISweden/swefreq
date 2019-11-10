<template>
<div class="dataset-viewer">
  <div class="container">
    <router-view></router-view>
    <coverage-plot></coverage-plot>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserCoverage from './BrowserCoverage.vue';

export default {
  name: 'DatasetViewer',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset', 'errorCode'])
  },
  props: ["datasetName", "datasetVersion"],
  components: {
    'coverage-plot': BrowserCoverage,
    
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
