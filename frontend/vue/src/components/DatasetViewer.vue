<template>
<div class="dataset-viewer">
  <div class="container">
    <router-view></router-view>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetInfo',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['dataset', 'collections', 'study'])
  },
  props: ["datasetName"],
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
