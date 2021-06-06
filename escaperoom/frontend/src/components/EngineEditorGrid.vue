<template>
  <div
    :style="{ 'min-width': width + 'px', 'min-height': height + 'px' }"
    class="engine-editor-grid"
  >
    <engine-editor-state
      v-for="state in states"
      :key="state.id"
      :state="state"
    />
  </div>
</template>

<script>
import EngineEditorState from '@/components/EngineEditorState.vue'

export default {
  name: 'EngineEditorGrid',
  components: { EngineEditorState },
  props: {
    states: {
      required: true,
      type: Array,
    },
  },
  data: () => ({
    width: null,
    height: null,
  }),
  mounted() {
    this.observer = new MutationObserver(this.resizeToContent);
    this.observer.observe(this.$el, {
      attributes: true, childList: false, subtree: false
    });
    this.resizeToContent();
  },
  beforeUnmount() {
    this.observer.disconnect();
  },
  methods: {
    resizeToContent() {
      this.width = this.$el.scrollWidth;
      this.height = this.$el.scrollHeight;
    },
  },
}
</script>

<style lang="scss" scoped>
.engine-editor-grid {
  position: relative;
}
</style>
