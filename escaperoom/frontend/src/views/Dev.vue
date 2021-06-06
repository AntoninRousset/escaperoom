<template>
  <div>
    <h1>
      {{ title }}
      <router-link
        v-if="selected"
        :to="{name: 'Dev'}"
      >
        <v-icon size="x-large">
          mdi-format-list-bulleted
        </v-icon>
      </router-link>
    </h1>
    <router-view v-if="selected" />
    <router-link
      v-for="dev in devs"
      v-else
      :key="dev.title"
      :to="dev.to"
    >
      {{ dev.title }}
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Dev',
  data: () => ({
    devs: [
      {
        title: 'Engine',
        to: { 'name': 'Dev - engine' },
      },
    ],
  }),
  computed: {
    title() {
      return this.$route.name;
    },
    selected() {
      return this.$route.name != 'Dev';
    }
  },
}
</script>
