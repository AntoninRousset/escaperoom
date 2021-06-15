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
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import EngineEditorGrid from './EngineEditorGrid.vue'

// TODO repair leak: after lot of drag, the responsiveness decreases

export default {
  name: 'EngineEditor',
  components: { EngineEditorGrid },
  computed: {
    ...mapState('engine/editor', ['drag', 'step']),
    ...mapGetters('engine/editor', ['rootStates']),
  },
  created() {
    window.addEventListener('mouseup', this.mouseUp);
  },
  unmounted() {
    window.removeEventListener('mouseup', this.mouseUp);
  },
  methods: {
    ...mapActions('engine', ['pull', 'push']),
    ...mapMutations('engine', ['changeState']),
    ...mapMutations('engine/editor', ['setDrag']),
    mouseMove(event) {
      event.stopPropagation();
      event.preventDefault();

      if (this.drag) {
        const x = Math.round((event.clientX - this.drag.start.x)/this.step);
        const y = Math.round((event.clientY - this.drag.start.y)/this.step);
        if (this.drag.state.x + x >= 0 && this.drag.state.y + y >= 0) {
          this.drag.delta = { x, y };
        }
      }
    },
    mouseUp() {
      if (this.drag) {
        this.changeState({
          id: this.drag.state.id,
          x: this.drag.state.x + this.drag.delta.x,
          y: this.drag.state.y + this.drag.delta.y,
        })
        this.setDrag(null);
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor{
  position: relative;
}
</style>
