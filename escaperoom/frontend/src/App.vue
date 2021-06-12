<template>
  <v-app>
    <v-navigation-drawer
      :model-value="true"
      permanent
      width="60"
    >
      <router-link
        v-for="tab in tabs"
        :key="tab.title"
        :to="tab.to"
      >
        <v-icon size="x-large">
          {{ tab.icon }}
        </v-icon>
      </router-link>
    </v-navigation-drawer>
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'App',
  data: () => {
    let tabs = [
      {
        title: 'Dashboard',
        icon: 'mdi-home',
        to: { 'name': 'Dashboard' }
      },
      {
        title: 'Engine',
        icon: 'mdi-abacus',
        to: { 'name': 'Engine' },
      },
      {
        title: 'Settings',
        icon: 'mdi-cog-outline',
        to: { 'name': 'Settings' },
      },
    ];
    if (process.env.NODE_ENV == 'development') {
      Array.prototype.push.apply(tabs, [
        {
          title: 'Dev',
          icon: 'mdi-test-tube',
          to: { 'name': 'Dev' },
        },
      ]);
    }
    return {
      tabs,
    };
  },
  computed: {
      ...mapState('settings', ['autoPull', 'autoPush']),
  },
  watch: {
    autoPull: {
      immediate: true,
      handler(autoPull, oldAutoPull) {
        if (autoPull && ! oldAutoPull) {
          this.startAutoPull();
        }
      }
    },
    autoPush: {
      immediate: true,
      handler(autoPush, oldAutoPush) {
        if (autoPush && ! oldAutoPush) {
          this.startAutoPush();
        }
      }
    },
  },
  created() {
    window.document.title = import.meta.env.VITE_APP_TITLE;
  },
  methods: {
    ...mapActions('engine', ['pull', 'push']),
    startAutoPull() {
      if (this.autoPull) {
        this.pull().finally(() => { setTimeout(this.startAutoPull, 200); });
      }
    },
    startAutoPush() {
      if (this.autoPush) {
        this.push().finally(() => { setTimeout(this.startAutoPush, 200); });
      }
    },
  },
}
</script>
