<template>
<div class="footer-bar text-center">
  <div class="container">
    <div class="row">
      <div class="col-sm-3 text-center">
        <a href="https://www.scilifelab.se/data/"><img class="logo scilife" :src="require('../assets/img/SLL_logo.png')" alt="SciLifeLab Data Centre logo"></a>
      </div>
      <div class="col-sm-3 text-center">
        <a href="https://ngisweden.scilifelab.se/"><img class="logo" :src="require('../assets/img/ngisweden_logo.png')" alt="NGI logo"></a>
      </div>
      <div class="col-sm-3 text-center">
        <a href="https://nbis.se"><img class="logo" :src="require('../assets/img/nbislogo-green.png')" alt="NBIS"></a>
      </div>
      <div class="col-sm-3 text-center">
        <a href="https://elixir.se"><img class="logo elixir" :src="require('../assets/img/ELIXIR_SWEDEN_white_background.png')" alt="Elixir Sweden"></a>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'FooterBar',
  data() {
    return {
    }
  },
  computed: {
    ...mapGetters(['user', 'loggedIn'])
  },
  created() {
    this.$store.dispatch('getUser');
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
