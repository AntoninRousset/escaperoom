<template>
  <div class="engine-editor">
    <engine-editor-grid :states="rootStates" />
  </div>
</template>

<script>
import EngineEditorGrid from '@/components/EngineEditorGrid.vue'

export default {
  name: 'EngineEditor',
  components: { EngineEditorGrid },
  data() {
    return {
    }
  },
  computed: {
    rootStates() {
      const states = this.$store.getters['engine/states'];
      const rootStates = [];
      states.forEach((state) => {
        state.children = state.children || [];
        if (state.parent) {
          state.parent.children = state.parent.children || [];
          state.parent.children.push(state);
        }
        if (! state.parent) {
          rootStates.push(state);
        }
      });
      return rootStates;
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor{
  position: relative;
}
</style>
