<template>
  <div>
    <h1>{{ title }}</h1>
    <engine-editor />
  </div>
</template>

<script>
import { EngineEditor } from '../components/EngineEditor'

export default {
  name: 'Engine',
  components: { EngineEditor },
  computed: {
    title() {
      return this.$route.name;
    },
  },
}
</script>
