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
        icon: 'mdi-cog-outline',
        to: { 'name': 'Engine' },
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
    return { tabs };
  },
  created() {
    window.document.title = import.meta.env.VITE_APP_TITLE;
    this.$store.dispatch('engine/pull')
  },
}
</script>
