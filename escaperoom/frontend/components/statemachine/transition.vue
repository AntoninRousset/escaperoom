<template>
  <path
  :d="path"
  fill="none"
  stroke="#aaa"
  stroke-width="2px"
  marker-end="url(#triangle)"/>
</template>

<script>
import {mapState} from 'vuex'

export default {

	name: 'ETransition',
  mixins: [],
  props: {
    'i': {
      type: Number,
    },
    'points': {
      type: Array,
      default: [],
    },
  },
  emits: [],

  computed: {
    path() {
      let points = this.points.map(p => `${p.x} ${p.y}`)
      return 'M ' + points.join(' L ')
    },
  }

}
</script>

<style lang="scss">
	@import "../../scss/colors.scss";

  path {
 }
</style>
