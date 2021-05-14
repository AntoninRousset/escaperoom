<template>
  <v-app>
    <v-navigation-drawer
      width="60"
      expand-on-hover
      permanent
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
      <v-container>
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
          title: 'Test',
          icon: 'mdi-test-tube',
          to: { 'name': 'Test' },
        },
      ]);
    }
    return { tabs };
  },
}
</script>
