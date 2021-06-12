<template>
  <div
    class="engine-editor"
    @mousemove="mouseMove"
  >
    <engine-editor-grid
      :states="rootStates"
    />
  </div>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';
import EngineEditorGrid from './EngineEditorGrid.vue'

// TODO repair leak: after lot of drag, the responsiveness decreases

export default {
  name: 'EngineEditor',
  components: { EngineEditorGrid },
  computed: {
    ...mapState('engine/editor', ['drag', 'step']),
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
  created() {
    window.addEventListener('mouseup', this.mouseUp);
  },
  unmounted() {
    window.removeEventListener('mouseup', this.mouseUp);
  },
  methods: {
    ...mapActions('engine', ['removeState', 'changeState', 'pull', 'push']),
    ...mapMutations('engine/editor', ['setDrag']),
    mouseMove(event) {
      event.stopPropagation();
      event.preventDefault();

      if (performance.now() - event.timeStamp > 200) {
        return  // catch up by dropping events
      }

      if (this.drag) {
        const delta = {
          x: Math.round((event.clientX - this.drag.start.x)/this.step),
          y: Math.round((event.clientY - this.drag.start.y)/this.step),
        };

        if (delta.x != this.drag.delta.x ||
            delta.y != this.drag.delta.y) {
          this.drag.delta = delta;

          if (this.drag.state.x + delta.x >= 0 &&
              this.drag.state.y + delta.y >= 0) {
            this.changeState({
              id: this.drag.state.id,
              x: this.drag.state.x + delta.x,
              y: this.drag.state.y + delta.y,
            });
          }
        }
      }
    },
    mouseUp() {
      this.setDrag(null);
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor{
  position: relative;
}
</style>
