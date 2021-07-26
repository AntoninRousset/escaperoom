<template>
  <line
    ref="transition"
    :x1="transition.src.x * step"
    :y1="transition.src.y * step"
    :x2="transition.dest.x * step"
    :y2="transition.dest.y * step"
    :style="{ stroke: color, strokeWidth: width }"
  />
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex';

export default {
  name: 'EngineEditorTransition',
  props: {
    transition: {
      default: null,
      type: Object,
    },
  },
  data: () => ({
    color: '#000000',
    width: '2',
  }),
  computed: {
    ...mapState('engine/editor', ['step']),
  },
  methods: {
    ...mapActions('engine', ['pull', 'push']),
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
.engine-editor-transition {}
</style>
