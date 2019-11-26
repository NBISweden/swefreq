<template>
<div class="dataset-terms">
  <div class="row">
    <div class="col-sm-12">
      <div class="dataset-panel">
        <div class="dataset-body" v-html="dataset.version.terms" />
      </div>
    </div>
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
