<template>
<div class="container">
  <div v-if="error">
    <div class="row">
      <div class="col-sm-12">
        <h1>{{ error }}</h1>
      </div>
    </div>
  </div>
  <div v-else>
    <!-- About me -->
    <div class="row">
      <div class="col-sm-12">
        <h1>About me</h1>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-12">
        <form class="form-horizontal" role="form" name="requestForm">
          <div class="form-group">
            <label for="user_name" class="col-sm-2 control-label">Name</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="user-name" :value="user.user" :disabled="true" placeholder="Your name">
            </div>
          </div>
          <div class="form-group">
            <label for="email" class="col-sm-2 control-label">E-mail</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="email" :value="user.email" required :disabled="true" placeholder="Your e-mail">
            </div>
          </div>
          <div class="form-group">
            <label for="affiliation" class="col-sm-2 control-label">Affiliation</label>
            <div class="col-sm-4">
              <input type="text" class="form-control" id="affiliation" name="affiliation" required :disabled="true" v-model="affiliation" placeholder="Your affiliation">
            </div>
          </div>
          <div class="form-group">
            <label for="country" class="col-sm-2 control-label">Country</label>
            <div class="col-sm-4">
              <select name="country" class="form-control" id="country"  v-model="country" required>
                <option value="">-- Select country --</option>
                <option v-for="country in availableCountries" :key="country.name" :value="country.name">{{country.name}}</option>
              </select>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Dataset Access -->
    <div class="row">
      <div class="col-sm-12">
        <h1>Dataset Access</h1>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-12">
        <table class="table table-striped">
          <tbody>
            <tr>
              <th>Dataset</th>
              <th>Subscribed to email updates</th>
              <th>Access</th>
            </tr>
            <tr v-for="row in userDatasets" :key="row.shortName">
              <td>{{row.shortName}}</td>
              <td>{{row.email ? "Yes" : "No"}}</td>
              <td>{{row.access ? (row.isAdmin ? "Admin" : "Approved" ) : "Request pending" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
      
    <!-- sFTP Access -->
    <div v-if="isAdmin">
      <div class="row">
        <div class="col-sm-12">
          <h1>sFTP Access</h1>
        </div>
      </div>
      <div class="row">
        <div class="col-sm-12">
          <table class="table table-striped">
            <tbody>
              <tr>
                <th>Username</th>
                <th>Password</th>
                <th>Expiry date</th>
                <th></th>
              </tr>
              <tr>
                <td>{{ sftp.user }}</td>
                <td>{{ sftp.password }}</td>
                <td>{{ sftp.expires }}</td>
                <td><button type="button" @click="createSFTPCredentials" class="btn btn-primary form-control">Generate Credentials</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'UserProfile',

  data() {
    return {
      affiliation: '',
      country: '',
      error: '',
      isAdmin: false,
      sftp: null,
      userDatasets: [],
    }
  },

  watch: {
    user: function () {
      this.affiliation = this.user.affiliation;
      this.country = this.user.country;
    }
  },

  computed: {
    ...mapGetters(['availableCountries', 'user'])
  },

  created() {
    this.$store.dispatch('getCountries');
    axios.get("/api/users/datasets")
      .then((response) => {
        this.userDatasets = response.data.data;
        this.userDatasets.forEach(function(dataset) {
          this.isAdmin = this.isAdmin | dataset.isAdmin;
        }, this);
      });
    this.affiliation = this.user.affiliation;
    this.country = this.user.country;

    this.getSFTPCredentials();
  },

  methods: {
    getXsrf() {
      let name = "_xsrf=";
      let decodedCookie = decodeURIComponent(document.cookie);
      let ca = decodedCookie.split(';');
      for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return ""
    },

    createSFTPCredentials () {
      let body = {
        '_xsrf': this.getXsrf()
      };
      axios({
        method: 'post',
        url: "/api/users/sftp_access",
        data: Object.keys(body).map(function(k) {
          return encodeURIComponent(k) + '=' + encodeURIComponent(body[k])
        }).join('&'),
        headers : {
          "Content-Type": "application/x-www-form-urlencoded;",

        }})
        .then((response) => {
          this.sftp = response.data;
        });
    },

    getSFTPCredentials () {
      axios.get("/api/users/sftp_access")
        .then((response) => {
          this.sftp = response.data;
        });
    },
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
