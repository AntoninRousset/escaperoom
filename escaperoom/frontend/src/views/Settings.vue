<template>
  <div>
    <h1>Settings</h1>
    <p>
      <label for="autoPull">Automatic pulling</label>
      <input
        v-model="autoPull"
        type="checkbox"
        name="autoPull"
      >
    </p>
    <p>
      <label for="autoPush">Automatic pushing</label>
      <input
        v-model="autoPush"
        type="checkbox"
        name="autoPush"
      >
    </p>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  computed: {
    autoPull: {
      get() { return this.$store.state.settings.autoPull; },
      set(autoPull) { this.$store.commit('settings/setAutoPull', autoPull) }
    },
    autoPush: {
      get() { return this.$store.state.settings.autoPush; },
      set(autoPush) { this.$store.commit('settings/setAutoPush', autoPush) }
    },
  },
}
</script>
