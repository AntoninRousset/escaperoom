<template>
  <div
    class="engine-editor"
    @dragover="dragOver"
    @dragend="dragEnd"
  >
    <v-btn
      @click="pull"
    >
      pull
    </v-btn>
    <v-btn
      @click="push"
    >
      push
    </v-btn>
    <engine-editor-grid
      :states="rootStates"
    />
  </div>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';
import EngineEditorGrid from '@/components/EngineEditorGrid.vue'

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
  methods: {
    ...mapActions('engine', ['removeState', 'changeState', 'pull', 'push']),
    ...mapMutations('engine/editor', ['setDrag']),
    dragOver(event) {
      if (performance.now() - event.timeStamp > 200) {
        // catch up by dropping events
        return
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
    dragEnd() {
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
