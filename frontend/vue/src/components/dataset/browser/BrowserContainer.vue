
<template>
<div class="dataset-viewer">
  <div class="container">
    <gene-info v-if="dataType==='gene'" :geneName="identifier" :datasetName="datasetName" :datasetVersion="datasetVersion"></gene-info>
    <coverage-plot></coverage-plot>
    <variant-list></variant-list>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserGene from './BrowserGene.vue';
import BrowserCoverage from './BrowserCoverage.vue';
import BrowserVariants from './BrowserVariants.vue';

export default {
  name: 'BrowserContainer',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset']),
    dataType() {
      let urlParts = this.$route.path.split('/');
      return urlParts[urlParts.length-2];
    },
  },
  props: ["datasetName", "datasetVersion", "identifier"],
  components: {
    'coverage-plot': BrowserCoverage,
    'variant-list': BrowserVariants,
    'gene-info': BrowserGene,
  },
  created() {
    this.$store.dispatch('getDataset', this.$props.datasetName);
    this.$store.dispatch('getVariants', {'dataset': this.$props.datasetName,
                                         'version': this.$props.datasetVersion,
                                         'datatype': this.dataType,
                                         'identifier': this.$props.identifier});

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
