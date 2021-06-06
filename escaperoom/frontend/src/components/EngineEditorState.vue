<template>
  <div
    class="engine-editor-state"
    :style="{ left: x + 'px', top: y + 'px', }"
  >
    <div class="engine-editor-state-header">
      {{ state.name }}
    </div>
    <engine-editor-grid
      v-if="Object.keys(state.children).length > 0"
      :states="state.children"
    />
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'

export default {
  name: 'EditorState',
  components: {
    EngineEditorGrid: defineAsyncComponent(
      () => import('@/components/EngineEditorGrid.vue')
    ),
  },
  props: {
    state: {
      type: Object,
      required: true,
    },
  },
  computed: {
    x() {
      return 50*this.state.x;
    },
    y() {
      return 50*this.state.y;
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor-state {
  position: absolute;
  border: solid black 1px;
}
.engine-editor-state-header {
  background: red;
}
.engine-editor-grid {
  margin: 10px;
}
</style>
