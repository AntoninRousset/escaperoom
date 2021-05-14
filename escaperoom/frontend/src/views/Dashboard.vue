<template>
  <div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script>
export default {
  name: 'Test',
  computed: {
    title() {
      return this.$route.name;
    },
  },
}
</script>
