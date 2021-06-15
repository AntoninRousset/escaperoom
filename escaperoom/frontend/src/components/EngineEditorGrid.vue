<template>
  <div
    :style="{ 'width': width + 'px', 'height': height + 'px' }"
    class="engine-editor-grid"
  >
    <div
      v-for="state in states"
      :key="state.id"
      :ref="(element) => statesRefs.push(element)"
      class="engine-editor-state"
      :style="{ left: state.x*step + 'px', top: state.y*step + 'px', }"
      @mousedown="mouseDown($event, state)"
    >
      <div class="engine-editor-state-header">
        {{ state.name }}
      </div>
      <engine-editor-grid
        v-if="Object.keys(state.children).length > 0"
        :states="state.children"
      />
    </div>
  </div>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';

export default {
  name: 'EngineEditorGrid',
  props: {
    states: {
      required: true,
      type: Array,
    },
  },
  data: () => ({
    statesRefs: [],
    width: undefined,
    height: undefined,
  }),
  computed: {
    ...mapState('engine/editor', ['step']),
  },
  mounted() {
    this.observer = new MutationObserver(this.resizeToContent);
    this.observer.observe(this.$el, {
      attributes: true, childList: true, subtree: true,
    });
    this.resizeToContent();
  },
  beforeUnmount() {
    this.observer.disconnect();
  },
  methods: {
    ...mapActions('engine', ['pull', 'push']),
    ...mapMutations('engine/editor', ['setDrag']),
    resizeToContent() {
      let width = 0;
      let height = 0;
      const gridRect = this.$el.getBoundingClientRect()
      for (const stateRef of this.statesRefs) {
        const stateRect = stateRef.getBoundingClientRect();
        width = Math.max(stateRect.right - gridRect.left, width);
        height = Math.max(stateRect.bottom - gridRect.top, height);
      }
      this.width = width;
      this.height = height;
    },
    mouseDown(event, state) {
      this.setDrag({
        state: state,
        start: { x: event.clientX, y: event.clientY },
        delta: { x: 0, y: 0 },
      });
      event.stopPropagation();
      event.preventDefault();
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor-grid {
  position: relative;
}
.engine-editor-state {
  position: absolute;
  border: solid black 1px;
  .engine-editor-grid {
    margin: 10px;
  }
}
.engine-editor-state-header {
  background: red;
}
</style>
