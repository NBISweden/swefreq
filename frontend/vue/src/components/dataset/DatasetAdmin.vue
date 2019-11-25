<template>
<div class="dataset-admin">
  <div v-if="!dataset.isAdmin">
    <p>You need to be logged in as an admin to use this page.</p>
  </div>
  <div v-else>
    <div class="container">
      <div class="row">
        <div class="admin-bar">
          <ul class="nav nav-tabs pull-right">
            <li class="active"><a data-target="#pending" data-toggle="tab">Pending requests</a></li>
            <li><a data-target="#approved" data-toggle="tab">Approved users</a></li>
            <li><a data-target="#emaillist" data-toggle="tab">Email list</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="tab-content">
      <div class="tab-pane active" id="pending">
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th></th>
                <th>Name</th>
                <th>E-mail</th>
                <th>Affiliation</th>
                <th>Country</th>
                <th>Applied date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in users.pending" :key="row.email">
                <td>
                  <div class="btn btn-primary btn-xs" data-toggle="tooltip" title="Give the user access" @click="approveUser(row)">Approve</div>
                  <div class="btn btn-danger btn-xs" data-toggle="tooltip" title="Deny access" @click="revokeUser(row)">Deny</div>
                </td>
                <td>{{row.user}}</td>
                <td>{{row.email}}</td>
                <td>{{row.affiliation}}</td>
                <td>{{row.country}}</td>
                <td>{{row.applyDate}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="tab-pane" id="approved">
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th></th>
                <th>Name</th>
                <th>E-mail</th>
                <th>Affiliation</th>
                <th>Country</th>
                <th>Applied date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in users.current" :key="row.email">
                <td>
                  <div class="btn btn-danger btn-xs" data-toggle="tooltip" title="Deny access" @click="revokeUser(row)">Revoke</div>
                </td>
                <td>{{row.user}}</td>
                <td>{{row.email}}</td>
                <td>{{row.affiliation}}</td>
                <td>{{row.country}}</td>
                <td>{{row.applyDate}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="tab-pane" id="emaillist">
        <span v-for="user in users.current" :key="user.name">
          <span v-if="user.newsletter">
            {{user.email}},
          </span>
        </span>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import axios from 'axios';

export default {
  name: 'DatasetAdmin',
  
  data() {
    return {
      users: {},
      nr_updates: 0,
      error: '',
    }
  },
  
  props: ['currentPage', 'datasetName'],
  
  computed: {
    ...mapGetters(['dataset', 'user'])
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

    getUsers() {
      let users = {"pending": [], "current": []};
      axios.get( "/api/dataset/" + this.datasetName + "/users_pending" )
        .then(function(request) {
          users.pending = request.data.data;
        }
             ),
      axios.get( "/api/dataset/" + this.datasetName + "/users_current" )
        .then(function(request) {
          users.current = request.data.data;
        });
      this.users = users;
    },

    approveUser(user) {
      axios({
        method: 'post',
        url: "/api/dataset/" + this.datasetName + "/users/" + user.email + "/approve",
        params: {
          "_xsrf": this.getXsrf("_xsrf")
        },
      })
        .then(() => {
          this.getUsers();
        });
    },

    revokeUser(user) {
      axios({
        method: 'post',
        url: "/api/dataset/" + this.datasetName + "/users/" + user.email + "/revoke",
        params: {
          "_xsrf": this.getXsrf("_xsrf")
        }
      })
        .then(() => {
          this.getUsers();
        });
    },
  },
  created () {
    this.getUsers();
  }
};

</script>

<style scoped>
</style>
