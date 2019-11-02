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
        <a class="navbar-brand" href="/#/">SweFreq &mdash; The Swedish Frequency resource for genomics</a>
      </div>

      <div class="collapse navbar-collapse" id="navbar-things">
        <ul class="nav navbar-nav navbar-right">
          <li><a ng-click="showAbout = !showAbout" style="cursor: pointer">About</a>
          <li class="dropdown" v-if="this.$store.loggedIn == true"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">{{ this.$store.user.user }}<span class="caret"></span></a>
            <ul class="dropdown-menu">
              <li><a href="/profile" target="_self">User Profile</a></li>
              <li><a :href="'/logout?next=' + this.$route.query.page" target="_self" :title="'Logout ' + this.$store.user.user">Logout</a></li>
            </ul>
          </li>
          <li class="dropdown" v-if="this.$store.loggedIn == false">
            <a href="'/elixir/login?next=' + this.$route.query.page" target="_self">Login</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  <router-link to="/" class="navigation-link"><span>Search</span></router-link>
  <router-link to="/browse" class="navigation-link"><span>Browse</span></router-link>
</div>
</template>

<script>
export default {
  name: 'TopBar',
  data() {
    return {
    }
  }
}
</script>

<style scoped>
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
