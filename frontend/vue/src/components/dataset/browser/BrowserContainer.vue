<template>
<div class="dataset-viewer">
  <div class="container">
    <router-view></router-view>
    <router-view name="coverage_plot"></router-view>
    <router-view name="variant_list"></router-view>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetViewer',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset', 'errorCode']),
    dataType() {
      let urlParts = this.$route.path.split('/');
      return urlParts[urlParts.length-2];
    },
  },
  props: ["datasetName", "datasetVersion", "identifier"],
  components: {
  },
  created() {
    this.$store.dispatch('getDataset', this.$props.datasetName);
    if (this.dataType == 'gene' ||
        this.dataType == 'transcript' ||
        this.dataType == 'region') {
      this.$store.dispatch('getVariants', {'dataset': this.$props.datasetName,
                                           'version': this.$props.datasetVersion,
                                           'datatype': this.dataType,
                                           'identifier': this.$props.identifier});
    }
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
