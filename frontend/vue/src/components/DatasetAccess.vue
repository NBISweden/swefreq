<template>
<div class="dataset-access">
  <div class="row">
    <div class="col-sm-12">
      <div class="alert" role="alert">
        <strong>Nota Bene:</strong> You can only request access to, and
        download, summary files here<span v-if="dataset.version.dataContactLink">,
          if you want access to the underlying individual data you need to
          {{ dataContactIsEmail ? "contact" : "visit" }}
          <a :href="dataContactIsEmail ? 'mailto:' : '' + dataset.version.dataContactLink">{{ dataset.version.dataContactName }}</a></span>.
      </div>
    </div>
  </div>
 </div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetAccess',
  data() {
    return {
    }
  },
  computed: {
    dataContactIsEmail () {
      return this.dataset.version.dataContactLink.includes("@");
    },
    ...mapGetters(['dataset', 'collections', 'study'])
    
  },
};

</script>

<style scoped>
</style>
