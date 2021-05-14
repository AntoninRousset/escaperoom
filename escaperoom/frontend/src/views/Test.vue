<template>
  <div>
    <h1>{{ title }}
      <router-link
        v-if="selected"
        :to="{name: 'Test'}"
      >
        <v-icon size="x-large">
          mdi-format-list-bulleted
        </v-icon>
      </router-link>
    </h1>
    <router-view v-if="selected" />
    <router-link
      v-else
      v-for="test in tests"
      :key="test.title"
      :to="test.to"
    >
     Test engine
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Test',
  data: () => ({
    tests: [
      {
        title: 'Engine',
        to: { 'name': 'Test - engine' },
      },
    ],
  }),
  computed: {
    title() {
      return this.$route.name;
    },
    selected() {
      return this.$route.name != 'Test';
    }
  },
}
</script>
