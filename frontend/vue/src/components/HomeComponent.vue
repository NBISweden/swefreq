<template>
<div class="container">
  <dataset-entry v-for="dataset in datasets" :key="dataset.id" :dataset="dataset"></dataset-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import DatasetEntry from '../components/DatasetEntry.vue';

export default {
  name: 'HomeComponent',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['datasets'])
  },
  components: {
    'dataset-entry': DatasetEntry,
  },
  created() {
    this.$store.dispatch('getDatasetList');
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
