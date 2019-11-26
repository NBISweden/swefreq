<template>
<div class="top-bar">
  <nav class="navbar navbar-default">
    <div class="container">
      <div class="navbar-header">
        <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-things" aria-expanded="false">
          <span class="sr-only">Toggle navigation</span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
        <router-link class="navbar-brand" to="/">SweFreq &mdash; The Swedish Frequency resource for genomics</router-link>
      </div>
      <div class="collapse navbar-collapse" id="navbar-things">
        <ul class="nav navbar-nav navbar-right">
          <li><a @click="showAbout = !showAbout" style="cursor: pointer">About</a>
          <li class="dropdown" v-if="user.user"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{{ user.user }}<span class="caret"></span></a>
            <ul class="dropdown-menu">
              <li><router-link to="/profile">User Profile</router-link></li>
              <li><a :href="'/logout?next=' + this.$route.path" target="_self" :title="'Logout ' + user.user">Logout</a></li>
            </ul>
          </li>
          <li class="dropdown" v-if="!user.user">
            <a :href="'/elixir/login?next=' + this.$route.path" target="_self">Login</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  <!-- About blurb -->
  <div class="blurb" v-if="showAbout">
    <div class="container">
      <div class="row">
        <div class="col-md-2"></div>
        <div class="col-sm-12 col-md-8">
          <p>The Swedish Frequency resource for genomics (SweFreq) is a
          website developed to make genomic datasets more findable and
          accessible in order to promote collaboration, new research and
          increase public benefit. You can contact <a href="mailto:swefreq@scilifelab.se">swefreq@scilifelab.se</a> if
          you want to find out more about this resource and how it could
          benefit you and your research.</p>
        </div>
        <div class="col-md-2"></div>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'TopBar',
  data() {
    return {
      showAbout: false
    }
  },
  computed: {
    ...mapGetters(['user'])
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
