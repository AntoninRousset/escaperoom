<template>
  <div
    :style="{ 'width': width + 'px', 'height': height + 'px' }"
    class="engine-editor-grid"
    @dblclick="doubleclick($event)"
  >
    <svg
      :height="height"
      :width="width"
    >
      <engine-editor-transition
        v-for="transition in transitions"
        :key="transition.id"
        :transition="transition"
      />
    </svg>
    <engine-editor-state
      v-for="state in states"
      :key="state.id"
      :ref="(element) => statesRefs.push(element)"
      :state="state"
      @mousedown="mouseDown($event, state)"
    >
      <engine-editor-grid
        v-if="Object.keys(state.children).length > 0"
        :states="state.children"
        :transitions="perStateTransitions[state.id] || []"
        :parent-state="state"
      />
    </engine-editor-state>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
import EngineEditorState from './State.vue'
import EngineEditorTransition from './Transition.vue'

export default {
  name: 'EngineEditorGrid',
  components: { EngineEditorState, EngineEditorTransition },
  props: {
    parentState: {
      default: null,
      type: Object,
    },
    states: {
      required: true,
      type: Array,
    },
    transitions: {
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
    ...mapGetters('engine/editor', ['perStateTransitions']),
    ...mapState('engine/editor', ['step']),
  },
  mounted() {
    this.observer = new MutationObserver((mutations) => {
      let sizeChanged = false;
      for (const mutation of mutations) {
        switch (mutation.type) {
          case 'attributes':
            if (mutation.attributeName == 'style') {
              sizeChanged = true;
            }
            break;
          case 'childList':
            sizeChanged = true;
            break;
        }
      }
      if (sizeChanged) {
        this.resizeToContent();
      }
    });
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
    ...mapMutations('engine', ['addState', 'removeState']),
    ...mapMutations('engine/editor', ['setDrag']),
    doubleclick(event) {
      const x = Math.round(event.layerX/this.step);
      const y = Math.round(event.layerY/this.step);
      this.addState({ room: 1, parent: this.parentState, x, y });

      event.stopPropagation();
      event.preventDefault();
    },
    resizeToContent() {
      let width = 0;
      let height = 0;
      const gridRect = this.$el.getBoundingClientRect()
      for (const stateRef of this.statesRefs) {
        if (stateRef) {
          const stateRect = stateRef.getBoundingClientRect();
          if (stateRect) {
            width = Math.max(stateRect.right - gridRect.left, width);
            height = Math.max(stateRect.bottom - gridRect.top, height);
          }
        }
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
    },
  },
}
</script>

<style lang="scss">
input {
  width: 100%;
}
.engine-editor-grid {
  position: relative;
  margin: 20px;
}
</style>
