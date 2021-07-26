<template>
  <div
    ref="state"
    class="engine-editor-state"
    :style="{ left: state.x*step + 'px', top: state.y*step + 'px', }"
  >
    <div class="bg-red pa-1 d-flex justify-space-between">
      <span style="user-select: none;">
        {{ state.name ? state.name : "No name" }}
      </span>
      <div
        class="mx-1"
        @click="removeState({ id: state.id })"
      >
        X
      </div>
    </div>
    <slot />
  </div>
</template>

<script>
import { mapMutations, mapState } from 'vuex';

export default {
  name: 'EngineEditorState',
  props: {
    state: {
      default: null,
      type: Object,
    },
  },
  computed: {
    ...mapState('engine/editor', ['step']),
  },
  methods: {
    ...mapMutations('engine', ['changeState', 'removeState']),
    getBoundingClientRect() {
      if (this.$refs['state']) {  // undefined on delete
        return this.$refs['state'].getBoundingClientRect();
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor-state {
  position: absolute;
  border: solid black 1px;
  .engine-editor-grid {
    margin: 10px;
  }
}
</style>
